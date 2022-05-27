import sqlite3
from datetime import datetime
from contextlib import closing
import os
import yaml
import base64
import ast

from config import logs_persistence, db_location


class db:

    def __init__(self, startup=False, env='live'):

        self.env = env

        # check if db already exists
        try:
            self.run_query("SELECT * FROM log")
            if startup:
                print('db: connected to existing')
        except sqlite3.OperationalError:
            if startup:
                print('db: not set up, creating now')
            self.build_db()

    def run_query(self, query, params=[], return_dict=False, return_columns=False):
        if self.env == 'live':
            connection = sqlite3.connect(f"{db_location}\log.db")
        else:
            connection = sqlite3.connect(f"{db_location}\log_test.db")
        cursor = connection.cursor()
        rows = cursor.execute(query, params).fetchall()

        if return_dict:
            to_return = []
            columns = [description[0]
                       for description in cursor.description]

            for row in rows:
                new_row = {}
                for count, cell in enumerate(row):
                    new_row[columns[count]] = cell
                to_return.append(new_row)
        elif return_columns:
            return {
                'columns': [description[0]
                            for description in cursor.description],
                'rows': rows
            }
        else:
            to_return = rows

        connection.commit()

        return to_return

    def build_db(self):

        self.run_query(
            "CREATE TABLE log(session_id INTEGER, job_name TEXT, message TEXT, time_logged TEXT)")

        self.run_query(
            "CREATE TABLE results(id INTEGER, job_name TEXT, message TEXT, result TEXT, time_logged TEXT)")

        self.run_query(
            "CREATE TABLE comms(id INTEGER, job_name TEXT, time_logged TEXT)")

        self.run_query(
            "CREATE TABLE queue(job_name TEXT)")

        self.run_query(
            "CREATE TABLE jobs(job_name TEXT, schedule REAL, last_run DATETIME, run_time INTEGER, last_result TEXT, last_message TEXT, running_now TEXT, active TEXT)")

        self.run_query(
            "CREATE TABLE job_history(job_name TEXT, run_completed DATETIME, run_time INTEGER, result TEST, message TEXT)")

    # JOBS

    def get_jobs_info(self, date_type='utc'):
        """Retrives the last message recorded for the job"""

        if date_type.lower() == 'utc':
            query = """SELECT j.job_name,
                    j.schedule,
                    last_run,
                    time(j.run_time, 'unixepoch') [run_time],
                    j.last_result,
                    j.last_message,
                    CASE (j.running_now) WHEN 0 THEN "no" ELSE "yes" END [running_now],
                    CASE (j.active) WHEN 0 THEN "no" ELSE "yes" END [active],
                    CASE (COUNT(q.job_name)) WHEN 0 THEN "no" ELSE "yes" END [in_queue]
                    FROM jobs j
                    LEFT JOIN queue q ON q.job_name=j.job_name
                    GROUP BY j.job_name, j.last_run, j.last_result, j.running_now, j.active """
        elif date_type.lower() == 'local':
            query = """SELECT j.job_name,
                    j.schedule,
                    datetime(last_run, 'localtime') [last_run],
                    time(j.run_time, 'unixepoch') [run_time],
                    j.last_result,
                    j.last_message,
                    CASE (j.running_now) WHEN 0 THEN "no" ELSE "yes" END [running_now],
                    CASE (j.active) WHEN 0 THEN "no" ELSE "yes" END [active],
                    CASE (COUNT(q.job_name)) WHEN 0 THEN "no" ELSE "yes" END [in_queue]
                    FROM jobs j
                    LEFT JOIN queue q ON q.job_name=j.job_name
                    GROUP BY j.job_name, j.last_run, j.last_result, j.running_now, j.active """

        results = self.run_query(query, return_dict=True)

        return results

    def get_job_history(self, job_name):

        query = f"""SELECT job_name,
                           datetime(run_completed, 'localtime') [run_completed],
                           time(run_time, 'unixepoch') [run_time],
                           result,
                           message
                FROM job_history
                WHERE job_name=?
                ORDER BY run_completed DESC"""

        return self.run_query(query, params=[job_name], return_dict=True)

    def add_job(self, job_name=None, status=False, schedule=None, run_time=0):
        print(f'ADDING JOB - {job_name}')

        query = f"INSERT INTO jobs VALUES(?, ?, NULL, ?, 'n/a', 'n/a', ?, ?)"

        self.run_query(
            query, params=[job_name, schedule, run_time, False, status])

    def delete_job(self, job_name=None):
        print(f'REMOVING JOB - {job_name}')

        query = f"DELETE FROM jobs WHERE job_name=?"

        self.run_query(query, params=[job_name])

        query = f"DELETE FROM job_history WHERE job_name=?"

        self.run_query(query, params=[job_name])

    def update_job_status(self, job_name=None, running=False):

        query = f"UPDATE jobs SET running_now=? WHERE job_name=?"

        self.run_query(query, params=[running, job_name])

    def set_jobs_to_not_running(self):
        query = f"UPDATE jobs SET running_now={False}"

        self.run_query(query)

    def update_result(self, job_name=None, result=False, schedule='n/a', message='n/a', run_time=0):

        if run_time == 0:
            run_time = 1

        query = f"UPDATE jobs SET last_result='{result}', last_message= ?, last_run=DATETIME(), run_time={run_time} WHERE job_name='{job_name}'"

        self.run_query(query,  params=(message,))

        query = f"INSERT INTO job_history VALUES ('{job_name}', DATETIME(), {run_time}, '{result}', ?)"

        self.run_query(query,  params=(message,))

    def job_refresh(self, job_name=None, status='', schedule=''):
        query = f"""UPDATE jobs
                    SET active=?,
                        schedule=?
                    WHERE job_name=?"""

        self.run_query(
            query, params=[status, str(schedule), job_name])

    def add_to_queue(self, job_name):

        query = f"INSERT INTO queue VALUES('{job_name}')"

        self.run_query(query)

    # QUEUE

    def get_queue(self):

        query = f"SELECT * FROM queue"

        jobs = [job[0] for job in self.run_query(query)]

        return jobs

    def get_jobs_in_queue(self):

        query = f"""SELECT * FROM queue q
                    LEFT JOIN jobs j ON j.job_name=q.job_name"""

        return self.run_query(query)

    def delete_from_queue(self, job_name=None):
        if job_name == '*':
            query = f"DELETE FROM queue"
        else:
            query = f"DELETE FROM queue WHERE job_name='{job_name}'"

        self.run_query(query)

    def clear_queue(self):
        query = f"DELETE FROM queue"

        self.run_query(query)

    def update_queue(self):

        query = f"SELECT job_name FROM jobs where (next_run<DATETIME() or next_run IS NULL or last_run IS NULL) and active=1"

        jobs = [job[0] for job in self.run_query(query)]

        for job in jobs:
            query = f"INSERT INTO queue VALUES (?)"
            self.run_query(query, params=[job])

    def get_last_run(self, job_name):

        query = f"SELECT last_run FROM jobs where job_name=?"

        last_run = self.run_query(query, params=[job_name], return_dict=True)[
            0]['last_run']

        if last_run == None:
            return None
        else:
            return datetime.strptime(last_run, '%Y-%m-%d %H:%M:%S')

    def get_last_result(self, job_name):

        query = f"SELECT last_result FROM jobs where job_name='{job_name}'"

        return self.run_query(query, return_dict=True)[0]['last_result']

    def get_last_message(self, job_name):

        query = f"SELECT last_message FROM jobs where job_name='{job_name}'"

        return self.run_query(query, return_dict=True)[0]['last_message']

    def clear_logs(self):

        query = f"DELETE FROM job_history WHERE run_completed < datetime('now', '-{str(logs_persistence)} Hour')"

        self.run_query(query)

    def get_failed_jobs(self, provide_message=False):

        if provide_message:
            query = f"SELECT job_name, last_message FROM jobs where last_result IN ('failed', 'error')"

            result = self.run_query(query, return_dict=True)

            return result
        else:

            query = f"SELECT job_name FROM jobs where last_result IN ('failed', 'error')"
            result = self.run_query(query, return_dict=True)

            return [job['job_name'] for job in result]

        return True

    def get_soteria_last_run(self):

        query = f"SELECT last_run FROM jobs ORDER BY last_run DESC LIMIT 1"

        result = self.run_query(query)[0][0]

        return result


if __name__ == "__main__":

    database = db()

    jobs = database.get_failed_jobs()

    print(jobs)
