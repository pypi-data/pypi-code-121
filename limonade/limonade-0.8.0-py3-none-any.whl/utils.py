import json
import sys
import time
import datetime as dt
from typing import Optional, Sequence, Union
from pathlib import Path
from types import SimpleNamespace

import appdirs
import numpy as np
from limonade import misc
import limonade.exceptions as ex


"""
Utils is a repository for generally useful functions definitions and classes for thing such as reading and writing.

"""

parsed_extras_list = ['multihit', 'latency']  # list of extras not handled in raw mode

def delete_channel_data(data_path, base_name, cfg):
    """
    Used to delete channel files after parsing.
    :param data_path:
    :param base_name:
    :param cfg:
    :return:
    """
    timenames, dnames, tnames = find_data_files(data_path, base_name, cfg, mode='channel')
    for fname in timenames + tnames:
        if fname.exists():
            fname.unlink()
    for chnamelist in dnames:
        for fname in chnamelist:
            if fname is not None:
                if fname.exists():
                    fname.unlink()

def find_data_files(data_path, base_name, cfg, mode):
    """
    Generate filenames (paths) of all the data produced by config. You can select either 'event' or 'channel'
    type names.

    :param data_path:
    :param base_name:
    :param cfg:         The config-dict
    :param mode:        raw or event -mode
    :return: timing, data,and index variable filenames as lists. Extra names are given
             as a list of names, one per extra (for each channel as in other data).
    """
    datas = cfg.det['datas']

    if mode == 'event':
        timenames = [data_path / (base_name + '_{}.dat'.format(cfg.det['index_variable']['name']))]
        #names = [data_path / (base_name + '_events.dat')]
        tnames = [data_path / (base_name + '_timing.dat')]
        dnames = []
        try:
            for adata in datas:
                dnames.append([data_path / (base_name + '_{}.dat'.format(adata['name']))])
        except TypeError:
            pass

    elif mode == 'channel':
        timenames = [data_path / (base_name + '_{}_ch{}.dat'.format(cfg.det['index_variable']['name'],
                                                                    x)) for x in cfg.det['ch_list']]
        #enames = [data_path / (base_name + '_{}_ch{}.dat'.format(x)) for x in cfg.det['ch_list']]
        tnames = [data_path / (base_name + '_timing_ch{}.dat'.format(x)) for x in cfg.det['ch_list']]
        dnames = []

        for adata in datas:
            dnames.append([])  # all datas get a position in list
            if adata['name'] not in parsed_extras_list:
                # this data type is present in channel data and will be combined either as
                # a bit in a bitmask or a column in a matrix.
                try:  # channel mask default is ones
                    ch_mask = np.array(adata['ch_mask'], dtype='bool')
                except:  # this should not fire anymore
                    ch_mask = np.ones((len(cfg.det['ch_cfg']),), dtype='bool')

                # Data names are retrieved by channel index. In cases there is no extra defined
                # for a channel we need to put something in to the list. Let it be None then.
                for ch_idx in range(len(cfg.det['ch_cfg'])):
                    dnames[-1].append(None)
                    if ch_mask[ch_idx]:
                        dfil = data_path / (base_name + '_{}_ch{}.dat'.format(adata['name'], ch_idx))
                        dnames[-1][-1] = dfil

    return timenames, dnames, tnames


def write_channel_metadata(data_path, base_name, channel, metadata):
    """
    Writes the metadata to disk. Some data entries in metadata dictionary are not directly serializable into json,
    so some parsing happens when reading/writing.

    :param data_path:       Path to data
    :param base_name:       Base name
    :param channel:         Channel to write. Writes all data if negative number.
    :param metadata:        List of metadata dictionaries, one per channel. Result of Metadata.dump().
    """
    # make sure no datetime objects or numpy numerical values end up in the json serializer.
    metadata = misc.sanitize_for_json(metadata)

    #datetime_type = ['start', 'stop']
    # make sure data_path is a pathlib Path
    data_path = Path(data_path)

    if channel >= 0:  # if saving single channel only
        channels = (channel, metadata[channel:channel+1])
    else:
        channels = enumerate(metadata)

    for ch_idx, meta_d in channels:
        try:
            temp_for_file = {key: value for key, value in meta_d.items()}  # if key not in datetime_type}
        except:
            print(meta_d.items())
            raise ex.LimonadeException('Error in write metadata')
        
        if 'notes' in meta_d:
            temp_for_file['notes'] = meta_d['notes']
        else:
            temp_for_file['notes'] = 'Metadata defined by raw files.'

        if meta_d['start'] is None:
            temp_for_file['notes'] += 'Missing start time substituted by compile time.'
            meta_d['start'] = dt.datetime.fromtimestamp(time.time())

        if meta_d['stop'] is None:
            temp_for_file['notes'] += 'Missing stop time calculated from timestamps.'
            meta_d['stop'] = meta_d['start'] + \
                                        dt.timedelta(seconds=int(meta_d['total_time']*1e-9))

        #for key in datetime_type:
        #    temp_for_file[key] = meta_d[key].isoformat()

        with (data_path / (base_name + '_metadata_ch{:02d}.json'.format(ch_idx))).open('w') as fil:
            #json.dump(temp_for_file, fil, indent=0, default=int)
            json.dump(temp_for_file, fil, indent=0)


