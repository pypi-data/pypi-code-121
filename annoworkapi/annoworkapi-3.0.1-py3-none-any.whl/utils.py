from __future__ import annotations

import datetime


def str_to_datetime(str_datetime: str) -> datetime.datetime:
    """
    WebAPIがサポートしているISO8601の文字列をdatetime objectに変換します。
    datetime objectはawareです。

    Args:
        str_datetime (str): ISO8601の文字列（例： ``2021-04-01T01:23:45.678Z`` ）

    Returns:
        datetime object
    """
    # 末尾がZだと、datetime.fromisoformatが利用できないので、strptimeでパースする
    return datetime.datetime.strptime(str_datetime, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.timezone.utc)


def datetime_to_str(dt: datetime.datetime) -> str:
    """
    datetime objectをWebAPIがサポートしているISO8601の文字列に変換します。
    datetime objectがnativeの場合、UTCとみなします。

    Args:
        datetime: ISO8601の文字列（例： ``2021-04-01T01:23:45.678Z`` ）

    Returns:
        ISO8601の文字列（例： ``2021-04-01T01:23:45.678Z`` ）

    Raises:
        ValueError: datetimeオブジェクトがnativeなオブジェクト（タイムゾーン情報が含まれていない）のとき
    """
    # strftimeメソッドを利用すると、マイクロ秒まで出力されるので、一旦`isoformat`メソッドでミリ秒まで出力してから、timezoneを"Z"に置換する
    if dt.tzinfo is None:
        raise ValueError("datetimeオブジェクトにはタイムゾーン情報が含まれていません。")
    return dt.astimezone(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")
