from kazoo.client import KazooClient,KazooState,KeeperState
import json
import time
import logging
import traceback
import sys


class ZkService:
    def __init__(self,config={}):
        #self.zk = config["settings"]
        self.config=config
        zk_config=config
        self.settings = config['settings']
        self.zk = KazooClient(hosts=self.settings.zk.url)
        self.zk.add_listener(onZkStateChanged)

    def register(self):
        try:
            time.sleep(5)
        except Exception as e:
            print(str(e))


        try:
            self.zk.start()
            traefik_path = ('/traefik/apps/%s-%s' % (self.config['APP_NAME'],self.config['uuid']))
            app_root =('%s/%s' % (self.settings.zk.path,self.config['APP_NAME']))
            app_path = ('%s/%s/%s' % (self.settings.zk.path,self.config['APP_NAME'],self.config['uuid']))
            #data = zk.get(settings.zk.path+"/iot-ext/e3da7179-f35b-4200-9732-71cd8f780a2f")
            if not self.zk.exists(traefik_path):
                self.zk.create(traefik_path)#,ephemeral=True)

            api_info = json.dumps(self.config['api_info'].toMap())
            s = str.encode(api_info)
            self.zk.set(traefik_path,s)
            print("--------------uuid:%s--------zk api ---------------------: %s" % (self.config['uuid'],s))
            if not self.zk.exists(app_root):
                self.zk.create(app_root)
            if not self.zk.exists(app_path):
                self.zk.create(app_path)#,ephemeral=True)
            instance_info = json.dumps(self.config['instance_info'].toMap())
            self.zk.set(app_path,str.encode(instance_info))
            print("--------------uuid:%s--------zk was called---------------------" % (self.config['uuid']))
    #        zk.close()
    #        zk.stop()
        except Exception as e:
            traceback.print_exc()
            print('While I was trying to register the node["%s"] to the zk, there was an exception: %s' % (self.config['uuid'],str(e)))
        finally:
            try:
                self.zk.stop()
                print("Close conection with zookeeper")

            except Exception as ee:
                print("Failed to close conection with zookeeper")


def onZkStateChanged(state):
    print("zookeeper client state is changed to %s" % str(state))

    if  state == KazooState.LOST:
        print("zookeeper client state is changed to lost!")
        """
        sys.path.append('../')
        from Settings import Settings
        settings = Settings.fetch_settings(config_url="http://config-server:8801/stat-api/dev", module=app.config['APP_NAME'],
                                profile=app.config['APP_MODE'])

        zk_client = ZkSerivce(settings)

        zk_client.register()
        """
    elif state == KazooState.SUSPENDED:
        print("zookeeper client state is changed to suspended!")
    else:
        print("zookeeper client state is changed to connected!")





