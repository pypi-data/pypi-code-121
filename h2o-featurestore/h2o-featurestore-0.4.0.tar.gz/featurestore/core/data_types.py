from . import CoreService_pb2 as pb

TINYINT = pb.FeatureDataType.Name(pb.FeatureDataType.TinyInt).upper()
SMALLINT = pb.FeatureDataType.Name(pb.FeatureDataType.SmallInt).upper()
BIGINT = pb.FeatureDataType.Name(pb.FeatureDataType.BigInt).upper()
INT = pb.FeatureDataType.Name(pb.FeatureDataType.Int).upper()
DOUBLE = pb.FeatureDataType.Name(pb.FeatureDataType.Double).upper()
FLOAT = pb.FeatureDataType.Name(pb.FeatureDataType.Float).upper()
STRING = pb.FeatureDataType.Name(pb.FeatureDataType.String).upper()
BINARY = pb.FeatureDataType.Name(pb.FeatureDataType.Binary).upper()
BOOLEAN = pb.FeatureDataType.Name(pb.FeatureDataType.Boolean).upper()
DATE = pb.FeatureDataType.Name(pb.FeatureDataType.Date).upper()
TIMESTAMP = pb.FeatureDataType.Name(pb.FeatureDataType.Timestamp).upper()
