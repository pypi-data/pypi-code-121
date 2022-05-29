import json
import os
import humanize
import time

# construct a function that loads my openai API key from home and then calls it
def load_config():
    config_path = os.path.join(os.path.expanduser('~'), 'dt_config.json')
    config = json.loads(open(config_path).read())   
    return config


def show_config():
    config = load_config()
    
    for k in config.keys():
        # specific printing for snippets
        if isinstance(config[k], list):
            print(f"{k}")
            for s in config[k]:
                # gets original stringified time and converts into timedelta from now
                orig_timestamp = time.strptime(s[1], '%Y-%m-%d %H-%M-%S')
                delta = humanize.naturaltime(time.time() - time.mktime(orig_timestamp))
                print(f" {s[0]} ({delta}): \n  {s[2]}")   
        else:
            print(f"{k}: \n {config[k]}")

