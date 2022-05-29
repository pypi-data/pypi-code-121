from typing import Optional

from pydantic import BaseModel


class WatchmenNotebook(BaseModel):
    name:str = None
    storageType:str = None
    storageLocation:str = None
    environment:dict = {}
    dependencies:dict = {}




test = WatchmenNotebook(name="A",storageLocation="")
print(test)


