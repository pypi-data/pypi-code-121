import requests
import logging

from django.http import HttpResponseForbidden, JsonResponse
from django.http.response import HttpResponse
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.utils.text import slugify
from django.core.cache import cache
from django.utils import timezone
from django.db import connection
from django.conf import settings
from django.db.models import Q
from django.views import View

from dnoticias_services.authentication.keycloak import keycloak_user_exists
from dnoticias_services.communications import send_email

logger = logging.getLogger(__name__)


class Select2View(View):
    RESULTS = "results"
    TEXT = "text"
    CHILDREN = "children"
    IMAGE = "img"
    ID = "id"

    TERM_QS = "term"
    Q_QS = "q"
    _TYPE_QS = "_type"
    PAGE_QS = "page"

    PAGINATION_SIZE = 20
    PAGINATION = "pagination"
    MORE = "more"

    SEARCH_PARAMS = [] # Need to override
    SEARCH_TYPE = "" # Need to override
    ORDER_BY_PARAMS = [] # Need to override
    MODEL = None # Need to override
    MODEL_DEFAULT_MANAGER = "_default_manager"
    MANAGER = MODEL_DEFAULT_MANAGER
    MODEL_VERBOSE_NAMES = {} # Need to override

    def get(self, request, *args, **kwargs):
        self.term = request.GET.get(self.TERM_QS, "")
        try:
            self.page = int(request.GET.get(self.PAGE_QS, 1))
        except Exception as e:
            self.page = 1

        default_manager = getattr(self.MODEL, self.MODEL_DEFAULT_MANAGER, None)
        model_manager = getattr(self.MODEL, self.MANAGER, default_manager)
        if not model_manager:
            model_manager = default_manager

        elements = model_manager.all()
        elements = self.get_initial_filter(elements, request, *args, **kwargs)
        if self.term:
            elements = self.filter_by_term(elements)

        group_by_context = self.group_elements_by_context(elements)

        has_more = []
        results = []
        for key in group_by_context:
            children = []
            paginator = Paginator(group_by_context[key], self.PAGINATION_SIZE)
            page = paginator.page(self.page)
            has_more.append(page.has_next())
            for element in page.object_list:
                element_context = {
                    self.ID : element.pk
                }
                str_element = self.stringify_element(element)
                if str_element:
                    element_context[self.TEXT] = str_element

                element_context.update(self.get_extra_context(element))
                children.append(element_context)
            results.append({
                self.TEXT : key,
                self.CHILDREN : children
            })

        response_context = {
            self.RESULTS : results,
            self.PAGINATION: {
                self.MORE: any(has_more)
            }
        }
        return JsonResponse(data=response_context)

    def get_extra_context(self, element):
        return {}

    def stringify_element(self, element):
        if element:
            return str(element)
        else:
            return None

    def group_elements_by_context(self, elements):
        group_by_context = {}
        for element in elements:
            model_name = element.__class__.__name__
            verbose_name = self.MODEL_VERBOSE_NAMES.get(model_name, model_name)
            if verbose_name in group_by_context:
                group_by_context[verbose_name].append(element)
            else:
                group_by_context[verbose_name] = [element]
        return group_by_context

    def filter_by_term(self, elements):
        qs = None
        filter_context = dict()
        for param in self.SEARCH_PARAMS:
            filter_context = {
                param + "__" + self.SEARCH_TYPE : self.term
            }
            if not qs:
                qs = Q(**filter_context)
                continue

            qs |= Q(**filter_context)
        return elements.filter(qs).order_by(*self.ORDER_BY_PARAMS)

    def get_initial_filter(self, queryset, request, *args, **kwargs):
        return queryset

