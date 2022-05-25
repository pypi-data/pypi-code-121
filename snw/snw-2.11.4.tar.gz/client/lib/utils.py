import logging
import math
import os
import json
import sys
from datetime import datetime, date

import requests
import six
from jsonschema import Draft4Validator
from prettytable import PrettyTable
from packaging import version

import client.launcher as launcher

_reqcache = {}
lookup_cache = {}
test_storages = None

launcher.LOGGER = logging.getLogger()


def getcache(url, auth, params):
    global _reqcache
    key = json.dumps([url, params])
    if key not in _reqcache:
        _reqcache[key] = requests.get(url, auth=auth, params=params)
    return _reqcache[key]


def entity_list(url, auth):
    r = getcache(os.path.join(url, "entity/list"),
                 auth=auth, params={"detail": True})
    return r.status_code, r.json()


def get_entity(url, auth, code):
    try:
        code_id = int(code)
        return True, code_id
    except Exception:
        pass
    status_code, entities = entity_list(url, auth)
    if status_code != 200:
        return False, "cannot get entity list"
    for e in entities:
        if e["entity_code"] == code or e["name"] == code:
            return True, e["id"]
    return False, "unknown entity"


def group_list(url, auth):
    r = getcache(os.path.join(url, "group/list"),
                 auth=auth, params={"detail": True})
    return r.status_code, r.json()


def get_group(url, auth, code):
    try:
        code_id = int(code)
        return True, code_id
    except Exception:
        pass
    codesplit = code.split(':')
    entity_id = None
    if len(codesplit) == 2:
        status_code, entity_id = get_entity(url, auth, codesplit[0])
        code = codesplit[1]
        if not status_code:
            return False, entity_id
    elif len(codesplit) > 2:
        return False, "invalid code"

    status_code, codes = group_list(url, auth)
    if status_code != 200:
        return False, "cannot get group list"
    for c in codes:
        if c.get("entity_id") == entity_id and c["name"] == code:
            return True, c["id"]
    return False, "unknown group"


def role_list(url, auth):
    r = getcache(os.path.join(url, "role/list"),
                 auth=auth, params={"detail": True})
    return r.status_code, r.json()


def get_role(url, auth, code):
    try:
        code_id = int(code)
        return True, code_id
    except Exception:
        pass
    codesplit = code.split(':')
    entity_id = None
    if len(codesplit) == 2:
        status_code, entity_id = get_entity(url, auth, codesplit[0])
        code = codesplit[1]
        if not status_code:
            return False, entity_id
    elif len(codesplit) > 2:
        return False, "invalid code"

    status_code, codes = role_list(url, auth)
    if status_code != 200:
        return False, "cannot get role list"
    for c in codes:
        if c.get("entity_id") == entity_id and c["name"] == code:
            return True, c["id"]
    return False, "unknown role"


def user_list(url, auth):
    r = getcache(os.path.join(url, "user/list"),
                 auth=auth, params={"detail": True})
    return r.status_code, r.json()


def get_user(url, auth, user):
    try:
        user_id = int(user)
        return True, user_id
    except Exception:
        pass

    status_code, users = user_list(url, auth)
    if status_code != 200:
        return False, "cannot get user list"
    for u in users:
        # warning: .lower() works for email but not for some special characters
        # https://stackoverflow.com/questions/319426/how-do-i-do-a-case-insensitive-string-comparison
        if u["email"].lower() == user.lower() or u["tid"].lower() == user.lower():
            return True, u["id"]
    return False, "unknown user"


def permission_list(url, auth):
    r = getcache(os.path.join(url, "permission/list"),
                 auth=auth, params={"detail": True})
    return r.status_code, r.json()


def get_permission(url, auth, permission):
    try:
        permission_id = int(permission)
        return True, permission_id
    except Exception:
        pass

    status_code, permissions = permission_list(url, auth)
    if status_code != 200:
        return False, "cannot get permission list"
    for p in permissions:
        if p["name"] == permission:
            return True, p["id"]
    return False, "unknown permission"


# write data to stdout for both python 2 and 3
def write_to_stdout(data):
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout.buffer.write(six.ensure_binary(data))
    else:
        sys.stdout.write(data)


