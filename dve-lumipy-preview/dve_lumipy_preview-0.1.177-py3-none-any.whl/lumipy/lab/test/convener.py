import datetime as dt
import os
import time
import uuid
from pathlib import Path
from tqdm import tqdm

import numpy as np
import pandas as pd

from lumipy.common.string_utils import indent_str
from .base import BaseExperiment
from multiprocessing import Queue


class Convener:
    """The convener class looks after the running of experiments and recording their data.

    """

    def __init__(
            self,
            experiment: BaseExperiment,
            work_dir: str,
            name: str,
            n_obs: int,
            **kwargs
    ):
        """Constructor of the convener class.

        Args:
            experiment (BaseExperiment): the experiment to run.
            work_dir (str): the working directory to write results to.
            name (str): the name of the experiment.
            n_obs (int): number of times to run the experiment and observe values.

        Keyword Args:
             seed (Optional[int]): random seed to set at the start of the experimental run. Will be chosen randomly if
             not specified.
             err_wait (Optional[int]): number of seconds to wait after getting an error.
             n_parallel (Optional[Union[int, List[int]]]): number of concurrent runs of the experiment to run each time.

        """

        self.__work_dir = work_dir
        self.__name = name
        self.__experiment = experiment
        self.__n_obs = n_obs
        self.__seed = kwargs.get('seed', np.random.randint(1989))
        self.__err_wait = kwargs.get('err_wait', 15)
        self.__n_parallel = kwargs.get('n_parallel', 1)
        self.__force_stop = False

        data_dir = f'{self.__work_dir}/data'
        self.__data_file = f'{data_dir}/{self.__name}.csv'

        Path(data_dir).mkdir(parents=True, exist_ok=True)
        Path(f'{self.__work_dir}/plots').mkdir(parents=True, exist_ok=True)

    def __job(self) -> pd.DataFrame:

        if isinstance(self.__n_parallel, int):
            n_parallel = self.__n_parallel
        else:
            np.random.seed((dt.datetime.utcnow() - dt.datetime(1970, 1, 2)).seconds)
            n_parallel = np.random.randint(self.__n_parallel[0], self.__n_parallel[1] + 1)

        queue = Queue()
        tasks = [self.__experiment.copy(self.__seed, True if i != 0 else self.__experiment._quiet) for i in range(n_parallel)]

        try:
            for t in tasks:
                t.attach_queue(queue)
                t.start()

            [t.join(force=False) for t in tasks]

        except KeyboardInterrupt:
            tqdm.write("\n🛑 Quitting the experimental run...\n")
            [t.join(force=True) for t in tasks]
            self.__force_stop = True

        rows = []
        while not queue.empty():
            row = queue.get()
            row['n_parallel'] = n_parallel
            rows.append(row)

        return pd.DataFrame(rows)

    def go(self) -> None:
        """Run the experiments.

        Notes:
            Can be halted with keyboard interrupt.

        """

        error_count = 0
        run_start = dt.datetime.utcnow()
        offset = dt.datetime.now() - dt.datetime.utcnow()

        # Very important. Do not remove.
        emoji = np.random.choice(['🧪', '🔭', '⚗️', '🧬', '🔬', '📐'])

        times = []
        start = None
        total_obs = 0

        tqdm.write(f"Experiment: {self.__name}")
        tqdm.write(str(self.__experiment))
        tqdm.write(f"Output file: {self.__data_file}")
        tqdm.write(f"Run start: {(run_start + offset).strftime('%Y-%m-%d %H:%M:%S')}")
        if self.__n_parallel != 1:
            tqdm.write(f"Concurrency: {self.__n_parallel}")

        pbar = tqdm(
            range(1, self.__n_obs + 1),
            desc=f'{emoji}Doing Science! ',
            unit='Obs',
            total=self.__n_obs,
            bar_format='{l_bar}{bar:10}{r_bar}{bar:-10b}'
        )
        with pbar as t:

            for i in t:

                new_start = dt.datetime.utcnow()
                if start is not None:
                    times.append((new_start - start).total_seconds())
                start = new_start

                if len(times) >= 1:
                    t_mean = np.mean(times)
                    est_len = self.__n_obs * t_mean / 60
                    est_finish = run_start + dt.timedelta(minutes=est_len) + offset
                    postfix = {
                        'finish_at' : f"{est_finish.strftime('%H:%M:%S')}",
                        'error_count' : error_count,
                    }
                    if error_count > 0:
                        postfix['error_rate'] = f"{round(100 * error_count / total_obs, 2)}%"
                    t.set_postfix(**postfix)

                df = self.__job()

                df['experiment_name'] = self.__name
                df['run_start'] = run_start
                experiment_id = str(uuid.uuid4())
                df['experiment_id'] = experiment_id

                total_obs += df.iloc[0].n_parallel

                df.to_csv(
                    self.__data_file,
                    index=False,
                    mode='a',
                    header=not os.path.exists(self.__data_file)
                )

                if self.__force_stop:
                    raise KeyboardInterrupt()

                errors = df[df.errored].error_message.tolist()
                if len(errors) > 0:
                    error_count += len(errors)
                    err_msg = '\n'.join(errors)
                    s = 's' if len(errors) > 1 else ''
                    tqdm.write(f"Error{s} in run {experiment_id}:\n{indent_str(err_msg)}")
                    time.sleep(self.__err_wait)

                self.__seed += 1

    @property
    def data_file_path(self) -> str:
        """Get the file path for the data CSV.

        Returns:
            str: the data csv file path
        """
        return self.__data_file

    def read_csv(self) -> pd.DataFrame:
        """Read the data CSV and return it as a pandas dataframe.

        Returns:
            DataFrame: the contents of the data CSV file.
        """
        return pd.read_csv(self.__data_file)

    def get_name(self):
        """Return the name of the experiment

        Returns:
            str: the name of the experiment
        """
        return self.__name
