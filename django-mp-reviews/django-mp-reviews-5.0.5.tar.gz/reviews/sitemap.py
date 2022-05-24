
from seo.sitemaps import get_urls_from_patterns


def get_urls(**kwargs):
    return get_urls_from_patterns([
        'reviews:list'
    ])
