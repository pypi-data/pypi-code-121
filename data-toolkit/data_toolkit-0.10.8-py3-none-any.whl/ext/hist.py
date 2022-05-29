import sys
import ipdb
import pandas as pd
import datetime as dt
import subprocess as sp
from Levenshtein import distance as dist
import os
import json
import humanize
import time

try:
    term_wdith = os.get_terminal_size().columns
except OSError:
    term_wdith = 80

pd.set_option('display.max_colwidth',term_wdith - 20)
pd.set_option('display.max_rows', None)

# TODO: treat 'cd' in a special way s.t. we can generate the absolute path wherever possible
FILTER_TERMS = ['ls','install','dt hist', 'git ', 'dt ', 'code',
                'ipython','htop','git push','git pull','git stash',
                'tmux', 'nvidia-smi', 'ping']

def dt_conv(l: str):
    try:
        pd_dt_repr = pd.to_datetime(dt.datetime.fromtimestamp(l[1]))
        return  humanize.naturaldelta(pd_dt_repr)
    except ValueError as e:
        # TODO: why does this occur
        print('ValueError', l)


def filter_term(term: tuple, excluded_terms = FILTER_TERMS):
    # Logic: all filter terms need to _not_ match
    if 'cd' in term[0][:2]:
        try:
            if term[0].split(' ')[1][0] not in ['~','/']:
                return False
            else:
                return True
        except:
            print(f"Error with {term[0]}")

    return all([ft not in term[0] for ft in excluded_terms])

def check_if_intlike(s:str):
    try:
        int(s)
        return True
    except ValueError:
        return False

def hist_tail(n_lines=20, excluded_terms = []):
    excluded_terms = FILTER_TERMS + excluded_terms
    
    shell = os.environ['SHELL'].split('/')[-1]

    if shell=='sh': shell = 'bashrc'

    # checks that we can find 
    zsh_hist = f"{os.path.expanduser('~')}/.{shell}_history"
    if not os.path.exists(zsh_hist):
        raise NotImplementedError('Not sure where to look')
    try:
        split_f = str(sp.check_output(['tail','-n',str(n_lines * 3), zsh_hist] )).split(':')
    except sp.CalledProcessError:
        sh_hist = f"{os.path.expanduser('~')}/.bash_history"
        split_f = str(sp.check_output(['tail',sh_hist,'-n',str(n_lines * 3), zsh_hist])).split(':')
        
        
    # Work Ubuntu 20.04 so far so good
    # TODO: fix this horrible line 
    parsed_commands = [ ''.join(l.replace('\\n','').strip().split(';')[-1:]) for l in split_f if '\\n' in l]
    # check if an item in split_f is convertable to int
    parsed_dt = [ int(t) for t in split_f if check_if_intlike(t)]

    parsed = list(zip(parsed_commands, parsed_dt))

    # remove FILTER_TERMS 
    cmds = [ t for t in parsed if filter_term(t, excluded_terms) ]

    # identify Levenstein distance
    lev_dist = [ dist(cmds[i][0],cmds[i+1][0]) for i in range(len(cmds)-1) ]

    # TODO: make more efficent
    # Lev dist with previous terms (1 approx to catch typos)
    ld = lev_dist + [9999]
    # dist_dict = { k:v for k,v in zip(cmds,ld) }
    dist_dict = { k:v for k,v in zip(cmds,ld) if v>4 }
    # TODO check if ordered before
    last_list = list(dist_dict.keys())[-n_lines:]

    # constructs DF with one line per command
    last_cmds = [ l[0].replace('\\','') for l in last_list ]
    # TODO: the time seems to be wrong still
    last_dt = [ dt_conv(l) for l in last_list]
    df = pd.DataFrame([last_cmds,last_dt]).T
    df.columns = ['Command', 'Time']

    return df

def hist_save(lines_to_save: list, snippet_name: str, n_lines: str):
    df = hist_tail(n_lines)
    
    snippets_path = os.path.join(os.path.expanduser('~'), 'dt_config.json')
    config = json.loads(open(snippets_path).read())

    # prepare the correct saving format
    saved_time = dt.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    # TODO: figure out why there's this horrible off by-one error
    parsed_lines = [df.iloc[x-1].Command for x in lines_to_save]
    saved_lines = [snippet_name, saved_time, parsed_lines]
    
    config['snippets'].append(saved_lines)
    
    json.dump(config, open(snippets_path, 'w'))
    
    