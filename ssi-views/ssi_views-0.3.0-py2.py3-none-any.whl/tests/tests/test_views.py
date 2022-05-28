import django
from django.test import Client


def test_404():
    client = Client()
    response = client.get('/ssi/unknown/')
    assert response.status_code == 404


def test_overriden_view():
    client = Client()
    response = client.get('/ssi/tests.simple/')
    assert response.status_code == 200
    assert response.content == b'But she hears only whispers of some quiet conversation'


def test_get():
    client = Client()
    get_response = client.get('/ssi/tests.method-get/')
    assert get_response.status_code == 200
    assert get_response.content == b'She\'s coming in twelve-thirty flight'

    post_response = client.post('/ssi/tests.method-get/')
    assert post_response.status_code == 405

    head_response = client.head('/ssi/tests.method-get/')
    assert head_response.status_code == 405


def test_cached():
    client = Client()
    response = client.get('/ssi/tests.cached/')
    assert response.status_code == 200
    assert response.content == b'Her moonlit wings reflect the stars that guide me towards salvation'

    cache_directives = set(map(str.strip, str(response['Cache-Control']).split(',')))
    assert cache_directives == {'max-age=0', 's-maxage=30', 'must-revalidate'}


def test_decorators():
    client = Client()
    response = client.get('/ssi/tests.never_cached/')
    assert response.status_code == 200
    assert response.content == b'I stopped an old man along the way'

    cache_directives = set(map(str.strip, str(response['Cache-Control']).split(',')))
    if django.VERSION >= (3, 0):
        assert cache_directives == {'max-age=0', 'no-cache', 'no-store', 'must-revalidate', 'private'}
    else:
        assert cache_directives == {'max-age=0', 'no-cache', 'no-store', 'must-revalidate'}


def test_cbv():
    client = Client()
    get_response = client.get('/ssi/tests.simple_cbv/')
    assert get_response.status_code == 200
    assert get_response.content == b'There\'s nothing that a hundred men or more could ever do'

    head_response = client.head('/ssi/tests.simple_cbv/')
    assert head_response.status_code == 200

    post_response = client.post('/ssi/tests.simple_cbv/')
    assert post_response.status_code == 405


def test_multiname():
    client = Client()
    response = client.get('/ssi/tests.foo/')
    assert response.status_code == 200
    assert response.content == b'He turned to me as if to say: Hurry boy, it\'s waiting there for you'

    response = client.get('/ssi/tests.bar/')
    assert response.status_code == 200
    assert response.content == b'He turned to me as if to say: Hurry boy, it\'s waiting there for you'

    response = client.get('/ssi/tests.baz/')
    assert response.status_code == 200
    assert response.content == b'He turned to me as if to say: Hurry boy, it\'s waiting there for you'
