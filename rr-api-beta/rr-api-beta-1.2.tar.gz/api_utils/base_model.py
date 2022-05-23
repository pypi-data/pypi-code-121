from api_utils.database import conn


class BaseModel:
    class Meta:
        database = conn
