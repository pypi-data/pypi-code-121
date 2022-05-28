import numpy as np
import pandas as pd

pd.set_option("display.max_rows", 30)
pd.set_option("display.max_columns", 30)
pd.set_option("display.width", 1000)


def blue_header(msg):
    print('\033[1m\033[94m' + (len(msg) + 5) * "/")
    print(4 * "/", msg, "\033[0m")


def printbold(msg, kwargs={}):
    # Blue EPM style paragraph title frame
    print('\033[1m\033[97m' + msg + "\033[0m", **kwargs)


def correlation_header(msg):
    # EPM style correlation header
    print(80 * '/' + f"\n\033[1m{msg} [%]\033[0m\n" + 80 * '/')


def section_header(msg, bold=True):
    # EPM style section header
    if bold:
        print('\n\033[1m' + (len(msg) + 32) * "-")
    else:
        print((len(msg) + 32) * "-")
    print(15 * '-' + f" {msg} " + 15 * '-')
    print((len(msg) + 32) * "-" + '\033[0m')


def warning(*msg):
    print("\033[1m\033[33m WARNING \033[0m", *msg)


def info(*msg):
    print("\033[1m\033[97m INFO \033[0m", *msg)


def raise_warning(cond, msg):
    if not cond:
        print(f"\033[1m\033[33m WARNING:\033[0m {msg}")


def raise_error(cond, msg):
    if not cond:
        print(f"\033[1m\033[31m ERROR:\033[0m {msg}")
        raise AssertionError


class FTCalibException(Exception):
    def __init__(self, msg):
        self.msg = msg
        super().__init__(msg)

    def __str__(self):
        return f"\033[1m\033[31m ERROR:\033[0m {self.msg}"


class MissingFile(FTCalibException):
    pass


class MissingTree(FTCalibException):
    pass


class MissingBranch(FTCalibException):
    pass


class PerfTable:
    """ Formatted table for summarising performances """

    def __init__(self, table_title, headers, tagger_names, pad=1, round_digits=4):
        self.headers      = headers
        self.tagger_names = tagger_names
        self.pad          = pad
        self.percentages  = False
        self.round_digits = round_digits
        self.table_title  = table_title

        self.data = []

    def fill_row(self, values):
        assert len(values) == len(self.headers)
        assert isinstance(values, list)
        self.data.append(values)

    def print_percentages(self):
        self.percentages = True

    def __str__(self):
        assert len(self.data) == len(self.tagger_names)
        # Format data

        def vformat(v):
            return np.round(v, self.round_digits)

        uvalue = f"{{:>{self.round_digits + 3}}} ± {{:>{self.round_digits + 2}}}"
        uvalue_cal = f"{{:>{self.round_digits + 3}}} ± {{:>{self.round_digits + 2}}}(stat) ± {{:>{self.round_digits + 2}}}(cal)"
        for r, row in enumerate(self.data):
            for c, val in enumerate(row):
                if isinstance(val, tuple):
                    if self.percentages:
                        if len(val) == 3:
                            self.data[r][c] = "(" + uvalue_cal.format(vformat((100 * val[0])), vformat((100 * val[1])), vformat((100 * val[2]))) + ")%"
                        else:
                            self.data[r][c] = "(" + uvalue.format(vformat((100 * val[0])), vformat((100 * val[1]))) + ")%"
                    else:
                        self.data[r][c] = uvalue.format(vformat(val[0]), vformat(val[1]))
                elif isinstance(val, float):
                    self.data[r][c] = vformat(val)
                else:
                    self.data[r][c] = str(val)

        self.data = self.data
        self.data.insert(0, ["Tagger"] + self.headers)
        for n, name in enumerate(self.tagger_names):
            self.data[n + 1].insert(0, name)

        self.data = np.array(self.data)

        # pad = self.pad * " "
        colwidths = np.array([max(len(v) for v in col) for col in self.data.T])
        rowformat = [f"{{:<{w}}}" for w in colwidths]

        linewidth = (np.sum(colwidths + 3) + 1)
        hline = np.array(list(linewidth * '─'), dtype=str)
        toprow = hline.copy()
        midrow = hline.copy()
        botrow = hline.copy()
        toprow[np.cumsum(colwidths + 3)] = '┬'
        midrow[np.cumsum(colwidths + 3)] = '┼'
        botrow[np.cumsum(colwidths + 3)] = '┴'
        toprow[[0, -1]] = ['╠', '╣']  # ['┌', '┐']
        midrow[[0, -1]] = ['├', '┤']
        botrow[[0, -1]] = ['└', '┘']
        toprow = ''.join(toprow) + '\n'
        midrow = ''.join(midrow) + '\n'
        botrow = ''.join(botrow) + '\n'

        body = '╔' + (linewidth - 2) * '═' + '╗\n'
        body += f'║ \033[1m{self.table_title}\033[0m' + (linewidth - len(self.table_title) - 3) * ' ' + '║\n'

        body += toprow.replace('─', '═').replace('┬', '╤')
        body += '│ ' + ' │ '.join([f"\033[1m\033[32;1m{fmt.format(data)}\033[0m" for fmt, data in zip(rowformat, self.data[0])]) + ' │\n'
        body += midrow
        for row in self.data[1:]:
            body += '│ ' f"\033[1m\033[32m{rowformat[0].format(row[0])}\033[0m"
            body += ' │ ' + ' │ '.join([fmt.format(data) for fmt, data in zip(rowformat[1:], row[1:])]) + ' │\n'
        body += botrow

        return body


