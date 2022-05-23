from functools import reduce
import json
import logging
import math as m
import os
import subprocess
from typing import List, Tuple, Union

from ..system import System
from ..job import JobConfiguration
from ..task import Task


class Farmer:
    """
    Farmer class.
    """

    def __init__(self,
                 system: System,
                 job_configuration_directory: str = f'{os.getcwd()}/job',
                 burn_in_time_seconds: int = 0):
        """
        Constructor of the farmer
        :param system:
        :param job_configuration_directory:
        :param burn_in_time_seconds:
        """
        self.__system = system
        self.__job_configuration_directory = job_configuration_directory
        self.__burn_in_time_seconds = burn_in_time_seconds

        self.log = logging.getLogger(f'farmer-{self.__system.name}')
        self.__jobs = {}

        self.log.info(f'Initializing the farmer for the system: {self.__system}')

    @property
    def system(self) -> System:
        """
        Getter for the system.
        :return: the system
        """
        return self.__system

    def __str__(self) -> str:
        """
        Get string message for print statement
        :return:
        """
        return f'Farmer<system:{self.__system.name}, n_jobs:{len(self.__jobs)}>'

    def add_global_job_configuration(self, global_job_configuration: JobConfiguration) -> None:
        """
        Add a new global job configuration.
        :param global_job_configuration:
        :return:
        """
        self.log.info(f'Adding the job: "{global_job_configuration.name}"')

        if global_job_configuration.name in self.__jobs:
            raise Exception(f'The job configuration '
                            f'"{global_job_configuration.name}" already exists')

        if global_job_configuration.queue not in self.__system.queues:
            raise Exception(
                f'The job configuration "{global_job_configuration.name}" '
                f'uses the queue "{global_job_configuration.queue}" '
                f'which is not available for {self.__system}. Available options are:'
                f'{self.__system.queues}')

        self.__jobs[global_job_configuration.name] = {'global_job_configuration':
                                                          global_job_configuration, 'tasks': []}

    def add_task(self, global_job_config: Union[str, JobConfiguration], task: Task) -> None:
        """
        Add a task and link it to a global job configuration.
        :param global_job_config: Name of object of the global job configuration
        :param task: Task to add
        :return:
        """
        if isinstance(global_job_config, str):
            global_job_config_name = global_job_config
        elif isinstance(global_job_config, JobConfiguration):
            global_job_config_name = global_job_config.name
        else:
            raise Exception(f'Impossible to read job name from the type {type(global_job_config)}')

        if global_job_config_name not in self.__jobs:
            raise Exception(f'The global job configuration "{global_job_config_name}" '
                            f'is not available. Options are:'
                            f'{list(self.__jobs.keys())}')

        self.__jobs[global_job_config_name]['tasks'].append(task)

    def add_tasks(self,
                  global_job_config: Union[str, JobConfiguration],
                  tasks: List[Task]) -> None:
        """
        Add multiple tasks from a task array and link them to a job configuration
        :param global_job_config: Name or object of the global job configuration
        :param tasks: List of tasks to add
        :return:
        """
        for task in tasks:
            self.add_task(global_job_config, task)

    def build(self) -> None:
        """
        Build the task-list and the slurm script.
        :return:
        """
        for job_name in self.__jobs.keys():
            self.log.info(f'Preparing the job {job_name}:')

            formatted_job_name = job_name.replace(' ', '_')
            slurm_directory, task_list_directory, logs_directory = Farmer.get_folders(
                f'{self.__job_configuration_directory}/{formatted_job_name}')

            global_job_configuration = self.__jobs[job_name]['global_job_configuration']
            global_job_configuration_dict = global_job_configuration.as_dict(drop_node_conf=True)

            job_tasks = self.__jobs[job_name]['tasks']

            max_threads_per_job = self.__system.threads_per_node \
                                  * global_job_configuration.max_node_per_job

            split_tasks = [[]]
            current_job_threads = 0

            for task in job_tasks:
                if current_job_threads + task.n_threads > max_threads_per_job:
                    split_tasks.append([])
                    current_job_threads = 0

                split_tasks[-1].append(task)
                current_job_threads += task.n_threads

            self.log.info(f'  - n_jobs: {len(split_tasks)}')

            self.__jobs[job_name]['slurm_filenames'] = []
            self.__jobs[job_name]['tasks_filenames'] = []

            for i, tasks in enumerate(split_tasks):
                n_threads = reduce(lambda accumulator, _task:
                                   accumulator + _task.n_threads,
                                   tasks, 0)
                n_nodes = int(m.ceil(n_threads / self.__system.threads_per_node))
                n_tasks = len(tasks)

                if n_tasks == 0:
                    self.log.info(f'  - sub-job {i} - n_tasks:{n_tasks} -- skipping configuration')
                    continue

                n_thread_per_task = int(n_threads / n_tasks)

                local_job_configuration = JobConfiguration(**global_job_configuration_dict,
                                                           n_threads=n_threads,
                                                           n_nodes=n_nodes,
                                                           n_tasks=n_tasks,
                                                           n_thread_per_task=n_thread_per_task
                                                           )

                self.log.info(f'  - sub-job {i} - n_tasks:{n_tasks}, n_threads:{n_threads}, n_nodes:{n_nodes}')

                task_list_filename = f'{task_list_directory}/task_list_{job_name}_{i}.py'
                job_script_filename = f'{slurm_directory}/slurm_{job_name}_{i}.sh'

                self.__jobs[job_name]['tasks_filenames'].append(task_list_filename)
                self.__jobs[job_name]['slurm_filenames'].append(job_script_filename)

                Farmer.__build_task_list(task_list_filename, tasks)
                Farmer.__build_job_script(system=self.__system,
                                          burn_in_time=self.__burn_in_time_seconds,
                                          job_configuration=local_job_configuration,
                                          job_script_filename=job_script_filename,
                                          task_list_filename=task_list_filename,
                                          logs_directory=logs_directory)

    def submit(self, dry_run: bool = True) -> None:
        """
        Submit the jobs to the batch system
        :param dry_run: If `False`, it will print the job submission commands and submit them.
         If `True`, it will only print the job submission commands and skip the submission.
         Default=`True` to avoid mistakes.
        :return:
        """
        if dry_run:
            self.log.info('No Automatic job submission, '
                          'the sbatch command will be printed for your convenience')
        else:
            self.log.info('Automatic job submission')

        for job_name in self.__jobs.keys():

            sbatch_commands = [
                f'sbatch {slurm_file}' for slurm_file in self.__jobs[job_name]['slurm_filenames']
            ]
            sbatch_commands_str = '\n'.join(sbatch_commands)
            self.log.info(f'For the job: {job_name}:\n{sbatch_commands_str}')

            if not dry_run:
                with subprocess.Popen(' && '.join(sbatch_commands), shell=True) as process:
                    process.communicate()
                    exit_code = process.wait()

    @staticmethod
    def get_folders(job_configuration_directory: str) -> Tuple[str, str, str]:
        """
        Get the slurm configuration, task-list and logs directories
        :param job_configuration_directory: input job configuration
        :return: Tuple with slurm configuration, task-list and logs directories
        """
        slurm_configuration_directory = f'{job_configuration_directory}/slurm'
        task_list_directory = f'{job_configuration_directory}/task_list'
        logs_directory = f'{job_configuration_directory}/logs'

        os.makedirs(slurm_configuration_directory, exist_ok=True)
        os.makedirs(task_list_directory, exist_ok=True)
        os.makedirs(logs_directory, exist_ok=True)

        return slurm_configuration_directory, task_list_directory, logs_directory

    @staticmethod
    def __build_task_list(task_list_filename: str, tasks: List[Task]) -> None:
        """
        Build the task-list file from an array of tasks
        :param task_list_filename: filename of the task-list
        :param tasks: List of tasks
        :return:
        """
        with open(task_list_filename, 'w', encoding="utf8") as task_list:
            tasks_json = json.dumps(tasks,
                                    default=Task.json_encoder,
                                    indent=4).replace('null', 'None')
            task_list.write(f'tasks = {tasks_json}')

    @staticmethod
    def __build_job_script(system: System,
                           burn_in_time: int,
                           job_configuration: JobConfiguration,
                           job_script_filename: str,
                           task_list_filename: str,
                           logs_directory: str) -> None:
        """
        Build the SLURM job script for the current job
        :param system: input system to use for the job configuration and constrains
        :param burn_in_time:
        :param job_configuration: input JobConfiguration object
        :param job_script_filename: filename of the SLURM script
        :param task_list_filename: filename of the task-list
        :param logs_directory: path to the log directory
        :return:
        """

        def check_node_value(__job_configuration: JobConfiguration, variable_mame: str) -> int:
            """
            Check the values of a node
            :param __job_configuration: input JobConfiguration
            :param variable_mame: Variable name to check
            :return:
            """
            value = getattr(__job_configuration, variable_mame)
            if value > 0:
                return value

            raise Exception(f'Job configuration incorrect '
                            f'value for the variable {variable_mame}.')

        n_nodes = check_node_value(job_configuration, 'n_nodes')
        n_tasks = check_node_value(job_configuration, 'n_tasks')
        n_thread_per_task = check_node_value(job_configuration, 'n_thread_per_task')

        job_script = ['#!/bin/bash',
                      f'#SBATCH -J {job_configuration.name}',
                      f'#SBATCH -A {job_configuration.account}',
                      f'#SBATCH -t {job_configuration.duration}',
                      f'#SBATCH -N {n_nodes}',
                      f'#SBATCH -q {job_configuration.queue}',
                      f'#SBATCH --output={logs_directory}/slurm-%x_%j_%t.out',
                      f'#SBATCH --error={logs_directory}/slurm-%x_%j_%t.err',
                      '']

        job_script.extend(system.get_constrains())
        job_script.extend(job_configuration.get_extra_configuration())

        dir_path = os.path.dirname(os.path.realpath(__file__))
        runner_path = 'job_runner'

        srun_comd = ['']

        if job_configuration.pre_container_env_setup_cmds is not None:
            srun_comd.append('# Job runner environment configuration')
            srun_comd.extend(job_configuration.pre_container_env_setup_cmds)
            srun_comd.append('')

        srun_comd.append('# Job execution')
        srun_comd.append(f'srun -n {n_tasks} -c {n_thread_per_task} '
                         f'{runner_path} --task-list {task_list_filename} --burn-in-time {burn_in_time}')

        job_script.extend(srun_comd)

        with open(job_script_filename, 'w', encoding="utf8") as job_script_file:

            job_script_file.write('\n'.join(job_script))
            job_script_file.write('\n')
