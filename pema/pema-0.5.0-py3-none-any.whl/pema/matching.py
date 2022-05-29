"""
Utility to match peaks from results of different processor versions / processor and simulator
"""
import numpy as np
import strax
import numba
import logging
from numpy.lib import recfunctions

log = logging.getLogger('Pema matching')

export, __all__ = strax.exporter()

INT_NAN = -99999
OUTCOME_DTYPE = '<U32'


@export
def match_peaks(allpeaks1,
                allpeaks2,
                matching_fuzz=0,
                unknown_types=(0,)):
    """
    Perform peak matching between two numpy record arrays with fields:
        time, endtime (or dt and length), id, type, area
    If a peak is split into many fragments (e.g. two close peaks split
    into three peaks), the results are unreliable and depend on which
    peak set is peaks1 and which is peaks2.

    Returns (allpeaks1, allpeaks2), each with two extra fields:
    outcome, matched_to:
        outcome: Can be one of:
            found:  Peak was matched 1-1 between peaks1 and peaks2 (type agrees,
             no other peaks in range).
                    Note that area, widths, etc. can still be quite different!
            missed: Peak is not present in the other list
            misid_as_XX: Peak is present in the other list, but has type XX
            merged: Peak is merged with another peak in the other list, the new
                'super-peak' has the same type
            merged_to_XX: As above, but 'super-peak' has type XX
            split: Peak is split in the other list, but more than one fragment
                has the same type as the parent.
            chopped: As split, but one or several fragments are unclassified,
                exactly one has the correct type.
            split_and_unclassified: As split, but all fragments are unclassified
                in the other list.
            split_and_misid: As split, but at least one fragment has a different
                peak type.
        matched_to: id of matching in *peak* in the other list if outcome is found
            or misid_as_XX, INT_NAN otherwise.
    """
    # Check required fields
    for i, d in enumerate((allpeaks1, allpeaks2)):
        assert hasattr(d, 'dtype'), 'Cannot work with non-numpy arrays'
        m = ''
        for k in ('area', 'type', 'id'):
            if k not in d.dtype.names:
                m += f'Argument {i} misses field {k} required for matching \n'
        if m != '':
            raise ValueError(m)
    log.debug('Appending fields')
    # Append id, outcome and matched_to fields
    allpeaks1 = append_fields(
        allpeaks1,
        ('outcome', 'matched_to'),
        (np.array(['missed'] * len(allpeaks1), dtype=OUTCOME_DTYPE),
         INT_NAN * np.ones(len(allpeaks1), dtype=np.int64)),
        dtypes=(OUTCOME_DTYPE, np.int64),
    )
    allpeaks2 = append_fields(
        allpeaks2,
        ('outcome', 'matched_to'),
        (np.array(['missed'] * len(allpeaks2), dtype=OUTCOME_DTYPE),
         INT_NAN * np.ones(len(allpeaks2), dtype=np.int64)),
        dtypes=(OUTCOME_DTYPE, np.int64),
    )

    log.debug('Getting windows')
    windows = strax.touching_windows(allpeaks1, allpeaks2, window=matching_fuzz)
    deep_windows = np.empty((0, 2), dtype=(np.int64, np.int64))
    # Each of the windows projects to a set of peaks in allpeaks2
    # belonging to allpeaks1. We also need to go the reverse way, which
    # I'm calling deep_windows below.
    if len(windows):
        # The order matters!! We matched allpeaks1->allpeaks2 so we now should match allpeaks2->allpeaks1
        deep_windows = get_deepwindows(windows, allpeaks2, allpeaks1, matching_fuzz)
        log.debug(f'Got {len(deep_windows)} deep windows and {len(windows)} windows')

    if not len(windows):
        # patch for empty data
        deep_windows = np.array([[-1, -1]], dtype=(np.int64, np.int64))
    assert np.shape(np.shape(deep_windows))[0] == 2, (
        f'deep_windows shape is wrong {np.shape(deep_windows)}\n{deep_windows}')

    # make array for numba
    unknown_types = np.array(unknown_types)

    # Inner matching
    _match_peaks(allpeaks1, allpeaks2, windows, deep_windows, unknown_types)
    return allpeaks1, allpeaks2


