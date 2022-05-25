import argparse
from collections import namedtuple
import json
import logging
import os
import re
import sys
import fnmatch
import socket
import semver
import tempfile
import time
import requests

import enlighten
from blessed import Terminal

import client.launcher as launcher
from lib.commands.user import User
from lib.commands.task import Task
import lib.utils as utils

term = Terminal()
hostname = socket.gethostname()
logger = logging.getLogger("snw trans")


def check_command(command):
    p = command.index("-o") if "-o" in command else -1
    if p == -1:
        return False
    return command[p+1].startswith("launcher:"+hostname+"()()")


def get_status(t):
    msg = ""
    if t["status"] == "queued":
        msg = term.black
    elif t["status"] == "running":
        msg = term.blue
    elif t["status"] == "terminating":
        if t["message"] == "completed":
            msg = term.orange
        else:
            msg = term.red
    elif t["status"] == "stopped":
        if t["message"] == "completed":
            msg = term.green
        else:
            msg = term.red
    msg += t["status"]
    if t.get("message"):
        msg += ":" + t["message"]
    msg += term.normal
    return msg


def is_lower_docker_version(current_image, comparison_version):
    _, version_main_number, image_name, tag = utils.parse_version_number(current_image)
    current_docker_version = tag[1:] if tag.startswith('v') else tag
    if semver.match(current_docker_version, "<"+comparison_version):
        return True

    return False


def argparse_define():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url',
                        help="url to the launcher")
    parser.add_argument('-l', '--log-level', default='INFO',
                        help="log-level (INFO|WARN|DEBUG|FATAL|ERROR)")
    parser.add_argument('-s', '--service', help="service name")
    parser.add_argument('-P', '--priority', type=int, default=0, help='task priority - highest better')
    parser.add_argument('-m', '--model', help='model')
    parser.add_argument('-c', '--config', help="configuration file (for `set` only)")
    parser.add_argument('-e', '--entity_owner', help='entity owner')
    parser.add_argument('-g', '--gpus', help="number of gpus", type=int)
    parser.add_argument('-i', '--docker_image',
                              default=os.getenv('LAUNCHER_IMAGE', None),
                              help='Docker image (can be prefixed by docker_registry:)')
    parser.add_argument('--srx', help="if provided will segment sentences")
    parser.add_argument('--lang', help="needed for srx")
    parser.add_argument('-p', '--pattern', help="file pattern for recursive selection of files")
    parser.add_argument("-r", "--recursive", action="store_true", help="recursive directory walk")
    parser.add_argument("-o", "--outsuffix", type=str, default=".out", help="suffix for output files")
    parser.add_argument("inputs", metavar="FILE", type=str, nargs='*',
                        help="input file to translate")
    return parser


def retrieve_file(args, task_id, filename, filepath, trim_joiner, auth):
    r = requests.get(os.path.join(args.url, "task/file", task_id,
                     filename), auth=auth)
    if r.status_code != 200:
        logger.error("[%s] cannot not retrieve translation: %s", task_id, str(r.text))
        return False
    else:
        with open(filepath, "w") as fw:
            if trim_joiner:
                tsegments = r.content.decode("utf-8").split("\n")
                for (left, seg, right) in trim_joiner:
                    if left:
                        fw.write(left)
                    if seg:
                        fw.write(tsegments.pop(0))
                    if right:
                        fw.write(right)
                return True
            else:
                fw.write(r.content.decode("utf-8"))
                return True


def retrieve_trim_joiner(args, task_id, auth):
    r = requests.get(os.path.join(args.url, "task/file", task_id,
                     "srx_splits"), auth=auth)
    if r.status_code != 200:
        logger.error("[%s] cannot not retrieve srx splits: %s", task_id, str(r.text))
        return None
    else:
        return [sp.split(";") for sp in r.content.decode("utf-8").split("|")]