def get_services(url, user_auth):
    response_services = requests.get(os.path.join(url, "service/list"),
                                     auth=user_auth, params={"minimal": True, "all": True})

    if response_services.status_code != 200:
        return False, (response_services.status_code, response_services.text)

    services = response_services.json()
    return True, services


def show_model_files_list(url, auth, model_name, directory):
    r = requests.get(os.path.join(url, "model/listfiles", model_name),
                     params={'directory': directory},
                     auth=auth)
    if r.status_code != 200:
        raise RuntimeError('incorrect result from \'model/listfiles\' service: %s' % r.text)

    res = PrettyTable(["Name", 'LastModified', 'Size (in byte)'])
    res.align["Path"] = "l"
    res.align["LastModified"] = "l"
    res.align["Size"] = "l"

    for k, v in six.iteritems(r.json()):
        file_name = k.split("/", 1)[1]
        if not file_name:
            continue
        date = datetime.fromtimestamp(v['last_modified']).strftime("%m/%d/%Y, %H:%M:%S") if v.get(
            'last_modified') else ''
        size = v.get('size') if v.get('size') else ''
        res.add_row([file_name, date, size])

    return res


def is_model_pruned(url, auth, model_name):
    r = requests.get(os.path.join(url, "model/list"),
                     params={'model': model_name},
                     auth=auth)
    if r.status_code != 200:
        raise RuntimeError('incorrect result from \'model/listfiles\' service: %s' % r.text)
    result = r.json()
    if result and result[0] and "pruned" in result[0] and result[0]["pruned"] is True:
        return True
    return False


def _get_test_storages(url, auth, service):
    global test_storages
    if test_storages is None:
        data = {'service': service}
        r = requests.get(os.path.join(url, "resource/list"), auth=auth, data=data)
        result = r.json()
        if r.status_code != 200:
            return False, (r.status_code, result.get('message'))
        test_storages = [{'name': v['name'], "entity": v["entity"]}
                         for v in result if v['type'] == "test"]
    return test_storages


def _lookup_repository(url, auth, service, remote_path, entity):
    id = (remote_path, entity)
    if id in lookup_cache:
        return True, lookup_cache[id]
    data = {'path': remote_path, 'service': service}
    if entity:
        data["entity"] = entity
    r = requests.get(os.path.join(url, "resource/list"), auth=auth, data=data)
    result = r.json()
    if r.status_code != 200:
        return False, (r.status_code, result['message'])
    lookup_cache[id] = [type(r) == dict and r.get('key') or fileObj.get('key')
                        for fileObj in result]
    return True, lookup_cache[id]


def _get_testfiles(url, auth, service, path, model, src_lang, tgt_lang):
    assert src_lang is not None and tgt_lang is not None, "src/tgt_lang not determined"
    test_storages = _get_test_storages(url, auth, service)
    if path.endswith("." + src_lang):
        (real_path, basename) = os.path.split(path)
    else:
        real_path = path
    res = []
    for t in test_storages:
        entity = t["entity"]
        storage_name = t["name"]
        status, result = _lookup_repository(url, auth, service, "%s:%s" %
                                            (storage_name, path), entity)
        if not status:
            if result[0] == 404:
                if entity == "CONF_DEFAULT":
                    entity = ""
                launcher.LOGGER.info('no test corpus found in %s (entity "%s")' %
                                     (storage_name + ":" + path, entity))
            else:
                launcher.LOGGER.error('cannot connect to test repository %s (entity "%s")' %
                                      (storage_name + ":" + path, entity))
                sys.exit(1)
        else:
            count = 0
            for f in result:
                if f.endswith("." + src_lang):
                    test_parts = f.split('/')
                    test_name = test_parts[len(test_parts) - 1]
                    res.append(
                        ("%s:%s" % (storage_name, f), "pn9_testtrans:" +
                            model + "/" + storage_name + "/" + real_path + "/" + test_name + "." + tgt_lang))
                    count += 1
            if entity == "CONF_DEFAULT":
                entity = ""
            launcher.LOGGER.info('found %d test files in %s (entity "%s")' %
                                 (count, storage_name + ":" + path, entity))
    return res


