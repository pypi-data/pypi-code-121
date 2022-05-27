"""
Code for creating the dashboard libraries
"""

import json
import datetime
from mysql import MySQL
import config

class DashboardLib:
    def __init__(self, host, user, password, database, port=3306):
        self.host = host #These shall be the same for Taskscheduler class and also for the MySQL
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.mysql = MySQL(host=config.mysql['host'],
                           user=config.mysql['user'],
                           password=config.mysql['password'],
                           database=config.mysql['database'])

    def _parse_reload_time(self):
        """
        Config as:
        client = 'medux'
        task_reload= {
            "reload":{
                        "month":0,
                        "day":1,
                        "hour":0,
                        "minute":0
                        },
            "next_reload":"2022-02-18 20:00:00"
        }
        """
        if 'reload' in config.task_reload:
            reload = {
                        "month":0,
                        "day":1,
                        "hour":0,
                        "minute":0
                        }
        else:
            reload = config.task_reload['reload']

        if 'next_reload' in config.task_reload:
            next_reload = (datetime.datetime.now() + datetime.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
        else:
            next_reload = datetime.datetime.strptime(config.task_reload['next_reload'], '%Y-%m-%d %H:%M:%S')
        frequency = r"{"+f'"month":{reload["month"]},"day":{reload["day"]},"hour":{reload["hour"]},"minute":{reload["minute"]}' + r"}"  #{"month":0,"day":1,"hour":0,"minute":0}
        frequency = self._string_decor(frequency)
        next_reload = self._string_decor(next_reload)
        return frequency, next_reload

    def _string_decor(self,str):
        return f"'{str}'"

    def _generate_query(self):
        title = self._string_decor(config.task_reload['title'])
        client = config.client
        description = self._string_decor(config.task_reload['description']) if 'description' in config.task_reload else 'null'
        docker_image = self._string_decor(config.task_reload['docker_image'])
        runfile_path = self._string_decor(config.task_reload['runfile_path'])
        frequency, next_reload = self._parse_reload_time()
        last_reload = 'null'
        last_error_message = 'null'
        status = 'DEFAULT'
        disabled = self._string_decor(config.task_reload['disabled']) if 'disabled' in config.task_reload else 'DEFAULT'
        run_instant = 'DEFAULT'
        sftp_mapping = self._string_decor(config.task_reload['sftp_mapping']) if 'sftp_mapping' in config.task_reload else 'DEFAULT'
        step_nr = 'DEFAULT'
        timezone = self._string_decor(config.task_reload['timezone']) if 'timezone' in config.task_reload else r"'Europe/Amsterdam'"
        stopped_by_user = 'DEFAULT'
        stop_is_allowed = self._string_decor(config.task_reload['stop_is_allowed']) if 'stop_is_allowed' in config.task_reload else '0'
        query = f"INSERT INTO sc_{client}.task_scheduler " \
                f"(title, description, docker_image, runfile_path, next_reload, frequency, last_reload, last_error_message, status, disabled, run_instant, sftp_mapping, step_nr, timezone, stopped_by_user, stop_is_allowed) " \
                f"VALUES ({title}, {description}, {docker_image}, {runfile_path}, {next_reload}, {frequency}, {last_reload}, {last_error_message}, {status}, {disabled}, {run_instant}, {sftp_mapping}, {step_nr}, {timezone}, {stopped_by_user}, {stop_is_allowed});"

        return query

    def set_up_task_scheduler(self):
        query = self._generate_query()
        self.mysql.raw_query(query=query, insert=True)

dl = DashboardLib(config.mysql['host'], config.mysql['user'], config.mysql['password'], config.mysql['database'])
dl.set_up_task_scheduler()