class SlugifyView(View):
    MODEL = None

    def get(self, request, *args, **kwargs):
        title = request.GET.get("title", "")
        pk = request.GET.get("pk", None)
        pk = pk if pk else None
        return JsonResponse(data={
            "slug" : self.get_unique_slug(title=title, pk=pk)
        })

    def get_unique_slug(title=None, pk=None):
        logger.debug("Transforming {} into a slug...".format(title))

        assert (title is not None and pk is not None)

        pk = pk if not bool(instance) else instance.pk
        title = title if not bool(instance) else instance.title
        slug = slugify(title)

        queryset = self.MODEL._default_manager.filter(~Q(pk=pk), slug=slug)
        if queryset:
            if pk:
                identifier = pk
            else:
                identifier = queryset.last().pk + 1 if queryset.exists() else 1
            slug = "{}-{}".format(slug, identifier)
        logger.debug("{} into a slug -> {}".format(title, slug))
        return slug

class AjaxSlugifyView(SlugifyView):
    def has_authorization(self, request, *args, **kwargs):
        return True

    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            if self.has_authorization(request, *args, **kwargs):
                return super().dispatch(request, *args, **kwargs)
            else:
                return HttpResponseForbidden("Not enough permissions to request slug via ajax")
        else:
            return HttpResponseBadRequest

class AjaxView(View):
    def dispatch(self, request, *args, **kwargs):
        if self.request.is_ajax():
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponseBadRequest()

class GenericDeleteView(View):
    model = None

    def has_authorization(self, request, instance, *args, **kwargs):
        return True

    def post(self, request, *args, **kwargs):
        pk = kwargs.pop("pk")
        redirect_url = request.POST.get("redirect")

        instance = self.model._default_manager.get(pk=pk)
        if not self.has_authorization(request, instance, *args, **kwargs):
            return HttpResponseForbidden("No authorization to delete")

        self.process_delete(instance)

        response_context = {
            "result" : "OK"
        }
        extra_response_context = self.get_extra_response_context()
        response_context.update(extra_response_context)

        if redirect_url:
            self.add_message(request)
            return redirect(redirect_url)
        else:
            return JsonResponse(
                response_context,
                safe=False
            )

    def process_delete(self, instance):
        instance.delete()

    def add_message(self, request):
        pass

    def get_extra_response_context(self):
        return {}


class LivenessCheckView(View):
    """
    Checks the liveness doing two simple tests:
    1. Ensure the connection with database
    2. Making a request to homepage and check the response code
    """
    def _is_error(self, status_code):
        return bool(400 <= status_code < 600)

    def get(self, *args, **kwargs):
        status_code = 200
        context = {
            'error_at': timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            'base_url': settings.BASE_URL
        }

        # ensure_connection returns None if everything is OK, else throws an exception
        try:
            connection.ensure_connection()
        except Exception as exception:
            status_code = 500
            context['error'] = '{0}'.format(exception)
            logger.exception(
                "Cannot connect to database in health check {}!".format(timezone.now())
            )

        # Test the homepage response if LIVENESS_CHECK_HOMEPAGE is True and the previous test
        # was OK (status 200)
        if settings.LIVENESS_CHECK_HOMEPAGE and not self._is_error(status_code):
            try:
                response = requests.get(settings.BASE_URL)
            except Exception as exception:
                status_code = 500
                context['error'] = 'Homepage check returned status code {}'.format(status_code)

        if settings.LIVENESS_CHECK_KEYCLOAK:
            try:
                keycloak_user_exists(settings.KEYCLOAK_ADMIN_USERNAME)
            except Exception as e:
                status_code = 500
                context['error'] = f'Cannot connect to keycloak. {repr(e)}'

        # If LIVENESS_SEND_EMAIL_ON_FAILURE is True and the status code is not 200
        # then we send an email to the IT team communicating the failure
        if self._is_error(status_code) and settings.LIVENESS_SEND_EMAIL_ON_FAILURE:

            cache.set(settings.LIVENESS_CACHE_NAME, settings.LIVENESS_EMAIL_COOLDOWN)
            context["error_code"] = status_code

            send_email(
                settings.DEFAULT_IT_EMAIL,
                settings.EMAIL_TEMPLATE_LIVENESS_FAIL_UUID,
                settings.EMAIL_BRAND_GROUP_UUID,
                "FATAL: Liveness check failure on {}!".format(settings.BASE_URL),
                context=context,
            )

            logger.info("Email notification sended to {}".format(settings.DEFAULT_IT_EMAIL))

        return HttpResponse('', status=status_code)
