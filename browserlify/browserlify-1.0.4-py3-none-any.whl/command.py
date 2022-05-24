from browserlify.option import Option
import requests


def _build_opt(url, options) -> dict:
    opt = {}
    if options:
        opt = options.payload

    if 'url' not in opt:
        if not url:
            raise Exception('url is required')
        opt['url'] = url

    if 'token' not in opt:
        raise Exception('token is required')

    return opt


def _do_content(function, url, options, endpoint) -> bytes:
    opt = _build_opt(url, options)
    u = '{0}/{1}?token={2}'.format(endpoint, function, opt['token'])
    resp = requests.post(u, json=opt)

    if resp.status_code != 200:
        raise Exception(resp.reason)

    if 'application/json' not in resp.headers['content-type']:
        return resp.content

    result = resp.json()
    if 'url' not in result:
        return resp.content

    result_url = result['url']
    return requests.get(result_url).content


def pdf(url: str, options: Option, endpoint: str = 'https://api.browserlify.com') -> bytes:
    return _do_content('pdf', url, options, endpoint)


def screenshot(url: str, options: Option, endpoint: str = 'https://api.browserlify.com') -> bytes:
    return _do_content('screenshot', url, options, endpoint)


def scrape(url: str, options: Option, endpoint: str = 'https://api.browserlify.com') -> bytes:
    return _do_content('scrape', url, options, endpoint)


def get_content(url: str, options: Option, endpoint: str = 'https://api.browserlify.com') -> bytes:
    return _do_content('content', url, options, endpoint)
