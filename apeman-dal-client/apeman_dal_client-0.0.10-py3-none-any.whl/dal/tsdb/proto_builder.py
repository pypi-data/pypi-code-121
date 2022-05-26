from apeman.dal.tsdb import tsdb_pb2
from apeman.dal.tsdb.enum import DataAmount
from apeman.dal.tsdb.enum import DataType


class ColumnDefinitionBuilder(object):

    def __init__(self):
        self.name: str = None
        self.data_type: DataType = None
        self.limit: int = None
        self.non_null: bool = None

    def set_name(self, name: str = None):
        self.name = name
        return self

    def set_type(self, data_type: DataType):
        self.data_type = data_type
        return self

    def set_limit(self, limit: int = None):
        self.limit = limit
        return self

    def set_non_null(self, non_null: bool = None):
        self.non_null = non_null
        return self

    def build(self) -> tsdb_pb2.ColumnDefinition:
        data_type = DataTypeBuilder().set_type(self.data_type).build()
        ret = tsdb_pb2.ColumnDefinition(name=self.name, type=data_type, limit=self.limit,
                                        nonNull=self.non_null)
        return ret


class CreateDatafeedRequestBuilder(object):

    def __init__(self):
        self.name: str = None
        self.tag: [tsdb_pb2.ColumnDefinition] = []
        self.field: [tsdb_pb2.ColumnDefinition] = []
        self.unique_key: [tsdb_pb2.UniqueKey] = []
        self.data_amount: DataAmount = None

    def set_name(self, name: str = None):
        self.name = name
        return self

    def add_tag(self, tag: tsdb_pb2.ColumnDefinition = None):
        self.tag.append(tag)
        return self

    def add_field(self, field: tsdb_pb2.ColumnDefinition = None):
        self.field.append(field)
        return self

    def add_unique_key(self, unique_key: tsdb_pb2.UniqueKey = None):
        self.unique_key.append(unique_key)
        return self

    def set_data_amount(self, data_amount: DataAmount = None):
        self.data_amount = data_amount
        return self

    def build(self) -> tsdb_pb2.CreateDatafeedRequest:
        data_amount = DataAmountBuilder().set_data_amount(self.data_amount).build()
        ret = tsdb_pb2.CreateDatafeedRequest(name=self.name, tag=self.tag, field=self.field,
                                             uniqueKey=self.unique_key, dataAmount=data_amount)
        return ret


class DataAmountBuilder(object):

    def __init__(self):
        self.data_amount: DataAmount = DataAmount.UNKNOWN.value

    def set_data_amount(self, data_amount: DataAmount = DataAmount.UNKNOWN):
        self.data_amount = data_amount.value
        return self

    def build(self) -> tsdb_pb2.DataAmount:
        ret = tsdb_pb2.DataAmount.Value(self.data_amount)
        return ret


class DataTypeBuilder(object):

    def __init__(self):
        self.data_type: DataType = DataType.UNKNOWN.value

    def set_type(self, data_type: DataType = DataType.UNKNOWN):
        self.data_type = data_type.value
        return self

    def build(self) -> tsdb_pb2.DataType:
        ret = tsdb_pb2.DataType.Value(self.data_type)
        return ret


class UniqueKeyBuilder(object):
    def __init__(self):
        self.name: [str] = []

    def __reset__(self):
        self.name = []

    def add(self, name: str = None):
        self.name.append(name)
        return self

    def build(self) -> tsdb_pb2.UniqueKey:
        ret = tsdb_pb2.UniqueKey(name=self.name)
        return ret


class ValBuilder(object):

    def __init__(self):
        self.s = None
        self.i64 = None
        self.i32 = None
        self.d = None
        self.f = None
        self.b = None
        self.ts = None

    def __reset__(self):
        self.s = None
        self.i64 = None
        self.i32 = None
        self.d = None
        self.f = None
        self.b = None
        self.ts = None

    def set_s(self, s: str = None):
        self.s = s
        return self

    def set_i64(self, i64: int = None):
        self.__reset__()
        self.i64 = i64
        return self

    def set_i32(self, i32: int = None):
        self.__reset__()
        self.i32 = i32
        return self

    def set_d(self, d: float = None):
        self.__reset__()
        self.d = d
        return self

    def set_f(self, f: float = None):
        self.__reset__()
        self.f = f
        return self

    def set_b(self, b: bool = None):
        self.__reset__()
        self.b = b
        return self

    def set_ts(self, epoch_in_millis: int = None):
        self.__reset__()
        self.ts = tsdb_pb2.Timestamp(epochInMillis=epoch_in_millis)
        return self

    def build(self) -> tsdb_pb2.Val:
        ret = tsdb_pb2.Val(s=self.s, i64=self.i64, i32=self.i32, d=self.d, f=self.f, b=self.b, ts=self.ts)
        return ret


