import json
import logging
from json import JSONDecodeError

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist, ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ForeignKey, Q
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from django.views import View

from pfx.pfxcore.decorator import rest_api
from pfx.pfxcore.exceptions import (
    APIError,
    ForbiddenError,
    JsonErrorAPIError,
    NotFoundError,
    UnauthorizedError,
)
from pfx.pfxcore.fields import MediaField
from pfx.pfxcore.http import JsonResponse
from pfx.pfxcore.models import UserFilteredQuerySetMixin
from pfx.pfxcore.shortcuts import f, get_object, parse_bool
from pfx.pfxcore.storage.s3_storage import StorageException

from .fields import VF, ViewField

logger = logging.getLogger(__name__)

LIST_META = ['count', 'pagination', 'order_options']


# HTTP 404 handler
def resource_not_found(request, exception):
    return NotFoundError().response


class ModelMixin():
    model = None
    fields = []
    select_related = []
    prefetch_related = []
    _class_fields = {}
    _class_select_related_fields = {}

    def filter_queryset(self, qs):
        if isinstance(qs, UserFilteredQuerySetMixin):
            return qs.user(self.request.user)
        if (hasattr(settings, 'PFX_FORCE_USER_FILTERED_QUERYSET') and
                settings.PFX_FORCE_USER_FILTERED_QUERYSET):
            raise Exception("The queryset must be a UserFilteredQuerySetMixin")
        return qs

    def get_queryset(self):
        return self.filter_queryset(
            self.model._default_manager.all()).select_related(
                *self.get_select_related_fields()
            ).prefetch_related(
                *self.prefetch_related
            )

    def get_object(self, **kwargs):
        return get_object(self.get_queryset(), **kwargs)

    def get_related_queryset(self, related_model):
        return self.filter_queryset(related_model._default_manager.all())

    def get_list_queryset(self):
        return self.get_queryset()

    @classmethod
    def _process_fields(cls, fields):
        if not fields:
            return {
                f.name: ViewField.from_model_field(f.name, f)
                for f in cls.model._meta.fields}

        def _field(e):
            if isinstance(e, ViewField):
                field = e
            elif isinstance(e, VF):
                field = e.to_field(cls.model)
            else:
                field = ViewField.from_name(cls.model, e)
            return field.alias, field

        return dict(_field(e) for e in fields)

    @classmethod
    def get_fields(cls):
        if cls not in cls._class_fields:
            cls._class_fields[cls] = cls._process_fields(cls.fields)
        return cls._class_fields[cls]

    @classmethod
    def get_select_related_fields(cls):
        if cls not in cls._class_select_related_fields:
            res = []
            for name, field in cls.get_fields().items():
                if field.select:
                    res.append(name)
            cls._class_select_related_fields[cls] = set(
                cls.select_related + [
                    name for name, field in cls.get_fields().items()
                    if field.select])
        return cls._class_select_related_fields[cls]

    @property
    def model_name(self):
        return self.model._meta.verbose_name

    @property
    def format_date(self):
        return parse_bool(self.request.GET.get('date_format'))

    def message_response(self, message, **kwargs):
        return JsonResponse(dict(message=message, **kwargs))


class ModelResponseMixin(ModelMixin):
    def serialize_object(self, obj, **fields):
        vals = obj.json_repr()
        vals.update(fields)
        return vals

    def response(self, o, **meta):
        return JsonResponse(self.serialize_object(o, **{
            f.alias: f.to_json(o, self.format_date)
            for f in self.get_fields().values()}, meta=meta))

    def validate(self, obj, created=False, **kwargs):
        obj.full_clean(**kwargs)

    def is_valid(self, obj, created=False):
        obj.save()
        message = (
                created and
                _("{model} {obj} created.") or
                _("{model} {obj} updated."))
        object = self.get_object(pk=obj.pk)
        return self.response(
            object, message=f(
                message, model=self.model_name, obj=object))

    def is_invalid(self, obj, errors):
        return JsonResponse(errors, status=422)

    def object_meta(self):
        return {n: f.meta() for n, f in self.get_fields().items()}

    @rest_api("/meta", method="get")
    def get_meta(self, *args, **kwargs):
        return JsonResponse(self.object_meta())


class BodyMixin:
    def deserialize_body(self):
        try:
            return json.loads(self.request.body)
        except JSONDecodeError as e:
            raise JsonErrorAPIError(e)


