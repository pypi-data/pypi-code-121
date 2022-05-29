# -*- Coding: utf-8 -*-

"""Helper class needed for the stevedore integration. Needs to provide
a description() method that returns a dict containing a description of
this node, and a factory() method for creating the graphical and non-graphical
nodes."""

import forcefield_step


class ForcefieldStep(object):
    my_description = {
        "description": "An interface for the setup and control of the forcefield",
        "group": "Simulations",
        "name": "Forcefield",
    }

    def __init__(self, flowchart=None, gui=None):
        """Initialize this helper class, which is used by
        the application via stevedore to get information about
        and create node objects for the flowchart
        """
        pass

    def description(self):
        """Return a description of what this extension does"""
        return ForcefieldStep.my_description

    def create_node(self, flowchart=None, **kwargs):
        """Return a new node object"""
        return forcefield_step.Forcefield(flowchart=flowchart, **kwargs)

    def create_tk_node(self, canvas=None, **kwargs):
        """Return the graphical Tk node object"""
        return forcefield_step.TkForcefield(canvas=canvas, **kwargs)
