###############################################################################
# (c) Copyright 2019 CERN for the benefit of the LHCb Collaboration           #
#                                                                             #
# This software is distributed under the terms of the GNU General Public      #
# Licence version 3 (GPL Version 3), copied verbatim in the file "LICENSE".   #
#                                                                             #
# In applying this licence, CERN does not waive the privileges and immunities #
# granted to it by virtue of its status as an Intergovernmental Organization  #
# or submit itself to any jurisdiction.                                       #
###############################################################################
"""stores a file."""


class File(object):
    def __init__(self):
        """initialize the class members."""
        self.name = ""
        self.type = ""
        self.typeID = -1
        self.version = ""
        self.params = []
        self.replicas = []
        self.qualities = []
        self.fileID = -1

    def addFileParam(self, param):
        """adds a file parameter."""
        self.params += [param]

    def exists(self, fileParam):
        """checks a given parameter."""
        for i in self.params:
            if i.name == fileParam:
                return True
        return False

    def getParam(self, fileParam):
        """returns the file parameters."""
        for i in self.params:
            if i.name == fileParam:
                return i

    def removeFileParam(self, param):
        """removes a file parameter."""
        self.params.remove(param)

    def addReplicas(self, replica):
        """adds a replicas."""
        self.replicas += [replica]

    def __repr__(self):
        """formats the output of print."""
        result = "\n File : \n"
        result += self.name + " " + self.version + " " + self.type

        for param in self.params:
            result += str(param)

        return result

    def writeToXML(self):
        """creates an xml string."""
        string = "  <OutputFile   Name='%s' TypeName='%s' TypeVersion='%s'>\n" % (self.name, self.type, self.version)

        for replica in self.replicas:
            string += replica.writeToXML()

        for param in self.params:
            string += param.writeToXML()

        string += "  </OutputFile>\n"

        return string
