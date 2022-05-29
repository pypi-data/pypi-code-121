import __init__
import unittest
import json
from TDhelper.network.http.RPC import RPC

class TestRPC(unittest.TestCase):
    def test_RPC_Register(self):
        pass

    def test_remote_call(self):
        RPC_CORE = RPC("http://192.168.50.2:9002/api/", "d74218cff240f446d341c4a2f3a8c588")
        RPC_LOADS=["APP_STORE"]
        class RPC_HANDLE:
            def __init__(self):
                self._cache = {}
                self.load()

            def call(self, serviceName, **args):
                assert (
                    len(serviceName.split(".")) == 2
                ), "serviceName formatter is errror. must (service.method)."
                m_service = serviceName.split(".")[0]
                if m_service in self._cache:
                    return self._cache[m_service].call(serviceName, **args)
                else:
                    return None

            def getHandle(self, key):
                if key in self._cache:
                    return self._cache[key]
                else:
                    return None

            def load(self):
                print("Begin load rpc service:")
                for m_prc_name in RPC_LOADS:
                    print("load %s" % m_prc_name)
                    m_rpc = RPC_CORE.handle(m_prc_name)
                    if m_rpc:
                        self._cache[m_prc_name] = m_rpc
                    else:
                        print("LOAD RPC %s error." % m_prc_name)
                print("End load rpc service.")

        # 在需要调用RPC的模块import R
        R = RPC_HANDLE()
        RPC_APP_STORE = R.getHandle("APP_STORE")
        ret=RPC_APP_STORE.call('APPVIEWSET_GETAPPSTATE',**{
            "developer_token":"*****",
            "app_token":"****"
        })
        print(ret)

if __name__ == "__main__":
    unittest.main()