# Copyright 2022 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.


class ConnectorFilter():
    """A filter to target a particular instance of a Connector that is joined to Cegal Hub Server.
    If a target_connector_id is provided this ensures that a connector with given id will be addressed.
    Alternatively a dictionary of labels may be provided. This dictionary of strings are key - value pairs 
    for labels that a Connector has. Any specified labels must be satisfied by the Connector for that Connector to be targeted.
    A target_connector_id is always used in preference to any labels that are defined."""

    def __init__(self, target_connector_id: str = None, labels_dict=None):
        """Creates a ConnectionFilter from the given parameters

        Args:
            target_connector_id (str, optional): the unique guid representing a particular connector instance. Defaults to None.
            labels_dict ([type], optional): key-value pairs for labels that must be satisfied to target a particular Connector instance. Defaults to None.
        """
        if target_connector_id is None:
            target_connector_id = ""
        self._target_connector_id = target_connector_id
        if labels_dict is None:
            labels_dict = {}
        self._labels_dict = labels_dict

    def __repr__(self):
        return "target_connector_id: " + self._target_connector_id + ", labels:" + repr(self._labels_dict) 

    @property
    def labels_dict(self):
        """The current labels dictionary key values

        Returns:
            [type]: The current key-values labels dictionary
        """        
        return self._labels_dict

    @labels_dict.setter
    def labels(self, labels_dict=None):
        """Update with a new key-values dictionary for the labels

        Args:
            labels_dict ([type], optional): The new dictionary key-values for the labels. Defaults to None.
        """        
        if labels_dict is None:
            labels_dict = {}
        self._labels_dict = labels_dict

    @property
    def target_connector_id(self):
        """Gets the target connector id that the ConnectorFilter will use to target a specific Connector instance

        Returns:
            [str]: The identifier representing the target connector for the ConnectorFilter
        """        
        return self._target_connector_id

    @target_connector_id.setter
    def target_connector_id(self, target_connector_id=None):
        """Updates the ConnectorFilter to set the identifier of the Connector which will be used for targeting

        Args:
            target_connector_id ([str], optional): The identifier of the Connector used for targeting. Defaults to None.
        """        
        if target_connector_id is None:
            target_connector_id = ""
        self._target_connector_id = target_connector_id
    