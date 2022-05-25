# port的想法：actor需要关注从指定的port获取数据，和把数据发送到指定的port
#            port的作用就是把数据发送到指定的位置，并把其提供相应拉取其数据的方式
#            当前关联的port就是提供数据
class Port:

    # 初始化数据，生成需要的相关配置
    def __init__(self, name=None, actor_name=None):
        self.name = name
        self.actor = actor_name