def read_channel_metadata(data_path, base_name, channel):
    try:
        with (data_path / (base_name + '_metadata_ch{:02d}.json'.format(channel))).open('r') as fil:
            temp_from_file = json.load(fil)
    except FileNotFoundError:
        raise ex.LimonadeDataNotFoundError('No metadata found!')
    metadata = misc.desanitize_json(temp_from_file)
    #datetime_type = ['start', 'stop']
    #metadata = {key: value for key, value in temp_from_file.items() if key not in datetime_type}
    #for key in datetime_type:
    #    #metadata[key] = dt.datetime.fromisoformat(temp_from_file[key]) # not present in python 3.6
    #    metadata[key] = misc.fromisoformat(temp_from_file[key])
    return metadata


def find_path(config: Union[dict, SimpleNamespace], name: str, suffix=None, from_global_conf=False):
    """
    Used to locate a given config file. The home directory of the data is automatically searched before
    the config path so that local changes stick.

    :param config: The detector configuration. This does not exist when loading the main detector configuration. In
                   that case a dict containing config and home paths is expected, as in config.paths. The detector
                   configuration used when generating the data will be loaded if it exists, otherwise the named
                   configuration (name parameter) is loaded from configuration directory.
    :param name:   Name of the configuration. Not used if loading local detector configuration.
    :param suffix: The configuration suffix. Often used values are
                   'plotcfg': for plots, 'ecal': for energy calibration, etc.
                   The configuration directory should be structured so, that there is a directory for each
                   suffix. It should be left as None when loading main detector configuration.
    :param from_global_conf: Load from global dir even if local configuration exists.

    :return:
    """

    if suffix is None:
        cfg = Path(config['cfg_dir'])
        home = Path(config['home'])
        print(home)
        # reading detector configuration. Suffix is ignored.
        if not from_global_conf:
            print('Searching for', home / (home.parts[-1] + '_cfg.json'))
            if (home / (home.parts[-1] + '_cfg.json')).exists():
                return home / (home.parts[-1] + '_cfg.json')
        elif name is None:
            raise ex.LimonadeConfigurationError('Cannot load global detector configuration without detector name!')
        print(cfg)
        print(name)
        loadpath = cfg / (name + '_cfg.json')
    else:
        # reading other configuration files
        home = Path(config.path['home'])
        cfg = Path(config.path['cfg_dir'])
        filename = Path(name + '_' + suffix + '.json')  # name of the file. E.g. 'gamma_plotcfg.json'
        if (home / filename).exists():
            loadpath = home / filename
            print('Found local config', loadpath)
        else:
            loadpath = cfg / suffix / filename

    return loadpath


def load_plot_config(config, plot_name):
    """
    Loads a plot configuration from a json file.

    :param config: Config data that has the config.path in it
    :param plot_name_list: plot config name without the _plotcfg.json postfix or a list of names
    :return: a plot config dictionary
    """
    print(plot_name)
    try:
        with find_path(config, plot_name, 'plotcfg').open('r') as fil:
            plot_config = json.load(fil)
    except FileNotFoundError:
        raise ex.LimonadeConfigurationError('Could not find plot configuration.')
    plot_config = misc.desanitize_json(plot_config)
    return plot_config


