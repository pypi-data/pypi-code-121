import logging
from typing import Any, Dict, Optional

from fiddler.connection import Connection
from fiddler.project import Project

from ..core_objects import CURRENT_SCHEMA_VERSION, MalformedSchemaException, SegmentInfo
from ..utils.general_checks import type_enforce

LOG = logging.getLogger()


class Segment:
    def __init__(self, connection: Connection, project_id: str, model_id: str) -> None:
        self.connection = connection
        self.project_id = project_id
        self.model_id = model_id

    def list_segments(
        self,
        activated: Optional[bool] = None,
        schema_version: Optional[float] = None,
    ):
        """
        List all segments currently associated with a model. Can filter by activated / schema_version if desired.

        activated = [None/True/False], for all, activated-only, deactivate-only, respectively
        schema_verios = [None/0.1] for all, 0.1 respectively
        """
        res = None
        path = ['list_segments', self.connection.org_id, self.project_id, self.model_id]
        payload: Dict[str, Any] = {}
        payload['activated'] = activated
        payload['schema_version'] = schema_version
        res = self.connection.call(path, json_payload=payload)
        if res is None:
            LOG.warning('Could not get segments for this model.')
        return res

    def upload_segment(
        self,
        segment_id: str,
        segment_info: SegmentInfo,
    ):
        """Validates and uploads an existing SegmentInfo object to Fiddler."""

        model_info = None
        try:
            model_info = (
                Project(self.connection, self.project_id)
                .model(self.model_id)
                .get_info()
            )
        except Exception as e:
            LOG.exception(
                f'Did not find ModelInfo for project "{self.project_id}" and model "{self.model_id}".'
            )
            raise e

        try:
            assert self._validate_segment(segment_id, segment_info, model_info)
        except MalformedSchemaException as mse:
            LOG.exception(
                f'Could not validate SegmentInfo, does the object conform to schema version {CURRENT_SCHEMA_VERSION}?'
            )
            raise mse
        seg_info = segment_info.to_dict()

        res = None
        path = [
            'define_segment',
            self.connection.org_id,
            self.project_id,
            self.model_id,
            segment_id,
        ]
        res = self.connection.call(path, json_payload=seg_info)
        if res is None:
            LOG.warning('Could not create segment.')
        return res

    def activate_segment(self, segment_id: str):
        """Activate an existing segment in Fiddler"""
        segment_id = type_enforce('segment_id', segment_id, str)
        res = None
        path = [
            'activate_segment',
            self.connection.org_id,
            self.project_id,
            self.model_id,
            segment_id,
        ]
        res = self.connection.call(path)
        if res is None:
            LOG.warning('Could not activate segment.')
        return res

    def deactivate_segment(self, segment_id: str):
        """Deactivate an existing segment in Fiddler"""
        segment_id = type_enforce('segment_id', segment_id, str)
        res = None
        path = [
            'deactivate_segment',
            self.connection.org_id,
            self.project_id,
            self.model_id,
            segment_id,
        ]
        res = self.connection.call(path)
        if res is None:
            LOG.warning('Could not deactivate segment.')
        return res

    def delete_segment(self, segment_id: str):
        """Deletes a deactivated segments from Fiddler"""
        segment_id = type_enforce('segment_id', segment_id, str)
        res = None
        path = [
            'delete_segment',
            self.connection.org_id,
            self.project_id,
            self.model_id,
            segment_id,
        ]
        res = self.connection.call(path)
        if res is None:
            LOG.warning('Could not delete segment.')
        return res

    def get_segment_info(self, segment_id: str):
        """Get the SegmentInfo specified from Fiddler"""
        segment_id = type_enforce('segment_id', segment_id, str)
        res = None
        path = [
            'get_segment',
            self.connection.org_id,
            self.project_id,
            self.model_id,
            segment_id,
        ]
        res = self.connection.call(path)
        if res is None:
            LOG.exception('Could not get segment_info.')
            raise RuntimeError('res is unexpectedly None')
        if res['success']:
            return SegmentInfo.from_dict(res['segment_info'])
        else:
            return None

    def _validate_segment(self, segment_id, segment_info, model_info):
        """helper to validate a segment"""
        if segment_info.segment_id != segment_id:
            raise MalformedSchemaException(
                f'Specified segment_id={segment_id} != segment_info.segment_id={segment_info.segment_id}.'
            )
        return segment_info.validate(model_info)
