from pine.config.common_site_config import update_config


def execute(pine_path):
	update_config({'live_reload': True}, pine_path)