@numba.jit(nopython=True, nogil=True, cache=True)
def _match_peaks(allpeaks1, allpeaks2, windows, deep_windows, unknown_types):
    """See match_peaks_strax where we do the functional matching here"""
    # Loop over left and right bounds for peaks 1 by matching to peaks 2
    for peaks_1_i, (l1, r1) in enumerate(windows):
        peaks_1 = allpeaks1[l1:r1]
        if l1 == r1:
            continue

        for p1_i, p1 in enumerate(peaks_1):
            # Matching the other way around using deep_windows
            l2, r2 = deep_windows[peaks_1_i]

            peaks_2 = allpeaks2[l2:r2]
            matching_peaks = peaks_2
            if len(matching_peaks) == 0:
                pass

            elif len(matching_peaks) == 1:
                # A unique match! Hurray!
                p2 = matching_peaks[0]
                p1['matched_to'] = p2['id']
                p2['matched_to'] = p1['id']
                # Do the types match?
                if p1['type'] == p2['type']:
                    p1['outcome'] = 'found'
                    p2['outcome'] = 'found'
                else:
                    if _in(p1['type'], unknown_types):
                        p2['outcome'] = 'unclassified'
                    else:
                        p2['outcome'] = 'misid_as_s' + str(p1['type'])
                    if _in(p2['type'], unknown_types):
                        p1['outcome'] = 'unclassified'
                    else:
                        p1['outcome'] = 'misid_as_s' + str(p2['type'])
                    # If the peaks are unknown in both sets, they will
                    # count as 'found'.
                matching_peaks[0] = p2
            else:
                # More than one peak overlaps p1
                handle_peak_merge(parent=p1,
                                  fragments=matching_peaks,
                                  unknown_types=unknown_types)

            # matching_peaks is a copy, not a view, so we have to copy
            # the results over to peaks_2 manually Sometimes I wish
            # python had references...
            for i_in_matching_peaks, i_in_peaks_2 in enumerate(range(l2, r2)):
                allpeaks2[i_in_peaks_2] = matching_peaks[i_in_matching_peaks]

        # Match in reverse to detect merged peaks >1 peaks in 1 may
        # claim to be matched to a peak in 2, in which case we should
        # correct the outcome...
        for p2_i, p2 in enumerate(peaks_2):
            selection = peaks_1['matched_to'] == p2['id']
            matching_peaks = peaks_1[selection]
            if len(matching_peaks) > 1:
                handle_peak_merge(parent=p2,
                                  fragments=matching_peaks,
                                  unknown_types=unknown_types)

            # matching_peaks is a copy, not a view, so we have to copy
            # the results over to peaks_1 manually Sometimes I wish
            # python had references...
            for i_in_matching_peaks, i_in_peaks_1 in enumerate(
                    np.where(selection)[0]):
                peaks_1[i_in_peaks_1] = matching_peaks[i_in_matching_peaks]


@numba.jit(nopython=True)
def handle_peak_merge(parent, fragments, unknown_types):
    found_types = fragments['type']
    is_ok = found_types == parent['type']
    is_unknown = _in1d(found_types, unknown_types)
    is_misclass = _combine_and_flip(is_ok, is_unknown)
    # We have to loop over the fragments to avoid making a copy
    for i in range(len(fragments)):
        if is_unknown[i] or is_misclass[i]:
            if _in(parent['type'], unknown_types):
                fragments[i]['outcome'] = 'merged_to_unknown'
            else:
                fragments[i]['outcome'] = 'merged_to_s' + str(parent['type'])
        else:
            fragments[i]['outcome'] = 'merged'
        # Link the fragments to the parent
        fragments[i]['matched_to'] = parent['id']
    if np.any(is_misclass):
        parent['outcome'] = 'split_and_misid'
    # All fragments are either ok or unknown. If more than one fragment
    # is given the same class as the parent peak, then call it "split".
    elif len(np.where(is_ok)[0]) > 1:
        parent['outcome'] = 'split'
    elif np.all(is_unknown):
        parent['outcome'] = 'split_and_unclassified'
    # If exactly one fragment out of > 1 fragments is correctly
    # classified, then call the parent chopped
    else:
        parent['outcome'] = 'chopped'
    # We can't link the parent to all fragments. Link to the largest one
    _max_idx = _argmax(fragments['area'])
    parent['matched_to'] = fragments[_max_idx]['id']


