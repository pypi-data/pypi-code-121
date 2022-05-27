import pytest

import tooltime


yes_overlap = [
    [
        (1600000000, 1600000001),
        (1600000001, 1600000002),
    ],
    [
        (1600000001, 1600000002),
        (1600000000, 1600000001),
    ],
    [
        (1600000000, 1600000002),
        (1600000001, 1600000003),
    ],
    [
        (1600000001, 1600000003),
        (1600000000, 1600000002),
    ],
]

no_overlap = [
    [
        (1600000000, 1600000001),
        (1600000002, 1600000003),
    ],
    [
        (1600000002, 1600000003),
        (1600000000, 1600000001),
    ],
]


@pytest.mark.parametrize('timeperiods', yes_overlap)
def test_yes_timeperiods_overlap(timeperiods):
    timeperiod_lhs, timeperiod_rhs = timeperiods
    assert tooltime.timeperiods_overlap(timeperiod_lhs, timeperiod_rhs)


@pytest.mark.parametrize('timeperiods', no_overlap)
def test_no_timeperiods_overlap(timeperiods):
    timeperiod_lhs, timeperiod_rhs = timeperiods
    assert not tooltime.timeperiods_overlap(timeperiod_lhs, timeperiod_rhs)


yes_contains = [
    [
        (1600000000, 1600000003),
        (1600000001, 1600000002),
    ],
    [
        (1600000000, 1600000003),
        (1600000000, 1600000002),
    ],
    [
        (1600000000, 1600000003),
        (1600000001, 1600000003),
    ],
    [
        (1600000000, 1600000003),
        (1600000000, 1600000003),
    ],
]

no_contains = [
    [
        (1600000001, 1600000002),
        (1600000000, 1600000003),
    ],
    [
        (1600000000, 1600000002),
        (1600000000, 1600000003),
    ],
    [
        (1600000001, 1600000003),
        (1600000000, 1600000003),
    ],
]


@pytest.mark.parametrize('timeperiods', yes_contains)
def test_yes_timeperiod_contains(timeperiods):
    timeperiod, other_timeperiod = timeperiods
    assert tooltime.timeperiod_contains(timeperiod, other_timeperiod)


@pytest.mark.parametrize('timeperiods', no_contains)
def test_no_timeperiod_contains(timeperiods):
    timeperiod, other_timeperiod = timeperiods
    assert not tooltime.timeperiod_contains(timeperiod, other_timeperiod)


superset_tests = [
    {
        'superset': (1600000000, 1600000002),
        'timeperiods': [
            (1600000000, 1600000001),
            (1600000001, 1600000002),
        ],
    },
    {
        'superset': (1600000000, 1600000002),
        'timeperiods': [
            (1600000001, 1600000002),
            (1600000000, 1600000001),
        ],
    },
    {
        'superset': (1600000000, 1600000003),
        'timeperiods': [
            (1600000000, 1600000002),
            (1600000001, 1600000003),
        ],
    },
    {
        'superset': (1600000000, 1600000003),
        'timeperiods': [
            (1600000001, 1600000003),
            (1600000000, 1600000002),
        ],
    },
    {
        'superset': (1600000000, 1600000003),
        'timeperiods': [
            (1600000000, 1600000001),
            (1600000002, 1600000003),
        ],
    },
    {
        'superset': (1600000000, 1600000003),
        'timeperiods': [
            (1600000002, 1600000003),
            (1600000000, 1600000001),
        ],
    },
    {
        'superset': (1600000000, 1600000007),
        'timeperiods': [
            (1600000000, 1600000001),
            (1600000006, 1600000007),
        ],
    },
]


@pytest.mark.parametrize('superset_test', superset_tests)
def test_create_superset_timeperiod(superset_test):
    timeperiods = superset_test['timeperiods']
    computed_superset = tooltime.create_superset_timeperiod(*timeperiods)
    assert superset_test['superset'] == computed_superset


create_overlapping_tests = [
    {
        'kwargs': {
            'timeperiod': (1600000000, 1600000010),
        },
        'result': (1600000000, 1600000010),
    },

    # trim
    {
        'kwargs': {
            'timeperiod': (1600000000, 1600000010),
            'trim_start_relative': 0.1,
        },
        'result': (1600000001, 1600000010),
    },
    {
        'kwargs': {
            'timeperiod': (1600000000, 1600000010),
            'trim_start_absolute': '2s',
        },
        'result': (1600000002, 1600000010),
    },
    {
        'kwargs': {
            'timeperiod': (1600000000, 1600000010),
            'trim_end_relative': 0.1,
        },
        'result': (1600000000, 1600000009),
    },
    {
        'kwargs': {
            'timeperiod': (1600000000, 1600000010),
            'trim_end_absolute': '2s',
        },
        'result': (1600000000, 1600000008),
    },

    # extend
    {
        'kwargs': {
            'timeperiod': (1600000000, 1600000010),
            'extend_start_relative': 0.1,
        },
        'result': (1599999999, 1600000010),
    },
    {
        'kwargs': {
            'timeperiod': (1600000000, 1600000010),
            'extend_start_absolute': '2s',
        },
        'result': (1599999998, 1600000010),
    },
    {
        'kwargs': {
            'timeperiod': (1600000000, 1600000010),
            'extend_end_relative': 0.1,
        },
        'result': (1600000000, 1600000011),
    },
    {
        'kwargs': {
            'timeperiod': (1600000000, 1600000010),
            'extend_end_absolute': '2s',
        },
        'result': (1600000000, 1600000012),
    },

]


@pytest.mark.parametrize('create_overlapping_test', create_overlapping_tests)
def test_create_overlapping_timeperiod(create_overlapping_test):
    kwargs = create_overlapping_test['kwargs']
    result = tooltime.create_overlapping_timeperiod(**kwargs)
    assert result == create_overlapping_test['result']

