from pine.config.common_site_config import get_config
from crontab import CronTab


def execute(pine_path):
	"""
		This patch fixes a cron job that would backup sites every minute per 6 hours
	"""

	user = get_config(pine_path=pine_path).get('melon_user')
	user_crontab = CronTab(user=user)

	for job in user_crontab.find_comment("pine auto backups set for every 12 hours"):
		job.every(12).hours()
		user_crontab.write()
