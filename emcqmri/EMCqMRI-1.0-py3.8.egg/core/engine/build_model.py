from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import sys
sys.path.insert(0, '../..')
sys.path.append('../')
import os

import argparse
import importlib
import logging
import ntpath
from ..utilities import configuration_utilities
from ..utilities import checkpoint_utilities
from ..utilities import core_utilities
from . import data_loader
import importlib
import logging
import torch
import torch.nn as nn


def check_override(config_object, override_modules):
    if override_modules:
        config_object = override_modules(config_object)
    
    return config_object


def configure_cuda(config_object):
    if config_object.args.engine.useCUDA:
        if torch.cuda.is_available():
            config_object.args.engine.device = torch.device("cuda:0")
            logging.info("Using CUDA")
        else:
            logging.warn("User selected runtime with CUDA, but CUDA is not available. Running on CPU instead.")
            config_object.args.engine.device = torch.device("cpu")
    else:
        config_object.args.engine.device = torch.device("cpu")
        logging.info("Using CPU")
    torch.backends.cudnn.benchmark = config_object.args.engine.runBenchmark


def load_likelihood_model(config_object):
    # VALIDATED LIKELIHOOD MODELS
    # OPTIONS: {'gaussian', 'rician'}
    if hasattr(config_object.args.engine, 'likelihood_model'):
        if hasattr(config_object.args.engine.likelihood_model, '__name__'):
            logging.info("Using CUSTOM likelihood model: {}".format(config_object.args.engine.likelihood_model.__name__))
        else:
            logging.info("Using unamed CUSTOM likelihood model: {}".format(config_object.args.engine.likelihood_model))
    else:
        if config_object.args.engine.likelihoodModel == 'custom':
            logging.warn("User selected custom likelihood model but did not override it")
        else:
            module_name = config_object.args.engine.likelihoodModel
            try:
                config_object.args.engine.likelihood_model = core_utilities.load_ext_module("core.models.likelihood." + 
                                                                                    module_name, module_name, config_object)
                if hasattr(config_object.args.engine.likelihood_model, '__name__'):
                    logging.info("Using INTERNAL likelihood model: {}".format(config_object.args.engine.likelihood_model.__name__))
                else:
                    logging.info("Using unamed INTERNAL likelihood model: {}".format(config_object.args.engine.likelihood_model))
            except:
                raise ImportError("Could not import the Likelihood model: {}".format(module_name))
            


def load_signal_model(config_object):
    # VALIDATED SIGNAL MODELS
    # OPTIONS: {'looklocker', 'fse'}
    if hasattr(config_object.args.engine, 'signal_model'):
        if hasattr(config_object.args.engine.signal_model, '__name__'):
            logging.info("Using CUSTOM signal model: {}".format(config_object.args.engine.signal_model.__name__))
        else:
            logging.info("Using unamed CUSTOM signal model: {}".format(config_object.args.engine.signal_model))
    else:
        if config_object.args.engine.signalModel == 'custom':
            logging.warn("User selected custom signal model but did not override it")
        else:
            module_name = config_object.args.engine.signalModel
            try:
                config_object.args.engine.signal_model = core_utilities.load_ext_module("core.models.signal." + 
                                                                                    module_name, module_name, config_object)
                if hasattr(config_object.args.engine.signal_model, '__name__'):
                    logging.info("Using INTERNAL signal model: {}".format(config_object.args.engine.signal_model.__name__))
                else:
                    logging.info("Using unamed INTERNAL signal model: {}".format(config_object.args.engine.signal_model))
            except:
                raise ImportError("Could not import the Signal model: {}".format(module_name))


def load_inference_model(config_object):
    # VALIDATED INFERENCE MODELS
    # OPTIONS: {'rim', 'mle', 'resnet'}
    if hasattr(config_object.args.engine, 'inference_model'):
        if hasattr(config_object.args.engine.inference_model, '__name__'):
            logging.info("Using CUSTOM inference model: {}".format(config_object.args.engine.inference_model.__name__))
        else:
            logging.info("Using unamed CUSTOM inference model: {}".format(config_object.args.engine.inference_model))
    else:
        if config_object.args.engine.inferenceModel == 'custom':
            logging.warn("User selected custom inference model but did not override it")
        else:
            module_name = config_object.args.engine.inferenceModel
            try:
                config_object.args.engine.inference_model = core_utilities.load_ext_module("core.models.inference." + 
                                                                                    module_name, module_name, config_object)
                if hasattr(config_object.args.engine.inference_model, '__name__'):
                    logging.info("Using INTERNAL inference model: {}".format(config_object.args.engine.inference_model.__name__))
                else:
                    logging.info("Using unamed INTERNAL inference model: {}".format(config_object.args.engine.inference_model))
            except:
                raise ImportError("Could not import the Inference model: {}".format(module_name))
   

