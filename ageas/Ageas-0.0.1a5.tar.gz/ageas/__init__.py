#!/usr/bin/env python3
"""
Ageas Reborn

author: jy, nkmtmsys
"""

import re
import os
import time
import warnings
from pkg_resources import resource_filename
import ageas.tool.json as json
import ageas.lib.config_maker as config_maker
import ageas.lib.pcgrn_caster as grn
import ageas.lib.trainer as trainer
from ageas.lib.gem_db_loader import Load
import ageas.lib.meta_grn_caster as meta_grn
import ageas.lib.model_interpreter as interpreter
import ageas.lib.feature_extractor as extractor
import ageas.database_setup.binary_class as binary_db



class Ageas:
    """
    Get candidate key factors and pathways
    and write report files into given folder
    """
    def __init__(self,
                class1_path = None,
                class2_path = None,
                clf_keep_ratio = 0.5,
                clf_accuracy_thread = 0.8,
                correlation_thread = 0,
                database_path = None,
                database_type = 'gem_file',
                factor_name_type = 'gene_name',
                feature_dropout_ratio = 0.1,
                feature_select_iteration = 1,
                interaction_database = 'biogrid',
                impact_depth = 3,
                top_grp_amount = 100,
                grp_changing_thread = 0.05,
                log2fc_thread = None,
                link_step_allowrance = 0,
                meta_load_path = None,
                meta_save_path = None,
                model_config_path = None,
                model_select_iteration = 2,
                mww_p_val_thread = 0.05,
                outlier_thread = 3,
                patient = 3,
                pcgrn_load_path = None,
                pcgrn_save_path = None,
                prediction_thread = 'auto',
                report_folder_path = None,
                specie = 'mouse',
                sliding_window_size = 20,
                sliding_window_stride = None,
                std_value_thread = None,
                std_ratio_thread = None,
                stabilize_iteration = 10,
                train_size = 0.95,
                warning = False,
                z_score_extract_thread = 0,):
        super(Ageas, self).__init__()

        """ Initialization """
        start = time.time()
        if not warning: warnings.filterwarnings('ignore')
        self.far_out_grps = {}
        self.patient = patient
        self.no_change_iteration_num = 0
        self.stabilize_iteration = stabilize_iteration
        self.grp_changing_thread = grp_changing_thread
        self.model_select_iteration = model_select_iteration
        self.link_step_allowrance = link_step_allowrance
        self.feature_select_iteration = feature_select_iteration
        # Set up database path info
        self.database_info = binary_db.Setup(database_path,
                                            database_type,
                                            class1_path,
                                            class2_path,
                                            specie,
                                            factor_name_type,
                                            interaction_database,
                                            sliding_window_size,
                                            sliding_window_stride)
        # load standard config file if not further specified
        if model_config_path is None:
            path = resource_filename(__name__, 'data/config/list_config.js')
            self.model_config = config_maker.List_Config_Reader(path)
        else:
            self.model_config = json.decode(model_config_path)
        print('Time to initialize : ', time.time() - start)

        """ Make or load pcGRNs and GRN construction guidance """
        start = time.time()
        if meta_load_path is not None and pcgrn_load_path is not None:
            pcGRNs = grn.Make(load_path = pcgrn_load_path)
            self.meta = meta_grn.Cast(load_path = meta_load_path)
        else:
            self.meta, pcGRNs=self.get_pcGRNs(database_info=self.database_info,
                                        std_value_thread = std_value_thread,
                                        std_ratio_thread = std_ratio_thread,
                                        mww_p_val_thread = mww_p_val_thread,
                                        log2fc_thread = log2fc_thread,
                                        prediction_thread = prediction_thread,
                                        correlation_thread = correlation_thread,
                                        meta_load_path = meta_load_path,)
        print('Time to cast or load pcGRNs : ', time.time() - start)
        if pcgrn_save_path is not None: pcGRNs.save(pcgrn_save_path)
        if meta_save_path is not None: self.meta.save_guide(meta_save_path)

        """ Model Selection """
        print('Entering Model Selection')
        start = time.time()
        clfs = trainer.Train(pcGRNs = pcGRNs,
                            database_info = self.database_info,
                            model_config = self.model_config,)
        clfs.successive_halving_process(iteration = self.model_select_iteration,
                                        clf_keep_ratio = clf_keep_ratio,
                                        clf_accuracy_thread=clf_accuracy_thread,
                                        last_train_size = train_size)
        print('Finished Model Selection', time.time() - start)
        start = time.time()
        self.grp_importances = interpreter.Interpret(clfs)
        self.factor = extractor.Extract(self.grp_importances,
                                        z_score_extract_thread,
                                        self.far_out_grps,
                                        top_grp_amount)
        print('Time to interpret 1st Gen classifiers : ', time.time() - start)

        """ Feature Selection """
        if (self.feature_select_iteration is not None and
            self.feature_select_iteration > 0):
            print('Entering Feature Selection')
            for i in range(self.feature_select_iteration):
                start = time.time()
                prev_grps = self.factor.grps.index
                rm = self.__get_grp_remove_list(self.grp_importances.result,
                                                feature_dropout_ratio,
                                                outlier_thread)
                pcGRNs.update_with_remove_list(rm)
                clfs.clear_data()
                clfs.grns = pcGRNs
                clfs.general_process(train_size = train_size,
                                    clf_keep_ratio = clf_keep_ratio,
                                    clf_accuracy_thread = clf_accuracy_thread)
                self.grp_importances = interpreter.Interpret(clfs)
                self.factor = extractor.Extract(self.grp_importances,
                                                z_score_extract_thread,
                                                self.far_out_grps,
                                                top_grp_amount)
                print('Time to do a feature selection : ', time.time() - start)
                if self.__early_stop(prev_grps, self.factor.grps.index):
                    self.stabilize_iteration = None
                    break

        """ Stabilizing Key GRPs """
        if (self.stabilize_iteration is not None and
            self.stabilize_iteration > 0):
            print('Stabilizing Key GRPs')
            start = time.time()
            denominator = 1
            for i in range(self.stabilize_iteration):
                denominator += i
                prev_grps = self.factor.grps.index
                clfs.general_process(train_size = train_size,
                                    clf_keep_ratio = clf_keep_ratio,
                                    clf_accuracy_thread = clf_accuracy_thread)
                self.grp_importances.add(interpreter.Interpret(clfs).result)
                self.factor = extractor.Extract(self.grp_importances,
                                                z_score_extract_thread,
                                                self.far_out_grps,
                                                top_grp_amount)
                if self.__early_stop(prev_grps, self.factor.grps.index):
                    break
            self.grp_importances.divide(denominator)
            self.factor = extractor.Extract(self.grp_importances,
                                            z_score_extract_thread,
                                            self.far_out_grps,
                                            top_grp_amount)
            print('Time to stabilize key GRPs : ', time.time() - start)

        """ Construct Regulons with Extracted GRPs and Access Them """
        print('Building Regulons with key GRPs')
        start = time.time()
        self.factor.build_regulon(meta_grn = self.meta.grn,
                                    impact_depth = impact_depth)

        # temporary codes to save reports and regulon before linking regulons
        if report_folder_path[-1] != '/': report_folder_path += '/'
        if not os.path.exists(report_folder_path):
            os.makedirs(report_folder_path)
        self.factor.change_regulon_list_to_dict()
        json.encode(self.factor.regulons,
                    report_folder_path + 'regulons_before_link.js')
        self.factor.report(self.meta.grn).to_csv(
                    report_folder_path + 'ageas_before_link.csv', index = False)
        self.factor.regulons = [e for e in self.factor.regulons.values()]

        if (self.link_step_allowrance is not None and
            self.link_step_allowrance > 0 and
            len(self.factor.regulons) > 1):
            print('Attempting to Connect Regulons')
            self.factor.link_regulon(meta_grn = self.meta.grn,
                                    allowrance = self.link_step_allowrance)
        self.factor.change_regulon_list_to_dict()
        print('Time to build key regulons : ', time.time() - start)

        """ Generate Report Files if specified path """
        if report_folder_path is not None:
            self.write_reports(report_folder_path)

    # get pseudo-cGRNs from GEMs or GRNs
    def get_pcGRNs(self,
                    database_info = None,
                    std_value_thread = 100,
                    std_ratio_thread = None,
                    mww_p_val_thread = 0.05,
                    log2fc_thread = 0.1,
                    prediction_thread = 'auto',
                    correlation_thread = 0.2,
                    meta_load_path = None,):
        meta = None
        # if reading in GEMs, we need to construct pseudo-cGRNs first
        if re.search(r'gem' , database_info.type):
            gem_data = Load(database_info,
                            mww_p_val_thread,
                            log2fc_thread,
                            std_value_thread)
            start1 = time.time()
            # Let kirke casts GRN construction guidance first
            meta = meta_grn.Cast(gem_data = gem_data,
                                prediction_thread = prediction_thread,
                                correlation_thread = correlation_thread,
                                load_path = meta_load_path)
            print('Time to cast GRN Guidnace : ', time.time() - start1)
            pcGRNs = grn.Make(database_info = database_info,
                                std_value_thread = std_value_thread,
                                std_ratio_thread = std_ratio_thread,
                                correlation_thread = correlation_thread,
                                gem_data = gem_data,
                                meta_grn = meta.grn)
        # if we are reading in GRNs directly, just process them
        elif re.search(r'grn' , database_info.type):
            pcGRNs = None
            print('trainer.py: mode grn need to be revised here')
        else:
            raise lib.Error('Unrecogonized database type: ', database_info.type)
        return meta, pcGRNs

    # take out some GRPs based on feature dropout ratio
    def __get_grp_remove_list(self, df = None,
                                    feature_dropout_ratio = 0.2,
                                    outlier_thread = 3):
        total_grp = len(df.index)
        gate_index = int(total_grp * (1 - feature_dropout_ratio))
        remove_list = list(df.index[gate_index:])
        for ele in self.__get_outliers(df, outlier_thread):
            self.far_out_grps[ele[0]] = ele[1]
            remove_list.append(ele[0])
        return remove_list

    # get outlier based on IQR value and outlier thread
    def __get_outliers(self, df, outlier_thread):
        # not using outlier filter if thread set to none
        if outlier_thread is None: return []
        result = []
        q3_value = df.iloc[int(len(df.index) * 0.25)]['importance']
        q1_value = df.iloc[int(len(df.index) * 0.75)]['importance']
        # set far out thread according to interquartile_range (IQR)
        far_out_thread = 3 * (q3_value - q1_value)
        # remove outliers as well
        prev_score = outlier_thread * 3
        for i in range(len(df.index)):
            score = df.iloc[i]['importance']
            if score >= max(far_out_thread, (prev_score / 3), outlier_thread):
                result.append([df.index[i], score])
                prev_score = score
            else: break
        return result

    # Stop iteration if key genes are not really changing
    def __early_stop(self, prev_grps = None, cur_grps = None):
        # just keep going if patient not set
        if self.patient is None: return False
        common = len(list(set(prev_grps).intersection(set(cur_grps))))
        change1 = (len(prev_grps) - common) / len(prev_grps)
        change2 = (len(cur_grps) - common) / len(cur_grps)
        change = (change1 + change2) / 2
        print('Average Key GRPs Changing Portion:', change)
        if change <= self.grp_changing_thread:
            self.no_change_iteration_num += 1
            if self.no_change_iteration_num == self.patient:
                print('Run out of patient! Early stopping!')
                return True
            else: return False
        else:
            self.no_change_iteration_num = 0
            return False

    # Write report files in give folder
    def write_reports(self, folder = 'report/'):
        if folder[-1] != '/': folder += '/'
        # Make path if not exist
        if not os.path.exists(folder): os.makedirs(folder)
        # meta GRN related
        meta_grn.Analysis(self.meta.grn['grps']).save(folder + 'grn_based.csv')
        # GRP importances
        self.grp_importances.save(folder + 'grps_importances.txt')
        json.encode(self.factor.regulons, folder + 'regulons.js')
        self.factor.report(self.meta.grn).to_csv(folder + 'ageas_based.csv',
                                                index = False)
