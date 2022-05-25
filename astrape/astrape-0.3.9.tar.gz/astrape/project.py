from multiprocessing.sharedctypes import Value
from astrape.models.models_lightning import *
from astrape.constants.astrape_constants import *
import numpy as np
from typing import Union, List, Dict, Any, Optional
import pytorch_lightning as pl
from sklearn.base import BaseEstimator
from matplotlib import pyplot as plt
from astrape.experiment import Experiment
from astrape.models.models_lightning import *
from astrape.constants.astrape_constants import *
import numpy as np
from typing import Union, List, Dict, Any, Optional, cast, overload
import pytorch_lightning as pl
from sklearn.base import BaseEstimator
import os, json, sys
import inspect
import math
import random
from datetime import datetime
from torch.utils.tensorboard import SummaryWriter
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as mcolors
from sklearn.decomposition import PCA, KernelPCA
import logging
from itertools import product
log = logging.getLogger(__name__)

available_domain_types = ["points", "image", "audio"]


class BaseProject:

    def __init__(
        self,
        project_name : str,
        X : "np.ndarray",
        y : "np.ndarray",
        X_test : Optional["np.ndarray"] = None,
        y_test : Optional["np.ndarray"] = None,
        n_classes : Optional[int] = None,
        path : str = "."
    ) -> None:
        self.project_name = project_name
        self.X = X
        self.y = y
        self.X_test = X_test
        self.y_test = y_test
        self.n_classes = n_classes
        self.path = path
        if self.path[-1] == "/":
            self.path = self.path[:-1]
        
        
        ###########################################
        # Attributes that are not originated from
        # input arguments
        ###########################################
        if len(X.shape) == 2:
            self.dims = X.shape[1]
        elif len(X.shape) > 2:
            self.dims = X.shape[1:]
        else:
            raise ValueError("Wrong dimension for input X.")

        self.project_path = self.path + "/" + self.project_name
        self._create_folder(self.project_path)
        self.log_dir = self.project_path + "/projectlogs"
        self._create_folder(self.log_dir)
        self.project_logger = SummaryWriter(log_dir=self.log_dir)

        self.project_metadata = {}
        now = datetime.now()
        self.birthday = now.strftime("%b-%d-%Y-%H-%M-%S")
        
        self.exps = {} # dictionary of experiments
        self.n_exp = 0

        # axes for plotting
        self.best_model_types = None
        self.random_states = []
        self.performances = None 
        self._create_folder(self.project_path+"/results")
        for exp_name, exp in self.create_experiments(amount=1, stack_exps=False).items():
            pseudoexp = exp
        self.pseudoexp = pseudoexp # use this dummy experiement for calling Experiment methods
    def update_project_metadata(
        self
    ):
        self.project_metadata.update({'date of birth of this project' : str(self.birthday)})
        self.project_metadata.update({'number of Experiments created' : self.n_exp})
        self.project_metadata.update({'size of this Project in MB' : float(os.path.getsize(self.project_path)/10**6)})

        json_name = self.project_path +"/project_metadata.json" 
        with open(json_name, 'w') as fout:
            json.dump(self.project_metadata, fout)
    
    def create_experiments(
        self,
        amount : int = 10,
        test_size : float = 0.01,
        stack_models : bool = True,
        stack_exps : bool = True
    ):
        exp_common_parameters = {
            'project_name' : self.project_name,
            'X' : self.X,
            'y' : self.y,
            'X_test' : self.X_test,
            'y_test' : self.y_test,
            'n_classes' : self.n_classes,
            'X_test' : self.X_test,
            'y_test' : self.y_test,
            'test_size' : test_size,
            'stack_models' : stack_models,
            'path' : self.path
        }
        
        temp_exps = {}

        for i in range(amount):
            seed = np.random.choice(range(10**5))
            if seed in self.random_states:
                while seed in self.random_states:
                    seed = np.random.choice(range(10**5))
            self.random_states.append(seed)
            exp_parameters = {}
            exp_parameters.update(exp_common_parameters)
            exp_parameters.update({'random_number' : seed})
            exp = Experiment(**exp_parameters)
            exp_name = 'random_state-{}'.format(exp.random_state)
            if stack_exps:
                self.exps.update({exp_name : exp})
            if not stack_exps:
                temp_exps.update({exp_name : exp})
        self.update_project_metadata()
        if stack_exps:
            return self.exps
        else:
            return temp_exps


    def add_experiment(
        self,
        experiment : Experiment
    ):
        random_state = experiment.random_state
        if random_state in self.random_states:
            raise ValueError('There is already an "Experiment" with the same random state.')
        exp_name = 'random_state-{}'.format(random_state)
        self.exps.update({exp_name : experiment})

        self.update_project_metadata()
    
    def set_models(
        self,
        model_type,
        random_states : Optional[List[int]] = None, # if None, same models are set for all experiments created in the Project
        **hparams
    ):
        random_state_str_list = []
        
        if not random_states:
            for exp_name, exp in self.exps.items():
                exp.set_model(model_type, **hparams)
        else:
            for random_state in random_states:
                random_state_str_list.append('random_state-{}'.format(random_state))
            for random_state_str in random_state_str_list: 
                if random_state_str not in self.exps.keys():
                    print('No "Experiment" with {} is defined. We will skip this experiment.'.format(random_state_str))
                    continue
                exp = self.exps[random_state_str]
                exp.set_model(model_type, **hparams)
        self.update_project_metadata()

    def set_trainers(
        self,
        random_states : Optional[List[int]] = None, # if None, same trainers are set for all experiments created in the Project
        **trainer_config
    ):
        random_state_str_list = []
        
        if not random_states:
            for exp_name, exp in self.exps.items():
                exp.set_trainer(**trainer_config)
        else:
            for random_state in random_states:
                random_state_str_list.append('random_state-{}'.format(random_state))
            for random_state_str in random_state_str_list: 
                if random_state_str not in self.exps.keys():
                    print('No "Experiment" with {} is defined. We will skip this experiment.'.format(random_state_str))
                    continue
                exp = self.exps[random_state_str]
                exp.set_trainer(**trainer_config)
        self.update_project_metadata()

    def fit_experiments(
        self,
        random_states : Optional[List[int]] = None, # if None, all experiments will be fitted,
        **trainer_config
    ):
        random_state_str_list = []
        
        if not random_states:
            for exp_name, exp in self.exps.items():
                exp.fit(**trainer_config)
        else:
            for random_state in random_states:
                random_state_str_list.append('random_state-{}'.format(random_state))
            for random_state_str in random_state_str_list: 
                if random_state_str not in self.exps.keys():
                    print('No "Experiment" with {} is defined. We will skip this experiment.'.format(random_state_str))
                    continue
                exp = self.exps[random_state_str]
                exp.fit(**trainer_config)
        self.update_project_metadata()

    def save_ckpts(
        self,
        random_states : Optional[List[int]] = None, # if None, all experiments will save checkpoints
    ):
        random_state_str_list = []
        if not random_states:
            for exp_name, exp in self.exps.items():
                exp.save_ckpt()
        else:
            for random_state in random_states:
                random_state_str_list.append('random_state-{}'.format(random_state))
                for random_state_str in random_state_str_list: 
                    if random_state_str not in self.exps.keys():
                        print('No "Experiment" with {} is defined. We will skip this experiment.'.format(random_state_str))
                        continue
                    exp = self.exps[random_state_str]
                    exp.save_ckpt()
        self.update_project_metadata()

    def save_stacks(
        self,
        random_states : Optional[List[int]] = None, # if None, all experiments will save stacks
    ):
        random_state_str_list = []
        if not random_states:
            for exp_name, exp in self.exps.items():
                exp.save_stack()
        else:
            for random_state in random_states:
                random_state_str_list.append('random_state-{}'.format(random_state))
                for random_state_str in random_state_str_list: 
                    if random_state_str not in self.exps.keys():
                        print('No "Experiment" with {} is defined. We will skip this experiment.'.format(random_state_str))
                        continue
                    exp = self.exps[random_state_str]
                    exp.save_stack()
        self.update_project_metadata()
        
    def save_project(
        self
    ):
        if self.exps:
            self.save_stacks()
        self.update_project_metadata()

    def flush_exps(
        self,
        save_stacks : bool = True
    ):
        if self.exps and save_stacks:
            self.save_stacks()
        del self.exps
        self.exps = {}
        self.update_project_metadata()

    def plot_data(
        self,
        domain_type : str,
        dataformats : str = "NHWC",
        n_data : int = 10
    ):
        points_dir = self.project_path + "/visualizations"
        self._create_folder(points_dir)
        if domain_type == "points": # data points
            if self.dims == 1: # 1D
                fig = plt.figure()
                points_dict = {}
                for label_idx in range(self.n_classes):
                    points_dict.update({label_idx: self.X[self.y==label_idx]})
                    plt.scatter(x=points_dict[label_idx][:,0], y=points_dict[label_idx][:,1], label=label_idx)
                plt.title('Data Distribution')
                plt.xlabel('positions')
                plt.legend(loc=(1.05,1.05))
                plt.show()
                plt.savefig(points_dir+ "/points_distribution.png")  
                self.project_logger.add_figure('data distribution', fig)
            elif self.dims == 2 : # 2D
                fig = plt.figure()
                points_dict = {}
                for label_idx in range(self.n_classes):
                    points_dict.update({label_idx: self.X[self.y==label_idx]})
                    plt.scatter(x=points_dict[label_idx][:,0], y=points_dict[label_idx][:,1], label=label_idx)
                plt.title('Data Distribution')
                plt.xlabel('x positions')
                plt.ylabel('y positions')
                plt.legend(loc=(1.,1.))
                plt.show()
                plt.savefig(points_dir+ "/points_distribution.png")  
                self.project_logger.add_figure('data distribution', fig)
            elif self.dims == 3 : # 3D 
                fig1 = plt.figure()
                ax = fig1.add_subplot(111, projection='3d')
                points_dict = {}
                for label_idx in range(self.n_classes):
                    points_dict.update({label_idx: self.X[self.y==label_idx]})
                    ax.scatter(xs=points_dict[label_idx][:,0], ys=points_dict[label_idx][:,1], zs= points_dict[label_idx][:,2], label=label_idx)
                ax.set_xlabel('x positions')
                ax.set_ylabel('y positions')
                ax.set_zlabel('z positions')
                plt.legend(loc=(1.,1.))
                plt.title('Data Distribution')
                plt.show()
                plt.savefig(points_dir+ "/points_distribution_1.png")  
                self.project_logger.add_figure('data_distribution_1', fig1)
                plt.close(fig1)
                fig2 = plt.figure()
                ax = fig2.add_subplot(111, projection='3d')
                points_dict = {}
                for label_idx in range(self.n_classes):
                    points_dict.update({label_idx: self.X[self.y==label_idx]})
                    ax.scatter(xs=points_dict[label_idx][:,0], ys=points_dict[label_idx][:,1], zs= points_dict[label_idx][:,2], label=label_idx)
                ax.set_xlabel('x positions')
                ax.set_ylabel('y positions')
                ax.set_zlabel('z positions')
                ax.view_init(0, 90)
                plt.legend(loc=(1.,1.))
                plt.title('Data Distribution')
                plt.show()
                plt.savefig(points_dir+ "/points_distribution_2.png")  
                self.project_logger.add_figure('data_distribution_2', fig2)
                plt.close(fig2)
                fig3 = plt.figure()
                ax = fig3.add_subplot(111, projection='3d')
                points_dict = {}
                for label_idx in range(self.n_classes):
                    points_dict.update({label_idx: self.X[self.y==label_idx]})
                    ax.scatter(xs=points_dict[label_idx][:,0], ys=points_dict[label_idx][:,1], zs= points_dict[label_idx][:,2], label=label_idx)
                ax.set_xlabel('x positions')
                ax.set_ylabel('y positions')
                ax.set_zlabel('z positions')
                ax.view_init(0, 180)
                plt.legend(loc=(1.,1.))
                plt.title('Data Distribution')
                plt.show()
                plt.savefig(points_dir+ "/points_distribution_3.png")  
                self.project_logger.add_figure('data_distribution_3', fig3)
                plt.close(fig3)
                fig4 = plt.figure()
                ax = fig4.add_subplot(111, projection='3d')
                points_dict = {}
                for label_idx in range(self.n_classes):
                    points_dict.update({label_idx: self.X[self.y==label_idx]})
                    ax.scatter(xs=points_dict[label_idx][:,0], ys=points_dict[label_idx][:,1], zs= points_dict[label_idx][:,2], label=label_idx)
                ax.set_xlabel('x positions')
                ax.set_ylabel('y positions')
                ax.set_zlabel('z positions')
                ax.view_init(0, 270)
                plt.legend(loc=(1.,1.))
                plt.title('Data Distribution')
                plt.show()
                plt.savefig(points_dir+ "/points_distribution_4.png")  
                self.project_logger.add_figure('data_distribution_4', fig4)
                plt.close(fig4)
            else: # higher dimensions -> use PCA
                print('The dimension of data is higher than 3. We will use PCA and visualize the data using 2 principal axes.')
                pca = PCA(n_components=2)
                pca_data = pca.fit_transform(self.X)
                fig = plt.figure()
                points_dict = {}
                for label_idx in range(self.n_classes):
                    points_dict.update({label_idx: pca_data[self.y==label_idx]})
                    plt.scatter(x=points_dict[label_idx][:,0], y=points_dict[label_idx][:,1], label=label_idx)
                plt.title('Data Distribution')
                plt.xlabel('1st principal axis')
                plt.ylabel('2nd principal axis')
                plt.legend(loc=(1.,1.))
                plt.show()
                plt.savefig(points_dir+ "/points_distribution_PCA.png")  
                self.project_logger.add_figure('data distribution_PCA', fig)

                
    
        elif domain_type == "image":

            if len(self.dims) == 1 :
                raise AssertionError("Wrong dimension {} for image data. It should be at least 2-dimensional.".format(self.dims))
            img_dir = self.project_path + "/visualizations"
            self._create_folder(img_dir)
            
            if len(self.dims) == 2 : # 2D, black & white
                imgs = np.reshape(self.X, (-1, *self.dims, 1)) # (# of samples, height, width, # of channels) i.e., NHWC       
            elif len(self.dims) > 2 : # 2D, colored images
                imgs = np.reshape(self.X, (-1, *self.dims)) # (# of samples, height, width, # of channels) i.e., NHWC


            sampling_idx = np.random.choice(range(imgs.shape[0]), size=n_data)
            imgs_to_show = imgs[sampling_idx]
            labels_to_show = self.y[sampling_idx]
            # for logging
            self.project_logger.add_images('sample_images', imgs_to_show, dataformats=dataformats)
            dataformats_without_N = dataformats.replace("N","")
            for i in range(n_data):
                self.project_logger.add_image(
                    "sample_images/image_{}_label_{}".format(i, labels_to_show[i]),
                    imgs_to_show[i],
                    dataformats=dataformats_without_N
                )
            # for plotting
            rows = int(math.sqrt(n_data)) + 1
            cols = int(math.sqrt(n_data))
            fig = plt.figure(figsize=(5*rows, 5*cols))
            idx = 0
            for i in range(1, rows+1):
                for j in range(1, cols+1):
                    idx += 1
                    if idx < n_data + 1:
                        img = fig.add_subplot(rows, cols, idx)
                        img.imshow(self.X[sampling_idx][idx-1])
                        img.set_title('label : {}'.format(labels_to_show[idx-1]))
            plt.show()
            plt.savefig(img_dir + "/image_samples.png")       

        elif self.domain_type == "audio":
            raise NotImplementedError("Audio data unimplemented.") # TODO: implement this
        else:
            raise NotImplementedError("Unsupported domain type {}. Supported domain types are {}".format(self.domain_type, available_domain_types))
        
        self.update_project_metadata()

    def get_available_random_states(
        self
    ):
        log_base_dir = self.project_path + "/FIT"
        random_state_dir_list = []
        for random_state_dir in os.listdir(log_base_dir):
            random_state_dir_list.append(log_base_dir + "/" + random_state_dir)

        return random_state_dir_list

    def search_standard(
        self,
        val_metric : str = 'val/acc'
    ):
        performances = []
        best_model_type = None
        best_metadata = None
        best_val = None
        best_model_structures = {}
        best_model_types = {}
        mode = 'min' if val_metric == 'val/loss' else 'max'
        random_state_dir_list = self.get_available_random_states()
        for random_state_dir in random_state_dir_list:
            jsonlog_dir = random_state_dir+"/logs/jsonlogs"
            for model_type_dir in os.listdir(jsonlog_dir): # .../logs/jsonlogs
                for metadata_dir in os.listdir(jsonlog_dir + "/" + model_type_dir): # ex) .../MLP
                    for version in os.listdir(jsonlog_dir + "/" + model_type_dir + "/" + metadata_dir): # ex) ../MLP-n_layers5...
                        for file in os.listdir(jsonlog_dir + "/" + model_type_dir + "/" + metadata_dir + "/" + version): # ex) .../version_1
                            file_path = jsonlog_dir + "/" + model_type_dir + "/" + metadata_dir + "/" + version + "/" + file # actual jsonfile
                            with open(file_path, "r") as json_file:
                                logs = json.load(json_file)
                                val_score = logs[val_metric] if isinstance(logs[val_metric], float) else logs[val_metric][-1]
                                if best_val is None:
                                    best_val = val_score
                                    best_model_type = model_type_dir
                                    best_metadata = metadata_dir
                                elif mode == "max" and val_score > best_val:
                                    best_val = val_score
                                    best_model_type = model_type_dir
                                    best_metadata = metadata_dir
                                elif mode == "min" and val_score < best_val:
                                    best_val = val_score
                                    best_model_type = model_type_dir
                                    best_metadata = metadata_dir
            # update best_model_types for each random state
            if best_model_type not in best_model_types.keys():
                best_model_types.update({best_model_type : 1})
            else:
                best_model_types.update({best_model_type : best_model_types[best_model_type]+1})

            # update best_model_structures for each random state
            if best_metadata not in best_model_structures.keys():
                best_model_structures.update({best_metadata: 1})
            else:
                best_model_structures.update({best_metadata : best_model_structures[best_metadata]+1})
            # update performances for each random state
            if best_val:
                performances.append(best_val)
        performances = np.array(performances)
        if performances == np.array([]):
            raise ValueError("None is in performances.")
        return performances, best_model_types, best_model_structures

    def search_with_model_type(
        self,
        model_type : Union["pl.LightningModule", "BaseEstimator"],
        val_metric : str = 'val/acc'
    ):
        performances = []
        best_model_structures = {}
        best_val = None
        best_metadata = None
        mode = 'min' if val_metric == 'val/loss' else 'max'
        random_state_dir_list = self.get_available_random_states()
        for random_state_dir in random_state_dir_list:
            jsonlog_dir = random_state_dir+"/logs/jsonlogs"
            for model_type_dir in os.listdir(jsonlog_dir): # .../logs/jsonlogs
                if str(model_type_dir) == model_type.__name__:
                    for metadata_dir in os.listdir(jsonlog_dir + "/" + model_type_dir): # .../MLP 
                        for version in os.listdir(jsonlog_dir + "/" + model_type_dir + "/" + metadata_dir): # .../MLP-n_layers5...
                            for file in os.listdir(jsonlog_dir + "/" + model_type_dir + "/" + metadata_dir + "/" + version): # .../version_1
                                file_path = jsonlog_dir + "/" + model_type_dir + "/" + metadata_dir + "/" + version + "/" + file # actual jsonfile
                                with open(file_path, "r") as json_file:
                                    logs = json.load(json_file)
                                    val_score = logs[val_metric] if isinstance(logs[val_metric], float) else logs[val_metric][-1]
                                    if best_val is None:
                                        best_val = val_score
                                        best_metadata = metadata_dir
                                    elif mode == "max" and val_score > best_val:
                                        best_val = val_score
                                        best_metadata = metadata_dir
                                    elif mode == "min" and val_score < best_val:
                                        best_val = val_score
                                        best_metadata = metadata_dir
            # update performances for each random state
            if best_val:
                performances.append(best_val)
            # update best_model_structures for each random state
            if best_metadata not in best_model_structures.keys():
                best_model_structures.update({best_metadata: 1})
            else:
                best_model_structures.update({best_metadata : best_model_structures[best_metadata]+1})
            
        performances = np.array(performances)

        if performances == np.array([]):
            raise ValueError("None is in performances. You may have not saved {}".format(model_type))

        return performances, best_model_structures

    def search_with_model_type_hparams(
        self,
        model_type : Union["pl.LightningModule", "BaseEstimator"], 
        val_metric : str = 'val/acc',
        **hparams
    ):
        performances = []
        best_val = None
        
        if BaseEstimator in inspect.getmro(model_type):
            pseudomodel = self.pseudoexp.set_model(model_type, **hparams)
            metadata = self.pseudoexp.set_model_metadata(pseudomodel, pseudomodel.__dict__)
        elif pl.LightningModule in inspect.getmro(model_type):
            pseudomodel = self.pseudoexp.set_model(model_type, **hparams)
            metadata = self.pseudoexp.set_model_metadata(pseudomodel, pseudomodel.hparams)     
        mode = 'min' if val_metric == 'val/loss' else 'max'
        random_state_dir_list = self.get_available_random_states()
        for random_state_dir in random_state_dir_list:
            jsonlog_dir = random_state_dir+"/logs/jsonlogs"
            for model_type_dir in os.listdir(jsonlog_dir):
                for metadata_dir in os.listdir(jsonlog_dir + "/" + model_type_dir):
                    if str(metadata_dir) == metadata: 
                        best_val = None
                        for version in os.listdir(jsonlog_dir + "/" + model_type_dir + "/" + metadata_dir):
                            for file in os.listdir(jsonlog_dir + "/" + model_type_dir + "/" + metadata_dir + "/" + version):
                                file_path = jsonlog_dir + "/" + model_type_dir + "/" + metadata_dir + "/" + version + "/" + file
                                with open(file_path, "r") as json_file:
                                    logs = json.load(json_file)
                                    val_score = logs[val_metric] if isinstance(logs[val_metric], float) else logs[val_metric][-1]
                                    if best_val is None:
                                        best_val = val_score
                                    elif mode == "max" and val_score > best_val:
                                        best_val = val_score
                                    elif mode == "min" and val_score < best_val:
                                        best_val = val_score
            if best_val:
                performances.append(best_val)
            
        performances = np.array(performances)
        if performances == np.array([]):
            raise ValueError("None is in performances. You may have inputted the wrong model strucutre.")
        return performances, metadata
                    
    def search_all_models(
        self,
        val_metric : str = 'val/acc'
    ):
        metadata_list = []
        performances_list = [] # list of performances(list). len(performances_list) == len(metadata_list)
        mode = 'min' if val_metric == 'val/loss' else 'max'
        random_state_dir_list = self.get_available_random_states()
        random_number_list = []
        best_val = None
        #best_val_dict = {}
        for random_number_dir in random_state_dir_list:
            random_number = random_number_dir.split("-")[-1]
            random_number_list.append(random_number)

        performances_per_metadata = {}
        for random_state_dir in random_state_dir_list:
            jsonlog_dir = random_state_dir+"/logs/jsonlogs"
            for model_type_dir in os.listdir(jsonlog_dir): # ../logs/jsonlogs
                for metadata_dir in os.listdir(jsonlog_dir + "/" + model_type_dir): # ../MLP
                    #best_val_dict.update({metadata_dir : []})
                    if metadata_dir not in metadata_list:
                        metadata_list.append(metadata_dir) 
                        performances_per_metadata.update({metadata_dir: []})
                    best_val = None
                    for version in os.listdir(jsonlog_dir + "/" + model_type_dir + "/" + metadata_dir): # ../MLP_n_layers...   
                        for file in os.listdir(jsonlog_dir + "/" + model_type_dir + "/" + metadata_dir + "/" + version): # ../version_0
                            file_path = jsonlog_dir + "/" + model_type_dir + "/" + metadata_dir + "/" + version + "/" + file # actual jsonfile
                            with open(file_path, "r") as json_file:
                                logs = json.load(json_file)
                                val_score = logs[val_metric] if isinstance(logs[val_metric], float) else logs[val_metric][-1]
                                if best_val is None:
                                    best_val = val_score
                                elif mode == "max" and val_score > best_val:
                                    best_val = val_score
                                elif mode == "min" and val_score < best_val:
                                    best_val = val_score
                    if best_val:
                        performances_per_metadata[metadata_dir].append(best_val)
        for metadata in metadata_list:
            performances_list.append(np.array(performances_per_metadata[metadata]))
        performances_list = np.array(performances_list)

        if not metadata_list or None in performances_list or performances_list == np.array([]):
            raise ValueError("Nothing has been logged.") 
        return metadata_list, performances_list

    @staticmethod
    def _create_folder(directory : str) -> str:
        os.makedirs(directory, exist_ok=True)
        return directory

    @staticmethod
    def _dict_to_str(dictionary : dict) -> str:
        out = str(dictionary).replace("{", "").replace("}","").replace(" ","-").replace(":","").replace("-","").replace("\n", "-").replace('"', "").replace(".","d").replace("'","")
        return out
        

