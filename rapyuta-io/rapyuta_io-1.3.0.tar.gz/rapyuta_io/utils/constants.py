NON_PACKAGE_ATTRIBUTES = ['ID', 'id', 'name', 'ownerProject', 'CreatedAt', 'UpdatedAt',
                          'DeletedAt', 'guid', 'metadata']
NON_DEPLOYMENT_ATTRIBUTES = ['ID', 'creator', 'CreatedAt', 'UpdatedAt', 'DeletedAt', 'ownerProject'
                             'errors', 'dependentDeploymentStatus',
                             'packageDependencyStatus']
NON_PLAN_ATTRIBUTES = ['ID', 'id', 'DeletedAt', 'UpdatedAt', 'CreatedAt']

DEPLOYMENT_STATUS_ATTRIBUTES = ['deploymentId', 'planId', 'packageId', 'status', 'phase',
                                'errors', 'componentInfo', 'dependentDeploymentStatus',
                                'packageDependencyStatus']

NON_VOLUME_INSTANCE_ATTRIBUTES = ['ID', 'id', 'creator', 'ownerProject', 'CreatedAt',
                                  'UpdatedAt', 'DeletedAt', 'guid', 'metadata']

VOLUME_INSTANCE_STATUS_ATTRIBUTES = ['deploymentId', 'name', 'planId', 'packageId', 'status', 'phase',
                                     'errors', 'componentInfo', 'dependentDeploymentStatus',
                                     'packageDependencyStatus']

DEVICE = 'device'
LABELS = 'labels'
DEVICE_ID = 'device_id'