def _get_outfiles(url, auth, service, path, model, src_lang, tgt_lang):
    assert src_lang is not None and tgt_lang is not None, "src/tgt_lang not determined"
    storage = "pn9_testtrans"
    res = []
    # If input path is file, get folder
    if path.endswith("." + src_lang + "." + tgt_lang):
        (real_path, basename) = os.path.split(path)
    else:
        real_path = path
    test_storages = _get_test_storages(url, auth, service)
    # Get test storage
    output_paths = list(map(lambda t: model + "/" + t["name"] + "/" + real_path, test_storages))
    output_paths.append(model + "/" + real_path)
    # Get translated path
    for output_path in output_paths:
        status, result = _lookup_repository(url, auth, service, "%s:%s" % (storage, output_path), None)
        if not status:
            if result[0] == 404:
                launcher.LOGGER.info('no output found in %s:%s' % (storage, output_path))
            else:
                launcher.LOGGER.error("cannot connect to testtrans repository: %s" % result[1])
                sys.exit(1)
        else:
            for f in result:
                if f.endswith("." + src_lang + "." + tgt_lang):
                    res.append("pn9_testtrans:" + f)
    return res


def _get_multi_ref(reffile, result, storage):
    reffile_str = ''
    if reffile in result:
        reffile_str = storage + reffile
    else:
        return None
    idx = 1
    while True:
        reffile_temp = reffile + '.' + str(idx)
        if reffile_temp in result:
            reffile_str += ',' + storage + reffile_temp
        else:
            break
        idx += 1
    return reffile_str


def _get_reffiles(url, auth, service, src_lang, tgt_lang, list_testfiles):
    res = []
    for (testfile, outfile) in list_testfiles:
        if not testfile.endswith("." + src_lang):
            continue
        split = testfile.split(':')
        if len(split) >= 2:
            storage = split[0] + ':'
            testfile = ':'.join(split[1:])
            dirname = os.path.dirname(testfile)
            status, result = _lookup_repository(url, auth, service, storage + dirname, None)
            if status:
                reffile = testfile[:-len(src_lang)] + tgt_lang
                reffile = _get_multi_ref(reffile, result, storage)
                if reffile is not None:
                    res.append((outfile, reffile))
        else:
            # localfile
            dirname = os.path.dirname(testfile)
            result = os.listdir(dirname)
            reffile = os.path.basename(testfile[:-len(src_lang)] + tgt_lang)
            reffile = _get_multi_ref(reffile, result, dirname + '/')
            if reffile is not None:
                res.append((outfile, reffile))
    return res


def _get_datafiles(url, auth, service, path, lang):
    assert lang is not None, "lang not determined"
    res = []
    status, result = _lookup_repository(url, auth, service, path, None)
    if not status:
        if result[0] == 404:
            launcher.LOGGER.info("no data corpus found in %s" % path)
        else:
            launcher.LOGGER.error("cannot connect to data repository %s" % result[1])
            sys.exit(1)
    else:
        count = 0
        for f in result:
            if f.endswith("." + lang + ".gz"):
                filename = os.path.basename(f)
                res.append(filename)
                count += 1
        launcher.LOGGER.info('found %d files with suffix %s in %s' % (count, lang, path))
    return res


def tree_display(res, lvl, l, idx_result, model_maxsize, scorenames, bestscores, avg_scores,
                 skip_noscores, has_noscores, show_owner, show_pruned, only_show_pruned, quiet=False):
    sorted_l = sorted(l, key=lambda k: float(idx_result[k]["date"]))
    pref = ' ' * lvl
    for k in sorted_l:
        item = idx_result[k]
        if not skip_noscores or len(item["scores"]) != 0:
            if item["date"] is not None and item["date"] != 0:
                d = date.fromtimestamp(math.ceil(float(item["date"]))).isoformat()
            else:
                d = ""
            model = pref + item["model"]
            if "count" in item:
                model = model + " (%d)" % item["count"]
            imageTag = item["imageTag"]
            p = imageTag.find(':')
            if p != -1:
                imageTag = imageTag[:p]
            p = imageTag.rfind('/')
            if p != -1:
                imageTag = imageTag[p + 1:]
            scorecols = []
            noscores = 0
            for s in scorenames:
                score = ""
                if s in item["scores"]:
                    score = "%.02f" % float(item["scores"][s])
                    if item["scores"][s] == bestscores[s]:
                        score = '*' + score
                    elif item["scores"][s] / bestscores[s] > 0.995:
                        score = '~' + score
                else:
                    noscores += 1
                scorecols.append(score)
            if has_noscores and noscores == 0:
                continue
            sentenceCount = ''
            if 'cumSentenceCount' in item and item['cumSentenceCount'] != 0:
                sentenceCount = "%.2fM" % (item['cumSentenceCount'] / 1000000.)
            pruned = ''
            if 'pruned' in item and show_pruned:
                pruned = item["pruned"]
            if quiet:
                res.append(item["model"])
            else:
                line_data = [d, item["lp"], imageTag, model, sentenceCount]
                if show_owner:
                    owner_obj = item.get("owner")
                    line_data.append(
                        owner_obj.get('entity_code') if owner_obj and isinstance(owner_obj, dict)
                        else owner_obj)
                if show_pruned:
                    line_data.append(pruned)
                if avg_scores:
                    avg_score = "%.02f" % float(item["avg_score"])
                    line_data.append(avg_score)
                res.add_row(line_data + scorecols)
        tree_display(res, lvl + 1, item['children_models'], idx_result, model_maxsize, scorenames, bestscores,
                     avg_scores, skip_noscores, has_noscores, show_owner, show_pruned, only_show_pruned, quiet)


