import re
import tomli
import os.path
import psycopg2
import multiprocessing
import signal
import yaml
from .constants import ConfigFormats, ExecutionStatus, ModelStatus, Systems
from configparser import ConfigParser
from .Object import Object
from .PostgreSQL import PostgreSQL
from .MySQL import MySQL

try:
    import importlib.resources as pkg_resources
except ImportError:
    # Try backported to PY<37 `importlib_resources`.
    import importlib_resources as pkg_resources


def _process_file(args):
    """
    Main multi thread worker process.
    Responsible For:
    1. Executing the sql for a given file

    :param args: Tuple containing input parameters to this invocation of this call
    :return: Filename That Was Executed, Execution Status, Database Error
    """
    filename_to_execute = args[0]
    sql_to_execute = args[1]
    system = args[2]

    if system['type'] == Systems.POSTGRESQL.value:
        return _postgresql_execute(system, filename_to_execute, sql_to_execute)
    elif system['type'] == Systems.MYSQL.value:
        return _mysql_execute(system, filename_to_execute, sql_to_execute)


def _mysql_execute(system, filename, sql):
    """
    :param system: Dictionary containing system level configuration (host, database, user, password)
    :param filename:
    :param sql:

    :return:
    """
    mysql = MySQL(system['host'], system['database'], system['user'], system['password'])

    try:
        mysql.execute(sql)
    except (Exception, psycopg2.DatabaseError) as error:
        return filename, ExecutionStatus.FAILED.value, error

    return filename, ExecutionStatus.SUCCEEDED.value, None


def _postgresql_execute(system, filename, sql):
    """

    :param system: Dictionary containing system level configuration (host, database, user, password)
    :param filename: Filename that is to be executed
    :param sql: SQL that will be executed
    :return:
    """
    postgres = PostgreSQL(system['host'], system['database'], system['user'], system['password'])

    try:
        postgres.execute(sql)
    except (Exception, psycopg2.DatabaseError) as error:
        return filename, ExecutionStatus.FAILED.value, error

    return filename, ExecutionStatus.SUCCEEDED.value, None


