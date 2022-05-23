
LIN_INSTANCE_TYPES = [
    {
        "cores": 8,
        "memory": 30.0,
        "description": "8 core, 30GB Mem",
        "name": "n1-standard-8",
        "operating_system": "linux"
    },
    {
        "cores": 64,
        "memory": 416.0,
        "description": "64 core, 416GB Mem",
        "name": "n1-highmem-64",
        "operating_system": "linux"
    },
    {
        "cores": 4,
        "memory": 26.0,
        "description": "4 core, 26GB Mem",
        "name": "n1-highmem-4",
        "operating_system": "linux"
    },
    {
        "cores": 32,
        "memory": 208.0,
        "description": "32 core, 208GB Mem",
        "name": "n1-highmem-32",
        "operating_system": "linux"
    }
]

WIN_INSTANCE_TYPES = [
    {
        "cores": 64,
        "memory": 416.0,
        "description": "64 core, 416GB Mem",
        "name": "n1-highmem-64-w",
        "operating_system": "windows"
    },
    {
        "cores": 4,
        "memory": 26.0,
        "description": "4 core, 26GB Mem",
        "name": "n1-highmem-4-w",
        "operating_system": "windows"
    },
    {
        "cores": 32,
        "memory": 208.0,
        "description": "32 core, 208GB Mem",
        "name": "n1-highmem-32-w",
        "operating_system": "windows"
    }
]

ALL_INSTANCE_TYPES = WIN_INSTANCE_TYPES+LIN_INSTANCE_TYPES


# This is useful for printing out the resolved package fixture data. 
# for d in DATA:
#     print(json.dumps(DATA, indent=2))
