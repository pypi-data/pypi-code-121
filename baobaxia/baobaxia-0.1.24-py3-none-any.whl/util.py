from pydantic import BaseModel

class GeoLocation(BaseModel):
    latitude: float = .0
    longitude: float = .0
    description: str = ''

def str_to_hash(base: str):
    import hashlib
    return hashlib.md5(base.encode()).hexdigest()


