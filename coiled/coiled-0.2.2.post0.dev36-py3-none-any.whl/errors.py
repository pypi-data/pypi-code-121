class ServerError(Exception):
    pass


class DoesNotExist(Exception):
    pass


class ClusterCreationError(Exception):
    def __init__(self, message, cluster_id=None):
        self.cluster_id = cluster_id
        super().__init__(
            message + (f" (cluster_id: {cluster_id})" if self.cluster_id else "")
        )
