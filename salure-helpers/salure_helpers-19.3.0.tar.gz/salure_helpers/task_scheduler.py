import sys
import datetime
import inspect
import time
from salure_helpers import MySQL, MailClient
from salure_helpers.salure_functions import SalureFunctions
import warnings
import re
from salure_helpers.elastic import Elastic


class TaskScheduler(object):

    def __init__(self, host, user, password, database, task_id, loglevel='INFO', email_after_errors=False,
                 mandrill_api_token=None, es_host=None, es_port=None, es_user=None, es_password=None):
        """
        The TaskScheduler is responsible for the logging to the database. Based on this logging, the next reload will
        start or not and warning will be given or not
        :param host: The MySQL host of the customer database
        :param user: MySQL user of the customer
        :param password: MySQL password of the customer
        :param database: the customer database
        :param task_id: The ID from the task as saved in the task_scheduler table in the customer database
        :param email_after_errors: a True or False value. When True, there will be send an email to a contactperson of the customer (as given in the database) with the number of errors
        :param mandrill_api_token: When an email should be send after the errors, there is a mandrill API token needed with which the mails could be send
        :param loglevel: Chose on which level you want to store the logs. Default is INFO. that means that a logline
        with level DEBUG not is stored
        :param es_host: The Elastic Search host of the customer database
        :param es_port: The port on which the Elastic Search customer database is located
        :param es_user: The Elastic Search user of the customer
        :param es_password: The Elastic Search password of the customer
        """
        self.mysql = MySQL(host, user, password, database)
        if es_host is not None:
            client_user = user
            client_password = password
            self.es = Elastic(es_host, es_port, es_user, es_password, client_user, client_password)
        else:
            self.es = None
        self.email_after_errors = email_after_errors
        self.mandrill_api_token = mandrill_api_token
        self.task_id = task_id
        self.loglevel = loglevel
        # If the task is started via the task_scheduler, the following 3 parameters will be passed by the scheduler
        if len(sys.argv[1:4]) > 0:
            self.started_local = False
            self.customer_db, self.task_id, self.run_id = sys.argv[1:4]
        # If the task is started locally, the parameters should be set locally
        else:
            self.started_local = True
            self.customer_db = 'placeholder'
            self.task_id = self.task_id
            self.run_id = int(round(time.time() * 100000))
            self.started_at = datetime.datetime.now()
        print(self.task_id, self.run_id)
        self.error_count = 0

        # Check if the log tables exists in the customer database. If not, create them
        # Mysql throws a warning when a table already exists. We don't care so we ignore warnings. (not exceptions!)
        warnings.filterwarnings('ignore')
        self.check_if_logging_tables_exists()

        # Check if the task is started on schedule or manual. store in a variable to use later in the script
        self.task_manual_started = self.check_if_task_manual_started()

        # Start the task and setup the data in the database
        self.start_task()

    def check_if_logging_tables_exists(self):
        """
        This function checks if all the needed tables for the task_scheduler exists. If they don't, this function
        creates the needed tables
        :return: nothing
        """
        # Check if the table task_scheduler exists. If not, create it
        new_table_query = 'CREATE TABLE IF NOT EXISTS `task_scheduler` (' \
                          '`id`                         int(11)                                 NOT NULL AUTO_INCREMENT,' \
                          '`dashboard_reload`           bool                                    NOT NULL DEFAULT \'0\',' \
                          '`title`                      varchar(50)                             NOT NULL,' \
                          '`description`                varchar(255)                            NOT NULL,' \
                          '`dashboard_guid`             varchar(255)                            NULL DEFAULT NULL,' \
                          '`docker_image`               varchar(255)                            DEFAULT NULL,' \
                          '`runfile_path`               varchar(255)                            DEFAULT NULL,' \
                          '`trigger_type`               enum("MANUAL", "TIME", "OTHER_TASK")    NOT NULL DEFAULT \'MANUAL\',' \
                          '`next_reload`                timestamp                               NULL DEFAULT NULL,' \
                          '`timezone`                   enum("Africa/Abidjan", "Africa/Accra", "Africa/Addis_Ababa", "Africa/Algiers", "Africa/Asmara", "Africa/Bamako", "Africa/Bangui", "Africa/Banjul", "Africa/Bissau", "Africa/Blantyre", "Africa/Brazzaville", "Africa/Bujumbura", "Africa/Cairo", "Africa/Casablanca", "Africa/Ceuta", "Africa/Conakry", "Africa/Dakar", "Africa/Dar_es_Salaam", "Africa/Djibouti", "Africa/Douala", "Africa/El_Aaiun", "Africa/Freetown", "Africa/Gaborone", "Africa/Harare", "Africa/Johannesburg", "Africa/Juba", "Africa/Kampala", "Africa/Khartoum", "Africa/Kigali", "Africa/Kinshasa", "Africa/Lagos", "Africa/Libreville", "Africa/Lome", "Africa/Luanda", "Africa/Lubumbashi", "Africa/Lusaka", "Africa/Malabo", "Africa/Maputo", "Africa/Maseru", "Africa/Mbabane", "Africa/Mogadishu", "Africa/Monrovia", "Africa/Nairobi", "Africa/Ndjamena", "Africa/Niamey", "Africa/Nouakchott", "Africa/Ouagadougou", "Africa/Porto-Novo", "Africa/Sao_Tome", "Africa/Tripoli", "Africa/Tunis", "Africa/Windhoek", "America/Adak", "America/Anchorage", "America/Anguilla", "America/Antigua", "America/Araguaina", "America/Argentina/Buenos_Aires", "America/Argentina/Catamarca", "America/Argentina/Cordoba", "America/Argentina/Jujuy", "America/Argentina/La_Rioja", "America/Argentina/Mendoza", "America/Argentina/Rio_Gallegos", "America/Argentina/Salta", "America/Argentina/San_Juan", "America/Argentina/San_Luis", "America/Argentina/Tucuman", "America/Argentina/Ushuaia", "America/Aruba", "America/Asuncion", "America/Atikokan", "America/Bahia", "America/Bahia_Banderas", "America/Barbados", "America/Belem", "America/Belize", "America/Blanc-Sablon", "America/Boa_Vista", "America/Bogota", "America/Boise", "America/Cambridge_Bay", "America/Campo_Grande", "America/Cancun", "America/Caracas", "America/Cayenne", "America/Cayman", "America/Chicago", "America/Chihuahua", "America/Costa_Rica", "America/Creston", "America/Cuiaba", "America/Curacao", "America/Danmarkshavn", "America/Dawson", "America/Dawson_Creek", "America/Denver", "America/Detroit", "America/Dominica", "America/Edmonton", "America/Eirunepe", "America/El_Salvador", "America/Fort_Nelson", "America/Fortaleza", "America/Glace_Bay", "America/Godthab", "America/Goose_Bay", "America/Grand_Turk", "America/Grenada", "America/Guadeloupe", "America/Guatemala", "America/Guayaquil", "America/Guyana", "America/Halifax", "America/Havana", "America/Hermosillo", "America/Indiana/Indianapolis", "America/Indiana/Knox", "America/Indiana/Marengo", "America/Indiana/Petersburg", "America/Indiana/Tell_City", "America/Indiana/Vevay", "America/Indiana/Vincennes", "America/Indiana/Winamac", "America/Inuvik", "America/Iqaluit", "America/Jamaica", "America/Juneau", "America/Kentucky/Louisville", "America/Kentucky/Monticello", "America/Kralendijk", "America/La_Paz", "America/Lima", "America/Los_Angeles", "America/Lower_Princes", "America/Maceio", "America/Managua", "America/Manaus", "America/Marigot", "America/Martinique", "America/Matamoros", "America/Mazatlan", "America/Menominee", "America/Merida", "America/Metlakatla", "America/Mexico_City", "America/Miquelon", "America/Moncton", "America/Monterrey", "America/Montevideo", "America/Montserrat", "America/Nassau", "America/New_York", "America/Nipigon", "America/Nome", "America/Noronha", "America/North_Dakota/Beulah", "America/North_Dakota/Center", "America/North_Dakota/New_Salem", "America/Ojinaga", "America/Panama", "America/Pangnirtung", "America/Paramaribo", "America/Phoenix", "America/Port-au-Prince", "America/Port_of_Spain", "America/Porto_Velho", "America/Puerto_Rico", "America/Punta_Arenas", "America/Rainy_River", "America/Rankin_Inlet", "America/Recife", "America/Regina", "America/Resolute", "America/Rio_Branco", "America/Santarem", "America/Santiago", "America/Santo_Domingo", "America/Sao_Paulo", "America/Scoresbysund", "America/Sitka", "America/St_Barthelemy", "America/St_Johns", "America/St_Kitts", "America/St_Lucia", "America/St_Thomas", "America/St_Vincent", "America/Swift_Current", "America/Tegucigalpa", "America/Thule", "America/Thunder_Bay", "America/Tijuana", "America/Toronto", "America/Tortola", "America/Vancouver", "America/Whitehorse", "America/Winnipeg", "America/Yakutat", "America/Yellowknife", "Antarctica/Casey", "Antarctica/Davis", "Antarctica/DumontDUrville", "Antarctica/Macquarie", "Antarctica/Mawson", "Antarctica/McMurdo", "Antarctica/Palmer", "Antarctica/Rothera", "Antarctica/Syowa", "Antarctica/Troll", "Antarctica/Vostok", "Arctic/Longyearbyen", "Asia/Aden", "Asia/Almaty", "Asia/Amman", "Asia/Anadyr", "Asia/Aqtau", "Asia/Aqtobe", "Asia/Ashgabat", "Asia/Atyrau", "Asia/Baghdad", "Asia/Bahrain", "Asia/Baku", "Asia/Bangkok", "Asia/Barnaul", "Asia/Beirut", "Asia/Bishkek", "Asia/Brunei", "Asia/Chita", "Asia/Choibalsan", "Asia/Colombo", "Asia/Damascus", "Asia/Dhaka", "Asia/Dili", "Asia/Dubai", "Asia/Dushanbe", "Asia/Famagusta", "Asia/Gaza", "Asia/Hebron", "Asia/Ho_Chi_Minh", "Asia/Hong_Kong", "Asia/Hovd", "Asia/Irkutsk", "Asia/Jakarta", "Asia/Jayapura", "Asia/Jerusalem", "Asia/Kabul", "Asia/Kamchatka", "Asia/Karachi", "Asia/Kathmandu", "Asia/Khandyga", "Asia/Kolkata", "Asia/Krasnoyarsk", "Asia/Kuala_Lumpur", "Asia/Kuching", "Asia/Kuwait", "Asia/Macau", "Asia/Magadan", "Asia/Makassar", "Asia/Manila", "Asia/Muscat", "Asia/Nicosia", "Asia/Novokuznetsk", "Asia/Novosibirsk", "Asia/Omsk", "Asia/Oral", "Asia/Phnom_Penh", "Asia/Pontianak", "Asia/Pyongyang", "Asia/Qatar", "Asia/Qostanay", "Asia/Qyzylorda", "Asia/Riyadh", "Asia/Sakhalin", "Asia/Samarkand", "Asia/Seoul", "Asia/Shanghai", "Asia/Singapore", "Asia/Srednekolymsk", "Asia/Taipei", "Asia/Tashkent", "Asia/Tbilisi", "Asia/Tehran", "Asia/Thimphu", "Asia/Tokyo", "Asia/Tomsk", "Asia/Ulaanbaatar", "Asia/Urumqi", "Asia/Ust-Nera", "Asia/Vientiane", "Asia/Vladivostok", "Asia/Yakutsk", "Asia/Yangon", "Asia/Yekaterinburg", "Asia/Yerevan", "Atlantic/Azores", "Atlantic/Bermuda", "Atlantic/Canary", "Atlantic/Cape_Verde", "Atlantic/Faroe", "Atlantic/Madeira", "Atlantic/Reykjavik", "Atlantic/South_Georgia", "Atlantic/St_Helena", "Atlantic/Stanley", "Australia/Adelaide", "Australia/Brisbane", "Australia/Broken_Hill", "Australia/Currie", "Australia/Darwin", "Australia/Eucla", "Australia/Hobart", "Australia/Lindeman", "Australia/Lord_Howe", "Australia/Melbourne", "Australia/Perth", "Australia/Sydney", "Canada/Atlantic", "Canada/Central", "Canada/Eastern", "Canada/Mountain", "Canada/Newfoundland", "Canada/Pacific", "Europe/Amsterdam", "Europe/Andorra", "Europe/Astrakhan", "Europe/Athens", "Europe/Belgrade", "Europe/Berlin", "Europe/Bratislava", "Europe/Brussels", "Europe/Bucharest", "Europe/Budapest", "Europe/Busingen", "Europe/Chisinau", "Europe/Copenhagen", "Europe/Dublin", "Europe/Gibraltar", "Europe/Guernsey", "Europe/Helsinki", "Europe/Isle_of_Man", "Europe/Istanbul", "Europe/Jersey", "Europe/Kaliningrad", "Europe/Kiev", "Europe/Kirov", "Europe/Lisbon", "Europe/Ljubljana", "Europe/London", "Europe/Luxembourg", "Europe/Madrid", "Europe/Malta", "Europe/Mariehamn", "Europe/Minsk", "Europe/Monaco", "Europe/Moscow", "Europe/Oslo", "Europe/Paris", "Europe/Podgorica", "Europe/Prague", "Europe/Riga", "Europe/Rome", "Europe/Samara", "Europe/San_Marino", "Europe/Sarajevo", "Europe/Saratov", "Europe/Simferopol", "Europe/Skopje", "Europe/Sofia", "Europe/Stockholm", "Europe/Tallinn", "Europe/Tirane", "Europe/Ulyanovsk", "Europe/Uzhgorod", "Europe/Vaduz", "Europe/Vatican", "Europe/Vienna", "Europe/Vilnius", "Europe/Volgograd", "Europe/Warsaw", "Europe/Zagreb", "Europe/Zaporozhye", "Europe/Zurich", "GMT", "Indian/Antananarivo", "Indian/Chagos", "Indian/Christmas", "Indian/Cocos", "Indian/Comoro", "Indian/Kerguelen", "Indian/Mahe", "Indian/Maldives", "Indian/Mauritius", "Indian/Mayotte", "Indian/Reunion", "Pacific/Apia", "Pacific/Auckland", "Pacific/Bougainville", "Pacific/Chatham", "Pacific/Chuuk", "Pacific/Easter", "Pacific/Efate", "Pacific/Enderbury", "Pacific/Fakaofo", "Pacific/Fiji", "Pacific/Funafuti", "Pacific/Galapagos", "Pacific/Gambier", "Pacific/Guadalcanal", "Pacific/Guam", "Pacific/Honolulu", "Pacific/Kiritimati", "Pacific/Kosrae", "Pacific/Kwajalein", "Pacific/Majuro", "Pacific/Marquesas", "Pacific/Midway", "Pacific/Nauru", "Pacific/Niue", "Pacific/Norfolk", "Pacific/Noumea", "Pacific/Pago_Pago", "Pacific/Palau", "Pacific/Pitcairn", "Pacific/Pohnpei", "Pacific/Port_Moresby", "Pacific/Rarotonga", "Pacific/Saipan", "Pacific/Tahiti", "Pacific/Tarawa", "Pacific/Tongatapu", "Pacific/Wake", "Pacific/Wallis", "US/Alaska", "US/Arizona", "US/Central", "US/Eastern", "US/Hawaii", "US/Mountain", "US/Pacific", "UTC") CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT \"Europe/Amsterdam\",' \
                          '`frequency`                  varchar(255)                            DEFAULT \'{"month":0,"day":0,"hour":0,"minute":0}\',' \
                          '`start_after_task_id`        int                                     DEFAULT NULL,' \
                          '`start_after_preceding_task` enum("FAILED", "SUCCESS")               DEFAULT NULL,' \
                          '`last_reload`                timestamp                               NULL DEFAULT NULL,' \
                          '`last_error_message`         varchar(255)                            DEFAULT NULL,' \
                          '`status`                     varchar(255)                            DEFAULT \'IDLE\',' \
                          '`disabled`                   tinyint(4)                              DEFAULT \'1\',' \
                          '`run_instant`                tinyint(1)                              DEFAULT \'0\',' \
                          '`sftp_mapping`               varchar(255)                            NOT NULL DEFAULT \'[]\',' \
                          '`step_nr`                    int                                     NOT NULL DEFAULT \'0\',' \
                          '`stopped_by_user`            tinyint(1)                              DEFAULT \'0\',' \
                          '`stop_is_allowed`            bool                                    NOT NULL DEFAULT \'0\',' \
                          'PRIMARY KEY (`id`),' \
                          'UNIQUE KEY `task_scheduler_id_uindex` (`id`),' \
                          'constraint task_scheduler_task_scheduler_id_fk foreign key (start_after_task_id) references task_scheduler (id)' \
                          ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci'
        self.mysql.raw_query(new_table_query)

        # Check if the table task_scheduler_log exists. If not, create it
        new_table_query = 'CREATE TABLE IF NOT EXISTS `task_scheduler_log` (' \
                          '`reload_id`      bigint          NOT NULL,' \
                          '`task_id`        int             NULL,' \
                          '`reload_status`  varchar(255)    NULL,' \
                          '`started_at`     datetime        NULL,' \
                          '`finished_at`    datetime        NULL' \
                          ') ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci'
        self.mysql.raw_query(new_table_query)

        # Check if the table check_task_execution_log exists. If not, create it
        new_table_query = 'CREATE TABLE IF NOT EXISTS `task_execution_log`(' \
                          '`reload_id`   bigint       NOT NULL,' \
                          '`task_id`     int          NULL,' \
                          '`log_level`   varchar(255) NULL,' \
                          '`created_at`  datetime     NULL,' \
                          '`line_number` int          NULL,' \
                          '`message`     longtext     NULL)' \
                          'ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci'
        self.mysql.raw_query(new_table_query)

        # If logging to Elastic Search is enabled, create an index template if it doesn't exist yet
        if self.es is not None:
            template_name = self.es.client_user
            index_template = {
                'index_patterns': [f'{template_name}*'],
                'settings': {
                    'number_of_shards': 2,
                    'number_of_replicas': 2
                },
                'mappings': {
                    "_source": {
                        "enabled": False
                    },
                    'properties': {
                        'reload_id': {
                            'type': 'long'
                        },
                        'task_id': {
                            'type': 'integer'
                        },
                        'log_level': {
                            'type': 'text'
                        },
                        'created_at': {
                            'type': 'date',
                            'format': 'yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis'
                        },
                        'line_number': {
                            'type': 'integer'
                        },
                        'message': {
                            'type': 'text'
                        }
                    }
                }
            }
            self.es.create_index_template(template_name, index_template)

        # Check if the table check_task_execution_steps exists. If not, create it
        new_table_query = 'CREATE TABLE IF NOT EXISTS `task_execution_steps`(' \
                          '`id`          bigint       NOT NULL AUTO_INCREMENT,' \
                          '`task_id`     int          NULL,' \
                          '`nr`          int          DEFAULT 0 NOT NULL,' \
                          '`description` varchar(255) DEFAULT \'ZzZzZz...\' NOT NULL,' \
                          'PRIMARY KEY (`id`),' \
                          'UNIQUE KEY `task_execution_steps_id_uindex` (`id`),' \
                          'UNIQUE INDEX `task_execution_steps_task_id_nr_uindex` (`task_id`, `nr`))' \
                          'ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci'
        self.mysql.raw_query(new_table_query)

        new_table_query = 'CREATE TABLE IF NOT EXISTS `task_variables`(' \
                          'id INT NOT NULL AUTO_INCREMENT,' \
                          'task_id INT NOT NULL,' \
                          'name VARCHAR(150) NOT NULL,' \
                          'description VARCHAR(255) NULL,' \
                          'type ENUM(\'INT\', \'TINYINT\', \'BIGINT\', \'FLOAT\', \'DOUBLE\', \'DATETIME\', \'TIMESTAMP\', \'TIME\', \'VARCHAR\', \'BLOB\', \'TEXT\', \'LONGBLOB\') NOT NULL,' \
                          'value VARCHAR(600) NULL,' \
                          'temp_value VARCHAR(600) NULL,' \
                          'PRIMARY KEY (`id`),' \
                          'UNIQUE KEY `task_variables_id_uindex` (`id`),' \
                          'UNIQUE INDEX `task_variables_name_value_uindex` (`task_id`, `name`, `value`), ' \
                          'INDEX `task_variables_name_index` (`name`),' \
                          'CONSTRAINT task_variables_task_scheduler_id_fk ' \
                          'FOREIGN KEY (`task_id`) REFERENCES task_scheduler (`id`) ON DELETE CASCADE)' \
                          'ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci'
        self.mysql.raw_query(new_table_query)

        # Add the variable 'email_errors_to' as default to the new added table if it doesn't exist for the current task
        response = self.mysql.select('task_variables', 'temp_value',
                                     f'WHERE name = \'email_errors_to\' AND task_id = {self.task_id}')
        if len(response) == 0:
            new_variables = f"-- INSERT INTO `task_variables` (`task_id`, `name`, `type`, `value`, `temp_value`) " \
                            f"VALUES ({self.task_id}, 'email_errors_to', 'TEXT', 'example@salure.nl, example2@salure.nl', 'example@salure.nl, example2@salure.nl')"
            self.mysql.raw_query(new_variables, insert=True)

    def create_task_execution_steps(self, step_details: list):
        """
        Check if the given steps already exists in the task_execution_steps table. If not, update or insert the values in the table
        :param step_details: list of dicts. Each dict must contain task details according to required_fields.
        Example: step_details = [
                                    {'nr': 1, 'description': 'test'},
                                    {'nr': 2, 'description': 'test2'}
                                ]
        :return: error (str) or response of mysql
        """
        # Check if the required fields are available in the given list
        required_fields = ['nr', 'description']
        for step in step_details:
            for field in required_fields:
                if field not in step.keys():
                    return 'Field {field} is required in step {step}. Required fields are: {required_fields}'.format(
                        field=field, step=step, required_fields=tuple(required_fields))

        # Reformat the list of dictionaries to a valid MySQL query
        values = ','.join(str((self.task_id, step['nr'], step['description'])) for step in step_details)
        response = self.mysql.raw_query("INSERT INTO task_execution_steps (`task_id`, `nr`, `description`) "
                                        "VALUES {step_values} ON DUPLICATE KEY UPDATE `description` = VALUES(description)".format(
            step_values=values), insert=True)
        return response

    def check_if_task_manual_started(self):
        """
        Check if the task manual is started of on schedule. If it's manual started, that's important for the variables in the db_variables function.
        In that case the dynamic variables should be used instead of the static ones
        :return: True of False
        """
        response = self.mysql.select('task_scheduler', 'run_instant', f'WHERE id = {self.task_id}')[0][0]
        if response == 1:
            # Reset the 1 back to 0 before sending the result
            self.mysql.update('task_scheduler', ['run_instant'], [0], 'WHERE `id` = {}'.format(self.task_id))
            return True
        else:
            return False

    def start_task(self):
        """
        Start the task and write this to the database. While the status is running, the task will not start again
        :return: if the update to the database is successful or not
        """
        # If the task is started from a local instance (not the task_scheduler), create a start log row in the task_scheduler_log
        if self.started_local:
            self.mysql.raw_query(f"INSERT INTO `task_scheduler_log` VALUES ({self.run_id}, {self.task_id}, 'Running', '{self.started_at}', null)", insert=True)
        return self.mysql.update('task_scheduler', ['status', 'step_nr'], ['RUNNING', 1], 'WHERE `id` = {}'.format(self.task_id))

    def db_variable(self, variable_name: str, default_value_if_temp_is_empty : bool = False):
        """
        Get a value from the task_variables table corresponding with the given name. If the task is manually started
        (run_instant = 1), then the temp_value will be returned. This is to give the possibility for users in the frontend to run
        a task once manual with other values then normal without overwriting the normal values.
        :param variable_name: the name of the variable
        :param default_value_if_temp_is_empty: bool to determine whether default value should be used if temp value is empty when manually started
        :return: the value of the given variable.
        """
        if self.task_manual_started is True:
            response = self.mysql.select('task_variables', 'temp_value, value',
                                         f'WHERE name = \'{variable_name}\' AND task_id = {self.task_id}')
        else:
            response = self.mysql.select('task_variables', 'value',
                                         f'WHERE name = \'{variable_name}\' AND task_id = {self.task_id}')
        if len(response) == 0:
            raise Exception(f'Variable with name \'{variable_name}\' does not exist')
        else:
            value = response[0][0]
            if value is None and default_value_if_temp_is_empty is True and len(response[0]) > 0:
                value = response[0][1]
            return value

    def write_execution_log(self, message: str, loglevel='INFO'):
        """
        Writes messages to the database. Give the message and the level of the log
        :param message: A string with a message for the log
        :param loglevel: You can choose between DEBUG, INFO, ERROR or CRITICAL (DEBUG is most granulated, CRITICAL the less)
        :return: If the write to the database is successful or not
        """
        allowed_loglevels = ['DEBUG', 'INFO', 'ERROR', 'CRITICAL']
        if loglevel not in allowed_loglevels:
            raise Exception('You\'ve entered a not allowed loglevel. Choose one of: {}'.format(allowed_loglevels))
        else:
            # Get the linenumber from where the logline is executed. Get the stacktrace of this action, jump 1 file up and pick then the linenumber (second item)
            linenumber = inspect.getouterframes(inspect.currentframe())[1][2]
            # Write the logline to the database, depends on the chosen loglevel in the task
            print('{} at line: {}'.format(message, linenumber))
            # Remove quotes from message since these break the query
            message = re.sub("[']", '', message)
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            information = {
                'reload_id': self.run_id,
                'task_id': self.task_id,
                'log_level': loglevel,
                'line_number': linenumber,
                'message': message,
                'created_at': timestamp
            }
            if self.loglevel == 'DEBUG':
                # Count the errors
                if loglevel == 'ERROR' or loglevel == 'CRITICAL':
                    self.error_count += 1
                if self.es is not None:
                    self.es.log_line(timestamp, information)
                return self.mysql.raw_query(
                    "INSERT INTO `task_execution_log` VALUES ({}, {}, '{}', '{}', {}, '{}')".format(self.run_id, self.task_id, loglevel, datetime.datetime.now(), linenumber, message), insert=True)
            elif self.loglevel == 'INFO' and (loglevel == 'INFO' or loglevel == 'ERROR' or loglevel == 'CRITICAL'):
                # Count the errors
                if loglevel == 'ERROR' or loglevel == 'CRITICAL':
                    self.error_count += 1
                if self.es is not None:
                    self.es.log_line(timestamp, information)
                return self.mysql.raw_query(
                    "INSERT INTO `task_execution_log` VALUES ({}, {}, '{}', '{}', {}, '{}')".format(self.run_id, self.task_id, loglevel, datetime.datetime.now(), linenumber, message), insert=True)
            elif self.loglevel == 'ERROR' and (loglevel == 'ERROR' or loglevel == 'CRITICAL'):
                self.error_count += 1
                if self.es is not None:
                    self.es.log_line(timestamp, information)
                return self.mysql.raw_query(
                    "INSERT INTO `task_execution_log` VALUES ({}, {}, '{}', '{}', {}, '{}')".format(self.run_id, self.task_id, loglevel, datetime.datetime.now(), linenumber, message), insert=True)
            elif self.loglevel == 'CRITICAL' and loglevel == 'CRITICAL':
                self.error_count += 1
                if self.es is not None:
                    self.es.log_line(timestamp, information)
                return self.mysql.raw_query(
                    "INSERT INTO `task_execution_log` VALUES ({}, {}, '{}', '{}', {}, '{}')".format(self.run_id,self.task_id, loglevel, datetime.datetime.now(), linenumber, message), insert=True)

    def update_execution_step(self, step_number: int):
        """
        Update the current step number in the task_scheduler table so that user's in the frontend of SalureConnect can see where a task is at any moment
        :param step_number: Give only a number
        :return: nothing
        """
        # Update the step number in the task_scheduler table
        return self.mysql.update('task_scheduler', ['step_nr'], [step_number], 'WHERE `id` = {}'.format(self.task_id))

    def error_handling(self, e: Exception, breaking=True, send_to_teams=False):
        """
        This function handles errors that occur in the scheduler. Logs the traceback, updates run statuses and notifies users
        :param e: the Exception that is to be handled
        :param task_id: The scheduler task id
        :param mysql_con: The connection which is used to update the scheduler task status
        :param logger: The logger that is used to write the logging status to
        :param breaking: Determines if the error is breaking or code will continue
        :param started_at: Give the time the task is started
        :return: nothing
        """
        # Format error to a somewhat readable format
        exc_type, exc_obj, exc_tb = sys.exc_info()
        error = str(e)[:400].replace('\'', '').replace('\"', '') + ' | Line: {}'.format(exc_tb.tb_lineno)
        # Get scheduler task details for logging
        task_details = \
            self.mysql.select('task_scheduler', 'docker_image, runfile_path', 'WHERE id = {}'.format(self.task_id))[0]
        taskname = task_details[0]
        customer = task_details[1].split('/')[-1].split('.')[0]

        if breaking:
            # Set scheduler status to failed
            self.mysql.update('task_scheduler', ['status', 'last_reload', 'last_error_message', 'step_nr'],
                              ['IDLE', datetime.datetime.now(), 'Failed', 0],
                              'WHERE `id` = {}'.format(self.task_id))
            # Log to database
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            information = {
                'reload_id': self.run_id,
                'task_id': self.task_id,
                'log_level': 'CRITICAL',
                'line_number': exc_tb.tb_lineno,
                'message': error,
                'created_at': timestamp
            }
            if self.es is not None:
                self.es.log_line(timestamp, information)
            self.mysql.raw_query(
                "INSERT INTO `task_execution_log` VALUES ({}, {}, 'CRITICAL', '{}', {}, '{}')".format(self.run_id,
                                                                                                      self.task_id,
                                                                                                      datetime.datetime.now(),
                                                                                                      exc_tb.tb_lineno,
                                                                                                      error),
                insert=True)
            self.mysql.update(table='task_scheduler_log',
                              columns=['reload_status', 'finished_at'],
                              values=['Failed', f'{datetime.datetime.now()}'],
                              filter=f'WHERE `reload_id` = {self.run_id}')
            # Notify users on Teams and If the variable self.send_mail_after_errors is set to True, send an email with the message that the task is failed
            if send_to_teams:
                SalureFunctions.send_error_to_teams(database=customer, task_number=self.task_id, task_title=taskname)
            if self.email_after_errors:
                self.email_errors(failed=True)
            # Remove the temp values from the variables table
            self.mysql.raw_query(f'UPDATE `task_variables` SET temp_value = null WHERE task_id = {self.task_id}', insert=True)

            # Start the chained tasks if it there are tasks which should start if this one is failed
            self.start_chained_tasks(finished_task_status='FAILED')

            raise Exception(error)
        else:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            information = {
                'reload_id': self.run_id,
                'task_id': self.task_id,
                'log_level': 'CRITICAL',
                'line_number': exc_tb.tb_lineno,
                'message': error,
                'created_at': timestamp
            }
            if self.es is not None:
                self.es.log_line(timestamp, information)
            self.mysql.raw_query(
                "INSERT INTO `task_execution_log` VALUES ({}, {}, 'CRITICAL', '{}', {}, '{}')".format(self.run_id,
                                                                                                      self.task_id,
                                                                                                      datetime.datetime.now(),
                                                                                                      exc_tb.tb_lineno,
                                                                                                      error),
                insert=True)
            if send_to_teams:
                SalureFunctions.send_error_to_teams(database=customer, task_number=self.task_id, task_title=taskname)
        self.error_count += 1

    def finish_task(self, reload_instant=False):
        """
        At the end of the script, write the outcome to the database. Write if the task is finished with or without errors, Email to a contactperson if this variable is given in the
        variables table. Also clean up the execution_log table when the number of lines is more than 1000
        :return:
        """
        # If reload instant is true, this adds an extra field 'run_instant' to the update query, and sets the value to 1. This makes the task reload immediately after it's finished
        field = ['run_instant', 'next_reload'] if reload_instant else []
        value = ['1', datetime.datetime.now()] if reload_instant else []
        if self.error_count > 0:
            self.mysql.update('task_scheduler', ['status', 'last_reload', 'last_error_message', 'step_nr'],
                              ['IDLE', datetime.datetime.now(), 'FinishedWithErrors', 0],
                              'WHERE `id` = {}'.format(self.task_id))
            self.mysql.update(table='task_scheduler_log',
                              columns=['reload_status', 'finished_at'],
                              values=['FinishedWithErrors', f'{datetime.datetime.now()}'],
                              filter=f'WHERE `reload_id` = {self.run_id}')
            # If the variable self.send_mail_after_errors is set to True, send an email with the number of errors to the given user
            if self.email_after_errors:
                self.email_errors(failed=False)
        else:
            self.mysql.update(table='task_scheduler',
                              columns=['status', 'last_reload', 'last_error_message', 'step_nr', 'stopped_by_user'] + field,
                              values=['IDLE', datetime.datetime.now(), 'FinishedSucces', 0, 0] + value,
                              filter='WHERE `id` = {}'.format(self.task_id))

            self.mysql.update(table='task_scheduler_log',
                              columns=['reload_status', 'finished_at'],
                              values=['FinishedSuccess', f'{datetime.datetime.now()}'],
                              filter=f'WHERE `reload_id` = {self.run_id}')

        # Remove the temp values from the variables table
        self.mysql.raw_query(f'UPDATE `task_variables` SET temp_value = null WHERE task_id = {self.task_id}', insert=True)

        # Start the new task if it there is a task which should start if this one is finished
        self.start_chained_tasks(finished_task_status='SUCCESS')

        # Clean up execution log
        self.mysql.delete("task_execution_log",
                          f"WHERE task_id = {self.task_id} AND reload_id NOT IN (SELECT reload_id FROM (SELECT reload_id FROM `task_execution_log` WHERE task_id = {self.task_id} AND log_level != 'CRITICAL' ORDER BY created_at DESC LIMIT 10000) temp)")

    def start_chained_tasks(self, finished_task_status: str):
        filter = f'WHERE start_after_task_id = \'{self.task_id}\' AND start_after_preceding_task = \'{finished_task_status}\''
        response = self.mysql.select(table='task_scheduler', selection='id', filter=filter)
        if len(response) > 0:
            tasks_to_run = [str(task[0]) for task in response]
            self.mysql.update(table='task_scheduler', columns=['run_instant'], values=['1'], filter=f'WHERE id IN({",".join(tasks_to_run)})')

    def email_errors(self, failed):
        # The mails to email to should be stored in the task_variables table with the variable email_errors_to
        email_variable = self.db_variable('email_errors_to')
        if email_variable is not None:
            email_to = email_variable.split(',')
            if isinstance(email_to, list):
                # The email_errors_to variable is a simple string. Convert it to a list and add a name because mandrill is asking for it
                email_list = []
                for i in email_to:
                    email_list.append({'name': 'SalureConnect User', 'mail': i.strip()})
                # Set the content of the mail and all other stuff
                email_from = 'connect@salure.nl'
                name_from = 'SalureConnect'
                task = self.mysql.select(table='task_scheduler', selection='title', filter=f'WHERE id = {self.task_id}')[0][
                    0]
                finished_at = \
                self.mysql.select(table='task_scheduler', selection='last_reload', filter=f'WHERE id = {self.task_id}')[0][
                    0]
                if failed:
                    subject = f'Task \'{task}\' has failed'
                    content = f'Task \'{task}\' with task ID \'{self.task_id}\' failed during its last run and was stopped at {finished_at}. ' \
                              f'The task is failed. ' \
                              f'to visit the SalureConnect scheduler, click here: <a href="https://salureconnect.com/connectors/task-scheduler/">here</a>. Here you can find the logs and find more information on why this task had failed.'
                else:
                    subject = f'Task \'{task}\' is finished with errors'
                    content = f'Task \'{task}\' with ID \'{self.task_id}\' has runned and is finished at {finished_at}. ' \
                              f'The task is finished with {self.error_count} errors. ' \
                              f'to visit the SalureConnect scheduler, click here: <a href="https://salureconnect.com/connectors/task-scheduler/">here</a>. Here you can find the logs and find more information on why this task had some errors.'
                MailClient().send_mail(api_token=self.mandrill_api_token, email_to=email_list, email_from=email_from,
                                       name_from=name_from, subject=subject, content=content, language='EN')
