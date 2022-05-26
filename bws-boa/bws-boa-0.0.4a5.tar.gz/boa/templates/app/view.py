template='''
from boa.admin.view import BaseFrontendView, BaseView
from boa.admin.urls import expose_json
from app import admin


@admin.expose("%(app)s/frontview")
class FrontView(BaseFrontendView):
    """
        Vista para interfaces registradas en el nodo principal (MAPP) 
    """
    def setup(self):
        self.name = "ms_%(app)s"
        """
            Icono que se usará en MAPP
        """
        self.ico = "fa-gear"
        """
            Ruta de esta vista en MAPP
        """
        self.endpoint_frontend = "-/ms/%(app)s"
        """
            Ruta para la api de la vista
        """
        self.endpoint_api = "%(app)s/frontview"

    @expose_json("/js")
    def js(self):
        """
            colocar los js
        """
        return []

    @expose_json("/css")
    def css(self):
        """
            colocar los ccs
        """
        return []
    
    @expose_json("/ctx")
    def context(self):
        """
            colocar los ctx
        """
        return {}
    
    @expose_json(url='/test', methods=('GET',))
    def get_test(self):
        return { "success" : True}


@admin.expose("%(app)s/apiview")
class ApiView(BaseView):
    """
        Vista para api
    """
    
    @expose_json(url='/test', methods=('GET',))
    def get_test(self):
        return { "success" : True}

'''
