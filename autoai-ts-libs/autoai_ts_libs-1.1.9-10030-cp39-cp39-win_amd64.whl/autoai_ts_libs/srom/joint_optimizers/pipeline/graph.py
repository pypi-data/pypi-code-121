################################################################################
# IBM Confidential
# OCO Source Materials
# 5737-H76, 5725-W78, 5900-A1R
# (c) Copyright IBM Corp. 2020, 2022. All Rights Reserved.
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.
################################################################################


class SROMGraph(object):
    
    @property
    def stages(self):
        return self._stages

    @property
    def paths(self):
        return self._paths

    @paths.setter
    def paths(self, value):
        self._paths = value

    @property
    def digraph(self):
        return self._graph

    @property
    def number_of_nodes(self):
        return self._graph.number_of_nodes()

    @property
    def number_of_edges(self):
        return self._graph.number_of_edges()
