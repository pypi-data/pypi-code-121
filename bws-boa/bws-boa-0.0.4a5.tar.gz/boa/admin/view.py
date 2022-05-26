import flask_admin
from .urls import expose
from flask import jsonify

class BaseView(flask_admin.base.BaseView):
    enable = True
    allow_access = True

    def _handle_view(self, name, **kwargs):
        if self.enable:
            return super()._handle_view(name, **kwargs)
        else:
            return 'Failure!'
    
    @expose("/")
    def index(self):
        return ""
    
    @expose("/urls")
    def method_get_urls(self):
        return jsonify(self._urls)


class BaseFrontendView(BaseView):
    """
        Vista para interfaces registradas en el nodo principal (MAPP) 
    """
    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.name = "MS"
        """
            Icono que se usará en MAPP
        """
        self.ico = "fa-gear"
        """
            Ruta de esta vista en MAPP
        """
        self.endpoint_frontend = "ms1"
        """
            Ruta para la api de la vista
        """
        self.endpoint_api = None
        self.setup()

    def setup(self):
        pass

    def js(self):
        """
            colocar los js
        """
        return []

    def css(self):
        """
            colocar los ccs
        """
        return []
    
    def context(self):
        """
            colocar los ctx
        """
        return {}
