from typing import List


class JobConfiguration:
    """
    Job configuration class.
    """

    def __init__(self,
                 name: str,
                 account: str,
                 queue: str,
                 duration: str,
                 max_nodes_per_job: int = 1000,
                 use_open_np: bool = False,
                 pre_container_env_setup_cmds: List[str] = None,
                 n_threads: int = -1,
                 n_nodes: int = -1,
                 n_tasks: int = -1,
                 n_thread_per_task: int = -1
                 ):
        """
        Job configuration constructor
        :param name: Name of the job
        :param account: Account used to charge for the job
        :param queue: Queue to use for the job
        :param duration: Job duration
        :param max_nodes_per_job: Maximum number of node to use per job.
        If the total of number of nodes requested exceed
        `max_nodes_per_job`, sub-jobs will be created.
        :param use_open_np: Using OPEN-MP directives.
        :param pre_container_env_setup_cmds:
        :param n_threads: Total number of threads needed to run the job
        :param n_nodes: Total number of nodes needed to run the job
        :param n_tasks: Total number of tasks needed to run the job
        :param n_thread_per_task: Total number of thread per task needed to run the job
        """
        self.__name = name
        self.__account = account
        self.__queue = queue
        self.__duration = duration
        self.__max_nodes_per_job = max_nodes_per_job
        self.__use_open_np = use_open_np
        self.__pre_container_env_setup_cmds = pre_container_env_setup_cmds
        self.__n_threads = n_threads
        self.__n_nodes = n_nodes
        self.__n_tasks = n_tasks
        self.__n_thread_per_task = n_thread_per_task

    def as_dict(self, drop_node_conf: bool = False) -> dict:
        """
        Return the job configuration as a dictionary
        :return:
        """
        dictionary = {}
        for key, value in vars(self).items():
            key = key.replace(f'_{self.__class__.__name__}__', '')
            if drop_node_conf and key in ['n_threads', 'n_nodes', 'n_tasks', 'n_thread_per_task']:
                continue
            dictionary[key] = value

        return dictionary

    @property
    def name(self) -> str:
        """
        Getter for name
        :return:
        """
        return self.__name

    @property
    def account(self) -> str:
        """
        Getter for account
        :return:
        """
        return self.__account

    @property
    def queue(self) -> str:
        """
        Getter for queue
        :return:
        """
        return self.__queue

    @property
    def duration(self) -> str:
        """
        Getter for duration
        :return:
        """
        return self.__duration

    @property
    def pre_container_env_setup_cmds(self) -> List[str]:
        """
        Getter for the environment setup commands
        :return:
        """
        return self.__pre_container_env_setup_cmds

    @property
    def max_node_per_job(self) -> int:
        """
        Getter for max_node_per_job
        :return:
        """
        return self.__max_nodes_per_job

    @property
    def n_threads(self) -> int:
        """
        Getter for n_threads
        :return:
        """
        return self.__n_threads

    @property
    def n_nodes(self) -> int:
        """
        Getter for n_nodes
        :return:
        """
        return self.__n_nodes

    @property
    def n_tasks(self) -> int:
        """
        Getter for n_tasks
        :return:
        """
        return self.__n_tasks

    @property
    def n_thread_per_task(self) -> int:
        """
        Getter for n_thread_per_task
        :return:
        """
        return self.__n_thread_per_task

    def get_extra_configuration(self) -> List[str]:
        """
        Get the extra configuration for the job
        :return:
        """
        extra_config = []

        if self.__use_open_np:
            extra_config.extend(JobConfiguration.get_open_mp())

        return extra_config

    @staticmethod
    def get_open_mp() -> List[str]:
        """
        Method that returns the Open-MP configuration
        :return:
        """
        open_mp_config = []

        return open_mp_config
