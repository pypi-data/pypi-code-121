# from app import admin
import importlib
import logging
from pathlib import Path

logger = logging.getLogger("Boot Admin")


def bootstrap(app, admin=None, types=["config", "api"]):    
    # Register admin of apps
    for type_ in types:
        for package in app.config["INSTALLED_APPS"]:
            if type_ in ["config"]:
                assert not admin is None 
                for file in ["config"]:
                    package_admin = "%s.%s" % (package, file)

                    path = Path(package_admin.replace('.', '/') + '.py')
                    if path.is_file():
                        logger.debug("import %s" % package_admin)
                        module = importlib.import_module(package_admin)
                        register_frontend_views = getattr(module, "register_frontend_views", lambda a: 0)
                        register_api_views = getattr(module, "register_api_views", lambda a: 0)
                        register_frontend_views(admin)
                        register_api_views(admin)
                        logger.debug("imported %s" % package_admin)

                
                # admin.bootstrap_frontends()

            elif type_ in ["api", "routes", "rpc"]:
                for file in ["api", "routes", "rpc"]:
                    package_admin = "%s.%s" % (package, file)
                    path = Path(package_admin.replace('.', '/') + '.py')
                    if path.is_file():
                        logger.debug("api.import %s" % package_admin)
                        __import__(package_admin)
                        logger.debug("api.imported %s" % package_admin)
            else:
                for file in [type_]:
                    package_admin = "%s.%s" % (package, file)
                    path = Path(package_admin.replace('.', '/') + '.py')
                    if path.is_file():
                        __import__(package_admin)
                        logger.debug("import %s" % package_admin)
