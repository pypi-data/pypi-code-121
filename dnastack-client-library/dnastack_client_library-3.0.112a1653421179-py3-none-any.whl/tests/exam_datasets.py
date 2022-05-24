from tests.exam_helper import DataConversionSample

data_conversion_samples = (
    # Date
    DataConversionSample.date('2134-06-07',
                              [lambda ts: self.assertEqual(ts.year, 2134),
                               lambda ts: self.assertEqual(ts.month, 6),
                               lambda ts: self.assertEqual(ts.day, 7),
                               ]),

    # Time without time zone
    DataConversionSample.time('12:34:56',
                              [lambda ts: self.assertEqual(ts.microsecond, 0)]),
    DataConversionSample.time('23:45:01.234',
                              [lambda ts: self.assertEqual(ts.microsecond, 234000)]),
    DataConversionSample.time('23:45:01.234567',
                              [lambda ts: self.assertEqual(ts.microsecond, 234567)]),

    # Time with time zone
    DataConversionSample.time_with_time_zone('12:34:56Z',
                                             [self.__assert_utc_time_zone]),
    DataConversionSample.time_with_time_zone('12:34:56-01',
                                             [self.__make_tzinfo_checker('UTC-01:00')]),
    DataConversionSample.time_with_time_zone('12:34:56+01',
                                             [self.__make_tzinfo_checker('UTC+01:00')]),
    DataConversionSample.time_with_time_zone('12:34:56-02:34',
                                             [self.__make_tzinfo_checker('UTC-02:34')]),
    DataConversionSample.time_with_time_zone('12:34:56+02:34',
                                             [self.__make_tzinfo_checker('UTC+02:34')]),
    DataConversionSample.time_with_time_zone('23:45:01.234Z',
                                             [self.__assert_utc_time_zone]),
    DataConversionSample.time_with_time_zone('23:45:01.234-01',
                                             [self.__make_tzinfo_checker('UTC-01:00')]),
    DataConversionSample.time_with_time_zone('23:45:01.234+01',
                                             [self.__make_tzinfo_checker('UTC+01:00')]),
    DataConversionSample.time_with_time_zone('23:45:01.234-02:34',
                                             [self.__make_tzinfo_checker('UTC-02:34')]),
    DataConversionSample.time_with_time_zone('23:45:01.234+02:34',
                                             [self.__make_tzinfo_checker('UTC+02:34')]),
    DataConversionSample.time_with_time_zone('23:45:01.234567Z',
                                             [self.__assert_utc_time_zone]),
    DataConversionSample.time_with_time_zone('23:45:01.234567-01',
                                             [self.__make_tzinfo_checker('UTC-01:00')]),
    DataConversionSample.time_with_time_zone('23:45:01.234567+01',
                                             [self.__make_tzinfo_checker('UTC+01:00')]),
    DataConversionSample.time_with_time_zone('23:45:01.234567-02:34',
                                             [self.__make_tzinfo_checker('UTC-02:34')]),
    DataConversionSample.time_with_time_zone('23:45:01.234567+02:34',
                                             [self.__make_tzinfo_checker('UTC+02:34')]),

    # Timestamp without time zone
    # NOTE: The samples are mixed with both "<date>T<time><tz>" and "<date> <time><tz>" of ISO 8601.
    DataConversionSample.timestamp('2345-06-07 12:34:56',
                                   [lambda ts: self.assertEqual(ts.time().microsecond, 0)]),
    DataConversionSample.timestamp('2345-06-07T23:45:01.234',
                                   [lambda ts: self.assertEqual(ts.time().microsecond, 234000)]),
    DataConversionSample.timestamp('2345-06-07 23:45:01.234567',
                                   [lambda ts: self.assertEqual(ts.time().microsecond, 234567)]),

    # Timestamp with time zone
    # NOTE: The samples are mixed with both "<date>T<time><tz>" and "<date> <time><tz>" of ISO 8601.
    DataConversionSample.timestamp_with_time_zone('2345-06-07 12:34:56Z',
                                                  [lambda ts: self.assertEqual(ts.time().microsecond, 0),
                                                   self.__assert_utc_time_zone]),
    DataConversionSample.timestamp_with_time_zone('2345-06-07T12:34:56-01',
                                                  [self.__make_tzinfo_checker('UTC-01:00')]),
    DataConversionSample.timestamp_with_time_zone('2345-06-07 12:34:56+01',
                                                  [self.__make_tzinfo_checker('UTC+01:00')]),
    DataConversionSample.timestamp_with_time_zone('2345-06-07T12:34:56-02:34',
                                                  [self.__make_tzinfo_checker('UTC-02:34')]),
    DataConversionSample.timestamp_with_time_zone('2345-06-07 12:34:56+02:34',
                                                  [self.__make_tzinfo_checker('UTC+02:34')]),
    DataConversionSample.timestamp_with_time_zone('2345-06-07T23:45:01.234Z',
                                                  [lambda ts: self.assertEqual(ts.time().microsecond, 234000),
                                                   self.__assert_utc_time_zone]),
    DataConversionSample.timestamp_with_time_zone('2345-06-07 23:45:01.234-01',
                                                  [self.__make_tzinfo_checker('UTC-01:00')]),
    DataConversionSample.timestamp_with_time_zone('2345-06-07T23:45:01.234+01',
                                                  [self.__make_tzinfo_checker('UTC+01:00')]),
    DataConversionSample.timestamp_with_time_zone('2345-06-07 23:45:01.234-02:34',
                                                  [self.__make_tzinfo_checker('UTC-02:34')]),
    DataConversionSample.timestamp_with_time_zone('2345-06-07T23:45:01.234+02:34',
                                                  [self.__make_tzinfo_checker('UTC+02:34')]),
    DataConversionSample.timestamp_with_time_zone('2345-06-07 23:45:01.234567Z',
                                                  [lambda ts: self.assertEqual(ts.time().microsecond, 234567),
                                                   self.__assert_utc_time_zone]),
    DataConversionSample.timestamp_with_time_zone('2345-06-07T23:45:01.234567-01',
                                                  [self.__make_tzinfo_checker('UTC-01:00')]),
    DataConversionSample.timestamp_with_time_zone('2345-06-07 23:45:01.234567+01',
                                                  [self.__make_tzinfo_checker('UTC+01:00')]),
    DataConversionSample.timestamp_with_time_zone('2345-06-07T23:45:01.234567-02:34',
                                                  [self.__make_tzinfo_checker('UTC-02:34')]),
    DataConversionSample.timestamp_with_time_zone('2345-06-07 23:45:01.234567+02:34',
                                                  [self.__make_tzinfo_checker('UTC+02:34')]),

    # Interval day to second
    # TODO Implement this
    DataConversionSample.interval_day_to_second('P3DT4H3M2S', []),
    DataConversionSample.interval_day_to_second('PT3M2S', []),
    DataConversionSample.interval_day_to_second('PT4H3M', []),

    # Interval year to month
    # TODO Implement this
    DataConversionSample.interval_year_to_month('P3Y2M', []),
)