# Calculate max depth of the trees
def tree_depth(lvl, l, idx_result):
    max_level = lvl
    for k in l:
        item = idx_result[k]
        sub_level = tree_depth(lvl + 1, item['children_models'], idx_result)
        if sub_level > max_level:
            max_level = sub_level
    return max_level


# Calculate cumulated sentenceCount
def cum_sentenceCount(l, idx_result, sentenceCount):
    for k in l:
        item = idx_result[k]
        if 'cumSentenceCount' not in item or item['cumSentenceCount'] is None:
            item['cumSentenceCount'] = item['sentenceCount'] + sentenceCount
        sub_level = cum_sentenceCount(item['children_models'], idx_result, item['cumSentenceCount'])


# Merge two configs (redundant code with method in nmt-wizard/server/nmtwizard/config.py and
# nmt-wizard-docker/nmtwizard/utils.py)
def merge_config(a, b):
    """Merges config b in a."""
    if isinstance(a, dict):
        for k, v in six.iteritems(b):
            if k in a and isinstance(v, dict) and type(a[k]) == type(v):
                merge_config(a[k], v)
            else:
                a[k] = v
    return a


def _get_params(lparam, listcmd):
    res = []
    idx = 0
    while idx < len(listcmd):
        if listcmd[idx] in lparam:
            idx = idx + 1
            while idx < len(listcmd) and not listcmd[idx].startswith('-'):
                res.append(listcmd[idx])
                idx += 1
            continue
        idx += 1
    return res


def _get_params_except_specified(lparam, listcmd):
    res = []
    idx = 0
    while idx < len(listcmd):
        if listcmd[idx] in lparam:
            idx = idx + 1
            while idx < len(listcmd) and not listcmd[idx].startswith('-'):
                idx += 1
        else:
            res.append(listcmd[idx])
            idx = idx + 1
            while idx < len(listcmd) and not listcmd[idx].startswith('-'):
                res.append(listcmd[idx])
                idx += 1
    return res


# Parse docker image name to get version pattern (e.g. "systran/pn9_tf:v1") and number (1)
def parse_version_number(image):
    p = image.find(".")
    if p == -1:
        # version incompletely qualified
        current_version_pattern = image
    else:
        # version completely qualified
        current_version_pattern = image[:p]
    q = current_version_pattern.find("v")
    if q == -1:
        version_main_number = 0
    else:
        version_main_number = int(current_version_pattern[q + 1:])

    i = image.find(":")
    tag = image[i + 1:]
    image_name = image[:i]
    return current_version_pattern, version_main_number, image_name, tag


