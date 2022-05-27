from ingestor.common.constants import USER_LABEL
from ingestor.user_rating.constants import VIEWED


class RatingQueryUtils:

    @staticmethod
    def get_user_content_network(graph):
        response = graph.custom_query(
            f'''g.V().hasLabel('{USER_LABEL}').outE('{VIEWED}').inV().path().by(elementMap())''', payload={
                USER_LABEL: USER_LABEL,
                VIEWED: VIEWED
            })
        return response

