import os

def parse_bool_env(env_name: str, default: bool):
    value = os.getenv(env_name, str(default)).lower()
    if value in ["true"]:
        return True
    else:
        return False
