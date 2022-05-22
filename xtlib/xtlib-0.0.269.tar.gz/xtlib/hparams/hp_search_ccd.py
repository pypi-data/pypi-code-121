# hp_search_ccd.py: implementation of cyclic coordinate descent HP algorithm

import json
import time
import random
import numpy as np
from interface import implements

from xtlib import console
from xtlib import utils
from xtlib.helpers import xt_config
from xtlib.helpers.bag import Bag
from xtlib.hparams.hparam_search import HParamSearch
from xtlib.storage.store import Store
from xtlib.hparams.hp_search_interface import HpSearchInterface

'''
ccd_control.dat: control file for CCD (JSON dict)
    control =  { "best": {}, "state": {}, "stats": {} }
'''

class CyclicCoordinateDescent(implements(HpSearchInterface)):
    def __init__(self) -> None:
        self.initialized = False
        self.report = ""

    def need_runs(self):
        return False

    def read_search_info(self, store, context):
        si_text = store.read_job_file(context.ws, context.job_id, "ccd_search_info.dat")
        si_etag = store.get_current_blob_etag()
        si = json.loads(si_text)
        return si, si_etag

    def write_search_info_if_missing(self, store, context, si):
        si_text = json.dumps(si)

        # fail silently if already exists
        try:
            store.create_job_file(context.ws, context.job_id, "ccd_search_info.dat", si_text, fail_if_exists=True)
        except BaseException as ex:
            if not "specified blob already exists" in str(ex):
                raise ex

    def update_search_info(self, store, context, si, si_etag):
        si_text = json.dumps(si)
        store.create_job_file(context.ws, context.job_id, "ccd_search_info.dat", si_text, etag=si_etag)

    def log_to_report(self, text):
        text += "\n"
        self.report += text

    def append_report_to_storage(self, store, context):
        store.append_job_file(context.ws, context.job_id, "ccd_report.txt", self.report)
        self.report = ""

    def initialize(self, hp_values_dict, store, context):
        # create initial best set of HP values
        best_set = {}
        search_keys = []

        for name, values in hp_values_dict.items():
            mid_index = len(values)//2
            value = values[mid_index].strip()
            best_set[name] = value

            if len(values) > 1:
                search_keys.append(name)

        # initial state (defines next HP name and value to use for next run)
        state = {"search_keys": search_keys, "key_index": 0, "value_index": 0, "value_run_index": 0, "pass_index": 0, "no_change": 0, 
            "started_run_count": 0, "completed_run_count": 0, "best_score": None}

        # initial scores (scores for each HP/value)
        scores = {}
        si = {"best_set": best_set, "state": state, "scores": scores}

        # write to blob storage for job 
        self.write_search_info_if_missing(store, context, si)

    def build_hp_values_dict(self, hp_records):
         # convert hp_records to a simple dict
        hp_values_dict = {}
       
        for hp in hp_records:
            hp_name = hp["name"]
            values = [value.strip() for value in hp["value"].split(",")]
            hp_values_dict[hp_name] = values

        return hp_values_dict

    def search(self, run_name, store, context, hp_records, runs):

        # convert hp_records to a simple dict
        hp_values_dict = self.build_hp_values_dict(hp_records)

        if not self.initialized:
            self.initialize(hp_values_dict, store, context)
            self.initialized = True

        retry_count = 25
        max_sleep = 5
        succeeded = False
        console.print("search() starting")
        next_set = None

        # wrap code in a retry loop in case other node writes the info file while we are processing it
        for i in range(retry_count):
            try:
                next_set = self.search_core(store, context, hp_values_dict)
                succeeded = True
                break

            except BaseException as ex:
                if not "ConditionNotMet" in str(ex):
                    # pass thru other exceptions
                    raise ex

                console.print("exception during hp_ccd.search: {}".format(ex))
                if i == (retry_count-1):
                    console.print("max retries exceeded")
                    raise ex

                console.print("exception retry #{}".format(1+i))
                time.sleep(max_sleep*random.random())
            
        return next_set

    def search_core(self, store, context, hp_values_dict):

        si, si_etag = self.read_search_info(store, context)
        best_set = si["best_set"]
        state = si["state"]
        scores = si["scores"]

        # stop search due to total_run_count
        if context.total_run_count and state["completed_run_count"] >= context.total_run_count:
            # exit controller now
            console.print("completed run_count == total_run_count ({}); stopping HP search".format(context.total_run_count))
            return None  

        # stop search due reaching goal
        if context.goal_metric:
            best_score = state["best_score"]
            if best_score is not None:
                eta = .000001
                if context.maximize_metric:
                    if best_score+eta >= context.goal_metric:
                        # exit controller now
                        console.print("maximize_metric: best_score ({}) >= context_goal_metric ({}); stopping HP search".format(best_score, context.goal_metric))
                        return None
                else:
                    if best_score-eta <= context.goal_metric:
                        # exit controller now
                        console.print("minimize_metric: best_score ({}) <= context_goal_metric ({}); stopping HP search".format(best_score, context.goal_metric))
                        return None


        search_keys = state["search_keys"]
        key_index = state["key_index"]
        value_index = state["value_index"]

        hp_name = search_keys[key_index]
        hp_values = hp_values_dict[hp_name]
        current_value = hp_values[value_index]

        # HP set for next run
        next_set = dict(best_set)
        next_set[hp_name] = current_value

        # update context (for processing end of run)
        context.ccd_hp_name = hp_name
        context.ccd_hp_value = current_value

        console.print("search_keys: {}".format(search_keys))
        console.print("hp_values_dict[{}]: {}".format(hp_name, hp_values_dict[hp_name]))
        console.print("setting HP: {}, value: {}".format(hp_name, current_value))

        stop_controller = self.update_state_for_next_run(context, hp_values_dict, search_keys, state)        

        self.update_search_info(store, context, si, si_etag)

        if stop_controller:
            # exit controller now
            return None

        return next_set

    def update_state_for_next_run(self, context, hp_values_dict, search_keys, state):
        value_run_index = state["value_run_index"]
        value_index = state["value_index"]
        key_index = state["key_index"]
        pass_index = state["pass_index"]
        started_run_count = state["started_run_count"]

        console.print("this run: value_run_index={}, value_index={}, key_index={}, pass_index={}, started_run_count={}".format( \
            value_run_index, value_index, key_index, pass_index, started_run_count))

        hp_name = search_keys[key_index]
        hp_values = hp_values_dict[hp_name]

        stop_controller = False

        value_run_index += 1
        started_run_count += 1

        if value_run_index >= context.runs_per_set:
            # done with this HP value
            value_run_index = 0
            value_index += 1

            if value_index >= len(hp_values):
                # done with this HP
                value_index = 0
                key_index += 1

                if key_index >= len(search_keys):
                    # done with this pass
                    key_index = 0
                    pass_index += 1

                    if context.max_passes and pass_index >= context.max_passes:
                        stop_controller = True

        state["started_run_count"] = started_run_count
        state["value_run_index"] = value_run_index
        state["value_index"] = value_index
        state["key_index"] = key_index
        state["pass_index"] = pass_index

        console.print("next run: value_run_index={}, value_index={}, key_index={}, pass_index={}, started_run_count={}".format( \
            value_run_index, value_index, key_index, pass_index, started_run_count))

        return stop_controller

    def process_end_of_run(self, store, context, hp_records):
        retry_count = 25
        max_sleep = 5
        exit_controller = False
        console.print("process_end_of_run() starting")

        # convert hp_records to a simple dict
        hp_values_dict = self.build_hp_values_dict(hp_records)

        # wrap code in a retry loop in case other node writes the info file while we are processing it
        for i in range(retry_count):
            try:
                self.report = ""
                exit_controller = self.process_run_core(store, context, hp_values_dict)
                break

            except BaseException as ex:
                if not "ConditionNotMet" in str(ex):
                    # pass thru other exceptions
                    raise ex

                console.print("exception during hp_ccd.process_end_of_run: {}".format(ex))

                if i == (retry_count-1):
                    console.print("max retries exceeded")
                    raise ex

                console.print("exception retry #{}".format(1+i))
                time.sleep(max_sleep*random.random())  

        # now that we have successfully updated search info, we can write our report info
        self.append_report_to_storage(store, context)

        return exit_controller

    def process_run_core(self, store, context, hp_values_dict):
        exit_controller = False

        si, si_etag = self.read_search_info(store, context)  

        best_set = si["best_set"]
        state = si["state"]
        scores = si["scores"]

        hp_name = context.ccd_hp_name 
        hp_value = context.ccd_hp_value

        if not hp_name in scores:
            scores[hp_name] = {}

        hp_scores = scores[hp_name]
        if not hp_value in hp_scores:
            hp_scores[hp_value] = []

        assert context.primary_metric

        # get last logged primary metric for this run
        filter_dict = {"run_name": context.run_name}
        metric = "metrics." + context.primary_metric
        filter_dict[metric] = {"$exists": True}
        fields_dict = {"run_name": 1, "hparams": 1, metric: 1}

        runs = store.get_all_runs(context.aggregate_dest, context.ws, context.dest_name, filter_dict, fields_dict,
            use_cache=False)

        # append primary metric value from run to hp_scores
        md = utils.safe_cursor_value(runs, "metrics")
        if md is None:
            raise Exception("run '{}' is missing primary metric '{}'".format(context.run_name, context.primary_metric))

        pm_value = md[context.primary_metric]
        hp_scores[hp_value].append(pm_value)

        self.log_to_report("node: {}, run: {}, hp_name: {}, hp_value: {}, score: {}".format( \
            context.node_index, context.run_name, hp_name, hp_value, pm_value))

        hp_runs = hp_scores[hp_value]
        if len(hp_runs) >= context.runs_per_set:
            avg_score = sum(hp_runs)/len(hp_runs)
            msg = "finished runs for HP name: {}, value: {}, avg_score: {}".format(hp_name, hp_value, avg_score)

            console.print(msg)
            self.log_to_report("  " + msg)

        # increment completed_run_count
        state["completed_run_count"] += 1

        no_change = state["no_change"]

        print("completed_run_count: {}, no_change: {}".format(state["completed_run_count"], no_change))

        # did we finish runs for this hp_name?
        if self.all_runs_completed(context, hp_name, hp_scores, hp_values_dict):

            # find best value for this hp_name
            best_value_index = self.get_best_value_index(hp_scores)
            best_scores = list(hp_scores.values())[best_value_index]
            best_score = sum(best_scores)/len(best_scores)
            best_hp_value = hp_values_dict[hp_name][best_value_index]

            if best_set[hp_name] != best_hp_value:
                # update our best_set with this highest scoring HP value
                best_set[hp_name] = best_hp_value

                # update best score
                state["best_score"] = best_score

                # remove all scores for this hp_name
                del scores[hp_name]

                msg = "\nIMPROVEMENT: updated best set: hp_name: {}, value: {}, new best_score: {}, completed_run_count: {}".format(\
                    hp_name, best_hp_value, best_score, state["completed_run_count"])
                console.print(msg)

                # log progress 
                self.log_to_report(msg)
                self.log_to_report("new best set: {}\n".format(best_set))

                if no_change:
                    no_change = 0

            else:
                # no change for specified hp
                no_change += 1

                if no_change >= len(hp_values_dict):
                    # we have been thru all HP variables without a change
                    console.print("no_change detected for all HP values; stopping HP search")
                    exit_controller = True

        state["no_change"] = no_change

        # write all info back to search into blob
        self.update_search_info(store, context, si, si_etag)

        return exit_controller

    def all_runs_completed(self, context, hp_name, hp_scores, hp_values_dict):
        completed = False
        required_value_count = len(hp_values_dict[hp_name])

        # do we have scores for all values?
        if len(hp_scores) >= required_value_count:

            # ensure each value has required number of scores
            completed = all(len(value_scores) == context.runs_per_set for value_scores in hp_scores.values() )

        return completed

    def get_best_value_index(self, hp_scores):
        # average scores for each value
        value_means = [sum(value_scores)/len(value_scores) for value_scores in hp_scores.values()]
        value_index = int(np.argmax(value_means))
        return value_index

