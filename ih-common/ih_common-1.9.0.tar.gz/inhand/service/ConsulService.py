import consul

class ConsulService(object):
    def __init__(self, host, port):
        '''初始化，连接consul服务器'''
        self._consul = consul.Consul(host, port)

    def registerService(self, name, service_id,host,port, tags=None):
        tags = tags or []
        # 注册服务
        self._consul.agent.service.register(
            name=name,
            service_id=service_id,
            address=host,
            port=port,
            tags=tags,
            # 健康检查ip端口，检查时间：5,超时时间：30，注销时间：30s
            check=consul.Check().http("http://{}:{}".format(host,port), "5s", "30s", "30s",None))

    def check(self,host,port, interval, timeout=None, deregister=None,header=None):
        return consul.Check.http("http://{}:{}".format(host,port),interval,timeout,deregister,header)

    def getService(self, name):
        services = self._consul.agent.services()
        service = services.get(name)
        if not service:
            return None, None
        addr = "{0}:{1}".format(service['Address'], service['Port'])
        return service, addr

"""
if __name__ == '__main__':
    import sys

    sys.path.append('../../')
    from inhand.utilities.Utility import Utility
    ip = Utility.getLocalIP(host="consul",port=8500)
    port = 8500

    tags=[]
    tags.append("group=inhand-poweris")
    tags.append("secure=flaes")
    tags.append("traefik.enable=true")

    tags.append("traefik.http.services.jx-attendance-api.loadbalancer.server.weight=1")
    consulService=ConsulService("consul",8500)
    name="jx-attandance-api-10-0-0-1"
    service_id="jx-attendance-api"
    consulService.registerService(name,service_id,"10.5.0.247",5000,tags)

    check=consulService.check("10.5.0.247",5000,"30s")
    print(check)
    res=consulService.getService(service_id)
    print(res)
"""






