
from django.http.response import HttpResponseBase
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required

from cap.views import render


def admin_render_view(template_name):

    def decorator(view_func):

        @staff_member_required
        def wrapper(request, *args, **kwargs):

            context = view_func(request, *args, **kwargs)

            if isinstance(context, HttpResponseBase):
                return context

            return render(request, template_name, context)

        return wrapper

    return decorator


def short_description(description):

    def decorator(f):

        def wrap(*args, **kwargs):
            return f(*args, **kwargs)

        wrap.short_description = description
        wrap.__name__ = f.__name__

        return wrap

    return decorator


def template_list_item(template_name, description=None):

    def decorator(f):

        def wrap(*args, **kwargs):
            return render_to_string(template_name, f(*args, **kwargs))

        if description is not None:
            wrap.short_description = description

        return wrap

    return decorator