def load_style_sheet(config, style_name_list):
    """
    Loads a matplotlib style sheet written as a json file.

    :param config: Detector configuration object
    :param style_name_list: style path or a list of paths
    :return: list of style dictionaries
    """
    style_cfg_list = []
    if isinstance(style_name_list, str):  # single stylesheet if string is given
        style_name_list = [style_name_list]
    while len(style_name_list) > 0:
        style_name = style_name_list.pop(0)
        try:
            with find_path(config, style_name, 'stylecfg').open('r') as fil:
                style_config = json.load(fil)
            style_cfg_list.append(style_config)
        except FileNotFoundError:
            raise ex.LimonadeConfigurationError('Could not find stylesheet.')

    return style_cfg_list


def load_effcal(config, eff=None):
    if eff is None:
        eff = config.det['effcal']

    with find_path(config, eff, 'effcal').open('r') as fil:
        temp = json.load(fil)
        effcal = temp
    return effcal


def load_strip_cal(config):
    """
    Load strip calibration files if they exist.
    """

    strips = []
    for ch in config.det['ch_cfg']:
        try:
            if ch['cal_array'] is not None:
                strips.append(ch['cal_array'])
        except KeyError:
            pass

    if strips:
        strip_cal = []
        try:
            for cal in strips:
                with find_path(config, cal, 'stripcal').open('r') as fil:
                    strip_cal.append(json.load(fil)['calibration'])
        except FileNotFoundError:
            print('Strip calibration file not found!')
            raise ex.LimonadeConfigurationError('Strip calibration file not found!')
        out = np.stack(strip_cal, axis=0)
        return out
    return None


def old_config(config_dict: dict) -> SimpleNamespace:
    """ 
    Makes new style dict-config into old-style namespace config.

    :param config_dict:      A new style dictionary config with, at the minimum, path, det, channel, readout and cal 
                        keywords defined.
    :result:            An old style config namespace with matching members to the input dict 
    """

    old_cfg = SimpleNamespace(**misc.desanitize_json(config_dict))

    return old_cfg


def _set_limonade_config():
    """
    This is exported as a command-line entry point set-limonade-config.
    """
    import argparse
    parser = argparse.ArgumentParser(description='Set path for configuration files.')
    parser.add_argument('cfg_path', metavar='cfg_path', type=str,
                        help='Set configuration directory path.')
    args = parser.parse_args()
    cfg_path = Path(args.cfg_path)
    local_cfg = {'cfg_dir': str(cfg_path)}

    if not cfg_path.exists():
        print('The configuration directory {} does not exist. Create it?'.format(cfg_path))
        ans = input('[Y, n] ')
        if ans == "" or ans.lower() == 'y':
            cfg_path.mkdir(parents=True)
        else:
            print('Config path not set.')
            return

    if not cfg_path.is_dir():
        raise NotADirectoryError('Given cfg_path is not a directory!')

    cfg_dir = Path(appdirs.user_config_dir('limonade', ""))
    if not cfg_dir.exists():
        cfg_dir.mkdir(parents=True)
    try:
        with (cfg_dir / 'local_cfg.json').open('r') as fil:
            old_cfg = json.load(fil)
        local_cfg = old_cfg.update(local_cfg)
    except FileNotFoundError:
        pass

    with (cfg_dir / 'local_cfg.json').open('w') as fil:
        json.dump(local_cfg, fil)
        print('Ok!')

def _set_limonade_data():
    """
    This is exported as a command-line entry point set-limonade-data.
    """
    import argparse
    parser = argparse.ArgumentParser(description='Set path for data files.')
    parser.add_argument('data_path', metavar='data_path', type=str,
                        help='Set data directory path.')
    args = parser.parse_args()
    data_path = Path(args.data_path)
    # local_cfg = {'data_dir': str(data_path)}

    if not data_path.exists():
        print('The data directory {} does not exist. Create it?'.format(data_path))
        ans = input('[Y, n] ')
        if ans == "" or ans.lower() == 'y':
            data_path.mkdir(parents=True)
        else:
            print('Data path not set.')
            return

    if not data_path.is_dir():
        raise NotADirectoryError('Given data_path is not a directory!')

    cfg_dir = Path(appdirs.user_config_dir('limonade', ""))
    if not cfg_dir.exists():
        cfg_dir.mkdir(parents=True)

    with (cfg_dir / 'local_cfg.json').open('r') as fil:
        local_cfg = json.load(fil)

    local_cfg.update({'data_dir': str(data_path)})

    with (cfg_dir / 'local_cfg.json').open('w') as fil:
        json.dump(local_cfg, fil)
        print('Ok!')

