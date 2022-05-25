from python_framework import ResourceManager

import ModelAssociation
from QueueManager import QueueManager


app = ResourceManager.initialize(__name__, ModelAssociation.MODEL, managerList=[
    QueueManager()
])
