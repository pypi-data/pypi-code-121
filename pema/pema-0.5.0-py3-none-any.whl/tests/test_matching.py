import pema
import numpy as np
from hypothesis import given, strategies, example, settings
import strax


def _create_dummy_records(data_length, n_data_types, truth_length, n_truth_types, max_duration, ):
    _DTYPE = [(('Start time since unix epoch [ns]', 'time'), np.int64),
              (('Exclusive end time since unix epoch [ns]', 'endtime'), np.int64),
              (('Number', 'id'), np.int64),
              (('type of p', 'type'), np.int16),
              (('area of p', 'area'), np.float64)]

    data = np.zeros(data_length, dtype=_DTYPE)
    data['id'] = np.arange(data_length)
    data['time'] = np.random.randint(0, 1e9, data_length)
    data.sort(order='time')

    data['endtime'] = data['time']
    if max_duration:
        # randint does not work for 0, 0 interval, hence we only add it if max_duration>0
        data['endtime'] += np.random.randint(0, max_duration, data_length)
        data['endtime'][:-1] = np.clip(data['endtime'][:-1], data['time'][:-1], data['time'][1:], )
    data['type'] = np.random.randint(0, n_data_types + 1, data_length)

    truth = np.zeros(truth_length, dtype=_DTYPE)
    truth['time'] = np.random.randint(0, 1e9, truth_length)
    truth.sort(order='time')

    truth['endtime'] = truth['time']
    if max_duration:
        # randint does not work for 0, 0 interval, hence we only add it if max_duration>0
        truth['endtime'] += np.random.randint(0, max_duration, truth_length)
        truth['endtime'][:-1] = np.clip(truth['endtime'][:-1], truth['time'][:-1],
                                        truth['time'][1:])
    truth['type'] = np.random.randint(0, n_truth_types + 1, truth_length)
    return data, truth


@settings(max_examples=100, deadline=None)
@given(strategies.integers(min_value=0, max_value=100),
       strategies.integers(min_value=0, max_value=2), )
@example(length=3, dtypenum=0)
def test_combine_and_flip(length, dtypenum):
    """Check that combine and flip works correctly"""
    known_dtypes = (np.bool_, np.int8, np.int64)
    dtype = known_dtypes[dtypenum]
    arr1 = np.random.randint(0, 2, length).astype(dtype)
    arr2 = np.random.randint(0, 2, length).astype(dtype)
    res = (True ^ arr1) & (True ^ arr2)
    numba_res = pema.matching._combine_and_flip(arr1, arr2)
    assert np.all(res == numba_res)


@settings(max_examples=100, deadline=None)
@given(
    # Max length of the data
    strategies.integers(min_value=0, max_value=1000),
    # Max length of the truth
    strategies.integers(min_value=0, max_value=1000),
    # Max duration in [ns]
    strategies.integers(min_value=0, max_value=10_000),
    # Number of peak-types in data
    strategies.integers(min_value=1, max_value=10),
    # Number of peak-types in truth
    strategies.integers(min_value=1, max_value=10),
)
@example(data_length=0,
         truth_length=10,
         max_duration=10,
         n_data_types=2,
         n_truth_types=2)
def test_matching(data_length,
                  truth_length,
                  max_duration,
                  n_data_types,
                  n_truth_types):
    data, truth = _create_dummy_records(data_length,
                                        n_data_types,
                                        truth_length,
                                        n_truth_types,
                                        max_duration,
                                        )
    d_matched, t_matched = pema.match_peaks(data, truth)
    assert len(d_matched) == len(data)
    assert len(t_matched) == len(truth)


@settings(max_examples=100, deadline=None)
@given(
    # Max length of the data
    strategies.integers(min_value=0, max_value=1000),
    # Max length of the truth
    strategies.integers(min_value=0, max_value=1000),
    # Max duration in [ns]
    strategies.integers(min_value=0, max_value=10_000),
    # Number of peak-types in data
    strategies.integers(min_value=0, max_value=10),
    # Number of peak-types in truth
    strategies.integers(min_value=1, max_value=10),
    # Matching fuzz
    strategies.integers(min_value=0, max_value=10_000),
)
@example(data_length=0,
         truth_length=10,
         max_duration=10,
         n_data_types=2,
         n_truth_types=2,
         matching_fuzz=1)
def test_deepwindows(data_length,
                     truth_length,
                     max_duration,
                     n_data_types,
                     n_truth_types,
                     matching_fuzz):
    data, truth = _create_dummy_records(data_length,
                                        n_data_types,
                                        truth_length,
                                        n_truth_types,
                                        max_duration, )
    allpeaks1 = truth.copy()
    allpeaks2 = data.copy()

    windows = strax.touching_windows(allpeaks1, allpeaks2, window=matching_fuzz)
    deepwindows_simple = get_deepwindows(windows, allpeaks1, allpeaks2, matching_fuzz)
    deepwindows_numba = pema.matching.get_deepwindows(windows, allpeaks1, allpeaks2, matching_fuzz)
    if len(deepwindows_simple) > 0 and len(deepwindows_numba) > 0:
        assert np.all(deepwindows_simple == deepwindows_numba)
    assert len(deepwindows_simple) == len(deepwindows_numba)


def get_deepwindows(windows, peaks_a, peaks_b, matching_fuzz):
    """Do it the non-numba way, should work as well but is slower"""
    _deep_windows = []
    for l1, r1 in windows:
        this_window = [-1, -1]
        if r1 - l1:
            match = strax.touching_windows(peaks_a,
                                           peaks_b[l1:r1],
                                           window=matching_fuzz)
            if len(match) > 0:
                this_window = match[0]
            else:
                pass
        _deep_windows.append(this_window)
    deep_windows = np.array(_deep_windows, dtype=(np.int64, np.int64))
    return deep_windows


def test_peak_merges():
    """Test some examples"""
    dtype = [(('outcome of matching', 'outcome'), pema.matching.OUTCOME_DTYPE),
             (('Number', 'id'), np.int64),
             (('matched to', 'matched_to'), np.int64),
             (('type of p', 'type'), np.int16),
             (('area of p', 'area'), np.float64)]
    unknown_types = np.array([0])
    parent = np.zeros(1, dtype=dtype)
    fragment = np.zeros(2, dtype=dtype)

    parent['type'] = 1
    fragment['type'] = 1, 2
    pema.matching.handle_peak_merge(parent[0], fragment, unknown_types)
    assert parent['outcome'] == 'split_and_misid'
    assert fragment[0]['outcome'] == 'merged'
    assert fragment[1]['outcome'] == 'merged_to_s1'

    parent['type'] = 1
    fragment['type'] = 1, 0
    pema.matching.handle_peak_merge(parent[0], fragment, unknown_types)
    assert parent['outcome'] == 'chopped'

    parent['type'] = 1
    fragment['type'] = 1, 2
    pema.matching.handle_peak_merge(parent[0], fragment, unknown_types)
    assert parent['outcome'] == 'split_and_misid'

    parent['type'] = 1
    fragment['type'] = 1, 1
    pema.matching.handle_peak_merge(parent[0], fragment, unknown_types)
    assert parent['outcome'] == 'split'

    parent['type'] = 0
    fragment['type'] = 1, 1
    pema.matching.handle_peak_merge(parent[0], fragment, unknown_types)
    assert fragment[0]['outcome'] == 'merged_to_unknown'

    parent['type'] = 1
    fragment['type'] = 0, 0
    pema.matching.handle_peak_merge(parent[0], fragment, unknown_types)
    assert parent['outcome'] == 'split_and_unclassified'
