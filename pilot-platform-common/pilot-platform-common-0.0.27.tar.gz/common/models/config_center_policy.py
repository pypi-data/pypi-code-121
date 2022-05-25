class ConfigCenterPolicy:
    @staticmethod
    def get_granted(srv_namespace):
        return {'service_download': ConfigCenterPolicy.service_download()}.get(srv_namespace, [])

    @staticmethod
    def service_download():
        return [
            'DOWNLOAD',
            'KEYCLOAK',
            'MINIO',
            'REDIS',
            'NEO4J_SERVICE',
            'PROVENANCE_SERVICE',
            'QUEUE_SERVICE',
            'UTILITY_SERVICE',
            'DATA_OPS_GR',
            'DATA_OPS_UTIL',
            'DATASET_SERVICE',
            'RDS_HOST',
            'RDS_PORT',
            'RDS_USER',
            'RDS_PWD',
            'RDS_DBNAME',
            'RDS_SCHEMA_DEFAULT',
            'OPEN_TELEMETRY_ENABLED',
            'CORE_ZONE_LABEL',
            'GREEN_ZONE_LABEL',
        ]
