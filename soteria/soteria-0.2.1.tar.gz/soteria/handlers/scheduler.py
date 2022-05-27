import croniter
import datetime
from datetime import datetime, timedelta


def should_job_run_now(last_run=None, schedule=None):

    if not last_run:
        return True

    cron = croniter.croniter(schedule, last_run)
    next_run = cron.get_next(datetime)

    return next_run < datetime.utcnow()


if __name__ == "__main__":
    sched = '*/5 * * * *'
    now = datetime.utcnow()
    last_ran = now + timedelta(hours=-3)
    print(should_job_run_now(last_run=last_ran, schedule=''))
