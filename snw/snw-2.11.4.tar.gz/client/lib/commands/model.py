import gzip
import json
import logging
import os
import sys
from collections import Counter
import tarfile

import requests
import six
from io import BytesIO
from prettytable import PrettyTable

from lib import utils
import client.launcher as launcher

launcher.LOGGER = logging.getLogger()


class Model:
    def __init__(self, options, auth):
        self.options = options
        self.auth = auth
        self.is_json = self.options.display == "JSON"

    def list(self):
        if self.options.skip_noscores and self.options.scores is None:
            raise RuntimeError('cannot use --skip_noscores without --scores')
        if self.options.has_noscores and self.options.scores is None:
            raise RuntimeError('cannot use --has_noscores without --scores')
        if self.options.has_noscores and self.options.skip_noscores:
            raise RuntimeError('cannot use --has_noscores with --skip_noscores')
        if self.options.show_pruned and self.options.only_show_pruned:
            raise RuntimeError('cannot use --show_pruned with --only_show_pruned')
        params = {'source': self.options.source,
                  'target': self.options.target,
                  'model': self.options.model,
                  'tags': self.options.tags}
        if self.options.scores is not None:
            params['scores'] = ",".join(self.options.scores)
        elif self.options.avg_scores:
            params['scores'] = ''
        if self.options.count:
            r = requests.get(os.path.join(self.options.url, "model/lp/list"), auth=self.auth)
            if r.status_code != 200:
                raise RuntimeError('incorrect result from \'model/lp/list\' service: %s' % r.text)
            response = r.json()
            if not self.is_json:
                res = PrettyTable(["LP", "#Models"])
                for item in response:
                    res.add_row([item["lp"], int(item["count_model"])])
            else:
                res = response
        else:
            r = requests.get(os.path.join(self.options.url, "model/list"),
                             params=params, auth=self.auth)
            if r.status_code != 200:
                raise RuntimeError('incorrect result from \'model/list\' service: %s' % r.text)
            response = r.json()
            result = []
            metrics = Counter()
            for item in response:
                if utils.check_condition_to_get_model(self.options, item):
                    if self.options.scores is not None or self.options.avg_scores:
                        new_scores = {}
                        total_score = 0
                        for p, v in six.iteritems(item['scores']):
                            if not self.is_json:
                                if isinstance(v, float):
                                    v = {'BLEU': v}
                                elif isinstance(v, dict) and "score" in v:
                                    v = v['score']
                                for m in v:
                                    metrics[m] += 1
                                v = v.get(self.options.metric)
                            if v is not None:
                                new_scores[p] = v
                                total_score += v
                        item['scores'] = new_scores
                        item['avg_score'] = total_score/len(new_scores) if new_scores else 0
                    result.append(item)
            if not self.is_json:
                scorenames = {}
                bestscores = {}

                # Calculate the aggregate sentence feed
                idx_result = {}
                root = []
                for r in result:
                    r['children_models'] = []
                    idx_result[r['lp'] + ":" + r['model']] = r
                for k, v in six.iteritems(idx_result):
                    parent_model = v['parent_model']
                    if 'parent_model' in v and v['parent_model'] is not None and \
                            v['lp'] + ":" + v['parent_model'] in idx_result:
                        p = v['lp'] + ":" + v['parent_model']
                        idx_result[p]['children_models'].append(k)
                    else:
                        root.append(k)
                utils.cum_sentenceCount(root, idx_result, 0)

                idx_result = {}
                root = []
                if self.options.aggr:
                    aggr_result = {}
                    for r in result:
                        model = r["model"]
                        q = model.find("_")
                        if q != -1:
                            q = model.find("_", q + 1)
                            model = model[q + 1:]
                            q = model.find("_")
                            if q != -1:
                                model = model[:q]
                        lpmodel = r["lp"]
                        if self.options.aggr == 'model':
                            lpmodel += ":" + model
                        if lpmodel not in aggr_result:
                            line_data = {'lp': r["lp"], 'cumSentenceCount': 0, 'date': 0,
                                         'model': '', 'scores': {}, 'count': 0,
                                         'imageTag': ''}
                            if self.options.show_owner:
                                line_data['owner'] = ''

                            aggr_result[lpmodel] = line_data
                            if self.options.aggr == 'model':
                                aggr_result[lpmodel]["imageTag"] = r["imageTag"]
                                aggr_result[lpmodel]["model"] = model
                                if self.options.show_owner:
                                    owner_obj = r.get('owner')
                                    aggr_result[lpmodel]["owner"] = owner_obj[
                                        "entity_code"] if owner_obj else ""

                        aggr_result[lpmodel]['count'] += 1
                        for s, v in six.iteritems(r['scores']):
                            if s not in aggr_result[lpmodel]['scores'] or \
                                    aggr_result[lpmodel]['scores'][s] < v:
                                aggr_result[lpmodel]['scores'][s] = v
                        if r["date"] > aggr_result[lpmodel]['date']:
                            aggr_result[lpmodel]['date'] = r["date"]
                        if r["cumSentenceCount"] > aggr_result[lpmodel]['cumSentenceCount']:
                            aggr_result[lpmodel]['cumSentenceCount'] = r["cumSentenceCount"]
                    result = [aggr_result[k] for k in aggr_result]
                for r in result:
                    r['children_models'] = []
                    lpmodel = r["lp"] + ":" + r["model"]
                    if 'parent_model' in r and r['parent_model'] is not None:
                        r["parent_model"] = r["lp"] + ':' + r["parent_model"]
                    idx_result[lpmodel] = r
                    for s, v in six.iteritems(r['scores']):
                        scorenames[s] = scorenames.get(s, 0) + 1
                        if s not in bestscores or v > bestscores[s]:
                            bestscores[s] = v
                for k, v in six.iteritems(idx_result):
                    if 'parent_model' in v and v['parent_model'] in idx_result:
                        p = v['parent_model']
                        idx_result[p]['children_models'].append(k)
                    else:
                        root.append(k)
                max_depth = utils.tree_depth(0, root, idx_result)
                model_maxsize = max_depth + 42
                scorenames_key = [] if self.options.scores is None else sorted(scorenames.keys())
                scoretable = []
                scorecols = []
                for i in range(len(scorenames_key)):
                    scorecols.append("T%d" % (i + 1))
                    scoretable.append("\tT%d:\t%s\t%d" % (i + 1, scorenames_key[i],
                                                          scorenames[scorenames_key[i]]))
                if self.options.quiet:
                    res = []
                    utils.tree_display(res, 0, root, idx_result, model_maxsize,
                                       scorenames_key, bestscores, self.options.avg_scores, self.options.skip_noscores,
                                       self.options.has_noscores, self.options.show_owner,
                                       self.options.show_pruned, self.options.only_show_pruned,
                                       self.options.quiet)
                else:
                    header = ["Date", "LP", "Type", "Model ID", "#Sentences"]
                    if self.options.show_owner:
                        header.append("Owner")
                    if self.options.show_pruned:
                        header.append("Pruned")
                    if self.options.avg_scores:
                        header.append("Average scores")
                    res1 = PrettyTable(header + scorecols)
                    res1.align["Model ID"] = "l"
                    utils.tree_display(res1, 0, root, idx_result, model_maxsize,
                                       scorenames_key, bestscores, self.options.avg_scores, self.options.skip_noscores,
                                       self.options.has_noscores, self.options.show_owner,
                                       self.options.show_pruned, self.options.only_show_pruned,
                                       self.options.quiet)
                    res = [res1]
                    res.append('* TOTAL: %d models\n' % len(result))
                    if metrics:
                        res.append("* AVAILABLE METRICS: %s" % ", ".join(metrics.keys()))
                    if len(scoretable):
                        res.append("* TESTSET:")
                        res.append('\n'.join(scoretable) + "\n")
            else:
                res = result
        return res

    def describe(self):
        r = requests.get(os.path.join(self.options.url, "model/describe", self.options.model),
                         auth=self.auth)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'service/describe\' service: %s' % r.text)
        res = r.json()
        return res

    def tagadd(self):
        taglist = []
        for tag in self.options.tags:
            taglist.append({'tag': tag})
        data = {
            'tags': taglist
        }
        r = requests.put(os.path.join(self.options.url, "model", self.options.model, "tags"),
                         auth=self.auth, json=data)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'model/tagadd\' service: %s' % r.text)
        res = "ok new tags \"%s\" attached to model %s" % (",".join(self.options.tags),
                                                           self.options.model)
        return res

    def tagdel(self):
        taglist = []
        for tag in self.options.tags:
            taglist.append({'tag': tag})
        data = {
            'tags': taglist
        }
        r = requests.delete(os.path.join(self.options.url, "model", self.options.model, "tags"),
                            auth=self.auth,
                            json=data)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'model/tagadd\' service: %s' % r.text)
        res = "ok tags \"%s\" are removed from model %s" % (",".join(self.options.tags),
                                                            self.options.model)
        return res

    def share(self):
        data = {
            'visibility': 'share',
            'model': self.options.model,
            'entity': self.options.entity_code
        }
        r = requests.post(os.path.join(self.options.url, "model", "visibility", "add"),
                          auth=self.auth, json=data)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'model/share\' service: %s' % r.text)
        res = 'ok model %s shared with entity %s' % (self.options.model, self.options.entity_code)
        return res

    def removeshare(self):
        data = {
            'visibility': 'share',
            'model': self.options.model,
            'entity': self.options.entity_code
        }
        r = requests.post(os.path.join(self.options.url, "model", "visibility", "delete"),
                          auth=self.auth,
                          json=data)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'model/removeshare\' service: %s' % r.text)
        res = 'ok share visibility removed on model %s for entity %s' % \
              (self.options.model, self.options.entity_code)
        return res

    def open(self):
        data = {
            'visibility': 'open',
            'model': self.options.model,
            'entity': self.options.entity_code
        }
        r = requests.post(os.path.join(self.options.url, "model", "visibility", "add"),
                          auth=self.auth,
                          json=data)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'model/open\' service: %s' % r.text)
        res = 'ok model %s opened with entity %s' % (self.options.model, self.options.entity_code)
        return res

    def removeopen(self):
        data = {
            'visibility': 'open',
            'model': self.options.model,
            'entity': self.options.entity_code
        }
        r = requests.post(os.path.join(self.options.url, "model", "visibility", "delete"),
                          auth=self.auth,
                          json=data)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'model/removeopen\' service: %s' % r.text)
        res = 'ok open visibility removed on model %s for entity %s' % \
              (self.options.model, self.options.entity_code)
        return res

    def get(self):
        if not self.options.file:
            if self.options.output:
                if not os.path.isdir(self.options.output):
                    raise Exception("Output is not a existing directory: %s" % self.options.output)
                output_path = self.options.output
            else:
                output_path = os.getcwd()
            r = requests.get(os.path.join(self.options.url, "model/listfiles", self.options.model),
                             auth=self.auth)
            if r.status_code != 200:
                raise RuntimeError('incorrect result from \'model/listfiles\' service: %s' % r.text)
            list_files = [f.split('/')[1] for f in list(r.json().keys())]
            if not list_files:
                raise Exception("Model does not exist any files: %s" % self.options.model)
            try:
                os.makedirs(os.path.join(output_path, self.options.model))
            except FileExistsError:
                pass
            for file in list_files:
                if file != '':
                    g = requests.get(os.path.join(self.options.url, "model/getfile/",
                                                  self.options.model, file),
                                     params={'is_compressed': True}, auth=self.auth)
                    if g.status_code != 200:
                        raise RuntimeError('incorrect result from \'model/getfile\' service: %s' % g.text)
                    with open(os.path.expanduser(os.path.join(output_path, self.options.model, file)),
                              'wb+') as output:
                        output.write(gzip.GzipFile('', 'r', 0, BytesIO(g.content)).read())
            sys.exit(0)

        with open(os.path.expanduser(self.options.output), 'wb+') \
                if self.options.output else sys.stdout as output:
            r = requests.get(os.path.join(self.options.url, "model/getfile/",
                                          self.options.model, self.options.file),
                             params={'is_compressed': True}, auth=self.auth)
            if r.status_code != 200:
                raise RuntimeError('incorrect result from \'model/getfile\' service: %s' % r.text)

            if self.options.output:
                output.write(gzip.GzipFile('', 'r', 0, BytesIO(r.content)).read())
            else:
                utils.write_to_stdout(gzip.GzipFile('', 'r', 0, BytesIO(r.content)).read())
            sys.exit(0)

    def delete(self):
        allres = []
        for m in self.options.models:
            if self.options.dryrun or not self.options.force:
                params = {'recursive': self.options.recursive, 'dryrun': True,
                          'include_released': self.options.include_released}
                r = requests.get(os.path.join(self.options.url,
                                              "model/delete/%s/%s/%s" % (self.options.source,
                                                                         self.options.target,
                                                                         m)),
                                 params=params, auth=self.auth)
                if r.status_code == 200:
                    mres = r.json()
                    if not mres:
                        launcher.LOGGER.info(
                            'Cannot find any models that are allowed to be deleted. '
                            + 'If you want to delete release models, use "include_released" option.')
                        continue
                else:
                    launcher.LOGGER.error('Cannot remove %s (%s)' % (m, r.text))
                    continue
                if m not in mres:
                    launcher.LOGGER.info('%s %d child(ren) of the model %s:\n\t%s' % (
                        self.options.dryrun and 'Without "--dryrun" option, will remove' or 'Removing', len(mres), m,
                        "\n\t".join(mres)))
                else:
                    launcher.LOGGER.info('%s %s and %d child(ren):\n\t%s' % (
                        self.options.dryrun and 'Without "--dryrun" option, will remove' or 'Removing', m,
                        len(mres) - 1, "\n\t".join(mres)))
            confirm = self.options.force
            if self.options.dryrun:
                continue
            confirm = confirm or launcher.confirm()
            if confirm:
                params = {'recursive': self.options.recursive, 'include_released': self.options.include_released}
                r = requests.get(os.path.join(self.options.url,
                                              "model/delete/%s/%s/%s" % (self.options.source,
                                                                         self.options.target,
                                                                         m)),
                                 params=params, auth=self.auth)
                if r.status_code == 200:
                    mres = r.json()
                    launcher.LOGGER.info('  => %d models removed: %s' % (len(mres), " ".join(mres)))
                    allres += mres
                else:
                    launcher.LOGGER.error('Cannot remove %s (%s)' % (m, r.text))
            else:
                launcher.LOGGER.info("  ... skipping")
        res = "Total %d models removed" % len(allres)
        return res

    def add(self):
        if not os.path.exists(self.options.file):
            raise RuntimeError('file `%s` does not exists' % self.options.file)
        if not self.options.file.endswith(".tgz"):
            raise RuntimeError('file `%s` should be a .tgz file' % self.options.file)
        filename = os.path.basename(self.options.file)[:-4]
        parts = filename.split('_')
        if len(parts) < 4 or len(parts) > 5:
            raise RuntimeError('incorrect model naming: %s' % filename)
        trid = parts.pop(0)
        lp = parts.pop(0)
        name = parts.pop(0)
        nn = parts.pop(0)
        tar = tarfile.open(self.options.file, "r:gz")
        try:
            f = tar.extractfile("%s/config.json" % filename)
            content = f.read()
            config_json = json.loads(content)
        except Exception as e:
            raise ValueError('cannot extract `%s/config.json` from model: %s' % (filename, str(e)))
        if config_json["model"] != filename:
            raise ValueError(
                'model name does not match directory %s/%s' % (config_json["model"], filename))

        params = {
            "ignore_parent": self.options.ignore_parent,
            "compute_checksum": self.options.compute_checksum,
            "name": self.options.name
        }
        files = {'tgz': (filename, open(self.options.file, mode='rb'), 'application/octet-stream')}
        r = requests.post(os.path.join(self.options.url, "model", "add", filename),
                          auth=self.auth, params=params, files=files)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'model/add\' service: %s' % r.text)
        res = r.json()
        return res

    def detail(self):
        res = utils.show_model_files_list(url=self.options.url, auth=self.auth,
                                          model_name=self.options.model,
                                          directory=self.options.directory)
        return res

    def prune(self):
        launcher.LOGGER.info("Pruning model %s:" % self.options.model)
        confirm = launcher.confirm()
        prune_model_count = 0
        if confirm:
            data = json.dumps({"include_released": self.options.include_released})
            r = requests.post(os.path.join(self.options.url, "model/prune", self.options.model), data=data,
                              auth=self.auth)
            if r.status_code == 200:
                prune_model_count += 1
                launcher.LOGGER.info("Model has been pruned: %s" % self.options.model)
            else:
                launcher.LOGGER.error('Cannot prune model %s: %s' % (self.options.model, r.text))
        else:
            launcher.LOGGER.info("  ... skipping")

        res = "%d model(s) pruned" % prune_model_count
        return res

    def execute_command(self):
        result = None
        if self.options.subcmd == "list":
            result = self.list()
        if self.options.subcmd == "get":
            result = self.get()
        if self.options.subcmd == "delete":
            result = self.delete()
        if self.options.subcmd == "add":
            result = self.add()
        if self.options.subcmd == "describe":
            result = self.describe()
        if self.options.subcmd == "tagadd":
            result = self.tagadd()
        if self.options.subcmd == "tagdel":
            result = self.tagdel()
        if self.options.subcmd == "share":
            result = self.share()
        if self.options.subcmd == "removeshare":
            result = self.removeshare()
        if self.options.subcmd == "open":
            result = self.open()
        if self.options.subcmd == "removeopen":
            result = self.removeopen()
        if self.options.subcmd == "detail":
            result = self.detail()
        if self.options.subcmd == "prune":
            result = self.prune()
        return result