def get_filelist(args, inputs, srx):
    global tmpdirname
    warnings = 0
    missing_pattern = False
    input_files = []
    input_outputs = []
    for input_file in inputs:
        if os.path.isfile(input_file):
            if not args.pattern or fnmatch.fnmatch(input_file, args.pattern):
                input_files.append((input_file, input_file+args.outsuffix))
        elif os.path.isdir(input_file):
            if not args.pattern:
                warnings += 1
                if not missing_pattern:
                    missing_pattern = True
                    logger.warning("Missing --pattern for recursive file selection")
            else:
                if args.recursive:
                    for root, dir, files in os.walk(input_file):
                        for item in fnmatch.filter(files, args.pattern):
                            full_path = os.path.join(root, item)
                            input_files.append((full_path, full_path+args.outsuffix))
                else:
                    for f in fnmatch.filter(os.listdir(input_file), args.pattern):
                        full_path = os.path.join(input_file, f)
                        if os.path.isfile(full_path):
                            input_files.append((full_path, input_file+args.outsuffix))
                        else:
                            logger.warning("`%s` is not a file", full_path)
                            warnings += 1
        else:
            warnings += 1
            logger.warning("File `%s` incorrect", input_file)

    if warnings:
        logger.error("incorrect file definition - aborting")
        sys.exit(1)

    tmpdirname = tempfile.TemporaryDirectory()

    for (input_file, output_file) in input_files:
        (input_head, input_tail) = os.path.split(input_file)
        os.makedirs(os.path.join(tmpdirname.name, input_head.lstrip('/')), exist_ok=True)
        tmpfile_path = os.path.join(tmpdirname.name, input_head.lstrip('/'), input_tail)
        nlines = 0
        with open(tmpfile_path, "w") as of:
            if srx:
                trim_joiner = ""
                with open(input_file) as f_in:
                    for line in f_in:
                        segments = srx.segment(line, trim=False)
                        for seg in segments:
                            m = re.match(r"^(\s*)(.*?)(\s*)$", seg)
                            if trim_joiner:
                                trim_joiner += "|"
                            trim_joiner += ";".join((m.group(1), m.group(2) and "x" or "", m.group(3)))
                            if m.group(2):
                                of.write(m.group(2)+"\n")
                                nlines += 1
            else:
                trim_joiner = None
                with open(input_file) as f_in:
                    for line in f_in:
                        of.write(line)
                        nlines += 1
            input_outputs.append((input_file, nlines, tmpfile_path, output_file, trim_joiner))
    return input_outputs