def get_limonade_config():
    """
    Returns a dictionary containing setup directory info.


    This is exported as a command-line entry point get-limonade-config.
    """
    cfg_dir = Path(appdirs.user_config_dir('limonade', ""))
    try:
        with (cfg_dir / 'local_cfg.json').open('r') as fil:
            local_cfg = json.load(fil)
        try:
            local_cfg['cfg_dir']
        except KeyError:
            print("Configuration directory is not set correctly. Keyword 'cfg_dir' not found.")
            return None
        return local_cfg
    except FileNotFoundError:
        print('Config dir not set!')
        return None

def _add_detector():
    """
    This is exported as a command-line entry point add-detector. The script creates minimal configuration files into
    configuration directory. Optional inputs can be used to set number of channels and extra data options. This is only
    a template, though and the configurations still need some editing.
    """
    import argparse
    parser = argparse.ArgumentParser(description='Create a minimal configuration file structure for a detector with n_ch channels.')
    parser.add_argument('name', metavar='name', type=str,
                        help='The name of the detector.')
    parser.add_argument('n_ch', metavar='n_ch', type=int,
                        help='Number of readout channels.')
    parser.add_argument('data_type', type=str,
                        help='Data type of the detector, selects which loader is used for raw data.')
    parser.add_argument('-e', '--extra_data', type=str,
                        help='Add extra data for the detector. Currently recognized extras are [l, p, m, c] for latency, '
                             'pileup-flag, multi-hit flag and coordinate.')
    args = parser.parse_args()
    local_cfg = get_limonade_config()
    if local_cfg is None:
        print("Configuration directory is not set. Please run 'set_limonade_config' first.")
        return

    cfg_dir = Path(local_cfg['cfg_dir'])

    det_cfg = {"name": args.name,
               "data_type": args.data_type,
               "latency": [0 for _x in range(args.n_ch)],
               "ch_list": [x for x in range(args.n_ch)],
               "coinc_win": 100,
               "sample_ns": 10,
               "cal_name": args.name,
               "ch_cfg": [],
               "index_variable": {
                                 "name": "time",
                                 "type": "u8",
                                 "raw_unit": "tick",
                                 "unit": {"s": 1e9, "m": 60e9, "h": 36e11, "d": 864e11, "ns": 1},
                                 "cal": 10},
               "datas": [{"name": "energy",
                          "type": "i2",
                          "num_col": 2,
                          "aggregate": "col",
                          "multi": "sum",
                          "raw_unit": "ch",
                          "unit": "keV",
                          "empty_val": -1}]
               }
    for ch in range(args.n_ch):
        det_cfg['ch_cfg'].append(
            {"name": "Ch{}".format(ch),
             "pdeadtime": 10})
    print(args.extra_data)
    if args.extra_data is not None:
        if 'l' in args.extra_data:
            det_cfg['datas'].append({"name": "latency",
                                      "main": 0})

        if 'p' in args.extra_data:
            det_cfg['datas'].append({"name": "pileup",
                                      "type": "u1",
                                      "aggregate": "bit",
                                      "multi": "max"})
        if 'm' in args.extra_data:
            det_cfg['datas'].append({"name": "multihit"})
        if 'c' in args.extra_data:
            det_cfg['datas'].append({"name": "coord",
                                      "type": "i1",
                                      "aggregate": "col",
                                      "ch_mask": [int(x < 2) for x in range(args.n_ch)],
                                      "multi": "max_e",
                                      "raw_unit": "strip",
                                      "unit": "mm",
                                      "empty_val": -1})

    # After the detector, we need a calibration file
    cal = {"energy": [[0, 1, 0] for _x in range(args.n_ch)]}
    if args.extra_data is not None and 'c' in args.extra_data:
        cal["coord"] = [[0, 1, 0] for _x in range(min(2, args.n_ch))]

    with (cfg_dir/'{}_cfg.json'.format(args.name)).open('w') as fil:
        #json.dump(det_cfg, fil, indent=2)
        fil.write(misc.json_pp(det_cfg))
    cal_dir = cfg_dir/'ecal'
    cal_dir.mkdir(exist_ok=True)
    with (cal_dir/'{}_ecal.json'.format(args.name)).open('w') as fil:
        #json.dump(cal, fil)
        fil.write(misc.json_pp(cal))