# Check upgrades for docker image and return upgraded version if available and accepted by user
# input image and tag
# output image:tag
def check_upgrades(auth, url, upgrade, image, tag):
    image_dec = image.split("/")
    image = '/'.join(image_dec[-2:])
    tag_prefix = ""
    if tag[0] == 'v':
        tag_prefix = "v"
        tag = tag[1:]
    try:
        version_parts = version.parse(tag).release
    except ValueError as err:
        raise RuntimeError('cannot parse version %s - %s' % (tag, str(err)))

    if version_parts and version_parts[0] >= 1 and (len(version_parts) < 3 or upgrade != "none"):
        tag_req = tag
        if len(version_parts) == 3:
            tag_req = "%d.%d" % (version_parts[0], version_parts[1])
        r = requests.get(os.path.join(url, "docker/versions"),
                         auth=auth, params={'version_pattern': image + ':' + tag_prefix + tag_req})
        result = r.json()
        if r.status_code != 200:
            raise RuntimeError('cannot retrieve docker images for current version %s -- %s' %
                               (image + ':' + tag_prefix + tag, r.text))
        if len(result) == 0:
            raise RuntimeError('unknown version %s' % (image + ':' + tag_prefix + tag))
        versions = [version.parse(r['image']) for r in result]
        latest_version_parse = max(versions)
        latest_version = latest_version_parse.base_version
        # selectively upgrade if later version available
        if version.parse(image + ':' + tag_prefix + tag) < latest_version_parse:
            if len(version_parts) < 3 or upgrade == "force":
                # version incompletely qualified
                launcher.LOGGER.info('automatically upgrading docker_image=%s to %s' %
                                     (image, latest_version))
                return latest_version, True
            else:
                # version completely qualified
                launcher.LOGGER.info('upgrading docker_image=%s to %s is available, '
                                     'do you want to upgrade? (y/n)' %
                                     (image + ':' + tag_prefix + tag, latest_version))
                while True:
                    response = input('Upgrade? ')
                    if response in {'y', 'yes'}:
                        launcher.LOGGER.info('upgrading docker_image=%s to %s' %
                                             (image + ':' + tag_prefix + tag, latest_version))
                        return latest_version, True
                    elif response in {'n', 'no'}:
                        break
                    else:
                        launcher.LOGGER.info('Please enter `y` or `n`.')
        elif version.parse(image + ':' + tag_prefix + tag) == latest_version_parse:
            if len(version_parts) < 3:
                # version incompletely qualified
                launcher.LOGGER.info('automatically upgrading docker_image=%s to %s' %
                                     (image, latest_version))
                return latest_version, True
    return image + ':' + tag_prefix + tag, False


# Announce the usage of a docker image
def announce_usage(image):
    split = image.split("/")
    if len(split) > 2:
        image = "/".join(split[-2:])
    launcher.LOGGER.info('** will be using -docker_image=%s' % image)


# Return a string with the list of all schema validation warnings
def get_schema_errors(schema, config):
    v = Draft4Validator(schema)
    all_errors = "\n\n**Your config has the following issues, please refer to the documentation:"
    for error in sorted(v.iter_errors(config), key=str):
        # format error message
        error_parts = error.message.split()
        error_message = ""
        for error_part in error_parts:
            if error_part.startswith("u'"):
                error_message += error_part[1:].replace("'", '"')
            elif error_part[1:].startswith("u'"):
                error_message += error_part[0] + error_part[2:].replace("'", '"')
            else:
                error_message += error_part
            error_message += ' '
        # format error path
        error_path = ""
        for path_part in list(error.path):
            if isinstance(path_part, int):
                error_path += "array[" + str(path_part) + "]"
            else:
                error_path += '"' + path_part + '"'
            error_path += '/'
        # write error message and path
        if error_path == "":
            all_errors += '\n - In the config, ' + error_message
        else:
            all_errors += '\n - In the option ' + error_path + ', ' + error_message
    return all_errors


def is_released_model(input_model):
    check_release = False
    check_push = False
    if input_model.get('releases'):
        for k, v in input_model['releases'].items():
            if k == 'unknown_task' or v.get('state') == 'completed' or v.get('state') == 'in progress':
                check_release = True
                break
    if not check_release and input_model.get('push'):
        for push in input_model['push']:
            if not push.get('error'):
                check_push = True
                break
        if not check_push and input_model.get('state') == 'deploying':
            check_push = True
    if check_release or check_push:
        return True

    return False


def check_condition_to_get_model(options, model):
    if options.show_pruned:
        return True
    elif options.only_show_pruned and model.get("pruned"):
        return True
    elif options.only_show_released and is_released_model(model):
        return True
    elif not options.show_pruned and not options.only_show_released and \
            not options.only_show_pruned and not model["pruned"]:
        return True

    return False
