import time
from datetime import datetime, timedelta, date
from os.path import dirname, basename, isfile, join
import glob
import importlib
import traceback
import sys
import threading
import holidays
import os


from soteria.handlers.db import db
from soteria.handlers.logging import Log
from soteria.handlers.jira import jira
from soteria.module import Module
from soteria.handlers.comms import Comms
from soteria.handlers.scheduler import should_job_run_now
from config import teams_url, run_length, rerun_failed_jobs
try:
    from jobs import *
except Exception as e:
    comms = Comms(env='live', teams_url=teams_url)
    comms.post_message('General', traceback.format_exc())
    sys.exit('unable to import modules')


class SoteriaScheduler:

    def __init__(self, env='test', run_once=False) -> None:
        self.db = db()
        self.env = env
        self.run_once = run_once

        self.comms = Comms(env=self.env,
                           teams_url=teams_url,
                           add_urls='')

        self.jira = jira()

        self.logger = Log()

    def start_scheduler(self):

        # if config set to re-run failed jobs
        if rerun_failed_jobs:
            failed_jobs = self.db.get_failed_jobs()
            for job in failed_jobs:
                self.db.add_to_queue(job)

        try:
            t_end = time.time() + run_length
            while time.time() < t_end:
                self.load_jobs()

                self.update_queue()

                self.run_queue()

                self.db.clear_logs()

                if self.run_once:
                    break

        except KeyboardInterrupt:
            print('Force Closing')

            self.db.clear_queue()
            self.db.set_jobs_to_not_running()

    def run_queue(self):
        """Loops through backlog, running each job"""

        queue = list(set(self.db.get_queue()))

        for job_name in queue:
            # thread = threading.Thread(
            #     target=self.run_job, args=(job_name), kwargs={})
            # thread.start()
            self.run_job(job_name)

    def update_queue(self):

        existing_jobs = self.db.get_jobs_info()

        for job_name in self.jobs:
            job_record = [
                j for j in existing_jobs if j['job_name'] == job_name][0]

            if type(job_record['last_run']) == str:
                last_run = datetime.strptime(
                    job_record['last_run'], '%Y-%m-%d %H:%M:%S')
            else:
                last_run = None

            if should_job_run_now(last_run=last_run, schedule=job_record['schedule']) and self.allowed_to_run(self.jobs[job_name]):
                    self.db.add_to_queue(job_name)

    def run_job(self, job_name):
        """"""
        self.logger.log(f'running: {job_name}')
        
        self.db.update_job_status(job_name=job_name, running=True)

        start_time = time.time()
        try:
            job = globals()[job_name].Job()
        except:
            # Test failed to load
            print(traceback.format_exc())

        try:
            response = job.__run__()
        except:
            # Test failed to run
            print(traceback.format_exc())
            formatted_error = traceback.format_exc(
            ).splitlines()[-1] + "."

            response = {
                'message': f"Test failed to run successfully - { formatted_error }",
                'result': 'error',
            }

        self.action_on_result(
            job_name, result=response['result'], message=response['message'], job=job)

        self.db.update_result(job_name=job_name,
                              result=response['result'],
                              message=response['message'],
                              run_time=int(time.time() - start_time))

        self.db.delete_from_queue(job_name)
        self.db.update_job_status(job_name=job_name, running=False)

    def load_jobs(self):
        """Find all jobs"""

        self.jobs = {}
        file_names = []

        for (dirpath, dirnames, filenames) in os.walk('jobs'):
            # file_names += [os.path.join(dirpath, file) for file in filenames if '.py' in file]
            # print(filenames)
            for file_name in filenames:
                if '.py' in file_name and '.pyc' not in file_name:
                    file_names.append(file_name)
        
        for f in file_names:
            if not '__init__.py' in f:
                self.jobs[basename(f)[:-3]] = globals()[basename(f)[:-3]].Job()

        existing_jobs = self.db.get_jobs_info()
        existing_job_names = [job['job_name'] for job in existing_jobs]

        # add new jobs
        for job_name in self.jobs:
            job = self.jobs[job_name]

            if job_name not in existing_job_names:  # add any new jobs into
                try:
                    self.db.add_job(job_name=job_name,
                                    status=job.setting_enabled,
                                    schedule='n/a')
                except KeyError:
                    # Issue with getting file contents
                    self.db.add_job(job_name=job_name,
                                    status=False,
                                    schedule=job.setting_schedule)
                    self.db.update_job_status(job_name=job_name,
                                              status='error')

            else:
                job = globals()[job_name].Job()
                self.db.job_refresh(job_name=job_name,
                                    status=job.setting_enabled,
                                    schedule=job.setting_schedule)

                # reload job
                try:
                    importlib.reload(globals()[job_name])
                except:
                    # Test failed to complete
                    formatted_error = traceback.format_exc(
                    ).splitlines()[-1] + "."
                    self.db.update_result(
                        job_name=job_name, result='error', message=f'Failed to import. {formatted_error}')

        # delete older jobs
        [self.db.delete_job(job['job_name'])
         for job in existing_jobs if job['job_name'] not in self.jobs]

    def get_jobs_settings(self, job='*'):
        """Returns all the settings for each module"""

        self.load_jobs()

        job_settings = {}
        defaults = self.get_default_variables()

        if job == '*':
            jobs = self.jobs
        else:
            jobs = [job]

        # where a setting has been updated, use that instead of default
        for job_name in jobs:

            current_settings = defaults.copy()
            manual_settings = globals()[job_name].Job().__dict__

            override_settings = {}

            for key in manual_settings:
                override_settings[key.replace(
                    'setting_', '')] = manual_settings[key]

            for setting in current_settings:
                if setting in override_settings:
                    current_settings[setting] = override_settings[setting]

            job_settings[job_name] = current_settings
        return job_settings[job]

    def get_default_variables(self, clean_settings=True):

        defaults = {}
        # grab default settings
        for setting in Module.__dict__:
            if 'setting_' in setting:
                if clean_settings:
                    defaults[setting.replace('setting_', '')] = Module.__dict__[
                        setting]
                else:
                    defaults[setting] = Module.__dict__[
                        setting]
        return defaults

    def get_job_variables(self, job_name):

        secret_values = ['password', 'secret', 'passwd',
                         'authorization', 'api_key', 'apikey', 'access_token', 'username']

        all_variables = globals()[job_name].Job().__dict__

        job_variables = {}
        defaults = self.get_default_variables()

        for setting in all_variables:

            if setting.replace('setting_', '') not in defaults:
                for value in secret_values:
                    job_variables[setting] = all_variables[setting]
                    if value in setting or value in str(all_variables[setting]):
                        job_variables[str(setting)] = '******'
                        break

        return job_variables

    def action_on_result(self, job_name=None, result=None, message=None, job=None):
        """Identifies what to do with the result from the test, acting accordingly."""

        last_result = self.db.get_last_result(job_name)

        if result == 'error':
            result = 'failed'
        if last_result == 'n/a':
            last_result = 'passed'

        if not last_result:
            last_result = 'passed'
        if last_result == 'error':
            last_result = 'failed'
        
        

        # PASSED ACTIONS
        if result == 'passed':
            if last_result == 'failed' and job.setting_teams_alerts:
                message = 'Issue has been resolved.'
                self.comms.post_message(job_name, message)

        # FAILED ACTIONS
        elif result == 'failed':
            if last_result == 'passed':
                if job.setting_teams_alerts:
                    self.comms.post_message(job_name, message)
                if job.setting_raise_tickets:
                    self.jira.raise_ticket(job_name, message)
            if last_result == 'failed' and job.setting_teams_alerts:
                # message has changed
                if message != self.db.get_last_message(job_name) and job.setting_teams_alerts:
                    self.comms.post_message(job_name, message)

    def allowed_to_run(self, job=None):

        dayLookup = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5, "Sunday": 6}
        now = str( datetime.now().time() )
        # Enabled

        if not job.setting_enabled:
            # self.logger.log(f'Job is not enabled')
            return False

        # Bank Holiday Check
        if date.today() in holidays.England() and not job.setting_bank_holidays:
            self.logger.log(f'Job not allowed to run on a bank holiday.')
            return False

        # Time Check
        if now < job.setting_start_time or now > job.setting_end_time:
            self.logger.log(f'Job set to run between {job.setting_start_time} and {job.setting_end_time}.')
            return False

        # Day Check
        for day in job.setting_exception_days:
            if date.today().weekday() == dayLookup[day]:
                self.logger.log(f'Job not set to run on {day}.')
                return False
        
        return True
        

if __name__ == "__main__":

    scheduler = SoteriaScheduler()
    print('starting')
    scheduler.load_jobs()
    # print(scheduler.get_jobs_settings())
