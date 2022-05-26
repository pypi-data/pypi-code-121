from apeman.dal.tsdb import ColumnDefinitionBuilder, CreateDatafeedRequestBuilder, \
    UniqueKeyBuilder
from apeman.dal.tsdb.enum import DataAmount
from apeman.dal.tsdb.enum import DataType
from apeman.dal.tsdb.proto_builder import TabularDataBuilder, ColumnMetaBuilder, TupleBuilder, ValBuilder, \
    DataAmountBuilder, DataTypeBuilder, TimestampBuilder, PutDataRequestBuilder, OutputColumnBuilder, \
    GetDataRequestBuilder
import time

from apeman.dal.tsdb import tsdb_client

print(tsdb_client)
test_val = ValBuilder().set_ts(epoch_in_millis=int(time.time()*1000)).build()
print(test_val)
# build create datafeed request
tag = ColumnDefinitionBuilder() \
    .set_name(name='tag_nae') \
    .set_non_null(non_null=True) \
    .set_type(data_type=DataType.TEXT) \
    .set_limit(limit=100).build()

field = ColumnDefinitionBuilder() \
    .set_name(name='field_name') \
    .set_non_null(non_null=True) \
    .set_type(data_type=DataType.TEXT) \
    .set_limit(limit=100).build()

data_type_builder = DataTypeBuilder().set_type(data_type=DataType.TEXT)
data_type = data_type_builder.build()

unique_key = UniqueKeyBuilder().add(name='tag_name').build()
unique_key_2 = UniqueKeyBuilder().add(name='field_name').build()

data_amount = DataAmountBuilder().set_data_amount(data_amount=DataAmount.SMALL).build()

create_datafeed_request = CreateDatafeedRequestBuilder() \
    .set_name(name='test') \
    .add_tag(tag=tag) \
    .add_field(field=field) \
    .add_unique_key(unique_key=unique_key) \
    .add_unique_key(unique_key=unique_key_2) \
    .set_data_amount(data_amount=DataAmount.SMALL) \
    .build()

column_a = ColumnMetaBuilder() \
    .set_name(name='column_a') \
    .set_data_type(data_type=DataType.TEXT) \
    .build()
column_b = ColumnMetaBuilder() \
    .set_name(name='column_b') \
    .set_data_type(data_type=DataType.BIGINT) \
    .build()

tuple_a = TupleBuilder() \
    .add_val(val=ValBuilder().set_i32(1000).build()) \
    .add_val(val=ValBuilder().set_i32(1000).build()) \
    .add_val(val=ValBuilder().set_i32(1000).build()) \
    .add_val(val=ValBuilder().set_i32(1000).build()) \
    .build()

tuple_b = TupleBuilder() \
    .add_val(val=ValBuilder().set_i32(1000).build()) \
    .add_val(val=ValBuilder().set_i32(1000).build()) \
    .add_val(val=ValBuilder().set_i32(1000).build()) \
    .add_val(val=ValBuilder().set_i32(1000).build()) \
    .build()

data = TabularDataBuilder() \
    .add_column(column=column_a) \
    .add_column(column=column_b) \
    .add_tuple(t=tuple_a) \
    .add_tuple(t=tuple_b) \
    .build()

ts_builder = TimestampBuilder().set_epoch_in_millis(epoch_in_millis=1000)
ts = ts_builder.build()

put_data_request_builder = PutDataRequestBuilder().set_datafeed(datafeed='test').set_tabular_data(tabular_data=data)
put_data_request = put_data_request_builder.build()

output_column_builder = OutputColumnBuilder().set_expr(expr='test').set_alias(alias='test')
output_column = output_column_builder.build()

get_data_request_builder = GetDataRequestBuilder()  \
                .add_column(column=output_column)  \
                .add_column(column=output_column)  \
                .set_datafeed(datafeed='test')  \
                .set_where(where='')  \
                .set_group_by(group_by='')  \
                .set_having(having='')  \
                .set_order_by(order_by='')  \
                .set_offset(offset=0)  \
                .set_limit(limit=100)  \
                .build()