class TimestampBuilder(object):

    def __init__(self):
        self.epoch_in_millis: int = None

    def set_epoch_in_millis(self, epoch_in_millis: int = None):
        self.epoch_in_millis = epoch_in_millis
        return self

    def build(self) -> tsdb_pb2.Timestamp:
        ret = tsdb_pb2.Timestamp(epochInMillis=self.epoch_in_millis)
        return ret


class TupleBuilder(object):

    def __init__(self):
        self.val: [tsdb_pb2.Val] = []

    def add_val(self, val: tsdb_pb2.Val):
        self.val.append(val)
        return self

    def build(self):
        ret = tsdb_pb2.Tuple(cell=self.val)
        return ret


class ColumnMetaBuilder(object):

    def __init__(self):
        self.data_type: DataType = None
        self.name: str = None

    def set_name(self, name: str):
        self.name = name
        return self

    def set_data_type(self, data_type: DataType):
        self.data_type = data_type
        return self

    def build(self):
        data_type_builder = DataTypeBuilder()
        data_type = data_type_builder.set_type(self.data_type).build()
        ret = tsdb_pb2.ColumnMeta(name=self.name, type=data_type)
        return ret


class TabularDataBuilder(object):

    def __init__(self):
        self.column: [tsdb_pb2.ColumnMeta] = []
        self.tuple: [tsdb_pb2.Tuple] = []

    def add_column(self, column: tsdb_pb2.ColumnMeta):
        self.column.append(column)
        return self

    def add_tuple(self, t: tsdb_pb2.Tuple = None):
        self.tuple.append(t)
        return self

    def build(self):
        ret = tsdb_pb2.TabularData(column=self.column, tuple=self.tuple)
        return ret


class PutDataRequestBuilder(object):

    def __init__(self):
        self.datafeed: str = None
        self.tabular_data: tsdb_pb2.TabularData = None

    def set_datafeed(self, datafeed: str):
        self.datafeed = datafeed
        return self

    def set_tabular_data(self, tabular_data: tsdb_pb2.TabularData):
        self.tabular_data = tabular_data
        return self

    def build(self):
        ret = tsdb_pb2.PutDataRequest(datafeed=self.datafeed, data=self.tabular_data)
        return ret


class OutputColumnBuilder(object):

    def __init__(self):
        self.expr: str = None
        self.alias: str = None

    def set_expr(self, expr: str):
        self.expr = expr
        return self

    def set_alias(self, alias: str):
        self.alias = alias
        return self

    def build(self):
        ret = tsdb_pb2.OutputColumn(expr=self.expr, alias=self.alias)
        return ret


class GetDataRequestBuilder(object):

    def __init__(self):
        self.datafeed: str = None
        self.column: [tsdb_pb2.OutputColumn] = []
        self.where: str = None
        self.group_by: str = None
        self.having: str = None
        self.order_by: str = None
        self.offset: int = 0
        self.limit: int = 100
        self.args: [tsdb_pb2.Val] = []

    def __init__(self, datafeed: str = None, column: tsdb_pb2.OutputColumn = [], where: str = None,
                 group_by: str = None, having: str = None, order_by: str = None, offset: int = 0, limit: int = 100):
        self.datafeed = datafeed
        self.column = column
        self.where = where
        self.group_by = group_by
        self.having = having
        self.order_by = order_by
        self.offset = offset
        self.limit = limit

    def set_datafeed(self, datafeed: str = None):
        self.datafeed = datafeed
        return self

    def add_column(self, column: tsdb_pb2.OutputColumn = None):
        self.column.append(column)
        return self

    def set_where(self, where: str = None):
        self.where = where
        return self

    def set_group_by(self, group_by: str = None):
        self.group_by = group_by
        return self

    def set_having(self, having: str = None):
        self.having = having
        return self

    def set_order_by(self, order_by: str = None):
        self.order_by = order_by
        return self

    def set_offset(self, offset: int = None):
        self.offset = offset
        return self

    def set_limit(self, limit: int = None):
        self.limit = limit
        return self

    def add_arg(self, argument: tsdb_pb2.Val = None):
        self.args.append(argument)
        return self

    def build(self) -> tsdb_pb2.GetDataRequest:
        ret = tsdb_pb2.GetDataRequest(datafeed=self.datafeed, column=self.column, where=self.where,
                                      groupBy=self.group_by, having=self.having, orderBy=self.order_by,
                                      offset=self.offset, limit=self.limit)
        return ret
