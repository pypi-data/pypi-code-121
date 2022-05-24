"""
# 	{
# 	    "name": "nPoints",
# 	    "description": "number of points"
# 	}
"""

class Dimension:
    """ A dimension"""

    def __init__(self, name:str, description:str=None) -> None:
        self.name = name
        self.description = description
