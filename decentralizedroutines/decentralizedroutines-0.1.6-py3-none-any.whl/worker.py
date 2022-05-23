# implements a decentralized routines worker 
# connects to worker pool
# broadcast heartbeat
# listen to commands


from cProfile import run
import os,sys,psutil,time,json,boto3,subprocess
from importlib.metadata import version

import numpy as np
from numpy import require
from multiprocessing.pool import ThreadPool

from concurrent.futures import process, thread
from pathlib import Path

from SharedData.Logger import Logger
logger = Logger(r'decentralizedroutines\worker',user='worker')

from SharedData.SharedDataAWSKinesis import KinesisStreamConsumer,KinesisStreamProducer

def restart_program():
    """Restarts the current program, with file objects and descriptors
       cleanup
    """
    Logger.log.info('restarting worker...')
    try:
        p = psutil.Process(os.getpid())
        children = p.children(recursive=True)
        for child in children:
            child.kill()                   
    except Exception as e:
        Logger.log.error(e)

    python = sys.executable
    os.execl(python, python, *sys.argv)

def send_command(command,env=None):
    Logger.log.debug('sending command: %s...' % (' '.join(command)))

    if env is None:
        process = subprocess.Popen(command,\
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,\
            universal_newlines=True, shell=True)        
    else:    
        process = subprocess.Popen(command,\
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,\
            universal_newlines=True, shell=True,env=env)        

    while True:
        output = process.stdout.readline()
        if ((output == '') | (output == b''))\
                & (process.poll() is not None):
            break        
        if (output) and not (output.startswith('Completed')):
            if output.rstrip()!='':
                Logger.log.debug('command response:'+output.rstrip())  
    rc = process.poll() #block until process terminated
    success= rc==0
    if success:
        Logger.log.debug('sending command DONE!')
        return True
    else:
        Logger.log.debug('sending command ERROR:%s!' % (''.join(process.stderr.readlines())))
        return False

GIT_TOKEN=''
if 'GIT_TOKEN' in os.environ:
    GIT_TOKEN=os.environ['GIT_TOKEN']
else:
    Logger.log.warning('GIT_TOKEN not found')
    
GIT_ACRONYM=''
if 'GIT_ACRONYM' in os.environ:
    GIT_ACRONYM=os.environ['GIT_ACRONYM']
else:
    Logger.log.warning('GIT_ACRONYM not found')

GIT_SERVER='github.com'
if 'GIT_SERVER' in os.environ:
    GIT_SERVER=os.environ['GIT_SERVER']

username=os.environ['USER_COMPUTER']

if 'REPO_FOLDER' in os.environ:
    repo_folder = os.environ['REPO_FOLDER']
else:
    repo_folder=os.environ['USERPROFILE']+'\\src\\'

SLEEP_TIME = 5    

try:
    Logger.log.info('Initializing decentralizedroutines worker version %s...' % \
        (version('decentralizedroutines')))
except:
    Logger.log.info('Initializing decentralizedroutines...')

routines = []
consumer = KinesisStreamConsumer('deepportfolio-workerpool', Logger.user)
producer = KinesisStreamProducer('deepportfolio-workerpool', Logger.user)

try:
    Logger.log.info('Initializing decentralizedroutines version %s STARTED!' % \
        (version('decentralizedroutines')))
except:
    Logger.log.info('Initializing decentralizedroutines STARTED!')

