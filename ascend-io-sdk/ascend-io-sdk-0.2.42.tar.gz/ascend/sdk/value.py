import ascend.protos.ascend.ascend_pb2 as ascend


def Bool(value: bool) -> ascend.Value:
  return ascend.Value(bool_value=value)


def Date(value=None) -> ascend.Value:
  return ascend.Value(date_value=value)


def DateTime(value=None) -> ascend.Value:
  return ascend.Value(datetime_value=value)


def Double(value=None) -> ascend.Value:
  return ascend.Value(double_value=value)


def Int(value: int) -> ascend.Value:
  return ascend.Value(int_value=value)


def Long(value=None) -> ascend.Value:
  return ascend.Value(long_value=value)


def Short(value=None) -> ascend.Value:
  return ascend.Value(short_value=value)


def String(value: str) -> ascend.Value:
  return ascend.Value(string_value=value)


def Struct(fields=None) -> ascend.Value:
  return ascend.Value(struct_value=ascend.Struct(fields=fields))


def Timestamp(value=None) -> ascend.Value:
  return ascend.Value(timestamp_value=value)


def Union(tag=None, fields=None, **kwargs):
  if tag is not None:
    assert not kwargs, f"Union should be defined in one of two ways: Union(tag='my_option', fields=my_option_fields) or Union(my_option=my_option_value)"
    union_value = ascend.Union(tag=tag, value=fields if isinstance(fields, ascend.Value) else Struct(fields or {}))
  else:
    assert fields is None and len(kwargs) <= 1, \
      f"Union should be defined in one of two ways: Union(tag='my_option', fields=my_option_fields) or Union(my_option=my_option_value)"
    maybe_case = next(iter(kwargs.items()), None)
    union_value = ascend.Union() if maybe_case is None else ascend.Union(tag=maybe_case[0], value=Struct(maybe_case[1]))

  return ascend.Value(union_value=union_value)
