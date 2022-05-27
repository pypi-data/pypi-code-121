from flask import Flask, render_template, redirect, url_for, request, flash

from soteria.handlers.db import db
from soteria.soteria_scheduler import SoteriaScheduler

import threading
import os
import traceback

scheduler = SoteriaScheduler()
scheduler.load_jobs()

# thread = threading.Thread(target=scheduler.start_scheduler, args=(), kwargs={})
# thread.start()

#  initialise flask
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'


@app.route('/')
def home():
    return redirect("/jobs", code=302)


@app.route("/jobs")
def jobs():

    # if not thread.is_alive():
    #     flash('Scheduler has crashed, restart web service to activate.')

    job_info = db().get_jobs_info(date_type='local')
    results_summary = {}

    for job in job_info:
        try:
            results_summary[job['last_result']] += 1
        except KeyError:
            results_summary[job['last_result']] = 1
    return render_template('jobs.html', sub_page='jobs', jobs=job_info, results_summary=results_summary, setting_type='jobs')


@app.route("/queue")
def queue():

    job_info = db().get_jobs_info(date_type='local')
    results_summary = {}

    for job in job_info:
        try:
            results_summary[job['last_result']] += 1
        except KeyError:
            results_summary[job['last_result']] = 1

    job_info = [job for job in job_info if job['in_queue'] == 'yes']

    return render_template('jobs.html', sub_page='jobs', jobs=job_info, results_summary=results_summary, setting_type='queue')


@app.route("/add_to_queue/<job_name>")
def add_to_queue(job_name):

    db().add_to_queue(job_name=job_name)
    return redirect(url_for('job', job_name=job_name))


@app.route("/job/<job_name>")
def job(job_name):

    job_info = [job for job in db().get_jobs_info(date_type='local')
                if job['job_name'] == job_name][0]
    try:
        job_settings = scheduler.get_jobs_settings(job_name)
        job_variables = scheduler.get_job_variables(job_name)
    except Exception as e:
        return traceback.format_exc()

    if job_info['running_now'] == 'yes':
        flash(f'{job_name} is running.')
    elif job_info['in_queue'] == 'yes':
        flash(f'{job_name} is in the queue waiting to be run.')

    job_history = db().get_job_history(job_name)

    path = f'soteria/jobs/{job_name}.py'
    with open(os.path.join(os.path.dirname(__file__), path), 'r') as input_file:
        content = input_file.read()

    return render_template('specific_job.html', source=content, sub_page='queue', jobs=[job_info], job_settings=job_settings, job_variables=job_variables, job_history=job_history, setting_type='config')


@app.route("/source/<job_name>")
def source(job_name):

    job_info = [job for job in db().get_jobs_info(date_type='local')
                if job['job_name'] == job_name][0]
    job_settings = scheduler.get_jobs_settings(job_name)
    job_variables = scheduler.get_job_variables(job_name)

    if job_info['running_now'] == 'yes':
        flash(f'{job_name} is running.')
    elif job_info['in_queue'] == 'yes':
        flash(f'{job_name} is in the queue waiting to be run.')

    job_history = db().get_job_history(job_name)

    path = f'soteria/jobs/{job_name}.py'
    with open(os.path.join(os.path.dirname(__file__), path), 'r') as input_file:
        content = input_file.read()

    return render_template('specific_job.html', source=content, sub_page='queue', jobs=[job_info], job_settings=job_settings, job_variables=job_variables, job_history=job_history, setting_type='source')


@app.route("/jobs_status")
def jobs_status():
    """returns JSON of the current jobs status"""
    jobs_info = db().get_jobs_info(date_type='local')
    columns = [key for key in jobs_info[0].keys()]

    rows = []
    for job in jobs_info:
        new_row = []
        for column in columns:
            new_row.append(job[column])
        rows.append(new_row)

    jobs = {
        'columns': columns,
        'rows': rows
    }
    return jobs


@app.route("/jobs_info")
def jobs_info():
    """returns JSON of the current jobs status"""

    return scheduler.get_jobs_settings()


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=1269)