while True:
    try:
            
        for proc in routines:
            if proc.poll() is not None:
                routines.remove(proc)

        consumer.consume()
        for record in consumer.stream_buffer:    
            print('Received:'+str(record))    
            
            command = record
            if ('job' in command) & ('target' in command):
                if ((command['target']==username) | (command['target']=='ALL')):
                    
                    if command['job'] == 'command':                    
                        send_command(command['command'])
                    elif command['job'] == 'gitpwd':                    
                        if 'GIT_TOKEN' in command:
                            GIT_TOKEN = command['GIT_TOKEN']
                        if 'GIT_ACRONYM' in command:
                            GIT_ACRONYM = command['GIT_ACRONYM']
                        if 'GIT_SERVER' in command:
                            GIT_SERVER = command['GIT_SERVER']
                        Logger.log.info('Updated git parameters!')
                    elif command['job'] == 'routine':
                        Logger.log.info('Running routine %s/%s' % (command['repo'],command['routine']))

                        repo_path=Path(repo_folder)/command['repo']
                        requirements_path = repo_path/'requirements.txt'
                        python_path=repo_path/'venv\\Scripts\\python.exe'
                        
                        repo_exists = repo_path.is_dir()
                        venv_exists = python_path.is_file()
                        install_requirements=~python_path.is_file()                    
                        runroutine = False

                        env = os.environ.copy()
                        env['VIRTUAL_ENV'] = str(repo_path/'venv')
                        env['PATH'] = str(repo_path/'venv')+';'+str(repo_path/'venv\\Scripts')+';'+env['PATH']
                        env['PYTHONPATH'] = str(repo_path/'venv')+';'+str(repo_path/'venv\\Scripts')
                        env['GIT_TERMINAL_PROMPT'] = "0"
                        
                        # GIT PULL OR GIT CLONE
                        if repo_exists:                 
                            Logger.log.info('Pulling repo %s/%s' % (command['repo'],command['routine']))    
                            requirements_lastmod = 0
                            if requirements_path.is_file():
                                requirements_lastmod = os.path.getmtime(str(requirements_path))
                            # pull existing repo   
                            
                            GIT_URL='https://'+GIT_TOKEN+'@'+GIT_SERVER+'/'+GIT_ACRONYM+'/'
                            cmd = ['git','-C',str(repo_path),'pull',GIT_URL+command['repo']]
                            if not send_command(cmd):
                                Logger.log.error('running routine %s/%s ERROR:could not pull repo!'\
                                    % (command['repo'],command['routine']))
                                runroutine = False
                            else:
                                install_requirements = os.path.getmtime(str(requirements_path))!=requirements_lastmod
                                runroutine=True                            
                        else:                        
                            Logger.log.info('Cloning repo %s/%s' % (command['repo'],command['routine']))
                            GIT_URL='https://'+GIT_TOKEN+'@'+GIT_SERVER+'/'+GIT_ACRONYM+'/'
                            cmd = ['git','-C',str(repo_path.parents[0]),\
                                'clone',GIT_URL+command['repo']]                                   
                            if not send_command(cmd):
                                Logger.log.error('running routine %s/%s ERROR:could not clone repo!'\
                                    % (command['repo'],command['routine']))
                                runroutine=False
                            else:               
                                runroutine=True

                        # CREATE VENV
                        if (runroutine) & (not venv_exists):
                            Logger.log.info('Creating venv %s/%s' % (command['repo'],command['routine']))
                            if not send_command(['python','-m','venv',str(repo_path/'venv')]):
                                Logger.log.error('running routine %s/%s ERROR:could not create venv!'\
                                    % (command['repo'],command['routine']))
                                runroutine=False
                            else:
                                runroutine=True
                                install_requirements=True
                        
                        # INSTALL REQUIREMENTS
                        if (runroutine) & (install_requirements):
                            Logger.log.info('Installing requirements %s/%s' % (command['repo'],command['routine']))
                            if not send_command([str(python_path),'-m','pip','install','-r',str(requirements_path)],env=env):
                                Logger.log.error('running routine %s/%s ERROR:could not install requirements!'\
                                    % (command['repo'],command['routine']))
                                runroutine=False
                            else:
                                Logger.log.debug('repo installed %s/%s!'\
                                    % (command['repo'],command['routine']))
                                runroutine=True
                                            
                        # RUN ROUTINE 
                        if runroutine:
                            Logger.log.info('Starting process %s/%s' % (command['repo'],command['routine']))                        
                            cmd = [str(repo_path/'venv\\Scripts\\python.exe'),str(repo_path/command['routine'])]                        
                            proc = subprocess.Popen(cmd,env=env)                            
                            routines.append(proc)    

                    elif command['job'] == 'clone':
                        Logger.log.info('Cloning %s...' % (command['repo']))

                        repo_path=Path(repo_folder)/command['repo']
                        requirements_path = repo_path/'requirements.txt'
                        python_path=repo_path/'venv\\Scripts\\python.exe'
                        
                        repo_exists = repo_path.is_dir()
                        venv_exists = python_path.is_file()
                        install_requirements=~python_path.is_file()                    
                        runroutine = False

                        env = os.environ.copy()
                        env['VIRTUAL_ENV'] = str(repo_path/'venv')
                        env['PATH'] = str(repo_path/'venv')+';'+str(repo_path/'venv\\Scripts')+';'+env['PATH']
                        env['PYTHONPATH'] = str(repo_path/'venv')+';'+str(repo_path/'venv\\Scripts')
                        env['GIT_TERMINAL_PROMPT'] = "0"
                        
                        # GIT PULL OR GIT CLONE
                        if repo_exists:                 
                            Logger.log.info('Pulling repo %s...' % (command['repo']))    
                            requirements_lastmod = 0
                            if requirements_path.is_file():
                                requirements_lastmod = os.path.getmtime(str(requirements_path))
                            # pull existing repo   
                            
                            GIT_URL='https://'+GIT_TOKEN+'@'+GIT_SERVER+'/'+GIT_ACRONYM+'/'
                            cmd = ['git','-C',str(repo_path),'pull',GIT_URL+command['repo']]
                            if not send_command(cmd):
                                Logger.log.error('cloning repo %s ERROR:could not pull repo!'\
                                    % (command['repo']))
                                runroutine = False
                            else:
                                install_requirements = os.path.getmtime(str(requirements_path))!=requirements_lastmod
                                runroutine=True                            
                        else:                        
                            Logger.log.info('Cloning repo %s...' % (command['repo']))
                            GIT_URL='https://'+GIT_TOKEN+'@'+GIT_SERVER+'/'+GIT_ACRONYM+'/'
                            cmd = ['git','-C',str(repo_path.parents[0]),\
                                'clone',GIT_URL+command['repo']]                                   
                            if not send_command(cmd):
                                Logger.log.error('cloning repo %s ERROR:could not clone repo!'\
                                    % (command['repo']))
                                runroutine=False
                            else:               
                                runroutine=True

                        # CREATE VENV
                        if (runroutine) & (not venv_exists):
                            Logger.log.info('Creating venv %s...' % (command['repo']))
                            if not send_command(['python','-m','venv',str(repo_path/'venv')]):
                                Logger.log.error('cloning repo %s ERROR:could not create venv!'\
                                    % (command['repo']))
                                runroutine=False
                            else:
                                runroutine=True
                                install_requirements=True
                        
                        # INSTALL REQUIREMENTS
                        if (runroutine) & (install_requirements):
                            Logger.log.info('Installing requirements %s...' % (command['repo']))
                            if not send_command([str(python_path),'-m','pip','install','-r',str(requirements_path)],env=env):
                                Logger.log.error('running routine %s ERROR:could not install requirements!'\
                                    % (command['repo']))
                                runroutine=False
                            else:
                                Logger.log.debug('repo installed %s!' % (command['repo']))
                                runroutine=True                             

                    elif command['job'] == 'status':    
                        Logger.log.info('Running %i process' % (len(routines)))
                        for proc in routines:
                            Logger.log.info('Process id %i' % (proc.pid))
                    elif command['job'] == 'restart':                    
                        restart_program()                
                    elif command['job'] == 'ping':
                        Logger.log.info('pong')
                    elif command['job'] == 'pong':
                        Logger.log.info('ping')

        consumer.stream_buffer = []
        time.sleep(SLEEP_TIME + SLEEP_TIME*np.random.rand() - SLEEP_TIME/2)

    except Exception as e:
        Logger.log.error('Worker ERROR:'+e)
        consumer.stream_buffer = []
        time.sleep(SLEEP_TIME + SLEEP_TIME*np.random.rand() - SLEEP_TIME/2)
    