def load_dataset_model(config_object):
    # VALIDATED DATASETS
    # OPTIONS: {'relaxometry'}
    if hasattr(config_object.args.engine, 'dataset_model'):
        if hasattr(config_object.args.engine.dataset_model, '__name__'):
            logging.info("Using CUSTOM dataset model: {}".format(config_object.args.engine.dataset_model.__name__))
        else:
            logging.info("Using unamed CUSTOM dataset model: {}".format(config_object.args.engine.dataset_model))
    else:
        if config_object.args.engine.datasetModel == 'custom':
            logging.warn("User selected custom dataset model but did not override it")
        else:
            module_name = config_object.args.engine.datasetModel
            try:
                module = importlib.import_module("core.models.dataset." + module_name)
                config_object.args.engine.dataset_model = module.DatasetModel(config_object)
                if hasattr(config_object.args.engine.dataset_model, '__name__'):
                    logging.info("Using INTERNAL dataset model: {}".format(config_object.args.engine.dataset_model.__name__))
                else:
                    logging.info("Using unamed INTERNAL dataset model: {}".format(config_object.args.engine.dataset_model))
            except:
                raise ImportError("Could not import the Module: {}".format(module_name))



def load_optimizer(config_object):
    # OPTIMIZER
    if isinstance(config_object.args.engine.inference_model, nn.Module):
        optimizer_options = ['ADAM', 'AdaDelta', 'RMSProp', 'SGD']
        if config_object.args.engine.optimizer == optimizer_options[0]:
            config_object.args.engine.optimizer = torch.optim.Adam(config_object.args.engine.inference_model.parameters(), lr=config_object.args.engine.learningRate)
        elif config_object.args.engine.optimizer == optimizer_options[1]:
            config_object.args.engine.optimizer = torch.optim.Adadelta(config_object.args.engine.inference_model.parameters(), lr=config_object.args.engine.learningRate)
        elif config_object.args.engine.optimizer == optimizer_options[2]:
            config_object.args.engine.optimizer = torch.optim.RMSprop(config_object.args.engine.inference_model.parameters(), lr=config_object.args.engine.learningRate)
        elif config_object.args.engine.optimizer == optimizer_options[3]:
            config_object.args.engine.optimizer = torch.optim.SGD(config_object.args.engine.inference_model.parameters(), lr=config_object.args.engine.learningRate)
        else:
            logging.warn("Optimizer '{}' not supported. Either choose between {} or implement your own optimizer".format(config_object.args.engine.lossFunction, optimizer_options))
    

def load_cost_function(config_object):
    # OPTIMIZER COST FUNCTION
    if hasattr(config_object.args.engine, 'objective_fun'):
        if config_object.args.engine.objective_fun.__name__:
            logging.info("Using CUSTOM training loss function: {}".format(config_object.args.engine.objective_fun.__name__))
    else:
        if config_object.args.engine.lossFunction == 'custom':
            logging.warn("User selected custom training loss function but did not override it")
        else:
            costfun_options = ['MSE', 'L1', 'NLLLoss', 'SmoothL1']
            if config_object.args.engine.lossFunction == costfun_options[0]:
                config_object.args.engine.objective_fun = torch.nn.MSELoss(reduction='mean')
            elif config_object.args.engine.lossFunction == costfun_options[1]:
                config_object.args.engine.objective_fun = torch.nn.L1Loss(reduction='mean')
            elif config_object.args.engine.lossFunction == costfun_options[2]:
                config_object.args.engine.objective_fun = torch.nn.NLLLoss(reduction='mean')
            elif config_object.args.engine.lossFunction == costfun_options[3]:
                config_object.args.engine.objective_fun = torch.nn.SmoothL1Loss(reduction='mean')
            else:
                logging.warn("Loss function '{}' not supported. Either choose between {} or implement your own loss function".format(config_object.args.engine.lossFunction, costfun_options))
            logging.info("Using INTERNAL training loss function: {}".format(config_object.args.engine.objective_fun))


