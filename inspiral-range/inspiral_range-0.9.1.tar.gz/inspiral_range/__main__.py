import os
import logging
import argparse

import numpy as np

from gpstime import GPSTimeParseAction

from . import __version__
from . import logger
from . import inspiral_range

logger.setLevel(os.getenv('LOG_LEVEL', 'WARNING').upper())
formatter = logging.Formatter(
    '%(asctime)s.%(msecs)d %(message)s',
    datefmt='%H:%M:%S',
)
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

##################################################

description = """Calculate GW detector inspiral range from ASD/PSD

Input should be a two-column ASCII data file (freq, strain), in
amplitude or power spectral density units.  The --divisor option can
be used to specify a scalar converstion for e.g. converting
displacement spectra to strain.  Use the --ligo option to pull the
official LIGO strain from NDS for the specified time (GPS or natural
language), e.g.:

  inspiral-range --ligo '2017-08-17 12:41:04 UTC'

By default range metrics are calculated for a binary neutron star with
m1=m2=1.4 Msolar.  Alternate waveform parameters can be specified as
PARAM=VALUE pairs, with mass parameters ('m1'/'m2') assumed to be in
solar masses (Msolar):

  inspiral-range --ligo 1126259462 m1=30 m2=30
"""

def parse_params(clparams):
    params = {}
    for param in clparams:
        try:
            k, v = param.split('=')
        except ValueError:
            raise ValueError("Could not parse parameter: {}".format(param))
        try:
            params[k] = float(v)
        except ValueError:
            params[k] = v
    return params


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=description,
)


class FileAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, 'file', values)
        setattr(namespace, 'stype', self.dest)
        delattr(namespace, 'asd')
        delattr(namespace, 'psd')


class ParamsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        try:
            params = parse_params(values)
        except ValueError as e:
            parser.error(e)
        setattr(namespace, self.dest, params)


parser.add_argument(
    '-v', '--version', action='version', version=__version__,
    help="show version info and exit")
igroup = parser.add_mutually_exclusive_group(required=True)
igroup.add_argument(
    '-a', '--asd', metavar='FILE', action=FileAction,
    help="noise spectrum file in amplitude spectral density units")
igroup.add_argument(
    '-p', '--psd', metavar='FILE', action=FileAction,
    help="noise spectrum file in power spectral density units")
igroup.add_argument(
    '-l', '--ligo', metavar='TIME', action=GPSTimeParseAction,
    help="pull LIGO calibrated strain from NDS for the specified time (GPS or natural language)")
parser.add_argument(
    '-d', '--divisor', default=1, type=float,
    help="factor to divide PSD (e.g. for converting displacement to strain)")
ogroup = parser.add_mutually_exclusive_group()
ogroup.add_argument(
    '-f', '--format', dest='fmt', choices=['txt', 'json', 'yaml'], default='txt',
    help="output format for range metric data (default: txt)")
ogroup.add_argument(
    '-s', '--single', metavar='FUNC',
    help="print value of single range metric only")
parser.add_argument(
    '--plot', action='store_true',
    help="plot the spectrum, waveform, and SenseMon range integrand")
parser.add_argument(
    'params', metavar='PARAM=VALUE', nargs='*', action=ParamsAction,
    help="waveform parameters")


def fetch_ligo_strain(gps, span=120):
    """LIGO calibrated strain spectrum from NDS data

    """
    from gwpy.timeseries import TimeSeries

    try:
        IFO = os.environ['IFO']
    except KeyError:
        exit("IFO environment variable must be specified.")
    C00 = f'{IFO}:GDS-CALIB_STRAIN_CLEAN'
    C01 = f'{IFO}:DCS-CALIB_STRAIN_CLEAN_C01'
    FREQ_CUTOFF = (10, 5e3)

    channel = C00
    start = gps
    end = start + span

    data = TimeSeries.get(channel, start, end, frametype='R')
    data_psd = data.psd(fftlength=8, overlap=4, window='hann')

    ind = np.where(
        (data_psd.frequencies.value > FREQ_CUTOFF[0]) & (data_psd.frequencies.value < FREQ_CUTOFF[1])
    )[0]
    freq = data_psd.frequencies.value[ind]
    psd = data_psd.value[ind]
    return freq, psd, channel


