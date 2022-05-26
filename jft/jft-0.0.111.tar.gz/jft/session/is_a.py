from requests.sessions import Session
from requests import session
f = lambda x: isinstance(x, Session)
t = lambda: all([f(session()), not f('a')])
