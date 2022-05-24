__author__ = "hugo.inzirillo"

from napoleontoolbox.dataloader.models import Ressources, Provider, Service

__all__ = ['Ressources',
           'Service',
           'Provider']


class DataLoader(object):
    def __init__(self):
        self.__ressources = Ressources()

    @property
    def ressources(self):
        return self.__ressources
