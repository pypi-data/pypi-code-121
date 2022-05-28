import datetime
from crontab import CronTab, CronItem
from LinuxServerStatsTelegramBot.commmand.Command import Command
import json


class CronStats(Command):
    def execute(self) -> str:
        crons = CronTab(user=True)
        cron_messages = []
        for job in crons:
            job_obj: CronItem = job
            if job_obj.is_enabled():
                sched_text = f"{str(job_obj.minute)} {str(job_obj.hour)} {str(job_obj.dom)} {str(job_obj.month)} {str(job_obj.dow)}"
                schedule = job.schedule(date_from=datetime.datetime.now())
                cron_messages.append(
                    f"Cron: {job_obj.comment} [{sched_text}] was executed at: {schedule.get_prev()} and the next execution will be {schedule.get_next()}"
                )
        return json.dumps(cron_messages, indent=4, sort_keys=True)