def main():
    args = parser.parse_args()

    if args.ligo:
        gps = args.ligo.gps()
        freq, psd, channel = fetch_ligo_strain(gps)
        title = '{}\n{} (GPS {})'.format(
            channel, args.ligo, gps
        )
    else:
        title = args.file
        data = np.loadtxt(args.file)
        freq = data[1:, 0]
        psd = data[1:, 1]
        psd /= args.divisor
        if args.stype == 'asd':
            psd **= 2

    metrics, H = inspiral_range.all_ranges(freq, psd, **args.params)

    if args.single:
        print(metrics[args.single][0])
    elif args.fmt == 'txt':
        print('metrics:')
        fmt = '  {:18} {:.3f} {}'
        for r, v in metrics.items():
            print(fmt.format(r+':', v[0], v[1] or ''))
        print('waveform:')
        fmt = '  {:18} {}'
        for p, v in H.params.items():
            print(fmt.format(p+':', v))
    else:
        out = {'metrics': dict(metrics), 'waveform': dict(H.params)}
        if args.fmt == 'json':
            import json
            print(json.dumps(out))
        elif args.fmt == 'yaml':
            import yaml
            print(yaml.safe_dump(out, default_flow_style=False))
        else:
            parser.error("Unknown output format: {}".format(args.fmt))

    if args.plot:
        import matplotlib.pyplot as plt
        from matplotlib.gridspec import GridSpec
        asd = np.sqrt(psd)
        # calc waveform strain
        dlum = metrics['range'][0]
        z = inspiral_range.horizon_redshift(freq, psd, H=H)
        hfreq, habs = H.z_scale(z)
        # put waveform in same units as noise strain
        habs *= 2*np.sqrt(hfreq)
        # limit the waveform plot range
        hmin = min(asd) / 100
        hind = np.where(habs > hmin)[0]
        hfreq = hfreq[hind]
        habs = habs[hind]
        find = np.where((hfreq >= freq[0]) & (hfreq <= freq[-1]))[0]
        hfreq = hfreq[find]
        habs = habs[find]
        # sensemon range integrand
        int73 = inspiral_range.sensemon_range(
            freq, psd, m1=H.params['m1'], m2=H.params['m2'], integrate=False,
        )
        # plot
        label = r"{} {}/{} $\mathrm{{M}}_\odot$ @ {:0.2f} Mpc".format(
            H.params['approximant'],
            H.params['m1'], H.params['m2'],
            dlum,
        )
        fig = plt.figure()
        gs = GridSpec(2, 1, height_ratios=(2, 1), hspace=0)
        ax0 = fig.add_subplot(gs[0])
        ax1 = fig.add_subplot(gs[1])
        ax1.sharex(ax0)
        ax0.loglog(freq, asd, label="strain noise ASD")
        ax0.loglog(hfreq, habs, linestyle='--', label=label)
        ax1.semilogx(freq, int73, label="sensemon range ASD")
        ax0.autoscale(enable=True, axis='x', tight=True)
        ax0.grid(True)
        ax1.grid(True)
        ax0.set_title(f"{title}")
        ax0.set_ylabel(u"Strain [1/\u221AHz]")
        ax0.tick_params(labelbottom=False)
        ax1.set_ylabel(u"Range [Mpc/\u221AHz]")
        ax1.set_xlabel("Frequency [Hz]")
        ax0.legend()
        ax1.text(
            0.985, 0.94,
            "SenseMon range {:0.2f} {}".format(*metrics['sensemon_range']),
            transform=ax1.transAxes, ha="right", va="top", size=12,
            bbox=dict(boxstyle="round", fc="w", ec="0.7", alpha=0.7),
        )
        plt.show()

##################################################

if __name__ == '__main__':
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
