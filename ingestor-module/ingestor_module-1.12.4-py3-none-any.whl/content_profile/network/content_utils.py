from graphdb import Node

from ingestor.common import CONTENT_CORE_ID, SEASON_ID, LABEL, SEASON, PROPERTIES, SEASON_NAME, CONTENT_CORE_SYNOPSIS, \
    CONTENT_CORE_SYNOPSIS_EN, CONTENT_CORE, CONTENT_CORE_TITLE, CONTENT_CORE_EPISODE, CREATED_ON, MODIFIED_ON


class ContentUtils:

    @staticmethod
    def prepare_content_core_properties(props, graph):
        final_content_core_props = {}
        if CONTENT_CORE_ID in props:
            ContentUtils.add_content_core_properties(final_content_core_props, props, graph)
            ContentUtils.add_content_core_synopsis(final_content_core_props, props, graph)
            ContentUtils.add_season(final_content_core_props, props, graph)
        return final_content_core_props

    @staticmethod
    def add_season(final_content_core_props, props, graph):
        if SEASON_ID in props:
            node_content_season = Node(**{LABEL: SEASON, PROPERTIES: {SEASON_ID: props[SEASON_ID]}})
            node_content_season = graph.find_node(node_content_season)
            final_content_core_props[SEASON_NAME] = node_content_season[0].properties[SEASON_NAME]

    @staticmethod
    def add_content_core_synopsis(final_content_core_props, props, graph):
        node_content_core_synopsis = Node(
            **{LABEL: CONTENT_CORE_SYNOPSIS, PROPERTIES: {CONTENT_CORE_ID: props[CONTENT_CORE_ID]}})
        node_content_core_synopsis = graph.find_node(node_content_core_synopsis)
        if len(node_content_core_synopsis) > 0:
            final_content_core_props[CONTENT_CORE_SYNOPSIS] = node_content_core_synopsis[0].properties[
                CONTENT_CORE_SYNOPSIS]
            final_content_core_props[CONTENT_CORE_SYNOPSIS_EN] = node_content_core_synopsis[0].properties[
                CONTENT_CORE_SYNOPSIS_EN]

    @staticmethod
    def add_content_core_properties(final_content_core_props, props, graph):
        node_content_core = Node(
            **{LABEL: CONTENT_CORE, PROPERTIES: {CONTENT_CORE_ID: props[CONTENT_CORE_ID]}})
        node_content_core = graph.find_node(node_content_core)
        final_content_core_props[CONTENT_CORE_ID] = node_content_core[0].properties[CONTENT_CORE_ID]
        final_content_core_props[CONTENT_CORE_TITLE] = node_content_core[0].properties[CONTENT_CORE_TITLE]
        final_content_core_props[CONTENT_CORE_EPISODE] = node_content_core[0].properties[CONTENT_CORE_EPISODE]
        final_content_core_props[CREATED_ON] = node_content_core[0].properties[CREATED_ON]
        final_content_core_props[MODIFIED_ON] = node_content_core[0].properties[MODIFIED_ON]