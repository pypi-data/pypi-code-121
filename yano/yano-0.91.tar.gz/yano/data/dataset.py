from .loaddata import fileinfo, loaddata




class dataset(object):

    def __init__(s, key, x=None, y=None, autoload=False):
        key=str(key)
        s.key = key
        s.x = x
        s.y = y
        s.loaded=not ((x is None) and (y is None))
        if autoload and not s.loaded:
            s.load()



    def info(s):
        return fileinfo(s.key)

    def name(s):
        return s.key

    def name_and_feat(s):
        return f"{s.name()}({s.info()['number_of_features']})"

    def load(s):
        s.x,s.y=loaddata(s.key)
        s.loaded=True

    def assert_loaded(s):
        if not s.loaded:
            s.load()

    def getx(s):
        s.assert_loaded()
        return s.x

    def gety(s):
        s.assert_loaded()
        return s.y

    def getxy(s):
        s.assert_loaded()
        return s.x,s.y

    def __str__(s):
        if s.loaded:
            return str(s.key)
        else:
            return "["+str(s.key)+"]"

    def __repr__(s):
        if s.loaded:
            return f"dataset({s.key},autoload=True)"
        else:
            return f"dataset({s.key})"