def print_tagger_statistics(taggers, calibrated, selected=True):
    """ Prints basic statistics of the input data for each tagger

        :param taggers: List of taggers
        :type taggers: list
        :param calibrated: Whether to show calibrated tagger statistics (after calibration)
        :type calibrated: bool
    """
    from lhcb_ftcalib.apply_tagger import TargetTagger, TargetTaggerCollection
    if calibrated:
        header = "CALIBRATED TAGGER STATISTICS"
    else:
        header = "RAW TAGGER STATISTICS"

    if isinstance(taggers, (TargetTagger, TargetTaggerCollection)) and selected:
        warning("Selected statistics unavailable for TargetTaggers (selected=True), setting to False")
        selected = False

    tagnames = [t.name for t in taggers]
    tab = PerfTable(header, ["#Evts", "Σw", "(Σw)² / Σw²", "#Tagged", "Σ_tag w"], tagnames)
    if selected:
        for t in taggers:
            if calibrated:
                tab.fill_row([t.stats.Ns, t.stats.Nws, t.stats.Neffs, t.stats.cal_Nts, t.stats.cal_Nwts])
            else:
                tab.fill_row([t.stats.Ns, t.stats.Nws, t.stats.Neffs, t.stats.Nts, t.stats.Nwts])
    else:
        for t in taggers:
            if calibrated:
                tab.fill_row([t.stats.N, t.stats.Nw, t.stats.Neff, t.stats.cal_Nt, t.stats.cal_Nwt])
            else:
                tab.fill_row([t.stats.N, t.stats.Nw, t.stats.Neff, t.stats.Nt, t.stats.Nwt])

    print(tab)


def print_tagger_performances(taggers, calibrated=False, selected=True, round_digits=4):
    """ Prints a table with standard performance numbers like the tagging rate,
        the mistag rate and the tagging power for each tager

        :param taggers: List of taggers
        :type taggers: list
        :param calibrated: Whether to show calibrated tagger statistics (after calibration)
        :type calibrated: bool
        :param selected: Whether to only use events in selection
        :type selected: bool
        :param round_digits: Number of digits to round to
        :type round_digits: int
    """
    tagnames = [t.name for t in taggers]
    if calibrated:
        tab = PerfTable("CALIBRATED TAGGING PERFORMANCES", ["Tagging Efficiency", "Avg. Mistag Rate", "Effective Mistag", "Tagging Power"], tagnames)
    else:
        tab = PerfTable("RAW TAGGING PERFORMANCES", ["Tagging Efficiency", "Avg. Mistag Rate", "Effective Mistag", "Tagging Power"], tagnames)

    for tagger in taggers:
        tab.fill_row([tagger.stats.tagging_efficiency(calibrated, selected),
                      tagger.stats.mistag_rate(calibrated, selected),
                      tagger.stats.effective_mistag(calibrated, selected),
                      tagger.stats.tagging_power(calibrated, selected)])

    tab.print_percentages()
    print(tab)


def print_calibration_parameters(taggers):
    paramnames = []
    values = []
    maxparams = 0

    # Get fit parameter values, determine table header
    for tagger in taggers:
        result = tagger.stats.params
        pnames, noms, errors = result.names_delta, result.params_delta, result.errors_delta
        paramnames.append(pnames)
        values.append([(n, u) for n, u in zip(noms, errors)])
        if len(pnames) > maxparams:
            maxparams = len(pnames)

    use_paramnames = paramnames[np.argmax([len(params) for params in paramnames])]

    # If different calibrations have different number of parameters, add missing value placeholders
    for j, row in enumerate(values):
        diff = maxparams - len(row)
        if diff > 0:
            deg = diff // 2
            npar = len(values[j]) // 2
            values[j] = row[:npar] + (deg * [" "]) + row[npar:] + (deg * [" "])

    # # Fill table
    tab = PerfTable("FINAL CALIBRATION PARAMETERS", use_paramnames, [t.name for t in taggers])
    for row in values:
        tab.fill_row(row)

    print(tab)


def print_tagger_correlation(taggers, option="all", calibrated=False, selected=False):
    """ Print different kinds of tagger correlations. By default, all correlations are printed

        :param taggers: List of taggers
        :type taggers: TaggerCollection
        :param option: Type of correlation to compute ("fire", "dec", "dec_weight")
        :type option: string
    """
    if selected:
        info("Correlations of selected events")
    if option in ("all", "fire"):
        correlation_header("Tagger Fire Correlations")
        print(100 * taggers.correlation("fire", selected=selected, calibrated=calibrated), '\n' + 80 * '/', '\n')
    if option in ("all", "dec"):
        correlation_header("Tagger Decision Correlations")
        print(100 * taggers.correlation("dec", selected=selected, calibrated=calibrated), '\n' + 80 * '/', '\n')
    if option in ("all", "dec_weight"):
        correlation_header("Tagger Decision Correlations (dilution weighted)")
        print(100 * taggers.correlation("dec_weight", selected=selected, calibrated=calibrated), '\n' + 80 * '/', '\n')
    if option in ("all", "both_fire"):
        correlation_header("Tagger Decision Correlations (If both fire)")
        print(100 * taggers.correlation("both_fire", selected=selected, calibrated=calibrated), '\n' + 80 * '/', '\n')
