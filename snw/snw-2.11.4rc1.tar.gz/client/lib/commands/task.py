import json
import logging
import os
import random
import re
import sys

import requests
from jsonschema import validate
from jsonschema.exceptions import ValidationError

import client.launcher as launcher
from lib import utils

launcher.LOGGER = logging.getLogger()


class Task:
    def __init__(self, options, auth):
        self.options = options
        self.auth = auth
        self.is_json = self.options.display == "JSON"
        self.skip_launch = False

    def change(self):
        if self.options.prefix is None and len(self.options.task_ids) == 0 \
                and self.options.gpus is None:
            raise RuntimeError('you need to specify either `--prefix PREFIX` '
                               'or task_id(s) or `--gpus NGPUS`')
        if self.options.prefix is not None and len(self.options.task_ids) != 0:
            raise RuntimeError('you cannot to specify both `--prefix PREFIX` '
                               'and task_id(s)')
        if self.options.service is None and self.options.priority is None:
            raise RuntimeError('you need to specify new service (`--service SERVICE`)'
                               ' and/or new priority (`--priority PRIORITY`)')
        if self.options.prefix:
            r = requests.get(os.path.join(self.options.url, "task/list",
                                          self.options.prefix + '*'), auth=self.auth)
            if r.status_code != 200:
                raise RuntimeError('incorrect result from \'task/list\' service: %s' % r.text)
            result = r.json()
            self.options.task_ids = [k["task_id"] for k in result]
            if len(result) == 0:
                raise RuntimeError('no task matching prefix %s' % self.options.prefix)
        launcher.LOGGER.info(
            'Change %d tasks (%s)' % (len(self.options.task_ids), ", ".join(self.options.task_ids)))
        if len(self.options.task_ids) == 1 or launcher.confirm():
            modification = ""
            if self.options.service:
                modification += "service=%s" % self.options.service
            if self.options.priority:
                if len(modification) > 0:
                    modification += ", "
                modification += "priority=%d" % self.options.priority
            if self.options.gpus:
                if len(modification) > 0:
                    modification += ", "
                modification += "ngpus=%d" % self.options.gpus
            launcher.LOGGER.info("modifying tasks (%s) for:" % modification)
            error = False
            for k in self.options.task_ids:
                launcher.LOGGER.info("*** %s" % k)
                p = self.options.priority
                if p is not None and self.options.priority_rand != 0:
                    p += random.randint(0, self.options.priority_rand)
                params = {'priority': p, 'service': self.options.service,
                          'ngpus': self.options.gpus, 'ncpus': self.options.cpus}
                r = requests.get(os.path.join(self.options.url, "task/change", k),
                                 auth=self.auth, params=params)
                if r.status_code != 200:
                    launcher.LOGGER.error('>> %s' % r.json()["message"])
                    error = True
                else:
                    launcher.LOGGER.info(">> %s" % r.json()["message"])
                res = ""
        else:
            res = ""
        return res

    def file(self):
        p = self.options.filename.find(':')
        if p == -1:
            r = requests.get(os.path.join(self.options.url, "task/file",
                                          self.options.task_id, self.options.filename),
                             auth=self.auth)
        else:
            r = requests.get(os.path.join(self.options.url, "task/file_storage",
                                          self.options.filename[0:p], self.options.task_id,
                                          self.options.filename[p + 1:]),
                             auth=self.auth)
        if r.status_code != 200:
            raise RuntimeError('incorrect result from \'task/file_extended\' service: %s' % r.text)
        res = r.content
        return res

    def launch(self):
        res = None
        mode = None
        model = None
        src_lang = None
        tgt_lang = None
        totranslate = None

        # first pass to get model if present and if no image given, determine
        # docker image to be used
        i = 0
        while i < len(self.options.docker_command):
            tok = self.options.docker_command[i]
            if mode is None and (tok == "-m" or tok == "--model"):
                assert i + 1 < len(self.options.docker_command), "`-m` missing value"
                model = self.options.docker_command[i + 1]
                is_pruned = utils.is_model_pruned(self.options.url, self.auth, model)
                assert is_pruned is False, "cannot launch task on pruned model"

                if self.options.docker_image is None:
                    # no image specified with -i, first try to infer it from model
                    r = requests.get(os.path.join(self.options.url, "model/describe", model),
                                     params={"short": True}, auth=self.auth)
                    if r.status_code != 200:
                        raise RuntimeError("cannot infer docker_image for "
                                           "model %s -- %s" % (model, r.text))
                    self.options.docker_image = r.json()['imageTag']
                    # if docker_tag option (-t) specified, it overrule on docker image modifier
                    if self.options.docker_tag:
                        p = self.options.docker_image.find(':')
                        if p != -1:
                            self.options.docker_image = self.options.docker_image[:p]

                split = model.split("_")
                if len(split) > 2 and src_lang is None:
                    lp = split[1]
                    m = re.match(r"^([a-z]{2}([-+][A-Z]+)?)([a-z]{2}.*)$", lp)
                    if m is not None:
                        src_lang = m.group(1)
                        tgt_lang = m.group(3)
                i += 1
            i += 1
        # second pass to apply other options -c, -T, -Tm, -t
        i = 0
        config = None
        while i < len(self.options.docker_command):
            tok = self.options.docker_command[i]
            if mode is None and (tok == "train" or tok == "trans" or
                                 tok == "preprocess" or tok == "release"):
                mode = tok
                assert mode != "trans" or model is not None, "missing model for `trans`"
            # get config if present to validate it against schema
            elif mode is None and (tok == "-c" or tok == "--config"):
                assert i + 1 < len(self.options.docker_command), "`-c` missing value"

                # get JSON config passed as parameter
                c = self.options.docker_command[i + 1]
                if c.startswith("@"):
                    with open(c[1:], "rt") as f:
                        c = f.read()
                config = json.loads(c)
                if "source" in config:
                    src_lang = config["source"]
                if "target" in config:
                    tgt_lang = config["target"]
                i += 1
            elif mode == "trans" and (tok == "-T" or tok == "-Tm" or tok == "-t"):
                files = []
                if tok == '-t':
                    assert i + 1 < len(self.options.docker_command), "`trans -t` missing value"
                    input_files = self.options.docker_command[i + 1:]
                    for filename in input_files:
                        # check filename
                        p = filename.rfind(".")
                        assert p != -1, "language suffix should end filename %s" % filename
                        if src_lang is None:
                            src_lang = filename[p + 1:]
                        else:
                            assert src_lang == filename[p + 1:], \
                                "incompatible language suffix in filename %s" % filename
                        if tgt_lang is None:
                            p = model.find("_")
                            q = model.find("_", p + 1)
                            assert p != -1 and q != -1, \
                                "cannot find language pair in model name %s" % model
                            lp = model[p + 1:q]
                            assert lp[
                                   :len(src_lang)] == src_lang, "model lp (%s) does not " \
                                                                "match language suffix (%s)" % (
                                                                    lp[:len(src_lang)], src_lang)
                            tgt_lang = lp[len(src_lang):]
                        # find file to translate
                        file_path = utils._get_testfiles(self.options.url, self.auth,
                                                         self.options.service, filename,
                                                         model, src_lang, tgt_lang)
                        assert len(
                            file_path) != 0, "no file corresponds to filename %s" % filename
                        files.extend(file_path)
                else:
                    assert i + 1 < len(self.options.docker_command), "`trans -T[m]` missing value"
                    path = self.options.docker_command[i + 1]
                    assert i + 2 == len(
                        self.options.docker_command), "`trans -T[m] [PATH]` has extra values"
                    p = path.rfind(".")
                    assert p == -1, "-T[m] PATH should be a folder not a file %s" % path
                    if path[-1:] == "/":
                        path = path[:-1]
                    # find files to translate
                    files = utils._get_testfiles(self.options.url, self.auth,
                                                 self.options.service, path,
                                                 model, src_lang, tgt_lang)
                    assert len(files) != 0, "no file found to translate in folder %s" % path
                    if (tok == '-Tm'):
                        # find translated files
                        translatedfiles = utils._get_outfiles(self.options.url, self.auth,
                                                              self.options.service,
                                                              path, model, src_lang, tgt_lang)
                        files = [(test, out)
                                 for (test, out) in files if self.is_untranslated_files(out, translatedfiles)]
                        assert len(
                            files) != 0, "-Tm translates only untranslated files but " \
                                         "all files already translated in %s" % path

                # if needed prepare translation
                launcher.LOGGER.info('found %d test files' % len(files))
                self.options.toscore = utils._get_reffiles(self.options.url, self.auth,
                                                           self.options.service,
                                                           src_lang, tgt_lang, files)
                launcher.LOGGER.info('found %d test references' % len(self.options.toscore))
                docker_command = self.options.docker_command
                res = []
                input_files = []
                output_files = []
                for f in files:
                    launcher.LOGGER.info("translating: " + f[0])
                    input_files.append(f[0])
                    output_files.append(f[1])
                new_params = ["-i"] + input_files + ["-o"] + output_files
                self.options.docker_command = docker_command[0:i]
                self.options.docker_command += new_params

                self.skip_launch = True
                break
            elif mode == "trans" and (tok == "-i" or tok == "-I") and (
                    "-bt" in self.options.docker_command):
                # if "-I" is set, search files with the provided prefix
                #    "-i shared_data:fr/train/mono_fr-XX_News__28779-STATMT-newscrawl-2016_2.fr.gz"
                #    "-I shared_data:fr/train/mono_fr-XX_News__28779-STATMT-newscrawl-2016"
                #    "-I shared_data:fr/train/mono_fr"
                def generate_decoder_options(c):
                    if c is None:
                        return "default"
                    options_str = ''
                    params = c.get("options", {}).get("config", {}).get("params", {})
                    if 'beam_width' in params:
                        options_str = options_str + 'beam_' + str(params['beam_width']) + '_'
                    if 'sampling_topk' in params:
                        options_str = options_str + 'sampling_' + str(
                            params['sampling_topk']) + '_'
                    params = c.get("postprocess", {})
                    if 'remove_placeholders' in params:
                        options_str = options_str + 'remove_' + str(
                            params['remove_placeholders']) + '_'
                    if options_str != '':
                        return options_str[:-1]
                    return "default"

                new_params = utils._get_params_except_specified(("-i", "--input", "-I", "-bt"),
                                                                self.options.docker_command[i:])
                input_files_opts = utils._get_params(("-i", "--input", "-I"),
                                                     self.options.docker_command[i:])
                output_files_opts = utils._get_params("-bt", self.options.docker_command[i:])
                if len(input_files_opts) != len(output_files_opts):
                    launcher.LOGGER.error("invalid trans command - misaligned input/bt_output")
                    sys.exit(1)

                if tok == "-I":
                    assert src_lang is not None, "cannot find source lang id"
                else:
                    filename = input_files_opts[0]
                    segments = filename.split(".")
                    assert len(segments) >= 3, "input file should have suffix like .fr.gz"
                    assert segments[-1] == "gz", "input file should be gzipped"
                    if src_lang is None:
                        src_lang = segments[-2]
                    else:
                        assert src_lang.startswith(segments[-2]), "incompatible language suffix"
                if tgt_lang is None:
                    segments = model.split("_")
                    assert len(segments) == 5, "illegal model name"
                    lp = segments[1]
                    assert lp[:len(src_lang)] == src_lang, "model lp does not match " \
                                                           "language suffix"
                    tgt_lang = lp[len(src_lang):]

                if "--copy_source" not in self.options.docker_command:
                    new_params += ["--copy_source"]
                self.options.docker_command = self.options.docker_command[0:i]

                if "--keep_placeholders_as_config" in self.options.docker_command:
                    self.options.docker_command.remove('--keep_placeholders_as_config')
                elif "--keep_placeholders_as_config" in new_params:
                    new_params.remove('--keep_placeholders_as_config')
                else:
                    if config is None:
                        config = {}
                        self.options.docker_command.insert(0, "-c")
                        self.options.docker_command.insert(1, "{}")
                    if "postprocess" in config:
                        config['postprocess']['remove_placeholders'] = True
                    else:
                        config['postprocess'] = {'remove_placeholders': True}
                    option_index = self.options.docker_command.index("-c") + 1
                    self.options.docker_command[option_index] = json.dumps(config)

                decoder_options = generate_decoder_options(config)
                if "--add_bt_tag" in self.options.docker_command or "--add_bt_tag" in new_params:
                    decoder_options = decoder_options + "_tagged"

                input_files = []
                output_files = []
                for f, b in zip(input_files_opts, output_files_opts):
                    files = []
                    if tok == "-I":
                        path, filename = os.path.split(f)
                        launcher.LOGGER.info("searching files in " + path)
                        monofiles = utils._get_datafiles(self.options.url, self.auth,
                                                         self.options.service,
                                                         path, src_lang)
                        files = [os.path.join(path, test) for test in monofiles if
                                 test.startswith(filename)]
                    else:
                        launcher.LOGGER.info("translating: " + f)
                        files.append(f)

                    output_path_name = os.path.join(b, src_lang + tgt_lang, model,
                                                    decoder_options)
                    transfiles = utils._get_datafiles(self.options.url, self.auth,
                                                      self.options.service,
                                                      output_path_name, tgt_lang)

                    for input in files:
                        filename = os.path.basename(input)
                        filename, _ = os.path.splitext(filename)  # remove ".gz"
                        filename, _ = os.path.splitext(filename)  # remove ".fr"
                        output_file_name = filename + "." + tgt_lang + ".gz"

                        if output_file_name in transfiles:
                            launcher.LOGGER.info("%s exists in %s, skip translating..." % (
                                output_file_name, output_path_name))
                        else:
                            input_files.append(input)
                            output_files.append(
                                os.path.join(output_path_name, output_file_name))
                if not input_files:
                    launcher.LOGGER.info("all files have already been there! exit!")
                    sys.exit(0)
                new_params += ["-i"] + input_files + ["-o"] + output_files
                self.options.docker_command += new_params

                break
            i += 1

        # Docker image checks
        if self.options.docker_image is None:
            raise RuntimeError('missing docker image (you can set LAUNCHER_IMAGE)')
        # if docker_tag option (-t) specified, it overrule on docker image modifier
        p = self.options.docker_image.find(':')
        if p != -1:
            if self.options.docker_tag is not None:
                raise RuntimeError("ambiguous definition of docker tag (-i %s/-t %s)",
                                   (self.options.docker_image, self.options.docker_tag))
            self.options.docker_tag = self.options.docker_image[p + 1:]
            self.options.docker_image = self.options.docker_image[:p]

        # check if we can upgrade version
        self.options.docker_image, upgraded = utils.check_upgrades(self.auth, self.options.url,
                                                                   self.options.upgrade,
                                                                   self.options.docker_image,
                                                                   self.options.docker_tag)
        self.options.docker_tag = None
        utils.announce_usage(self.options.docker_image)

        # if we are translating check if there are reference files
        if mode == "trans":
            idx = self.options.docker_command.index("trans")
            input_files = utils._get_params(("-i", "--input"),
                                            self.options.docker_command[idx + 1:])
            output_files = utils._get_params(("-o", "--output"),
                                             self.options.docker_command[idx + 1:])
            if len(input_files) != len(output_files):
                launcher.LOGGER.error("invalid trans command - misaligned input/output")
                sys.exit(1)
            self.options.toscore = utils._get_reffiles(self.options.url, self.auth,
                                                       self.options.service,
                                                       src_lang, tgt_lang,
                                                       list(zip(input_files, output_files)))
            launcher.LOGGER.info('found %d test references' % len(self.options.toscore))
            if "--chaintuminer" in self.options.docker_command:
                self.options.totuminer = list(zip(input_files, output_files))
                self.options.docker_command.remove("--chaintuminer")

        if mode == "trans" and (tok == "-T" or tok == "-Tm" or tok == "-t"):
            status, serviceList = utils.get_services(url=self.options.url, user_auth=self.auth)
            res.append(launcher.process_request(serviceList, self.options.cmd, self.options.subcmd,
                                                self.options.display == "JSON",
                                                self.options, auth=self.auth))

        # merge -c and -m configs and validate it against schema
        if self.options.novalidschema:
            launcher.LOGGER.warning(
                "schema validation is skipped, your config is potentially erroneous")
        else:
            if not (config is None) or upgraded:
                if model:
                    # if model is present, collect its config
                    r = requests.get(os.path.join(self.options.url, "model/describe", model),
                                     auth=self.auth)
                    if r.status_code != 200:
                        raise RuntimeError("cannot retrieve configuraton for "
                                           "model %s -- %s" % (model, r.text))
                    model_config = r.json()
                    if config:
                        # merge to validate complete config
                        config = utils.merge_config(model_config, config)
                    else:
                        config = model_config

                image = self.options.docker_image
                _, version_main_number, image_name, tag = utils.parse_version_number(image)
                if version_main_number > 0:
                    r = requests.get(os.path.join(self.options.url, "docker/schema"),
                                     params={'image': image_name, 'tag': tag}, auth=self.auth)
                    if r.status_code != 200:
                        raise RuntimeError('cannot retrieve schema from docker image: %s' % image)
                    schema_res = r.json()
                    schema = json.loads(schema_res)
                    # validate config against JSON schema
                    try:
                        validate(config, schema)
                    except ValidationError as error:
                        all_errors = utils.get_schema_errors(schema, config)
                        raise ValidationError(all_errors)

        if mode == "release":
            self.options.docker_command += ["-d", "pn9_release:"]
        if self.options.no_test_trans:
            assert mode == "train", "`--no_test_trans` can only be used with `train` mode"
        elif mode == "train":
            assert not (src_lang is None or tgt_lang is None), "src/tgt_lang not determined: " \
                                                               "cannot find test sets"
            if src_lang < tgt_lang:
                test_dir = src_lang + "_" + tgt_lang
            else:
                test_dir = tgt_lang + "_" + src_lang
            self.options.totranslate = utils._get_testfiles(self.options.url, self.auth,
                                                            self.options.service, test_dir,
                                                            "<MODEL>", src_lang, tgt_lang)
            self.options.toscore = utils._get_reffiles(self.options.url, self.auth,
                                                       self.options.service, src_lang,
                                                       tgt_lang, self.options.totranslate)
            launcher.LOGGER.info('found %d test references' % len(self.options.toscore))
        return res

    def is_untranslated_files(self, out, translated_paths):
        if len(translated_paths) == 0:
            return True
        # Check output is new format and existed
        if (out in translated_paths):
            return False
        # Check output is old format and existed: check by name and number of character /
        # the number of character / in old format is less than new format
        # (Eg: old format 'pn9_testtrans:model/path/test_name.en.de', new format
        # 'pn9_testtrans:model/storage/path/test_name.en.de')
        translated_files = list(filter(lambda path:
                                       self.compare_test_name(out, path) and out.count('/') != path.count('/'),
                                       translated_paths))

        return len(translated_files) == 0

    def compare_test_name(self, out, translated_path):
        out_name = os.path.basename(out)
        translated_path_name = os.path.basename(translated_path)

        return out_name == translated_path_name

    def execute_command(self):
        result = None
        if self.options.subcmd == "change":
            result = self.change()
        if self.options.subcmd == "file":
            result = self.file()
        if self.options.subcmd == "launch":
            result = self.launch()
        return result
