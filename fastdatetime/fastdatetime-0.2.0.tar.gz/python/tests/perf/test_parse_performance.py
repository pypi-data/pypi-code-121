from datetime import datetime

import fastdatetime
from dateutil import parser


def test_parse_pydateutil(benchmark):    
    result: datetime = benchmark.pedantic(
        parser.parse, 
        args=("July 15th 2018",),
        iterations=1_000, 
        rounds=100,
    )

    assert result.year == 2018
    assert result.month == 7
    assert result.day == 15


def test_parse_fast(benchmark):
    result: datetime = benchmark.pedantic(
        fastdatetime.parse, 
        args=("July 15th 2018",),
        iterations=1_000, 
        rounds=100,
    )

    assert result.year == 2018
    assert result.month == 7
    assert result.day == 15