def load_checkpoint(config_object):
    # LOAD PRE-TRAINED MODEL
    if isinstance(config_object.args.engine.inference_model, nn.Module):
        config_object.args.engine.inference_model.to(device=config_object.args.engine.device)
        if config_object.args.engine.loadCheckpoint:
            logging.info("Loading model checkpoint from {}.".format(config_object.args.engine.loadCheckpointPath))
            checkpoint_utilities.load(config_object)



def make(mode="training", override_modules=None):
    """Links all configurations to internal modules, which are dinamically imported.

    Args:
        config_object ([type: Configuration]): [Object containing all backend configuration settings]
        Required config_object.args:
            - useCUDA
            - device
            - runBenchmark
            - likelihoodModel
            - signalModel
            - inferenceModel
            - task
            - optimizer
            - learningRate
            - lossFunction
            - loadCheckpoint
            - loadCheckpointPath

    Returns:
        [type: Configuration]: Updated config_object containing all imported Python modules
    """

    config_object = Configuration(mode)

    if override_modules is not None:
        config_object = check_override(config_object, override_modules)
        
    configure_cuda(config_object)

    # LOAD CORE MODULES
    load_likelihood_model(config_object)

    load_signal_model(config_object)
    
    load_inference_model(config_object)

    load_dataset_model(config_object)    
    
    load_optimizer(config_object)

    load_cost_function(config_object)
            
    # DEFINITION OF DATALOADER 
    data_loader.create_dataloader(config_object)

    # DEFINITION OF TRAINING/ESTIMATION ENGINE
    core_utilities.get_engine(config_object)

    # LOAD MODEL CHECKPOINT
    load_checkpoint(config_object)

    if config_object.args.engine.displayConfigurations:
        print("")
        logging.info("*"*40)
        logging.info("CURRENT CONFIGURATIONS:")
        logging.info(config_object.args.__list_attr__())
        logging.info("*"*40)
        print("")

    return config_object


