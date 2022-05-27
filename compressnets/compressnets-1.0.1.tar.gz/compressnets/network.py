import numpy as np
import json


class TemporalNetwork:
    """
    Stores consecutive Snapshot() objects representing static
    adjacency matrices for each snapshot for consecutive time windows.
    """

    def __init__(self, snapshots):
        """
        Create a TemporalNetwork instance from a list of Snapshot objects.

        :param snapshots: list of Snapshot objects
        """
        self.snapshots = snapshots
        self.length = len(snapshots)

    def get_ordered_pairs(self):
        pairs = list([(self.snapshots[i], self.snapshots[i + 1]) for i in range(0, len(self.snapshots) - 1)])
        return pairs

    def get_time_network_map(self):
        return {snapshot.end_time: snapshot.A for snapshot in self.snapshots}

    def equals(self, another_net):
        if self.length != another_net.length:
            return False
        else:
            for i in range(self.length):
                if not self.snapshots[i].equals(another_net.snapshots[i]):
                    return False
        return True

    def set_all_betas(self, new_beta):
        for snapshot in self.snapshots:
            snapshot.set_new_beta(new_beta)


class Snapshot:
    """
    One static network for a single time window of a temporal network.
    Provide instance with start time, end time, adjacency matrix A as a numpy array, and infection rate beta.
    """

    def __init__(self, start_time, end_time, beta, A):
        """

        :param start_time: float or int
        :param end_time: float or int
        :param beta: float between (0,1), infection rate for snapshot
        :param A: numpy array, representing the adjacency matrix
        """
        self.start_time = start_time
        self.end_time = end_time
        self.A = A
        self.N = len(self.A)
        self.beta = beta
        self.duration = self.end_time - self.start_time
        self.dd_normalized = self.set_dd_dist()

    def scaled_matrix(self):
        return self.beta * (self.end_time - self.start_time) * self.A

    def equals(self, another_snapshot):
        return self.start_time == another_snapshot.start_time and self.end_time == another_snapshot.end_time \
               and self.beta == another_snapshot.beta and self.duration == another_snapshot.duration \
               and np.array_equal(self.A, another_snapshot.A)

    def set_dd_dist(self):
        dd = np.array([np.sum(self.A[i]) / self.N for i in range(self.N)])
        if np.sum(dd) == 0:
            return dd
        dd = dd / np.sum(dd)
        return dd

    def set_new_beta(self, new_beta):
        self.beta = new_beta


class TemporalData:
    """
    Helper object to hold list of adjacency matrices and temporal data
    """
    def __init__(self, matrices, interval, beta):
        """

        :param matrices: list of arrays
        :param interval: time interval for each duration of snapshot
        :param beta: desired beta for snapshot infection rate for compression algorithm
        """
        self.matrices = matrices
        self.interval = interval
        self.beta = beta

    def to_snapshot_list(self):
        """
        Generate list of Snapshot objects for each adjacency matrix provided
        :return: list
        """
        m = len(self.matrices)
        times = [t*self.interval for t in range(m)]
        times.append(m*self.interval)
        snapshot_list = list([Snapshot(times[i], times[i+1],
                                       self.beta,
                                       self.matrices[i]) for i in range(m)])
        return snapshot_list



class TemporalNetworkEncoder(json.JSONEncoder):
    """
    Encode a TemporalNetwork object to JSON
    """
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            cont_obj = np.ascontiguousarray(obj)
            assert(cont_obj.flags['C_CONTIGUOUS'])
            return obj.tolist()  ## instead, utilize numpy builtin tolist() method
        try:
            my_dict = obj.__dict__   ## <-- ERROR raised here
        except TypeError:
            pass
        else:
            return my_dict
        return json.JSONEncoder.default(self, obj)


class TemporalNetworkDecoder:

    @staticmethod
    def decode_snapshot(snapshot_as_dict):
        return Snapshot(start_time=snapshot_as_dict['start_time'],
                                    end_time=snapshot_as_dict['end_time'],
                                    beta=snapshot_as_dict['beta'],
                                    A=np.array(snapshot_as_dict['A']))

    def decode(self, fname=None, json_str=None):
        """
        Decode a file or JSON string to a TemporalNetwork object
        :param fname: If stored as json file, provide file name
        :param json_str: If stored in memory as a JSON string, provide string
        :return: TemporalNetwork
        """
        if fname is not None:
            fp = open(fname, 'r')
            loaded_network = json.load(fp)
            fp.close()
        elif json_str is not None:
            loaded_network = json.loads(json_str)
        else:
            raise Exception("Must provide either fname or json_str")
        snapshots_as_list = loaded_network['snapshots']
        snapshots = list([self.decode_snapshot(s) for s in snapshots_as_list])
        return TemporalNetwork(snapshots)
