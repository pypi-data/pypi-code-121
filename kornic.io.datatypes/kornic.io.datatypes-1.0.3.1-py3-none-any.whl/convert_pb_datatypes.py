import edge_core.datatypes.io_property_pb2 as io_prop
import edge_core.datatypes.data_source_property_pb2 as ds_prop


def make_pb_io_value(value: any, data_type: io_prop.IoValue):
    io_value = io_prop.IoValue()
    if data_type == io_prop.DataType.SINT32:
        io_value.sint32_value = int(value)
    elif data_type == io_prop.DataType.SINT64:
        io_value.sint64_value = int(value)
    elif data_type == io_prop.DataType.UINT32:
        io_value.uint32_value = int(value)
    elif data_type == io_prop.DataType.UINT64:
        io_value.uint64_value = int(value)
    elif data_type == io_prop.DataType.FLOAT:
        io_value.float_value = float(value)
    elif data_type == io_prop.DataType.DOUBLE:
        io_value.double_value = float(value)
    elif data_type == io_prop.DataType.STRING:
        io_value.string_value = str(value)
    elif data_type == io_prop.DataType.BYTES:
        io_value.bytes_value = bytes(value)
    elif data_type == io_prop.DataType.BOOL:
        io_value.bool_value = bool(value)
    else:
        io_value.bool_value = bool(value)
    return io_value


pb_enum_tb = {
    'INT': io_prop.DataType.SINT32,
    'SINT32': io_prop.DataType.SINT32,
    'SINT64': io_prop.DataType.SINT64,
    'UINT32': io_prop.DataType.UINT32,
    'UINT64': io_prop.DataType.UINT64,
    'FLOAT': io_prop.DataType.FLOAT,
    'DOUBLE': io_prop.DataType.DOUBLE,
    'STR': io_prop.DataType.STRING,
    'STRING': io_prop.DataType.STRING,
    'BYTES': io_prop.DataType.BYTES,
    'BOOL': io_prop.DataType.BOOL
}


def str_to_data_type(str_data_type: str) -> io_prop.DataType:
    res = io_prop.DataType.UNDEFINED
    dt = str_data_type.upper()
    if dt in pb_enum_tb:
        res = pb_enum_tb[dt]
    return res


def str_to_io_type(str_io_type: str) -> io_prop.IoType:
    if str_io_type.upper() == 'OUTPUT':
        res = io_prop.IoType.OUTPUT
    else:
        res = io_prop.IoType.INPUT
    return res


def str_to_method_type(method_type: io_prop.MethodType) -> str:
    res = None
    if method_type == io_prop.MethodType.READ:
        res = 'READ'
    elif method_type == io_prop.MethodType.WRITE:
        res = 'WRITE'
    return res


def str_to_collection_type(str_collection_type: str) -> ds_prop.CollectionType:
    if str_collection_type.upper() == 'BATCH':
        res = ds_prop.CollectionType.BATCH
    elif str_collection_type.upper() == 'IO':
        res = ds_prop.CollectionType.IO
    elif str_collection_type.upper() == 'STREAM':
        res = ds_prop.CollectionType.STREAM
    else:
        res = ds_prop.CollectionType.IO
    return res


def str_to_dataset_type(str_dataset_type: str) -> io_prop.DatasetType:
    if str_dataset_type.upper() == 'SINGLE':
        res = io_prop.DatasetType.SINGLE
    elif str_dataset_type.upper() == 'MULTI':
        res = io_prop.DatasetType.MULTI
    else:
        res = io_prop.DatasetType.SINGLE
    return res