class ModelBodyMixin(BodyMixin, ModelMixin):
    def get_model_data(self, obj, data, created):
        fields = self.get_fields()

        def can_write(fname):
            if fname not in fields:
                return False
            if fields[fname].is_readonly(created=created):
                logger.warning(
                    "Field %s is ignored because it is readonly on view %s",
                    fname, self.__class__.__name__)
                return False
            return True

        return dict(
            fields[k].to_model_value(v, self.get_related_queryset)
            for k, v in data.items()
            if can_write(k))

    def set_values(self, obj, **values):
        for fname, value in values.items():
            setattr(obj, fname, value)


class ListRestViewMixin(ModelResponseMixin):
    list_fields = []
    filters = []

    def get_list_fields(self):
        return self._process_fields(self.list_fields or self.fields)

    def parse_list_meta(self):
        meta_arg = self.request.GET.get('meta', 'all')
        meta = meta_arg.split(',') or []
        if 'all' in meta:
            return LIST_META
        return meta

    def _list_meta_count(self):
        return self.get_list_queryset().count()

    def _list_meta_pagination(self):
        return dict(
            page_size=int(self.request.GET.get('page_size', 10)),
            page=int(self.request.GET.get('page', 1)),
            page_subset=int(self.request.GET.get('page_subset', 5)))

    def _list_meta_subset(self):
        return dict(
            limit=int(self.request.GET.get('limit', 10)),
            offset=int(self.request.GET.get('offset', 0)))

    def _list_meta_order_options(self):
        def get_db_fields(model, models=None):
            models = models or [model]
            new_models = models + [
                field.related_model for field in model._meta.fields
                if isinstance(field, ForeignKey)]
            for field in model._meta.fields:
                if isinstance(field, ForeignKey):
                    if field.related_model not in models:
                        yield field.name
                        yield from [
                            f"{field.name}__{fn}" for fn in get_db_fields(
                                field.related_model, new_models)]
                    continue
                else:
                    yield field.name == 'id' and 'pk' or field.name

        return list(get_db_fields(self.model))

    def build_list_meta(self):
        def _meta(meta):
            fn = getattr(self, f'_list_meta_{meta}', None)
            if not callable(fn):
                raise APIError(
                    _("Meta {meta} does not exists.").format(meta=meta))
            return fn

        return {
            meta: _meta(meta)()
            for meta in self.parse_list_meta()}

    def search_filter(self, search):  # pragma: no cover
        return Q()

    @rest_api("/filters", method="get")
    def get_filter(self, *args, **kwargs):
        return JsonResponse({
            'items': [f.meta for f in self.filters]})

    def get_list_queryset(self):
        qs = super().get_list_queryset()
        search = self.request.GET.get('search')
        for filter in self.filters:
            qs = qs.filter(filter.query(self.request.GET))
        if search:
            qs = qs.filter(
                self.search_filter(search))
        order = self.request.GET.get('order')
        if order:
            qs = qs.order_by(*order.split(','))
        return qs

    def get_list_result(self, qs):
        for o in qs:
            yield self.serialize_object(o, **{
                f.alias: f.to_json(o, self.format_date)
                for f in self.get_list_fields().values()})

    @rest_api("", method="get")
    def get_list(self, *args, **kwargs):
        res = {}
        meta = self.build_list_meta()
        qs = self.get_list_queryset()
        if 'pagination' in meta:
            count = qs.count()
            pagination = meta['pagination']
            page = pagination['page']
            limit = pagination['page_size']
            page_count = (1 + (count - 1) // limit) or 1
            offset = (page - 1) * limit
            subset = pagination['page_subset']
            subset_first = min(
                max(page - subset // 2, 1), max(page_count - subset + 1, 1))
            qs = qs.all()[offset:offset + limit]
            pagination.update(dict(
                count=count,
                page_count=page_count,
                subset=list(range(
                    subset_first,
                    min(subset_first + subset, page_count + 1)))))
        elif 'subset' in meta:
            count = qs.count()
            subset = meta['subset']
            limit = subset['limit']
            page_count = (1 + (count - 1) // limit) or 1
            offset = subset['offset']
            qs = qs.all()[offset:offset + limit]
            subset.update(dict(
                count=count,
                page_count=page_count,
                limit=limit,
                offset=offset))
        else:
            qs = qs.all()
        if meta:
            res['meta'] = meta
        res['items'] = list(self.get_list_result(qs))
        return JsonResponse(res)


class DetailRestViewMixin(ModelResponseMixin):
    @rest_api("/<int:id>", method="get")
    def get(self, id, *args, **kwargs):
        obj = self.get_object(pk=id)
        return self.response(obj)


class SlugDetailRestViewMixin(ModelResponseMixin):
    SLUG_FIELD = "slug"

    @rest_api("/slug/<slug:slug>", method="get")
    def get_by_slug(self, slug, *args, **kwargs):
        obj = self.get_object(**{self.SLUG_FIELD: slug})
        return self.response(obj)


class CreateRestViewMixin(ModelBodyMixin, ModelResponseMixin):
    default_values = {}

    def get_default_values(self):
        return dict(self.default_values)

    def new_object(self):
        return self.model(**self.get_default_values())

    def object_create_perm(self, data):
        return True

    @rest_api("", method="post")
    def post(self, *args, **kwargs):
        obj = self.new_object()
        data = self.get_model_data(obj, self.deserialize_body(), created=True)
        forbidden = False
        if not self.object_create_perm(data):
            forbidden = True
        self.set_values(obj, **data)
        try:
            self.validate(obj, created=True)
            if forbidden:
                raise ForbiddenError
            return self.is_valid(obj, created=True)
        except ValidationError as e:
            return self.is_invalid(obj, errors=e)


class UpdateRestViewMixin(ModelBodyMixin, ModelResponseMixin):
    def object_update_perm(self, obj, data):
        return True

    @rest_api("/<int:id>", method="put")
    def put(self, id, *args, **kwargs):
        obj = self.get_object(pk=id)
        data = self.get_model_data(obj, self.deserialize_body(), created=False)
        forbidden = False
        if not self.object_update_perm(obj, data):
            forbidden = True
        self.set_values(obj, **data)
        try:
            self.validate(obj, created=False)
            if forbidden:
                raise ForbiddenError
            return self.is_valid(obj, created=False)
        except ValidationError as e:
            return self.is_invalid(obj, errors=e)


class DeleteRestViewMixin(ModelMixin):
    def object_delete_perm(self, obj):
        return True

    @rest_api("/<int:id>", method="delete")
    def delete(self, id, *args, **kwargs):
        obj = self.get_object(pk=id)
        if not self.object_delete_perm(obj):
            raise ForbiddenError()
        try:
            with transaction.atomic():
                obj.delete()
            return self.message_response(f(
                _("{model} {obj} deleted."), model=self.model_name, obj=obj))
        except IntegrityError as e:
            logger.debug("IntegrityError: %s", e)
            raise APIError(f(_(
                "{obj} cannot be deleted because "
                "it is referenced by other objects."), obj=obj))


class MediaRestViewMixin(ModelMixin):
    def _get_model_field(self, field):
        try:
            model_field = self.model._meta.get_field(field)
            if not isinstance(model_field, MediaField):
                raise NotFoundError  # pragma: no cover
        except FieldDoesNotExist:  # pragma: no cover
            raise NotFoundError
        return model_field

    @rest_api("/<int:pk>/<str:field>/upload-url/<str:filename>", method="get")
    def field_media_upload_url(self, pk, field, filename, *args, **kwargs):
        obj = self.get_object(pk=pk)
        try:
            res = self._get_model_field(field).get_upload_url(
                self.request, obj, filename)
        except StorageException as e:  # pragma: no cover
            logger.exception(e)
            raise APIError(_("Unexpected storage error", status=500))
        return JsonResponse(res)

    @rest_api("/<int:pk>/<str:field>", method="get")
    def field_media_get(self, pk, field, *args, **kwargs):
        obj = self.get_object(pk=pk)
        try:
            url = self._get_model_field(field).get_url(self.request, obj)
        except StorageException as e:  # pragma: no cover
            logger.exception(e)
            raise APIError(_("Unexpected storage error", status=500))
        if self.request.GET.get('redirect', '0').lower() in ['0', 'false']:
            return JsonResponse(dict(url=url))
        return redirect(url)


class SecuredRestViewMixin(View):
    default_public = False

    def perm(self):
        return True

    def _is_public(self, public, func_name):
        param = f'{func_name}_public'
        if hasattr(self, param):
            public = getattr(self, param)
        if public is None:
            public = self.default_public
        return public

    def check_perm(self, public, func_name, *args, **kwargs):
        if self._is_public(public, func_name):
            return
        if not self.request.user.is_authenticated:
            raise UnauthorizedError()
        if not self.perm():
            raise ForbiddenError()
        fperm = f'{func_name}_perm'
        if hasattr(self, fperm) and not getattr(self, fperm)(*args, **kwargs):
            raise ForbiddenError()


class BaseRestView(SecuredRestViewMixin, View):
    pass


class RestView(
        ListRestViewMixin,
        DetailRestViewMixin,
        CreateRestViewMixin,
        UpdateRestViewMixin,
        DeleteRestViewMixin,
        BaseRestView):
    pass
