import itertools

import numpy as np
from cartesio.utils.json_utils import read


class ProfilingInfo:
    def __init__(self, filename):
        json_data = read(filename)
        self.method = json_data["method"]
        self.channels = {}
        for c in json_data["channels"].keys():
            self.channels[int(c)] = json_data["channels"][c]
        self.separator = json_data["separator"]
        self.conditions = json_data["conditions"]


class CellStainingProfile:
    def __init__(self, infos):
        self.infos = infos
        self.lst = list(itertools.product([0, 1], repeat=len(infos.channels)))
        self.lst = sorted(self.lst, key=lambda c: sum(c), reverse=True)

    def get_profile(self, cell, stainings):
        inside_cell = cell.mask > 0
        labels = []
        profile = []
        channels_true = {}
        channels_false = {}
        for i, channel in self.infos.channels.items():
            channel_data = stainings[:, i]
            name = channel["name"]
            threshold = channel["threshold"]
            channel_true = channel_data >= threshold[0]
            channel_false = ~channel_true
            channels_true[name] = channel_true & inside_cell
            channels_false[name] = channel_false & inside_cell

        for combination in self.lst:
            combination_names = []
            combination_values = []
            for i, channel in self.infos.channels.items():
                name = channel["name"]
                if combination[i] == 1:
                    combination_names.append(name)
                    combination_values.append(channels_true[name])
                else:
                    combination_values.append(channels_false[name])
            s = np.count_nonzero(np.logical_and.reduce(combination_values))
            label_name = f"{self.infos.separator}".join(combination_names)
            labels.append(label_name)
            profile.append(s)

        for i, channel in self.infos.channels.items():
            name = channel["name"]
            labels.append(f"{name}+")
            profile.append(np.count_nonzero(channels_true[name]))

        for i, channel in self.infos.channels.items():
            name = channel["name"]
            labels.append(f"{name}-SUM")
            profile.append(np.sum(stainings[:, i], where=channels_true[name]))
        return profile, labels
