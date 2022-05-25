from __future__ import absolute_import

from lendsmart_api.objects import Base, Property

class PredictionSegment(Base):

    api_endpoint = '/prediction_segements'

    properties = {
        "id": Property(identifier=True),
        "created_at": Property(is_datetime=True),
        "updated_at": Property(is_datetime=True),
        "object_meta": Property(mutable=True, filterable=True),
        "type_meta": Property(mutable=True, filterable=True),
        "chunk_segments": Property(mutable=True, filterable=True),
        "status": Property(),
    }

class PredictionInference(Base):

    api_endpoint = '/prediction_inferences'

    properties = {
        "id": Property(identifier=True),
        "created_at": Property(is_datetime=True),
        "updated_at": Property(is_datetime=True),
        "object_meta": Property(mutable=True, filterable=True),
        "type_meta": Property(mutable=True, filterable=True),
        "result": Property(mutable=True, filterable=True),
        "status": Property(),
    }

class PredictionWorkflow(Base):
    api_endpoint = 'prediction_workflows'
    properties = {
        "id": Property(identifier=True),
        "created_at": Property(is_datetime=True),
        "updated_at": Property(is_datetime=True),
        "object_meta": Property(mutable=True, filterable=True),
        "type_meta": Property(mutable=True, filterable=True),
        "mergeable": Property(),
        "inference_considered_valid": Property(),
        "status": Property()
    }