def ccd_test(ws, job_id, run_name):
    config = xt_config.get_merged_config()
    store = Store(config=config)

    # dummy up a context object for testing
    context = Bag()
    context.ws = ws
    context.job_id = job_id
    context.aggregate_dest = "job"
    context.dest_name  = job_id
    context.hp_sweep = "hp-config-dir/scan_sweep.yaml"
    context.search_type = "ccd"
    context.providers = {"hp-search": {"ccd": "xtlib.hparams.hp_search_ccd.CyclicCoordinateDescent"} } 
    context.total_run_count = 2000
    context.primary_metric = "best-eval-acc"
    context.maximize_metric = True
    context.run_name = run_name
    context.node_index = 0

    # new context fields for CCD (from run cmd)
    context.goal_metric = 1.0000
    context.runs_per_set = 3
    context.max_passes = 5

    # read associated HP file and perform a search
    yaml_text = store.read_job_file(context.ws, context.dest_name, context.hp_sweep)
    hp_search = HParamSearch()

    for i in range(5000):
        # request search for new run
        hp_set = hp_search.generate_hparam_set(yaml_text, run_name, store, context)
        if not hp_set:
            break

        # wrapup run
        context.run_name = run_name
        hp_search.process_end_of_run(store, context)
            
        #print("hp_set: {}".format(hp_set))
    
if __name__ == "__main__":
    console.set_level("normal")

    # force an exception 
    # try:
    #     i = 34/0
    # except Exception as ex:
    #     print(ex)
    # v1 storage
    
    #ccd_test("tpx", "job2151")

    # v3 stoarge
    ccd_test("tpx", "job5", "run5.0")
