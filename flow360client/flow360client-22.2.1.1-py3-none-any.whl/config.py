class Config:
    S3_REGION="us-gov-west-1"
    CASE_BUCKET="flow360cases"
    MESH_BUCKET="flow360meshes"
    STUDIO_BUCKET="flow360studio"
    FLOW360_WEB_API_ENDPONT= "https://flow360-api.simulation.cloud"
    PORTAL_API_ENDPONT = "https://portal-api.simulation.cloud"
    # auth info
    auth = None
    user = None

    #other
    auth_retry = 0
