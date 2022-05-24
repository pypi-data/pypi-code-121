import requests
from . import logger
from . import cfg

log = logger.logger


def _test_gitlab_auth_token(token):
    try:
        r = requests.get("https://gitlab.com/api/v4/personal_access_tokens", headers={'PRIVATE-TOKEN': f'{token}'})
        log.debug('Gitlab authentication succeeded')
        return r.ok
    except Exception as e:
        log.error(e)
        return False


def _new_auth_setup():
    # Ask if user wants to setup auth now
    auth_now_answer = input(f"Do you want to (re)authenticate now? (y/n) ") or "n"
    if auth_now_answer.lower() == 'y':
        log.info('Go to https://gitlab.com/-/profile/personal_access_tokens and generate a new access token (api, read_user, read_repository, write_repository)')
        entered_access_token = None
        while not entered_access_token:
            entered_access_token = input(f"Enter the Gitlab Access Token: ") or None
            if not entered_access_token:
                log.error('Not a valid token. Please try again')
            elif not _test_gitlab_auth_token(entered_access_token):
                log.error('Gitlab authentication failed, did you enter the correct token?')
                entered_access_token = None
            else:
                cfg.write_default_config(entered_access_token)
                return entered_access_token
    else:
        log.info('Ok. To setup authentication manually, follow these steps:\n'
            + '  1. Go to https://gitlab.com/-/profile/personal_access_tokens and generate a new access token (api, read_user, read_repository, write_repository)\n'
            +f'  2. Create a `{cfg.RC_FILE_NAME}` in your home directory (`~/{cfg.RC_FILE_NAME}`) with the following contents:\n'
            + '     [auth]\n'
            + '     gitlab_access_token = YOUR_GITLAB_ACCESS_TOKEN\n'
            + '  3. Re-run this script to try again'
        )
        exit(1)


def initial_auth_flow_if_necessary(gitlab_access_token=None):
    if not gitlab_access_token:
        log.error('Could not authenticate because no access token was specified or previously saved.')
        return _new_auth_setup()

    elif not _test_gitlab_auth_token(gitlab_access_token):
        log.error('Gitlab authentication failed')
        return _new_auth_setup()

    return gitlab_access_token