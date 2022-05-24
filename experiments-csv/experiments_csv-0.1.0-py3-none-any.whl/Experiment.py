"""
An abstract class that represents an experiment.
"""

from typing import Dict, List, Any, Callable
import pandas, os, logging, shutil, pathlib
from experiments_csv.dict_product import dict_product
from experiments_csv.dict_to_row import dict_to_row
from datetime import datetime

import logging
logger = logging.getLogger(__name__)


class Experiment:

    def __init__(self, results_folder="results", results_filename="results.csv", backup_folder="results_backup"):
        """
        :param columns: an ordered list of column names for this table.
        :param results_file: a path to a file that will be used to backup this table.

        If the file exists, it is read into the new table.
        If the file does not exist, an empty table is initialized and the file will be created when the table is "done".
        """
        pathlib.Path(results_folder).mkdir(parents=True, exist_ok=True)            
        pathlib.Path(backup_folder).mkdir(parents=True, exist_ok=True)
        results_file = os.path.join(results_folder, results_filename)
        if os.path.isfile(results_file):
            # Load existing file:
            self.dataFrame = pandas.read_csv(results_file)
            logger.info("Loaded %d rows from %s.", self.dataFrame.shape[0], results_file)

            # Backup existing file into the 'backup' folder:
            modification_timestamp = os.path.getmtime(results_file)
            modification_datetime = datetime.fromtimestamp(modification_timestamp).strftime("%Y_%m_%d__%H_%M_%S")
            backup_filename = results_filename.replace(".csv",f".{modification_datetime}.csv")
            backup_file = os.path.join(backup_folder, backup_filename)
            shutil.copyfile(results_file, backup_file)

        else:
            self.dataFrame = None  # will be initialized when the first row is added
            logger.info("Initialized an empty DataFrame bound to %s.", results_file)
        self.results_file = results_file


    def to_csv(self, filename):
        self.dataFrame.to_csv(filename, columns=self.dataFrame.columns, index=False)
        # index=False means to not save the automatically-added index column.
        # This is important - without it we might have problems later when adding new rows after load.

    def add(self, new_row:dict):
        """
        Add a data-row whose values exactly match the columns in self.columns.
        """
        if self.dataFrame is None:
            columns = list(new_row.keys())
            logger.debug("    Inserting first row: setting columns to %s", columns)
            self.dataFrame = pandas.DataFrame(columns=columns)

        index_of_new_row = self.dataFrame.shape[0]
        self.dataFrame.loc[index_of_new_row] = pandas.Series(new_row) # Works only if there are no "holes" in the index (requires "index=False" in saving to csv).
        # self.dataFrame.iloc[index_of_new_row] = pandas.Series(dataRow) # IndexError: single positional indexer is out-of-bounds
        # self.dataFrame = self.dataFrame.append(pandas.Series(dataRow), ignore_index=True) # This is inefficient! It creates and returns a new dataFrame.
        self.to_csv(self.results_file)

    def run(self, 
        single_run: Callable[[Any], Dict],
        input_ranges: Dict[str,List[Any]]
        ):
        """
        Runs the experiment, changing each parameter in the given range.

        :param single_run:   a function that performs a single run. It accepts the run parameters (independent variables), and returns a dict with the run outcomes.
        :param input_ranges: a dict where the key is the parameter name, and the value is a list of possible values for that parameter.
        """
        for input in dict_product(input_ranges):
            if self.dataFrame is None:
                output = single_run(**input)
            else:
                existing_row = dict_to_row(self.dataFrame, input)
                if existing_row:
                    logger.info("\nskipped input: %s\nexisting row: %s", input, existing_row)
                    continue
                else:
                    output = single_run(**input)
            if not isinstance(output, dict):
                raise ValueError(f"single_run must return a dict output, mapping each output variable name to its value. It returned {type(output)}.")
            logger.info("\ninput: %s\noutput: %s", input, output)
            self.add({**input, **output})

        logger.info("Done!")
        # self.to_csv(self.results_file)
        # if os.path.exists(self.csvFileNameTemp):
        #     logger.info("Removing temporary CSV file %s", self.csvFileNameTemp)
        #     os.remove(self.csvFileNameTemp)


Experiment.logger = logger
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())
