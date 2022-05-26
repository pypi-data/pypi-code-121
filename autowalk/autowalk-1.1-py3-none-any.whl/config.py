#!/usr/bin/python

import re
from pathlib import Path
from collections import namedtuple

from utils.assign import Assign


class CONFIG:
    # auto generate config file for user at home dir
    GLOBAL_CONFIG = None
    CONFIG_NAME = ".autowalk.py"  

    # these are default configs, there will be generated into config file
    DEFAULT_CONFIG = dict(
        # choose the recursion depth
        recursion_depth = [2],

        # Config Your Start Dir(One Or More)
        recursion_root_list = [
            '/mnt/d',
            '/mnt/e',
            '/mnt/d/lin',
        ],
        black_list_dirname = [
            # Some is for WSL2 (Windows Sub Linux)
            "$RECYCLE.BIN",
            "BaiduNetdiskDownload",
            "Config.Msi",
            "System Volume Information",
            "Recovery",
        ],
        black_list_dirname_prefix = [
            '.',
            '【',
            '_',
            '__',
            '$',
        ],

        # This Config Just For Autojump 
        weight_value_only_for_autojump = [
            1000
        ],

        autojump_default_config = [
            "~/.local/share/autojump/autojump.txt"
        ],

        # This Config Just For Ranger 
        # If you use ranger you can config it
        prefix_and_suffix_only_for_ranger = [
            "g",
            ","
        ],
        ranger_remap_output_file = [
            "~/.rc_remap.conf"
        ],

        default_map_only_for_ranger = [
            'map g/ cd /',
            'map g~ cd ~',  # WSL Home
            'map gr, cd /',
            'map gc, cd /mnt/c',
            'map gd, cd /mnt/d',
            'map ge, cd /mnt/e',
            'map gm, cd /mnt',
            'map gh, cd /mnt/c/Users/96338', # Windows Home
            'map gr, cd ~/.config/ranger',   # Ranger Home
            'map grs, cd /mnt/d/lab/ranger', # ranger script Home
        ]
    )

    @staticmethod
    def make_config_dict():
        """
            generate config file for user 
            and load global variable for use
        """
        regex = re.compile(r'(.*?)=([\s\S]*?\])')
        config_path = (Path.home() / f'{CONFIG.CONFIG_NAME}')

        if not config_path.exists():
            with open(str(config_path), "w") as f:
                final_config_str = Assign.dict_list(CONFIG.DEFAULT_CONFIG)
                f.write(final_config_str)

        with open(str(config_path), "r") as f:
            config_str = '\n'.join([line for line in f if not line.strip().startswith("#") or not line.strip()])
            result = regex.findall(config_str.strip())
            CONFIG.DEFAULT_CONFIG = {k.strip():v.strip() for k,v in result}


        add_name = namedtuple(
            "GLOBAL_CONFIG",
            CONFIG.DEFAULT_CONFIG.keys()  # add keys
        )

        CONFIG.DEFAULT_CONFIG = { k:eval(v) for k,v in CONFIG.DEFAULT_CONFIG.items() }
        CONFIG.GLOBAL_CONFIG = add_name._make(CONFIG.DEFAULT_CONFIG.values())  # add value