class Project(BaseProject):
    def __init__(
        self,
        project_name : str,
        X : "np.ndarray",
        y : "np.ndarray",
        X_test : Optional["np.ndarray"] = None,
        y_test : Optional["np.ndarray"] = None,
        n_classes : Optional[int] = None,
        path : str = "."
    ):
        super().__init__(
            project_name=project_name,
            X=X,
            y=y,
            X_test=X_test,
            y_test=y_test,
            n_classes=n_classes,
            path=path
        )

    def plot_best_models(
            self,
            val_metric : str = 'val/acc',
            plt_title : Optional[str] = None
        ):

            performances, best_model_types, best_model_structures = self.search_standard(val_metric)
            random_state_dir_list = self.get_available_random_states()
            ymin = performances.min() - 0.1 if performances.min() > 0.1 else 0
            ymax = performances.max() + 0.1 if performances.max() < 0.9 else 1
            random_number_list = []
            for random_number_dir in random_state_dir_list:
                random_number = random_number_dir.split("-")[-1]
                random_number_list.append(random_number)
            fig1 = plt.figure()
            x = np.arange(len(performances)) / 2
            plt.bar(x, performances, width=0.1)
            plt.xticks(x, random_number_list)
            plt.xticks(rotation=70)
            plt.xlabel("random state")
            plt.grid(True)
            plt.ylabel(val_metric)

            if not plt_title:
                plt_title = 'Best Performances'
            plt.title(plt_title)
            plt.ylim = (ymin, ymax)
            self._create_folder(self.project_path+"/results")
            plt.show()
            plt.savefig(self.project_path+"/results/{}.png".format(plt_title))
            self.project_logger.add_figure("results/{}".format(plt_title), fig1)
            
            plt.close(fig1)

            info = {'best model structures' : best_model_structures, 'best model types' : best_model_types}

            return performances, info

    def plot_characteristics(
        self,
        val_metric : str = 'val/acc',
        plt_title : Optional[str] = None
    ):
        
        performances, best_model_types, best_model_structures = self.search_standard(val_metric)
        fig2 = plt.figure()
        sizes = list(best_model_structures.values())
        wedges, texts, autotexts = plt.pie(sizes, autopct='%1.1f%%',textprops=dict(color="w"))
        if not plt_title:
            plt_title = 'Frequencies of'
        plt.title('{} the Best Model Structures'.format(plt_title))
        plt.legend(wedges, best_model_structures.keys(), title="Model Structures", loc="center left",bbox_to_anchor=(1, 0, 0.5, 1))
        plt.setp(autotexts, size=8, weight="bold")
        plt.axis('equal')
        plt.show()
        plt.savefig(self.project_path+"/results/{} the Best Model Structures.png".format(plt_title))
        self.project_logger.add_figure("results/{} the Best Model Structures".format(plt_title), fig2)
        plt.close(fig2)
        
        fig3 = plt.figure()
        sizes = list(best_model_types.values())
        wedges, texts, autotexts = plt.pie(sizes,  autopct='%1.1f%%') 
        plt.axis('equal')
        plt.setp(autotexts, size=8, weight="bold")
        plt.title('{} the Best Model Types'.format(plt_title))
        plt.legend(wedges, best_model_types.keys(), title="Model Types", loc="center left",bbox_to_anchor=(1, 0, 0.5, 1))
        plt.show()
        plt.savefig(self.project_path+"/results/{} the Best Model Types.png".format(plt_title))
        self.project_logger.add_figure("results/{} the Best Model Types".format(plt_title), fig3)
        plt.close(fig3)

        self.update_project_metadata()
        info = {'best model structures' : best_model_structures, 'best model types' : best_model_types}

        return performances, info
        

    def plot_identical_model_type(
        self,
        model_type : Union["pl.LightningModule","BaseEstimator"],
        val_metric : str = "val/acc",
        plt_title : Optional[str] = None
    ):
        performances, best_model_structures = self.search_with_model_type(val_metric=val_metric, model_type=model_type)
        random_state_dir_list = self.get_available_random_states()
        ymin = performances.min() - 0.1 if performances.min() > 0.1 else 0
        ymax = performances.max() + 0.1 if performances.max() < 0.9 else 1
        random_number_list = []
        for random_number_dir in random_state_dir_list:
            random_number = random_number_dir.split("-")[-1]
            random_number_list.append(random_number)

        fig1 = plt.figure()
        x = np.arange(len(random_number_list))
        plt.bar(x, performances, width=0.1) #, bins=len(performances), label=val_metric)
        plt.xticks(x, random_number_list)
        plt.xticks(rotation=70)
        plt.xlabel("random state")
        plt.ylabel(val_metric)
        plt.grid(True)
        plt.ylim = (ymin, ymax)
        if not plt_title:
            plt_title = 'Best Performances : Model Type \n{}'.format(model_type.__name__)
        plt.title(plt_title)
        plt.show()
        plt.savefig(self.project_path+"/results/{}.png".format(plt_title))
        self.project_logger.add_figure("results/{}".format(plt_title), fig1)
        plt.close(fig1)
        self.update_project_metadata()
        info = {'best model structures' : best_model_structures}

        return performances, random_number_list, info

    def plot_identical_model_structure(
        self,
        model_type : Union["pl.LightningModule","BaseEstimator"],
        val_metric : str = "val/acc",
        plt_title : Optional[str] = None,
        **hparams
    ):
        performances, metadata = self.search_with_model_type_hparams(val_metric=val_metric, model_type=model_type, **hparams)
        random_state_dir_list = self.get_available_random_states()
        ymin = performances.min() - 0.1 if performances.min() > 0.1 else 0
        ymax = performances.max() + 0.1 if performances.max() < 0.9 else 1
        random_number_list = []
        for random_number_dir in random_state_dir_list:
            random_number = random_number_dir.split("-")[-1]
            random_number_list.append(random_number)
        fig1 = plt.figure()
        x = np.arange(len(performances))
        plt.plot(performances, 'ro') #, bins=len(performances), label=val_metric)
        plt.plot(performances, label=metadata)
        plt.xticks(x, random_number_list)
        plt.xticks(rotation=70)
        plt.xlabel("random state")
        plt.ylabel(val_metric)
        plt.grid(True)
        plt.legend(title="Model Structures", loc="center left",bbox_to_anchor=(1, 0, 0.5, 1))
        plt.ylim = (ymin, ymax)
        
        if not plt_title:
            plt_title = 'Performances of a Model Structure'
        plt.title(plt_title)
        plt.savefig(self.project_path+"/results/{}.png".format(metadata))
        plt.show()
        self.project_logger.add_figure('results/{}'.format(metadata), fig1)
        plt.close(fig1)

        self.update_project_metadata()

        return performances, random_number_list
    
    @staticmethod
    def generate_marker_style(amount):
        color_list = ['b','g','r','c','m','y','k','w']
        shape_list = [".", "v", "1", "*", "^", "s", "<"]
        random.shuffle(color_list)
        random.shuffle(shape_list)
        marker_styles = []
        for color, shape in product(color_list, shape_list):
            marker_styles.append(color+shape)
            if len(marker_styles) == amount:
                break
        return marker_styles
    def plot_all_models(
        self,
        val_metric : str = "val/acc",
        plt_title : Optional[str] = None
    ):

        # find all available model structures
        
        metadata_list, performances_list = self.search_all_models(val_metric)
        random_state_dir_list = self.get_available_random_states()
        random_number_list = []
        for random_number_dir in random_state_dir_list:
            random_number = random_number_dir.split("-")[-1]
            random_number_list.append(random_number)
        fig1 = plt.figure()
        ymin_list = ymax_list = []
        marker_styles = self.generate_marker_style(len(metadata_list))
        for idx, (metadata, performance_per_metadata) in enumerate(zip(metadata_list, performances_list)):
            ymin_list.append(performance_per_metadata.min())
            ymax_list.append(performance_per_metadata.max())
            plt.plot(performance_per_metadata, marker_styles[idx])
            plt.plot(performance_per_metadata, label=metadata)
            
        ymin_list, ymax_list = np.array(ymin_list), np.array(ymax_list)
        ymin, ymax = ymin_list.min(), ymax_list.max()
        
        if not plt_title:
            plt_title = "Performances Among Models"
        plt.title(plt_title)
        x = np.arange(len(random_number_list))
        plt.xticks(x, random_number_list)
        plt.xticks(rotation=70)
        plt.xlabel("random state")
        plt.ylabel(val_metric)
        plt.grid(True)
        plt.ylim = (ymin, ymax)
        plt.legend(title="Model Structures", loc="center left",bbox_to_anchor=(1, 0, 0.5, 1))
        plt.show()
        plt.savefig(self.project_path+"/results/{}.png".format(plt_title))
        self.project_logger.add_figure('results/{}'.format(plt_title), fig1)
        
        plt.close(fig1)

        fig2 = plt.figure()
        plot_dict = {}
        for metadata, performances in zip(metadata_list, performances_list):    
            plot_dict.update({metadata : performances}) 
        keys = list(plot_dict.keys())
        data = list(plot_dict.values())
        
        legend_dict = {}
        for idx, metadata in enumerate(keys):
            bp = plt.boxplot(
                data[idx], positions=[idx+1], 
                patch_artist=True, boxprops=dict(facecolor="C{}".format(2*idx))
                )
            legend_dict.update({'bp{}'.format(idx): bp})
        plt.legend(
            [bp["boxes"][0] for bp in legend_dict.values()], 
            [metadata for metadata in keys],
            title="Model Structures", 
            loc="center left", 
            bbox_to_anchor=(1, 0, 0.5, 1)
        )
    
        plt.title('{}: Box Plot'.format(plt_title))
        plt.xlabel("model structure")
        plt.ylabel(val_metric)
        plt.grid(True)
        plt.show()
        plt.savefig(self.project_path+"/results/{}_boxplot.png".format(plt_title))
        self.project_logger.add_figure('results/{}_boxplot'.format(plt_title), fig2)


        return metadata_list, performances_list

    

