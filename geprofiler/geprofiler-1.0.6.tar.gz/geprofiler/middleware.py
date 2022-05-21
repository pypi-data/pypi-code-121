import io
import os
import re
import sys
import time
import urllib.parse
import webbrowser
from datetime import datetime
from faulthandler import is_enabled

from django.conf import settings
from django.http import HttpResponse
from django.utils.module_loading import import_string

from geprofiler import Profiler
from geprofiler.renderers import Renderer
from geprofiler.renderers.html import HTMLRenderer
from geprofiler.renderers.jsonrenderer import JSONRenderer

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object


def get_renderer(path) -> Renderer:
    """Return the renderer instance."""
    if path:
        try:
            renderer = import_string(path)()
        except ImportError as exc:
            print("Unable to import the class: %s" % path)
            raise exc

        if not isinstance(renderer, Renderer):
            raise ValueError(f"Renderer should subclass: {Renderer}")

        return renderer
    else:
        return HTMLRenderer()


class GeprofileType(object):
    DEFAULT = "default"
    JSON = "json"


class ProfilerMiddleware(MiddlewareMixin):
    def process_request(self, request):
        is_profile_enabled = (
            "geprofiler" in request.GET or 
            "geprofiler" in request.headers 
        )
        if is_profile_enabled:
            profiler = Profiler()
            profiler.start()
            request.profiler = profiler

    def process_response(self, request, response):
        if hasattr(request, "profiler"):
            profile_session = request.profiler.stop()

            url = re.sub(r"\?geprofiler=*\w*", "", request.build_absolute_uri())
            profile_session.url = url

            geprofile_type = request.GET.get("geprofiler") or request.headers.get("geprofiler")
            if geprofile_type not in [GeprofileType.JSON]:
                geprofile_type = GeprofileType.DEFAULT

            if geprofile_type == GeprofileType.JSON:
                renderer = JSONRenderer()
                output = renderer.render(profile_session)
                return HttpResponse(output, content_type="application/json")
            else:
                renderer = HTMLRenderer()
                profile_dir = getattr(settings, "GEPROFILER_PROFILE_DIR", None)
                file_path = None
                if profile_dir:
                    filename = (
                        "{total_time:.3f}s_{url}_{date}.{ext}".format(
                            total_time=profile_session.duration,
                            url=url,
                            date=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
                            ext=renderer.output_file_extension,
                        )
                        .replace("/", "_")
                        .replace("?", "_")
                    )

                    file_path = os.path.join(profile_dir, filename)

                    if not os.path.exists(profile_dir):
                        os.mkdir(profile_dir)

                renderer.open_in_browser(profile_session, file_path)

            return response
        else:
            return response
