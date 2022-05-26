import rapyuta_io
from rapyuta_io.utils.object_converter import ObjBase, enum_field


class InternalDeploymentStatus(ObjBase):
    """
    InternalDeploymentStatus represents Internal Deployment Status.

    :ivar phase: phase of the internal deployment
    :vartype phase: :py:class:`rapyuta_io.clients.deployment.DeploymentPhaseConstants`
    :ivar status: (full-only) status of the internal deployment
    :vartype status: :py:class:`rapyuta_io.clients.deployment.DeploymentStatusConstants`
    :ivar error_code: error code of the internal deployment
    :vartype error_code: list(str)

    :param phase: phase of the internal deployment
    :type phase: :py:class:`rapyuta_io.clients.deployment.DeploymentPhaseConstants`
    :param status: status of the internal deployment
    :type status: :py:class:`rapyuta_io.clients.deployment.DeploymentStatusConstants`
    :param error_code: error code of the internal deployment
    :type error_code: list(str)
    """
    def __init__(self, phase, status=None, error_code=None):
        self.phase = phase
        self.status = status
        self.error_code = error_code

    def get_deserialize_map(self):
        return {
            'phase': enum_field('phase', rapyuta_io.DeploymentPhaseConstants),
            'status': enum_field('status', rapyuta_io.DeploymentStatusConstants),
            'error_code': 'error_code'
        }

    def get_serialize_map(self):
        return {}