class DataBeaver(Object):
    """
    Responsible For
    - Data Model Orchestration (the building of 1 or more data models)
    """
    FIELD_PROCESSES = "processes"
    FIELD_SYSTEM = "system"
    SECTION_DATABEAVER = "DataBeaver"
    DEFAULT_LOGGER = "DataBeaver"
    EXECUTION_SUCCEEDED = "Succeeded"
    EXECUTION_FINISHED_STATUSES = [ExecutionStatus.FAILED.value, ExecutionStatus.SUCCEEDED.value,
                                   ExecutionStatus.SKIPPED.value]

    def __init__(self, config_file=None, config_format=None):
        """

        :param config_file: Name of the configuration file to be used
        :param config_format: Optional command line arguments (used when DataBeaver is invoked via the command line)

        """
        # Call Object.__init__()
        super().__init__()

        self._config_format = config_format
        self._config_file = config_file
        self._config = None

        # Configure logging and instantiate the _logger
        self._logger = self.get_logger()

        # Determine the config file format if we do not yet know
        extension = config_file.split('.')[-1].lower().strip()
        if (self._config_format is None) and (extension == 'ini'):
            self._config_format = ConfigFormats.INI
        elif (self._config_format is None) and (extension == 'toml'):
            self._config_format = ConfigFormats.TOML
        elif (self._config_format is None) and (extension == 'yaml'):
            self._config_format = ConfigFormats.YAML
        elif (self._config_format is None) and (extension == 'json'):
            self._config_format = ConfigFormats.JSON

        # Check if we have a configuration file, if we do not we are done
        if self._config_file is None:
            self._logger.warning('No configuration file supplied. Default values will be used.')
            return

        # Load configuration from the supplied configuration file
        if self._config_format is ConfigFormats.TOML:
            with open(self._config_file, "rb") as f:
                self._config = tomli.load(f)
                self._logger.info(self._config)
        elif self._config_format is ConfigFormats.INI:
            self._config = {}
            config = ConfigParser()
            config.read(self._config_file)
            for section in config.sections():
                self._config[section] = {}
                for option in config.options(section):
                    self._config[section][option] = config.get(section, option)
            self._logger.info(self._config)
        elif self._config_format is ConfigFormats.YAML:
            with open(self._config_file, 'r') as stream:
                self._config = yaml.safe_load(stream)

        # Supply default values as needed
        if self.SECTION_DATABEAVER not in self._config:
            self._config[self.SECTION_DATABEAVER] = {}

        if self.FIELD_PROCESSES not in self._config[self.SECTION_DATABEAVER]:
            self._logger.warning("Default number of processes not specified. Defaulting to 1")
            self._config[self.SECTION_DATABEAVER][self.FIELD_PROCESSES] = 1

    def _parse_sql(self, model_info, file_info, schema):
        """

        :param model_info: Model level information
        :param file_info: File level information
        :return: file_info: File Info (with added dependencies based off model references and parsed sql)
        """
        # Check For Model References To Add To File Dependencies
        for file_name, file in file_info.items():
            self._logger.info(f"Processing SQL for {file_name}")
            model_name = file_name[file_name.rfind('/') + 1:file_name.find('.')]

            # Add any dependencies that are introduced by model references
            ref_positions = re.finditer(r"ref\(", file['raw_sql'])
            for match in ref_positions:
                close_tag_pos = file['raw_sql'].find(')', match.end())
                referred_model_name = file['raw_sql'][match.end():close_tag_pos]
                referred_model = model_info[referred_model_name]
                if referred_model_name != model_name \
                        and referred_model['steps'][-1] not in file_info[file_name]['dependencies']:
                    file_info[file_name]['dependencies'].append(referred_model['steps'][-1])

            # Create the compiled sql that we will need for execution
            tag_matches = re.finditer(r"\{\{", file['raw_sql'])
            current_position = 0
            parsed_model_sql = ""
            for match in tag_matches:
                close_tag_pos = file['raw_sql'].find(r"}}", match.end())
                tag_contents = file['raw_sql'][match.end() + 1:close_tag_pos]
                parsed_model_sql += file['raw_sql'][current_position: match.start()]
                tag_parsed = False

                # Process {{ ref(<model>) }} tags
                function_pos = tag_contents.find('ref(')
                if function_pos > -1:
                    pos = tag_contents.find("(")
                    end_pos = tag_contents.find(")", pos + 1)
                    referred_model_name = tag_contents[pos + 1:end_pos]
                    parsed_model_sql += f" {referred_model_name} "

                # Process {{ full_table_name }} tags
                table_name_pos = tag_contents.find('full_table_name')
                if table_name_pos > -1:
                    parsed_model_sql += f"{schema}.{model_name}"
                    tag_parsed = True

                # Process {{ table_name }} tags (and only table_name)
                table_name_pos = tag_contents.find('table_name')
                if table_name_pos > -1 and tag_parsed is False:
                    parsed_model_sql += f"{model_name}"

                # Process {{ model_name }} tags
                table_name_pos = tag_contents.find('model_name')
                if table_name_pos > -1:
                    parsed_model_sql += f"{model_name}"

                # Set the current position where the tag was closed
                current_position = close_tag_pos + 2

            # Store the parsed sql for each file
            parsed_model_sql += file['raw_sql'][current_position:]
            file_info[file_name]['sql'] = parsed_model_sql

        return file_info

    def build(self, model=None):
        """
        Responsible for
        1. Determining model file dependencies
        2. Determining sql file dependencies
        3. Parsing sql files into executable code
        4. Executing the sql against the target system

        :return: (model_info, file_info)
        """

        # Look for models in the directories specified in the project file
        model_files = []
        for directory in self._config[model]['model_directories'].split(','):
            files = [f"{directory}/{file}" for file in os.listdir(directory)]
            model_files.extend(files)

        # Iterate over all the models and generate the compiled sql that we will run against the database
        # We will also generate the model dependencies
        model_info = {}
        file_info = {}
        for model_file_name in model_files:
            model_name = model_file_name[model_file_name.rfind('/') + 1:model_file_name.find('.')]

            # Check if this is the first time we have seen this model
            if model_name not in model_info:
                model_info[model_name] = {'steps': [], 'current_step': 0, 'status': ModelStatus.NOT_BUILT.value}

            if model_file_name not in file_info:
                file_info[model_file_name] = {'dependencies': [], 'status': ExecutionStatus.NOT_EXECUTED.value}

            # Add this model to the steps for the table
            model_info[model_name]['steps'].append(model_file_name)

            # Add any dependency based on having prior steps in the model to run
            if model_file_name.count('.') == 3:
                # Get the index number
                start_pos = model_file_name.find('.') + 1
                end_pos = model_file_name.find('.', start_pos, len(model_file_name))
                index_number = int(model_file_name[start_pos:end_pos])

                if index_number > 1:
                    previous_sql_name = model_file_name.replace(f'.{index_number}.', f'.{index_number - 1}.')
                    file_info[model_file_name]['dependencies'].append(previous_sql_name)
            else:
                self._logger.error(f"{model_file_name} can not be parsed and will be ignored.")
                continue

            # Load the sql out of the file
            with open(model_file_name, 'r') as model_file:
                raw_sql = model_file.read()
            file_info[model_file_name]['raw_sql'] = raw_sql

        file_info = self._parse_sql(model_info, file_info, self._config[model]['schema'])

        # Determine the number of processes to use, either by using a model specific configuration or default
        if self.FIELD_PROCESSES in self._config[model]:
            processes = int(self._config[model][self.FIELD_PROCESSES])
        else:
            processes = int(self._config[self.SECTION_DATABEAVER][self.FIELD_PROCESSES])

        # Get the system configuration
        system_config = self._config[self._config[model][self.FIELD_SYSTEM]]

        original_sigint_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
        with multiprocessing.Pool(processes) as pool:
            signal.signal(signal.SIGINT, original_sigint_handler)

            # Loop over the models we will create until no more work can be done
            continue_processing = True
            loop_counter = 1

            while continue_processing:
                self._logger.info(f"Pass #{loop_counter}")
                loop_counter += 1

                # Determine all files we want to process in this pass
                files_to_process = []
                continue_processing = False
                for model_name in model_info.keys():
                    # Only process MODEL_NOT_BUILT models
                    if model_info[model_name]['status'] != ModelStatus.NOT_BUILT.value:
                        continue

                    # Get the file we will process for this model in this pass
                    current_step = model_info[model_name]['current_step']
                    filename_to_execute = model_info[model_name]['steps'][current_step]

                    # If all the dependencies have been satisfied, add the file to the list of files to be processed
                    if len(file_info[filename_to_execute]['dependencies']) == 0:
                        self._logger.info(f"{model_name} : {filename_to_execute} will be executed.")
                        files_to_process.append((filename_to_execute, file_info[filename_to_execute]['sql'],
                                                 system_config))

                # Execute all the sql statements for this pass in parallel
                results = pool.imap_unordered(_process_file, files_to_process)

                # Update file dependencies and model build status based on the results returned
                for (filename_executed, execution_status, db_error) in results:
                    executed_model_name = filename_executed[
                                          filename_executed.rfind('/') + 1:filename_executed.find('.')]

                    # This file successfully executed and can be removed from any dependencies
                    if ExecutionStatus.SUCCEEDED.value == execution_status:
                        # Something succeeded so we need to keep processing
                        continue_processing = True
                        self._logger.info(f"{filename_executed} - {execution_status}")

                        # Increment current_step
                        model_info[executed_model_name]['current_step'] = current_step + 1

                        # If we executed the last file in steps the model is built
                        if model_info[executed_model_name]['current_step'] == len(
                                model_info[executed_model_name]['steps']):
                            model_info[executed_model_name]['status'] = ModelStatus.BUILT.value

                        for file_name, file in file_info.items():
                            if filename_executed in file['dependencies']:
                                file_info[file_name]['dependencies'].remove(filename_executed)

                    elif ExecutionStatus.FAILED.value == execution_status:
                        self._logger.info(f"{model_name} - {ModelStatus.FAILED.value}")
                        model_info[executed_model_name]['status'] = ModelStatus.FAILED.value

    def create_project(self, name, config_format=ConfigFormats.TOML):
        """
        Create a new empty
        :return:
        """
        self._logger.info('Creating new project')

        # Get the project name from the user and generate the directory name we will use
        directory_name = re.sub(' ', '_', name)
        directory_name = re.sub('[^A-Za-z0-9_]+', '', directory_name)
        self._logger.info(f"Project name is '{name}'")

        # Check if the directory already exists
        if os.path.isdir(directory_name):
            self._logger.error(f"{directory_name} already exists, operation can not be completed.")
            return

        # Make the top level project directory
        os.mkdir(directory_name)
        self._logger.info(f'Created {directory_name}')

        # Make the directory for configuration files
        config_directory = f"{directory_name}/system"
        os.mkdir(config_directory)
        self._logger.info(f'Created {config_directory}')

        # Get the data for the sample config file and set the file name for the sample config file
        config_sample = ''
        if config_format is ConfigFormats.TOML:
            file_name = "databeaver.toml"
            config_sample = pkg_resources.read_text('databeaver.data', 'configSample.toml')
        elif config_format is ConfigFormats.YAML:
            file_name = "databeaver.yaml"
        elif config_format is ConfigFormats.INI:
            file_name = "databeaver.ini"
            config_sample = pkg_resources.read_text('databeaver.data', 'configSample.ini')
        elif config_format is ConfigFormats.JSON:
            file_name = "databeaver.json"

        # Write the config file to the file system
        file_path = f"{config_directory}/{file_name}"
        with open(file_path) as f:
            f.write(config_sample)