def execute(args, auth):
    logger.setLevel(args.log_level)

    if args.inputs and (not args.service or not args.model):
        logger.error("need --service and --model to translate files")
        sys.exit(1)

    try:
        # get user id
        dictionary = {"display": "JSON", "url": args.url}
        user = User(namedtuple("args", dictionary.keys())(*dictionary.values()), auth)
        trainer_id = user.whoami()['tid']
    except RuntimeError as err:
        logger.error('cannot find user id: %s', str(err).strip())
        sys.exit(1)

    if args.srx:
        from srx.segmenting import Segmenter
        srx = Segmenter(args.srx, args.lang)
    else:
        srx = None

    file_to_translate = get_filelist(args, args.inputs, srx)

    for input_file, nsent, tmp_file, output_file, trim_joiner in file_to_translate:
        if os.path.isfile(output_file):
            os.remove(output_file)
        output_path = hostname+"()()"
        output_path += os.path.abspath(output_file).replace("/", "()S()")
        logger.info("launch translation %s srx of %s (%d sentences) => %s",
                    srx and "w/" or "w/out", input_file, nsent, output_file)
        args_launch = ["-d", "JSON", "-u", args.url, "task", "launch", '-T', '']
        args_launch += ["-s", args.service]
        if args.entity_owner:
            args_launch += ["-e", args.entity_owner]
        args_launch += ["-P", str(args.priority)]
        if args.gpus:
            args_launch += ["-g", str(args.gpus)]
        if args.docker_image:
            args_launch += ["-i", args.docker_image, "--upgrade", "none"]
        args_launch += ["--novalidschema"]
        args_launch += ["--", "-m", args.model]
        if args.config:
            args_launch += ["-c", args.config]
        args_launch += ["--config_update_mode", "merge"]
        args_launch += ["trans", "-i", tmp_file]
        args_launch += ["-o", "launcher:"+output_path]

        launcher.argparse_preprocess()
        launch_args = launcher.parser.parse_args(args_launch)

        try:
            task = Task(launch_args, auth)
            task.execute_command()
            # Add {"postprocess": {"remove_placeholders": true}} config to docker command
            # if the version of the systran/pn9_tf image < 1.64.0 (Ticket #57654)
            if not args.config and is_lower_docker_version(launch_args.docker_image, "1.64.0"):
                docker_command = launch_args.docker_command
                launch_args.docker_command = ["-c", '{"postprocess":{"remove_placeholders":true}}'] + docker_command

            status, service_list = utils.get_services(url=args.url, user_auth=auth)
            res = launcher.process_request(service_list, launch_args.cmd, launch_args.subcmd,
                                           True, launch_args, auth=auth)
            task_id = res.split("\t")[1]
            if trim_joiner is not None:
                r = requests.post(os.path.join(args.url, "task/file",
                                  task_id, "srx_splits"), auth=auth, data=trim_joiner,
                                  headers={'Content-Type': 'application/octet-stream'})
        except RuntimeError as err:
            logger.error(str(err))
            sys.exit(1)
        except ValueError as err:
            logger.error(str(err))
            sys.exit(1)

    r = requests.get(os.path.join(args.url, "task/list",
                                  trainer_id + '*'), auth=auth)
    if r.status_code != 200:
        raise RuntimeError('incorrect result from \'task/list\' service: %s' % r.text)

    manager = enlighten.get_manager()
    status_format = "{task}: {file}{fill}{stage} ({time})"
    list_tasks = []
    for t in sorted(r.json(), key=lambda t: t["launched_time"] if t["launched_time"] is not None else "0"):
        if t["task_id"].endswith("_trans"):
            list_tasks.append([t["task_id"], None])

    logger.info("monitoring tasks - you can safely interrupt with CTRL-C")

    try:
        count_task = 0
        while True:
            running = False
            for task in list_tasks:
                if task[0] is None or task[1] is False:
                    continue
                task_id = task[0]
                fields_list = ["content", "status", "message", "files", "queued_time", "allocated_time", "running_time",
                               "terminating_time", "stopped_time"]
                params = {"fields": ",".join(fields_list)}
                r = requests.get(os.path.join(args.url, "task/status", task[0]), auth=auth, params=params)
                if r.status_code != 200:
                    logger.error('[%s] failed \'task/status\' service: %s', task[0], r.text)
                    sys.exit(1)
                t = r.json()
                if task[1] is None:
                    if t["content"] is None:
                        task[1] = False
                        continue
                    content = json.loads(t["content"])
                    if "docker" not in content or not check_command(content["docker"]["command"]):
                        task[1] = False
                        continue
                times = []
                for k in t:
                    if k.endswith('_time') and t.get(k):
                        times.append(k)
                sorted_times = sorted(times, key=lambda k: float(t[k]))
                last = -1
                tmsg = ""
                last_k = ""
                the_file = ""
                for f in t["files"]:
                    if f != "srx_splits" and f != "log" and f.find("()") == -1:
                        the_file = f
                        break
                for k in sorted_times:
                    if k != "updated_time":
                        current = float(t[k])
                        delta = current - last if last != -1 else 0
                        last = current
                        if last_k in ["queued_time", "allocated_time", "running_time", "terminating_time"]:
                            tmsg = last_k[:-5]+" for %ds" % delta
                        last_k = k
                if t["status"] in ["queued", "allocated", "running", "terminating"]:
                    running = True
                elif t["status"] == 'stopped':
                    task[0] = None
                    if t["message"] == 'completed':
                        trim_joiner = None
                        for f in t["files"]:
                            if f == "srx_splits":
                                trim_joiner = retrieve_trim_joiner(args, task_id, auth)
                        for f in t["files"]:
                            if f.startswith(hostname+"()()"):
                                fout = f[len(hostname)+4:].replace("()S()", "/")
                                logger.info("retrieve %s %s from task %s",
                                            trim_joiner and "with srx" or "",
                                            fout,
                                            task_id)
                                if retrieve_file(args, task_id, f, fout, trim_joiner, auth):
                                    logger.info("delete task %s", task_id)
                                    r = requests.delete(os.path.join(args.url, "task",
                                                                     task_id), auth=auth)
                if task[1]:
                    task[1].update(stage=get_status(t),
                                   time=tmsg)
                else:
                    task[1] = manager.status_bar(
                                autorefresh=True,
                                status_format=status_format,
                                task=task_id,
                                file=the_file,
                                stage=get_status(t),
                                time=tmsg)
                    count_task += 1

            if not running:
                break
            time.sleep(5)
    except KeyboardInterrupt:
        logger.warning("User interruption - aborting")

    logger.info("processed %d tasks", count_task)
