# Module for finger.farm publishing function

import subprocess
import sys
import requests


def publish(config):
    """Get API key and publish data"""
    if not config.options.push:
        return

    retval = subprocess.run(config.apikey.cmd, shell=True,
                            capture_output=True)
    retcode = retval.returncode
    if retcode == 0:
        config.apikey.token = retval.stdout.decode('utf-8')
    else:
        print('ERROR: Token command returned non-zero status'
              f' ({retcode})', file=sys.stderr)
        print(retval.stderr.decode('utf-8'), file=sys.stderr)
        sys.exit(1)

    def push(config, reqtype):
        forobj = config.__dict__[reqtype]
        text = forobj.content.new
        if forobj.content.mod or config.options.skip_check:
            data = {'token': config.apikey.token,
                    'data': text}
            url = f'https://finger.farm/api/{config.user}/{reqtype}'
            with requests.put(url, data=data) as resp:
                if resp.ok:
                    print(f'INFO: Published {reqtype} successfully!',
                          file=sys.stderr)
                else:
                    print(f'ERROR: Push of {reqtype} failed!',
                          file=sys.stderr)
                print('DEBUG: Response: '
                      f'{resp.status_code} ({resp.reason})',
                      file=sys.stderr)
        else:
            print(f'WARNING: Content of {reqtype} is unchanged.'
                  ' Skipping publishing!', file=sys.stderr)
            print('TIP: Use --skip-check to force push.',
                  file=sys.stderr)

    push(config, 'plan')
    push(config, 'project')
        