class Configuration(object):
    def __init__(self, mode):
        self.parser = argparse.ArgumentParser(description='Global configuration for inference models')
        self.group_global = self.parser.add_argument_group('global_config')
        
        configuration_types = {'dataset': configuration_utilities.DictToAttribute(),
                               'inference': configuration_utilities.DictToAttribute(),
                               'engine': configuration_utilities.DictToAttribute()
                                }

        self.args = configuration_utilities.OptsToAttributes()
        self.args.__update__(**configuration_types)

        self.args.engine.mode = mode
        self.args.engine.state_name = mode
        self.set_global_config()

    def set_global_config(self):
        self.group_global.add_argument('configurationFile', type=str, help='Path to Engine configuration file.')
        self.temp_args, _ = self.parser.parse_known_args()
        if os.path.isfile(self.temp_args.configurationFile):
            configuration_ = configuration_utilities.parse_json_configuration(self.temp_args.configurationFile)
            self.args.engine.__update__(**configuration_)
            self.required = False
        else:
            self.required = True
        cmd_configuration = self.parse_command_line_configuration()
        self.args.engine.__update__(**cmd_configuration)
        config_parser = configuration_utilities.ParseConfiguration()

        self.set_dataset_config(config_parser)
        self.set_inference_config(config_parser)

    def parse_imported_cmd_configuration(self, config_file):
        absolute_path = ntpath.abspath(config_file)
        norm_path = ntpath.normpath(ntpath.splitext(absolute_path)[0]).split('\\')
        module_name = norm_path[-1]
        module_path = '/'.join(ntpath.splitext(absolute_path)[0].split('\\')) + '.py'
        try:
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module 
            spec.loader.exec_module(module)

            cmd_config = module.Configuration(self)
            parsed_config = cmd_config.parse_configuration()
            return parsed_config

        except FileNotFoundError:
            print("")
            logging.warning("Could not find configuration file for module {}, at location {}".format(module_name, module_path))
            logging.info("Skipping parsing of command line arguments for {}".format(module_name))
            print("")
            return None

            
    def parse_command_line_configuration(self):
       
        self.group_global.add_argument('-configInference', required=self.required, type=str, help='Path to configuration file of the inference model')
        self.group_global.add_argument('-configDataset', required=self.required, type=str, help='Path to configuration file of the dataset model')
        
        self.group_global.add_argument('-inferenceModel', required=self.required, type=str, help='Name of inference model to generate or load data')
        self.group_global.add_argument('-signalModel', required=self.required, type=str, help='Name of signal model to generate or load data')
        self.group_global.add_argument('-likelihoodModel', required=self.required, type=str, help='Name of likelihood model to generate or load data')
        self.group_global.add_argument('-datasetModel', required=self.required, type=str, help='Name of dataset model to generate or load data')
        self.group_global.add_argument('-lossFunction', required=self.required, type=str, help='Cost function for network training')
        self.group_global.add_argument('-trainerModule', required=self.required, type=str, help='Trainer module (emcqmri, monai)')
        self.group_global.add_argument('-estimatorModule', required=self.required, type=str, help='Validation and estimation module (emcqmri, monai)')
        self.group_global.add_argument('-optimizer', required=self.required, type=str, help='Optimizer')
        self.group_global.add_argument('-useCUDA', required=self.required, type=configuration_utilities.str2bool, help='If True, use GPU. If False or not specified, use CPU')
        self.group_global.add_argument('-runBenchmark', required=self.required, type=configuration_utilities.str2bool, help='if True (default), run GPU optimization benchmark')
        self.group_global.add_argument('-allowCMDoverride', required=self.required, type=configuration_utilities.str2bool, help='If True, options in command line will override configuration file')
        self.group_global.add_argument('-displayConfigurations', required=self.required, type=configuration_utilities.str2bool, help='If True, display all parsed arguments from configuration file')
        
        self.group_global.add_argument('-trainingDataPath', required=self.required, type=str, help='Path to training data')
        self.group_global.add_argument('-runValidation', required=self.required, type=configuration_utilities.str2bool, help='If True, the training routine will also execute a validation step.')
        self.group_global.add_argument('-validationDataPath', required=self.required, type=str, help='Path to validation data')
        self.group_global.add_argument('-testingDataPath', required=self.required, type=str, help='Path to testing data')
        self.group_global.add_argument('-fileExtension', required=self.required, type=str, help='File extension of the dataset')
        self.group_global.add_argument('-preLoadData', required=self.required, type=configuration_utilities.str2bool, help='If True, it loads all data within folders. Avoid if data folder is very large')
        
        self.group_global.add_argument('-learningRate', required=self.required, type=float, help='Learning rate for network training (default:0.0001)')
        self.group_global.add_argument('-batchSize', required=self.required, type=float, help='Size of training batch')
        self.group_global.add_argument('-epochs', required=self.required, type=float, help='Number of training epochs. If mode=testing, epochs=1')
        self.group_global.add_argument('-loadCheckpoint', required=self.required, type=configuration_utilities.str2bool, help='Load existing checkpoint in -loadCheckpointPath')
        self.group_global.add_argument('-loadCheckpointPath', required=self.required, type=str, help='Path + filename to existing model checkpoint')
        self.group_global.add_argument('-saveResults', required=self.required, type=configuration_utilities.str2bool, help='Save estimates at each epoch at the specified -resultsPath')
        self.group_global.add_argument('-saveResultsPath', required=self.required, type=str, help='Path to save model output data. Required if -saveResults is True')
        self.group_global.add_argument('-saveCheckpoint', required=self.required, type=configuration_utilities.str2bool, help='Save a model checkpoint to the path specified in -saveCheckpointPath')
        self.group_global.add_argument('-saveCheckpointPath', required=self.required, type=str, help='Path to save model checkpoint')
        self.group_global.add_argument('-sulfixCheckpoint', required=self.required, type=str, help='Suffix to add to save checkpoint file')
        
        config_args, _ = self.parser.parse_known_args()
        configuration = configuration_utilities.convert_argparse_to_attr(config_args)

        return configuration
    
    def set_dataset_config(self, config_parser):
        ## Set configuration of the dataset
        dataset_configuration = config_parser.parse_configuration(self.args.engine.configDataset)
        self.args.dataset.__update__(**dataset_configuration)
        if self.args.engine.allowCMDoverride:
            config_ = self.parse_imported_cmd_configuration(self.args.engine.configDataset)
            if config_:
                self.args.dataset.__update__(**config_)

    def set_inference_config(self, config_parser):
        ## Set configuration of inference method
        method_configuration = config_parser.parse_configuration(self.args.engine.configInference)
        self.args.inference.__update__(**method_configuration)
        if self.args.engine.allowCMDoverride:
            config_ = self.parse_imported_cmd_configuration(self.args.engine.configInference)
            if config_:
                self.args.inference.__update__(**config_)


