#!/usr/bin/python3

from datetime import datetime
import numpy as np

class FieldData(np.ndarray):
     def __array_finalize__(self, obj):
        if obj is None: return
        self.objects_ids = getattr(obj, 'objects_ids', None)
        self.update_time = getattr(obj, 'update_time', None)

     def __new__(cls, data, objects_ids, update_time: datetime = None):
        self = np.asarray(data).view(cls)
        self.objects_ids = np.asarray(objects_ids)
        self.update_time = update_time
        return self
    
     def get_object_id(self, i: int):
         return self.objects_ids[i]

class VTCommandLineArgsBase:
    def __init__(self, metadata_file, execution_url, debug, output_filename, api_access_key, insecure, cert, start_utc, end_utc, field_objects):
        self.metadata_file = metadata_file
        self.execution_url = execution_url
        self.debug = debug
        self.output_filename = output_filename
        self.api_access_key = api_access_key
        self.insecure = insecure
        self.cert = cert
        self.start_utc = start_utc
        self.end_utc = end_utc
        self.field_objects = field_objects
