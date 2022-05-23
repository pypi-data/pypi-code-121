import subprocess, os, psutil, logging, json, argparse, time, re

from logging.handlers import TimedRotatingFileHandler
from screenutils import list_screens, Screen

from alphaz.models.config import AlphaConfig

import requests

LOG = None

def error(message,quit=False):
    if message is None or message.strip() == "":
        if quit:
            exit()
        return
    global LOG
    print("ERROR: %s"%message)
    if LOG is not None:
        LOG.error(message)
    if quit:
        exit()

def info(message, end="\n"):
    if message is None or message.strip() == "":
        return
    global LOG
    print("INFO: %s"%message,end=end)
    if LOG is not None:
        LOG.info(message)

def get_cmd_output(cmd):
    result = subprocess.check_output(cmd, shell=True)
    lines = str(result).split("\\n")
    i = 0
    output_lines = []
    for line in lines:
        line = line.replace("\\t", "    ").replace("\\r", "")
        output_lines.append(line)
        i += 1
    return output_lines

def replace_envs(text):
    if type(text) != str:
       return text
    envs = re.findall(r"\$[_a-zA-Z]+",text)
    for env in envs:
        if env[1:] in os.environ:
            text = text.replace(env, os.environ[env[1:]].strip())
    return text

def log_config():
    global LOG
    
    LOG = logging.getLogger(log_file.split(os.sep)[-1].split(".")[0])
    LOG.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    log_handler = TimedRotatingFileHandler(log_file, when="midnight", backupCount=30)
    log_handler.setFormatter(formatter)
    LOG.addHandler(log_handler)
    
def check_screen(screen, single=False):
    restarted = False
    info(screen["check_message"])
    info("Fetching %s"%screen["request"])
    time.sleep(screen["sleep"])
    
    times = screen["retries"] if not single else 1
    for i in range(times):
        if restarted:
            continue
        try:
            print('         ' + '.'*(times - i))
            r = requests.get(screen["request"], timeout=screen["timeout"])
            if "success" in str(r.content):
                info(screen["success_message"])
                restarted = True
                continue
        except Exception as ex:
            time.sleep(screen["sleep"])
    if not restarted:
        error(screen["failed_message"])
    return restarted

def launch_cmd(screen, s=None):
    if s is None:
        s = Screen(screen["name"],True)
    s.enable_logs()
    s.send_commands("cd %s"%screen["dir"])
    s.send_commands(screen["shell_cmd"])
    s.detach()
    
    info("Screen %s restarted" % screen["name"])
    if "request" in screen and screen["request"]:
        restarted = check_screen(screen)

    print(next(s.logs))
    s.disable_logs()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ensure that a screen is running")

    parser.add_argument("--log", "-l", help="log file path")
    parser.add_argument("--file", "-f", help="Input configuration file")
    
    parser.add_argument("--name", "-n", help="Screen name")
    parser.add_argument("--cmd", "-c", help="Command to run")
    
    parser.add_argument("--envs", "-e", nargs="+", default=[], help="Command to run")
    
    parser.add_argument("--directory", "-d", help="Working directory")
    parser.add_argument("--request", "-req", help="Request to check the response")
    parser.add_argument("--retries", "-ret", type=int, default=10, help="Number of check before fail state")
    parser.add_argument("--sleep", "-s", type=int, default=3, help="Sleep time (s)")
    parser.add_argument("--timeout", "-t", type=int, default=10, help="Sleep time (s)")
    
    parser.add_argument("--message", "-m", help="Check message")
    parser.add_argument("--failed_message", "-fm", help="Failed message")
    parser.add_argument("--success_message", "-sm", help="Success message")
    
    parser.add_argument("--restart", "-r",action="store_true", help="Force a restart")

    args = parser.parse_args()

    log_file = args.log
    
    defaults = {
        "active": True,
        "name": args.name,
        "dir": args.directory if args.directory else os.getcwd(),
        "request": None if not args.request else args.request,
        "sleep": args.sleep,
        "retries": args.retries,
        "timeout": args.timeout,
        "restart": args.restart,
        "check_message": "" if not args.message else args.message,
        "failed_message": "Failed" if not args.failed_message else args.failed_message,
        "success_message": "Success" if not args.success_message else args.success_message,
    }
    
    for env in args.envs:
        envs_p = re.findall(r'^(\w+)="?([^"]+)"?', env)
        if len(envs_p) != 1:
            error("<%s> environment variable is not weel defined, it must be like this: var=value")
            exit()
        name, value = envs_p[0][0], envs_p[0][1]
        info("Set environment variable <%s> to <%s>"%(name, value))
        os.environ[name] = value

    if args.file:
        file_path = args.file
        if not ".json" in file_path:
            file_path = file_path + ".json"
        if not os.path.exists(file_path):
            error("Configuration file does not exist: %s"%file_path, quit=True)
        config = AlphaConfig(filepath=file_path)
        screens = config.get("screens")
        if screens is None:
            error("Missing entry <screens> in configuration file %s"%file_path, quit=True)
        if type(screens) != dict:
            error("<screens> entry in configuration file %s is not valid"%file_path, quit=True)
        if not "configurations" in screens:
            error("No <configurations> entry <screens> entry in configuration file %s"%file_path, quit=True)
        if type(screens["configurations"]) != dict:
            error("<screens> entry in configuration file %s is not valid"%file_path, quit=True)
        screens_dict = screens["configurations"]
    elif args.name and args.cmd:
        screens_dict = {args.name: defaults}
    else:
        error("You need to specify a configuration file or at least a screen name (--name) and a command (--cmd)")
        exit()

    screens_list = list_screens()
        
    for name, screen in screens_dict.items():
        screen = {x:replace_envs(y) for x,y in screen.items()}
        active = screen["active"]
        screen_name = screen["name"]
        
        if not active:
            info("Screen configuration <%s> is DISABLED"%screen_name)
            continue
            
        
        for key, value in defaults.items():
            if not key in screen or screen is None:
                screen[key] = value
                info("Set default key <%s> to <%s>"%(key, value))
        
        info("Processing screen configuration <%s>"%screen_name)
        
        screen_exist_list = [x for x in screens_list if x.name == screen_name]
        if len(screen_exist_list) != 0:
            for screen_entity in screen_exist_list:
                info("Screen %s %s is running ..." % (screen_entity.id, screen_entity.name))
                if screen["restart"]:
                    screen_entity.kill()
                    info("Screen %s %s killed !" % (screen_entity.id, screen_entity.name))
                
                if "request" in screen and screen["request"]:
                    restarted = check_screen(screen, single=True)
                    if not restarted or screen["restart"]:
                        launch_cmd(screen)
        
        elif len(screen_exist_list) == 0 or screen["restart"]:
            launch_cmd(screen)