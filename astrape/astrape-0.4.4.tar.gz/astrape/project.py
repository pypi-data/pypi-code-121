from multiprocessing.sharedctypes import Value
from astrape.models.models_lightning import *
from astrape.constants.astrape_constants import *
import numpy as np
from typing import Union, List, Dict, Any, Optional
import pytorch_lightning as pl
from sklearn.base import BaseEstimator
from matplotlib import pyplot as plt
import pandas as pd
from astrape.experiment import Experiment
from astrape.models.models_lightning import *
from astrape.constants.astrape_constants import *
import numpy as np
from typing import Union, List, Dict, Any, Tuple, Optional, cast, overload
import pytorch_lightning as pl
from sklearn.base import BaseEstimator
import os, json
import inspect
import math
import random
from datetime import datetime
from torch.utils.tensorboard import SummaryWriter
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.colors as mcolors
from sklearn.decomposition import PCA
import logging
from itertools import product
log = logging.getLogger(__name__)

available_domain_types = ["points", "image", "audio"]


class BaseProject:
    r"""Parent class of ``Project`` class. 
    
    Methods will perform 1)plotting data, 2)generating ``Experiments``,
    3)setting models across the generated `Experiment`s, 4)setting trainers across the generated ``Experiments``,
    5)training models across the generated `Experiment`s, 6)updating project metadata,
    7)adding individual ``Experiment`` to the project, 8)saving checkpoints for ``Experiments`` saved in ``exps``,
    9)saving stacks for each ``Experiment`` in ``exps``, 9)flushing all ``exps``. 

    Attributes:

        project_name (str): Name of the project. Directory of {path}/{project_name} will be created.

        X (np.ndarray or torch.Tensor or pd.DataFrame): Data for the project. If X_test is not specified, X would be splitted(stratify=y) into train/val data with a given random state.

        y (np.ndarray or torch.Tensor or pd.DataFrame): Labels for the project. If y_test is not specified, y would be splitted(stratify=y) into train/val labels with a given random state.

        X_test (np.ndarray or torch.Tensor or pd.DataFrame, optional): Test data for the project. Specify this when there is a separate test data.
            Default: ``None``

        y_test (np.ndarray or torch.Tensor or pd.DataFrame, optional): Test labels for the project. Specify this when there is a separate test data.
            Default: ``None``

        n_classes (int): Number of classes for the classification task. Don't specify this when performing regression tasks.
            Default: ``None``

        path (str): Base path for the project. Default is the current directory.
            Default: ``'.'``

        dims (:obj:`int` or :obj:`tuple` of `int`) : Dimensions of the data. Number of samples is excluded in dims.

        project_path (:obj:`str`): Path for the project. It will be {path}/{project_name}.

        log_dir (:obj:`str`): Path for saving plotted images and figures. It will be {project_path}/{projectlogs}.

        project_logger (:obj:`SummaryWriter`): TensorBoard Logger for logging.

        project_metadata (:obj:`dict`): Dictionary describing the project.

        birthday (str): Time when the project is created.

        exps (:obj:`dict` of :obj:`str`, :obj:`Experiment`): `Project` can control ``Experiments`` in ``exps``.
        
        n_exps (int): Number of ``Experiemnt``s in ``exps``.

        pseudoexp (`Experiment`): Dummy ``Experiment`` for applying methods in ``Experiment``.
    """

    def __init__(
        self,
        project_name : str,
        X : Union["np.ndarray", "torch.Tensor", "pd.DataFrame"],
        y : Union["np.ndarray", "torch.Tensor", "pd.DataFrame"],
        X_test : Optional[Union["np.ndarray", "torch.Tensor", "pd.DataFrame"]] = None,
        y_test : Optional[Union["np.ndarray", "torch.Tensor", "pd.DataFrame"]] = None,
        n_classes : Optional[int] = None,
        path : str = "."
    )->None:
        r"""Creates a ``Project``.

        Args:
            
            project_name (str): Name of the project. Directory of {path}/{project_name} will be created.

            X (np.ndarray or torch.Tensor or pd.DataFrame): Data for the project. If X_test is not specified, X would be splitted(stratify=y) into train/val data with a given random state.

            y (np.ndarray or torch.Tensor or pd.DataFrame): Labels for the project. If y_test is not specified, y would be splitted(stratify=y) into train/val labels with a given random state.

            X_test (np.ndarray or torch.Tensor or pd.DataFrame, optional): Test data for the project. Specify this when there is a separate test data.
                Default: ``None``

            y_test (np.ndarray or torch.Tensor or pd.DataFrame, optional): Test labels for the project. Specify this when there is a separate test data.
                Default: ``None``

            n_classes (int): Number of classes for the classification task. Don't specify this when performing regression tasks.
                Default: ``None``

            path (str): Base path for the project. Default is the current directory.
                Default: ``'.'``

        Returns:

            None
        """
        self.project_name = project_name
        self.X = X
        self.y = y
        self.X_test = X_test
        self.y_test = y_test
        self.n_classes = n_classes
        self.path = path
        if self.path[-1] == "/":
            self.path = self.path[:-1] # format path
        
        if len(X.shape) == 2:
            self.dims = X.shape[1]
        elif len(X.shape) > 2:
            self.dims = X.shape[1:]
        else:
            raise ValueError(f"Wrong dimension for input X.")

        self.project_path = f'{self.path}/{self.project_name}' 
        self._create_folder(self.project_path)
        self.log_dir = f'{self.project_path}/projectlogs'
        self._create_folder(self.log_dir)
        self.project_logger = SummaryWriter(log_dir=self.log_dir)
        self.random_states = []
        now = datetime.now()
        birthday = now.strftime("%b-%d-%Y-%H-%M-%S")
        self.project_metadata = {'date of birth of this project' : str(birthday)}
        
        
        self.exps = {}
        self.n_exp = 0

        self._create_folder(f'{self.project_path}/results')
        for exp_name, exp in self.create_experiments(amount=1, stack_exps=False).items():
            pseudoexp = exp
        self.pseudoexp = pseudoexp # use this dummy experiement for calling Experiment methods

    def update_project_metadata(
        self
    )->None:
        r"""Updates metadata of the project.
        """
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
    )->Dict[str, "Experiment"]: # {name of the experiment} : Experiment
        r"""Generates ``Experiments`` and stack them to ``exps`` if needed.

        Args:
            
            amount (int) : The number of ``Experiments`` you want to generate.
                Default: ``10``
            
            test_size (float) : Test size when splitting the data. Neccessary for creating ``Experiments``.
                Default: ``1e-2``
            
            stack_models (bool) : Whehter to stack models in each ``Experiment`` or not.
                Default: ``True``
            
            stack_exps (bool) : Whether to stack generated ``Experiments`` to ``exps`` or not.
                Default: ``True``
        
        Returns:
            
            dict: dictionary of ``Experiments``. Will be ``exps`` if ``stack_exps`` is True, dictionary of ``Experiments`` if ``stack_exps`` is False.
        
        """
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
            exp_name = f'random_state-{exp.random_state}'
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
    )->None:
        r"""Add an individual ``Experiment`` to ``exps``.

        Args:

            experiment (:obj:``Experiment``): ``Experiment`` you want to add.

        Returns:

            None
        """
        random_state = experiment.random_state
        if random_state in self.random_states:
            raise ValueError('There is already an "Experiment" with the same random state.')
        exp_name = f'random_state-{random_state}'
        self.exps.update({exp_name : experiment})

        self.update_project_metadata()
    
    def set_models(
        self,
        model_type,
        random_states : Optional[List[int]] = None, # if None, same models are set for all experiments created in the Project
        **hparams
    )->None:
        r"""Set identical models across ``Experiments``.

        Args:

            model_type (``LightningModule`` or ``BaseEstimator``): Class of the model you want to use.

            **hparams (Any): Hyperparameters for the model. 

            random_states (:obj:``list`` of `int`, optional): The list of random states of ``Experiments`` you want to set model to. If None, will set models for all ``Experiments`` in ``exps``.
                Default: ``None``

        Returns:

            None
        """
        random_state_str_list = []
        
        if not random_states:
            for exp_name, exp in self.exps.items():
                exp.set_model(model_type, **hparams)
        else:
            for random_state in random_states:
                random_state_str_list.append(f'random_state-{random_state}')
            for random_state_str in random_state_str_list: 
                if random_state_str not in self.exps.keys():
                    raise ValueError(f'No "Experiment" with {random_state_str} is defined.')
                    
                exp = self.exps[random_state_str]
                exp.set_model(model_type, **hparams)
        self.update_project_metadata()

    def set_trainers(
        self,
        random_states : Optional[List[int]] = None, # if None, same trainers are set for all experiments created in the Project
        **trainer_config
    )->None:
        r"""Set identical trainers across ``Experiments``.

        Args:

            **trainer_config (Any): Trainer configurations.

            random_states (:obj:``list`` of `int`, optional): The list of random states of ``Experiments`` you want to set trainer to. If None, will set trainers for all ``Experiments`` in ``exps``.
                Default: ``None``

        Returns:
            
            None
    
        """
        random_state_str_list = []
        
        if not random_states:
            for exp_name, exp in self.exps.items():
                exp.set_trainer(**trainer_config)
        else:
            for random_state in random_states:
                random_state_str_list.append(f'random_state-{random_state}')
            for random_state_str in random_state_str_list: 
                if random_state_str not in self.exps.keys():
                    raise ValueError(f'No "Experiment" with {random_state_str} is defined.')
                exp = self.exps[random_state_str]
                exp.set_trainer(**trainer_config)
        self.update_project_metadata()

    def fit_experiments(
        self,
        random_states : Optional[List[int]] = None, # if None, all experiments will be fitted,
        **trainer_config
    )->None:
        r"""Fit models in ``Experiments`` stacked in ``exps``.

        Args:

            **trainer_config (Any): Trainer configurations.

            random_states (:obj:``list`` of `int`, optional): The list of random states of ``Experiments`` you want to fit. If None, will fit all ``Experiments`` in ``exps``.
                Default: ``None``

        Returns:

            None
        
        """
        random_state_str_list = []
        
        if not random_states:
            for exp_name, exp in self.exps.items():
                exp.fit(**trainer_config)
        else:
            for random_state in random_states:
                random_state_str_list.append(f'random_state-{random_state}')
            for random_state_str in random_state_str_list: 
                if random_state_str not in self.exps.keys():
                    raise ValueError(f'No "Experiment" with {random_state_str} is defined.')
                exp = self.exps[random_state_str]
                exp.fit(**trainer_config)
        self.update_project_metadata()

    def save_ckpts(
        self,
        random_states : Optional[List[int]] = None, # if None, all experiments will save checkpoints
    )->None:
        r"""Save checkpoints in ``Experiments`` stacked in ``exps``.

        Args:

            random_states (:obj:``list`` of `int`, optional): The list of random states of ``Experiments`` you want to save checkpoint. If None, will save checkpoint for all ``Experiments`` in ``exps``.
                Default: ``None``

        Returns:

            None
        
        """
        random_state_str_list = []
        if not random_states:
            for exp_name, exp in self.exps.items():
                exp.save_ckpt()
        else:
            for random_state in random_states:
                random_state_str_list.append(f'random_state-{random_state}')
                for random_state_str in random_state_str_list: 
                    if random_state_str not in self.exps.keys():
                        raise ValueError(f'No "Experiment" with {random_state_str} is defined.')
                    exp = self.exps[random_state_str]
                    exp.save_ckpt()
        self.update_project_metadata()

    def save_stacks(
        self,
        random_states : Optional[List[int]] = None, # if None, all experiments will save stacks
    )->None:
        r"""Apply ``save_stack()`` for ``Experiments`` in ``exps``.

        Args:

            random_states (:obj:``list`` of `int`, optional): The list of random states of ``Experiments`` you want to save stack. If None, will save stack for all ``Experiments`` in ``exps``.
                Default: ``None``

        Returns:

            None
        
        """
        random_state_str_list = []
        if not random_states:
            for exp_name, exp in self.exps.items():
                exp.save_stack()
        else:
            for random_state in random_states:
                random_state_str_list.append('random_state-{random_state}')
                for random_state_str in random_state_str_list: 
                    if random_state_str not in self.exps.keys():
                        raise ValueError(f'No "Experiment" with {random_state_str} is defined.')
                    exp = self.exps[random_state_str]
                    exp.save_stack()
        self.update_project_metadata()
        
    def save_project(
        self
    )->None:
        r"""Save all ``Experiments``.
        """
        if self.exps:
            self.save_stacks()
        self.update_project_metadata()

    def flush_exps(
        self,
        save_stacks : bool = True
    )->None:
        r"""Flushes ``exps`` after saving it.
        """
        if self.exps and save_stacks:
            self.save_stacks()
        del self.exps
        self.exps = {}
        self.update_project_metadata()

    def plot_data(
        self,
        domain_type : str,
        dataformats : Optional[str] = "NHWC",
        n_data : Optional[int] = 10
    )->None:
        r"""Visualizes the data.
        
        Args:

            domain_type (str): The domain type the data inhabits in. e.g., "image", "points"

            dataformats (str, optional): The dimensions specifying the orderings of (`N`,`H`,`W`,`C`) for image data. Does nothing when domain type is not "image".
                Default: ``NHWC``

            n_data (int): Number of image samples you want to visualize. Does nothing when domain type is not "image".
                Default: ``10``
        
        Returns:

            None
        """
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
                log.detail(f'The dimension of data is higher than 3. (Input dimension: {self.dims})\n \
                     We will use PCA and visualize the data using 2 principal axes.')
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
                plt.savefig(points_dir+ f"/points_distribution_PCA.png")  
                self.project_logger.add_figure('data distribution_PCA', fig)

                
    
        elif domain_type == "image":

            if len(self.dims) == 1 :
                raise AssertionError(f"Wrong dimension {self.dims} for image data. It should be at least 2-dimensional.")
            img_dir =  f"{self.project_path}/visualizations"
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
                    f"sample_images/image_{i}_label_{labels_to_show[i]}",
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
                        img.set_title('label : {labels_to_show[idx-1]}')
            plt.show()
            plt.savefig(f"{img_dir}/image_samples.png")       

        elif self.domain_type == "audio":
            raise NotImplementedError("Audio data unimplemented.") # TODO: implement this
        else:
            raise NotImplementedError("Unsupported domain type {self.domain_type}. Supported domain types are {[*available_domain_types]}")
        
        self.update_project_metadata()

    def get_available_random_states(
        self
    )->List[str]:
        r"""Returns list of directories of ``Experiments`` that has been fitted and logged.

        Returns:

            list of `str`: All directories of fitted and logged ``Experiments``.
        """
        log_base_dir = f"{self.project_path}/FIT"
        random_state_dir_list = []
        for random_state_dir in os.listdir(log_base_dir):
            random_state_dir_list.append(f'{log_base_dir}/{random_state_dir}')

        return random_state_dir_list

    def search_standard(
        self,
        val_metric : str = 'val/acc'
    )->Tuple["np.ndarray", Dict[str,int], Dict[str,int]]: 
        r"""Search method for finding the model type/structure with best validation performance.

        Args:

            val_metric (str): The validation metric.
                Default: ``'val/acc'``

        Returns:

            tuple: (numpy ndarray of validation performances across ``Experiments``, dictionary of {model type:it's frequency}, dictionary of {model structure:it's frequency}).

        """ 
        performances = []
        best_model_type = None
        best_metadata = None
        best_val = None
        best_model_structures = {}
        best_model_types = {}
        mode = 'min' if val_metric == 'val/loss' else 'max'
        random_state_dir_list = self.get_available_random_states()
        for random_state_dir in random_state_dir_list:
            jsonlog_dir = f"{random_state_dir}/logs/jsonlogs"
            for model_type_dir in os.listdir(jsonlog_dir): 
                for metadata_dir in os.listdir(f'{jsonlog_dir}/{model_type_dir}'): 
                    for version in os.listdir(f'{jsonlog_dir}/{model_type_dir}/{metadata_dir}'): 
                        for file in os.listdir(f'{jsonlog_dir}/{model_type_dir}/{metadata_dir}/{version}'): 
                            file_path = f'{jsonlog_dir}/{model_type_dir}/{metadata_dir}/{version}/{file}'  
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
            raise ValueError(f"No performances are saved.")
        return (performances, best_model_types, best_model_structures)

    def search_with_model_type(
        self,
        model_type : Union["pl.LightningModule", "BaseEstimator"],
        val_metric : str = 'val/acc'
    )->Tuple["np.ndarray",Dict[str,int]]:
        r"""Search method for finding validation performances for a specific model type.

        Args:

            model_type (`LightningModule` or `BaseEstimator`): The model type of interest. e.g., ``MLP``, ``LogisticRegression``.

            val_metric (str): The validation metric.
                Default: ``'val/acc'``

        Returns:

            tuple: (numpy ndarray of validation performances, dictionary of {model structure:it's frequency}).
        """
        performances = []
        best_model_structures = {}
        best_val = None
        best_metadata = None
        mode = 'min' if val_metric == 'val/loss' else 'max'
        random_state_dir_list = self.get_available_random_states()
        for random_state_dir in random_state_dir_list:
            jsonlog_dir = f'{random_state_dir}/logs/jsonlogs'
            for model_type_dir in os.listdir(jsonlog_dir): 
                if str(model_type_dir) == model_type.__name__:
                    for metadata_dir in os.listdir(f'{jsonlog_dir}/{model_type_dir}'): 
                        for version in os.listdir(f'{jsonlog_dir}/{model_type_dir}/{metadata_dir}'): 
                            for file in os.listdir(f'{jsonlog_dir}/{model_type_dir}/{metadata_dir}/{version}'):
                                file_path = f'{jsonlog_dir}/{model_type_dir}/{metadata_dir}/{version}/{file}'
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
            raise ValueError(f"None is in performances. You may have not saved {model_type}")

        return (performances, best_model_structures)

    def search_with_model_type_hparams(
        self,
        model_type : Union["pl.LightningModule", "BaseEstimator"], 
        val_metric : str = 'val/acc',
        **hparams
    )->Tuple["np.ndarray", str]:
        r"""Search method for finding validation performances of a specific model structure.

        Args:

            model_type (`LightningModule` or `BaseEstimator`): The model type of interest. e.g., ``MLP``, ``LogisticRegression``.

            **hparams (Any): Hyperparameters for the model.

            val_metric (str): The validation metric.
                Default: ``'val/acc'``

        Returns:

            tuple: (numpy ndarray of validation performances, metadata specifying the specified model structure).
        """
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
            raise ValueError(f"None is in performances. You may have inputted the wrong model strucutre.")
        return (performances, metadata)
                    
    def search_all_models(
        self,
        val_metric : str = 'val/acc'
    )->Tuple["np.ndarray", List[str]]:
        r"""Method for searching validation performances of all saved models.

        Args:

            val_metric (str): The validation metric.
                Default: ``'val/acc'``

        Returns:

            tuple: (numpy ndarray of list of validation performances, list of searched model metadata)
        """
        metadata_list = []
        performances_list = [] # list of performances(list). len(performances_list) == len(metadata_list)
        mode = 'min' if val_metric == 'val/loss' else 'max'
        random_state_dir_list = self.get_available_random_states()
        random_number_list = []
        best_val = None
        for random_number_dir in random_state_dir_list:
            random_number = random_number_dir.split("-")[-1]
            random_number_list.append(random_number)

        performances_per_metadata = {}
        for random_state_dir in random_state_dir_list:
            jsonlog_dir = f'{random_state_dir}/logs/jsonlogs'
            for model_type_dir in os.listdir(jsonlog_dir): 
                for metadata_dir in os.listdir(f'{jsonlog_dir}/{model_type_dir}'):
                    if metadata_dir not in metadata_list:
                        metadata_list.append(metadata_dir) 
                        performances_per_metadata.update({metadata_dir: []})
                    best_val = None
                    for version in os.listdir(f'{jsonlog_dir}/{model_type_dir}/{metadata_dir}'): 
                        for file in os.listdir(f'{jsonlog_dir}/{model_type_dir}/{metadata_dir}/{version}'): 
                            file_path = f'{jsonlog_dir}/{model_type_dir}/{metadata_dir}/{version}/{file}' 
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
            raise ValueError(f"Nothing has been logged.") 
        return (metadata_list, performances_list)

    @staticmethod
    def _create_folder(directory : str)->str: #path of directory
        r"""Creates folder.
        
        Args:

            directory (str): The path of folder you want to create. When the folder already exists, the method does nothing.

        Returns: 

            str: directory 
        """
        os.makedirs(directory, exist_ok=True)
        return directory

    
        

