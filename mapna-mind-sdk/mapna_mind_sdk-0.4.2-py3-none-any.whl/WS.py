import cherrypy

@cherrypy.popargs('key')
class MindSdkWebService:

    __instance=None


    # def __init__(self):
    #     cherrypy.quickstart(MindSdkWebService())

    @staticmethod
    def getInstance():

        if MindSdkWebService.__instance==None:
            MindSdkWebService()
        return MindSdkWebService.__instance


    results = {}

    list_dict={}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def index( key):
        return MindSdkWebService.results[key]

    @cherrypy.expose
    def getResult(key):
        return MindSdkWebService.results[key]

    @cherrypy.expose
    def getList(key):
        return MindSdkWebService.list_dict[key]


    def set(key, value):
        MindSdkWebService.results[key]=value
        return  "aaa"

    def add(key, value):
        if MindSdkWebService.list_dict.get(key)==None:
            MindSdkWebService.list_dict[key]=[]
        MindSdkWebService.list_dict[key].append(value)


if __name__ == '__main__':
    # MindSdkWebService.getInstance()
    print("started")