@numba.jit(cache=True)
def get_deepwindows(windows, peaks_a, peaks_b, matching_fuzz):
    """Get matching window of the matched peak versus the original peak"""
    n_windows = len(windows)
    _deep_windows = np.ones((n_windows, 2), dtype=np.int64) * -1
    return _get_deepwindows(windows, peaks_a, peaks_b, matching_fuzz, _deep_windows)


@numba.njit(nogil=True, cache=True)
def _get_deepwindows(windows, peaks_a, peaks_b, matching_fuzz, _deep_windows):
    # Calculate the endtimes once
    peak_a_endtimes = strax.endtime(peaks_a)
    peak_b_endtimes = strax.endtime(peaks_b)

    # If we previously started on an index, the next index will not be 
    # before this, if we start here, we save time.
    prev_start = 0
    for window_i, w in enumerate(windows):
        l1, r1 = w
        if r1 - l1:
            match = strax.processing.general._touching_windows(
                peaks_a['time'][prev_start:], peak_a_endtimes[prev_start:],
                peaks_b[l1:r1]['time'], peak_b_endtimes[l1:r1],
                window=matching_fuzz)
            if len(match):
                # We have skipped the first prev_start items, add here
                this_window = match[0] + prev_start
                _deep_windows[window_i] = this_window
                prev_start = max(match[0][0], prev_start)
            else:
                # No match
                pass
    return _deep_windows


@export
def append_fields(base, names, data, dtypes=None, fill_value=-1,
                  usemask=False,  # Different from recfunctions default
                  asrecarray=False):
    """Append fields to numpy structured array
    Does nothing if array already has fields with the same name.
    """
    if isinstance(names, (tuple, list)):
        not_yet_in_data = True ^ np.in1d(names, base.dtype.names)
        if dtypes is None:
            dtypes = [d.dtype for d in data]
        # Add multiple fields at once
        return recfunctions.append_fields(
            base,
            np.array(names)[not_yet_in_data].tolist(),
            np.array(data)[not_yet_in_data].tolist(),
            np.array(dtypes)[not_yet_in_data].tolist(),
            fill_value,
            usemask,
            asrecarray)
    else:
        # Add single field
        if names in base.dtype.names:
            return base
        else:
            return recfunctions.append_fields(
                base, names, data, dtypes, fill_value, usemask, asrecarray)


# --- Numba functions where numpy does not suffice ---
@numba.njit
def _in1d(arr1, arr2):
    """
    Copy np.in1d logic for numba
    Five times faster than numpy #ohyeah
    """
    res = np.zeros(len(arr1), dtype=np.bool_)
    for i1 in range(len(arr1)):
        for v2 in arr2:
            if arr1[i1] == v2:
                res[i1] = 1
                break
    return res


@numba.jit(nopython=True)
def _in(val, arr):
    """
    Check if val is in array
    1.5x faster than val in np.array
    """
    for a in arr:
        if val == a:
            return True
    return False


@numba.jit(nopython=True)
def _argmax(arr):
    """
    Get index of max argument (np.argmax)
    Slightly faster than np.argmax
    """
    m = INT_NAN
    i = INT_NAN
    leng = len(arr)
    for j in range(leng):
        if arr[j] > m:
            m = arr[j]
            i = j
    return i


@numba.njit
def _combine_and_flip(arr1, arr2):
    """Combine the flipped arrays"""
    return _bool_flip(arr1).astype(np.bool_) & _bool_flip(arr2.astype(np.bool_))


@numba.njit
def _bool_flip(arr):
    """Use True ^ array"""
    res = np.zeros(len(arr), dtype=np.bool_)
    for i, a in enumerate(arr):
        if not a or a == 0:
            res[i] = 1
    return res