class Project(BaseProject):
    r"""Project class that plots results of the ML project.

    Attributes:

        project_name: Name of the project. Directory of {path}/{project_name} will be created.

        X: Data for the project. If X_test is not specified, X would be splitted(stratify=y) into train/val data with a given random state.

        y: Labels for the project. If y_test is not specified, y would be splitted(stratify=y) into train/val labels with a given random state.

        X_test : Test data for the project. Specify this when there is a separate test data.
            Default: ``None``

        y_test : Test labels for the project. Specify this when there is a separate test data.
            Default: ``None``

        n_classes : Number of classes for the classification task. Don't specify this when performing regression tasks.
            Default: ``None``

        path : Base path for the project. Default is the current directory.
            Default: ``.``

        dims (:obj:`int` or :obj:`tuple` of `int`) : Dimensions of the data. Number of samples is excluded in dims.

        project_path (:obj:`str`): Path for the project. It will be {path}/{project_name}.

        log_dir (:obj:`str`): Path for saving plotted images and figures. It will be {project_path}/{projectlogs}.

        project_logger (:obj:`SummaryWriter`): TensorBoard Logger for logging.

        project_metadata (:obj:`dict`): Dictionary describing the project.

        birthday (str): Time when the project is created.

        exps (:obj:`dict` of :obj:`str`, :obj:`Experiment`): `Project` can control ``Experiments`` in ``exps``.
        
        n_exps (int): Number of ``Experiemnt``s in ``exps``.

        pseudoexp (`Experiment`): Dummy ``Experiment`` for applying methods in ``Experiment``.

    Methods:


    """
    def __init__(
        self,
        project_name : str,
        X : "np.ndarray",
        y : "np.ndarray",
        X_test : Optional["np.ndarray"] = None,
        y_test : Optional["np.ndarray"] = None,
        n_classes : Optional[int] = None,
        path : str = "."
    )->None:
        r"""
        
        Args:

            project_name: Name of the project. Directory of {path}/{project_name} will be created.

            X: Data for the project. If X_test is not specified, X would be splitted(stratify=y) into train/val data with a given random state.

            y: Labels for the project. If y_test is not specified, y would be splitted(stratify=y) into train/val labels with a given random state.

            X_test : Test data for the project. Specify this when there is a separate test data.
                Default: ``None``

            y_test : Test labels for the project. Specify this when there is a separate test data.
                Default: ``None``

            n_classes : Number of classes for the classification task. Don't specify this when performing regression tasks.
                Default: ``None``

            path : Base path for the project. Default is the current directory.
                Default: ``.``        
        """
        super().__init__(
            project_name=project_name,
            X=X,
            y=y,
            X_test=X_test,
            y_test=y_test,
            n_classes=n_classes,
            path=path
        )

    def plot_best_performances(
            self,
            val_metric : str = 'val/acc',
            plt_title : Optional[str] = None
        )->Tuple["np.ndarray",Dict[str,Dict[str,int]]]: # (validation performances, information)
            r"""Plots the best validation performance for each ``Experiment``.

            Args:

                val_metric (str): The validation metric.
                    Default: ``'val/acc'``

                plt_title (str, optional): The title for the plot. If left None, title will be 'Best Performance for Each Random State'.
                    Default: None

            Returns:

                tuple: (numpy ndarray of validation performances, dictionary containing information of the search)
            """
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
                plt_title = 'Best Performance for Each Random State'
            plt.title(plt_title)
            plt.ylim = (ymin, ymax)
            self._create_folder(self.project_path+"/results")
            plt.show()
            plt.savefig(self.project_path+f"/results/{plt_title}.png")
            self.project_logger.add_figure(f"results/{plt_title}", fig1)
            
            plt.close(fig1)

            info = {'best model structures' : best_model_structures, 'best model types' : best_model_types}

            return (performances, info)

    def plot_best_model_frequencies(
        self,
        val_metric : str = 'val/acc',
        plt_title : Optional[str] = None
    )->Tuple["np.ndarray",Dict[str,Dict[str,int]]]: # (validation performances, information)
        r"""Plots pie graphs showing the frequencies of 1)best model type and 2)best model structure for each ``Experiment``.

        Args:

            val_metric (str): The validation metric/
                Default: ``'val/acc'``
            
            plt_title (str, optional): The title for the plot. If left None, title will be 'Frequencies of the Best Model Types/Structures' respectively.
                Default: None

            Returns:

                tuple: (numpy ndarray of validation performances, dictionary containing information of the search)
        """
        performances, best_model_types, best_model_structures = self.search_standard(val_metric)
        fig2 = plt.figure()
        sizes = list(best_model_structures.values())
        wedges, texts, autotexts = plt.pie(sizes, autopct='%1.1f%%',textprops=dict(color="w"))
        if not plt_title:
            plt_title = 'Frequencies of'
        plt.title(f'{plt_title} the Best Model Structures')
        plt.legend(wedges, best_model_structures.keys(), title="Model Structures", loc="center left",bbox_to_anchor=(1, 0, 0.5, 1))
        plt.setp(autotexts, size=8, weight="bold")
        plt.axis('equal')
        plt.show()
        plt.savefig(self.project_path+f"/results/{plt_title} the Best Model Structures.png")
        self.project_logger.add_figure(f"results/{plt_title} the Best Model Structures", fig2)
        plt.close(fig2)
        
        fig3 = plt.figure()
        sizes = list(best_model_types.values())
        wedges, texts, autotexts = plt.pie(sizes,  autopct='%1.1f%%') 
        plt.axis('equal')
        plt.setp(autotexts, size=8, weight="bold")
        plt.title(f'{plt_title} the Best Model Types')
        plt.legend(wedges, best_model_types.keys(), title="Model Types", loc="center left",bbox_to_anchor=(1, 0, 0.5, 1))
        plt.show()
        plt.savefig(self.project_path+f"/results/{plt_title} the Best Model Types.png")
        self.project_logger.add_figure(f"results/{plt_title} the Best Model Types", fig3)
        plt.close(fig3)

        self.update_project_metadata()
        info = {'best model structures' : best_model_structures, 'best model types' : best_model_types}

        return (performances, info)
        

    def plot_identical_model_type(
        self,
        model_type : Union["pl.LightningModule","BaseEstimator"],
        val_metric : str = "val/acc",
        plt_title : Optional[str] = None
    )->Tuple["np.ndarray", List[str], Dict[str,Dict[str,int]]]: 
        r"""Plots validation performances across different random states for a given model type.

        Args:

            model_type (`LightningModule` or `BaseEstimator`): The model type of interest.

            val_metric (str): The validation metric.
                Default: ``'val/acc'``

            plt_title (str, optional): The title for the plot. If left None, title will be 'Best Performances : Model Type {name of the model type}' respectively.
                Default: ``None``

        Returns:

            tuple: (numpy ndarray of validation performances, list of random states of saved ``Experiments``, dictionary containing information of the search)
        """
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
        plt.bar(x, performances, width=0.1)
        plt.xticks(x, random_number_list)
        plt.xticks(rotation=70)
        plt.xlabel("random state")
        plt.ylabel(val_metric)
        plt.grid(True)
        plt.ylim = (ymin, ymax)
        if not plt_title:
            plt_title = f'Best Performances : Model Type \n{model_type.__name__}'
        plt.title(plt_title)
        plt.show()
        plt.savefig(self.project_path+f"/results/{plt_title}.png")
        self.project_logger.add_figure(f"results/{plt_title}", fig1)
        plt.close(fig1)
        self.update_project_metadata()
        info = {'best model structures' : best_model_structures}

        return (performances, random_number_list, info)

    def plot_identical_model_structure(
        self,
        model_type : Union["pl.LightningModule","BaseEstimator"],
        val_metric : str = "val/acc",
        plt_title : Optional[str] = None,
        **hparams
    )->Tuple["np.ndarray",List[str]]: 
        r"""Plots validation performances across different random states for a given model structure.

        Args:

            model_type (`LightningModule` or `BaseEstimator`): The model type of interest.

            **hparams (Any): Model hyperparameters. 

            val_metric (str): The validation metric.
                Default: ``'val/acc'``

            plt_title (str, optional): The title for the plot. If left None, title will be 'Performances of a Model Structure'.
                Default: ``None``

        Returns:

            tuple: (numpy ndarray of validation performances, list of random states of saved ``Experiments``)
        """
        performances, metadata = self.search_with_model_type_hparams(
            val_metric=val_metric, model_type=model_type, **hparams
            )
        random_state_dir_list = self.get_available_random_states()
        ymin = performances.min() - 0.1 if performances.min() > 0.1 else 0
        ymax = performances.max() + 0.1 if performances.max() < 0.9 else 1
        random_number_list = []
        for random_number_dir in random_state_dir_list:
            random_number = random_number_dir.split("-")[-1]
            random_number_list.append(random_number)
        fig1 = plt.figure()
        x = np.arange(len(performances))
        plt.plot(performances, 'r.')
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
        plt.savefig(self.project_path+f"/results/{metadata}.png")
        plt.show()
        self.project_logger.add_figure(f'results/{metadata}', fig1)
        plt.close(fig1)

        self.update_project_metadata()

        return (performances, random_number_list)
    
    @staticmethod
    def generate_marker_style(amount)->List[str]: 
        r"""Returns a string specifying the marker style
        """
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

    def plot_all_model_structures(
        self,
        val_metric : str = "val/acc",
        plt_title : Optional[str] = None
    )->Tuple["np.ndarray", List[str]]:
        r"""Plots validation performances across different random states for all model structures saved. 
        
        Will plot 1)line graphs and 2)box plots.

        Args:

            val_metric (str): The validation metric.
                Default: ``'val/acc'``

            plt_title (str, optional): The title for the plot. If left None, title will be 'Performances For All Models' and 'Performances For All Models:Box Plot'.
                Default: ``None``

        Returns:

            tuple: (numpy ndarray of validation performances, list of random states of saved ``Experiments``)
        """
    # (validation performances, list of model metadata)
        
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
            plt_title = 'Performances For All Models'
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
        plt.savefig(self.project_path+f"/results/{plt_title}.png")
        self.project_logger.add_figure(f'results/{plt_title}', fig1)
        
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
                patch_artist=True, boxprops=dict(facecolor=f"C{idx}")
                )
            legend_dict.update({f'bp{idx}': bp})
        plt.legend(
            [bp["boxes"][0] for bp in legend_dict.values()], 
            [metadata for metadata in keys],
            title="Model Structures", 
            loc="center left", 
            bbox_to_anchor=(1, 0, 0.5, 1)
        )
    
        plt.title(f'{plt_title}: Box Plot')
        plt.xlabel(f"model structure")
        plt.ylabel(val_metric)
        plt.grid(True)
        plt.show()
        plt.savefig(self.project_path+f"/results/{plt_title}_boxplot.png")
        self.project_logger.add_figure(f'results/{plt_title}_boxplot', fig2)

        return (performances_list, metadata_list)

    

