from typing import List

from ascend.protos.schema import schema_pb2

string_schema = schema_pb2.Schema(string=schema_pb2.String())


def Array(name: str, element_schema: schema_pb2.Field) -> schema_pb2.Field:
  return schema_pb2.Field(
      name=name,
      schema=schema_pb2.Schema(array=schema_pb2.Array(element_schema=element_schema)),
  )


def Binary(name: str) -> schema_pb2.Field:
  return schema_pb2.Field(
      name=name,
      schema=schema_pb2.Schema(binary=schema_pb2.Binary()),
  )


def Boolean(name: str) -> schema_pb2.Field:
  return schema_pb2.Field(
      name=name,
      schema=schema_pb2.Schema(boolean=schema_pb2.Boolean()),
  )


def Byte(name: str) -> schema_pb2.Field:
  return schema_pb2.Field(
      name=name,
      schema=schema_pb2.Schema(byte=schema_pb2.Byte()),
  )


def Date(name: str) -> schema_pb2.Field:
  return schema_pb2.Field(
      name=name,
      schema=schema_pb2.Schema(date=schema_pb2.Date()),
  )


def Decimal(name: str, precision: int = 10, scale: int = 0) -> schema_pb2.Field:
  return schema_pb2.Field(name=name, schema=schema_pb2.Schema(decimal=schema_pb2.Decimal(
      precision=precision,
      scale=scale,
  )))


def Dictionary(name: str, key_type: schema_pb2.Field, value_type: schema_pb2.Field) -> schema_pb2.Field:
  return schema_pb2.Field(name=name, schema=schema_pb2.Schema(dictionary=schema_pb2.Dictionary(
      key_schema=key_type.schema,
      value_schema=value_type.schema,
  )))


def Double(name: str) -> schema_pb2.Field:
  return schema_pb2.Field(
      name=name,
      schema=schema_pb2.Schema(double=schema_pb2.Double()),
  )


def Float(name: str) -> schema_pb2.Field:
  return schema_pb2.Field(
      name=name,
      schema=schema_pb2.Schema(float=schema_pb2.Float()),
  )


def Int(name: str) -> schema_pb2.Field:
  return schema_pb2.Field(
      name=name,
      schema=schema_pb2.Schema(int=schema_pb2.Int()),
  )


def Long(name: str) -> schema_pb2.Field:
  return schema_pb2.Field(
      name=name,
      schema=schema_pb2.Schema(long=schema_pb2.Long()),
  )


def Map(name: str, field: List[schema_pb2.Field]) -> schema_pb2.Field:
  return schema_pb2.Field(
      name=name,
      schema=schema_pb2.Schema(map=schema_pb2.Map(field=field)),
  )


def Short(name: str) -> schema_pb2.Field:
  return schema_pb2.Field(
      name=name,
      schema=schema_pb2.Schema(short=schema_pb2.Short()),
  )


def String(name: str) -> schema_pb2.Field:
  return schema_pb2.Field(
      name=name,
      schema=schema_pb2.Schema(string=schema_pb2.String()),
  )


def Timestamp(name: str) -> schema_pb2.Field:
  return schema_pb2.Field(
      name=name,
      schema=schema_pb2.Schema(timestamp=schema_pb2.Timestamp()),
  )


def StringStruct(name: str, fields: List[str]) -> schema_pb2.Field:
  return schema_pb2.Field(
      name=name,
      schema=schema_pb2.Schema(map=schema_pb2.Map(field=[schema_pb2.Field(name=n, schema=string_schema) for n in fields])),
  )


def StringArray(name: str) -> schema_pb2.Field:
  return schema_pb2.Field(
      name=name,
      schema=schema_pb2.Schema(array=schema_pb2.Array(element_schema=string_schema)),
  )
