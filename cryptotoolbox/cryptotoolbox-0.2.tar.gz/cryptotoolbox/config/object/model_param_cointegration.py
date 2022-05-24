__author__ = "hugo.inzirillo"

from napoleontoolbox.napoleon_config_tools.object.modelparamtemplate import ModelParamTemplate


# todo exemple mais cette classe sera à sortir et à déplacer dans un repertoire qui contient tous les modèles de params
# todo faire la config complete

class ModelParamCointegration(ModelParamTemplate):
    def __init__(self):
        super(ModelParamCointegration, self).__init__()
        self.__alpha = None
