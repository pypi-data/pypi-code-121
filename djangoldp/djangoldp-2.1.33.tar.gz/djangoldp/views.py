import json
import validators
from collections import OrderedDict
from django.apps import apps
from django.conf import settings
from django.conf.urls import include, re_path
from django.contrib.auth import get_user_model
from django.core.exceptions import FieldDoesNotExist, ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.urls.resolvers import get_resolver
from django.utils.decorators import classonlymethod
from django.views import View
from pyld import jsonld
from rest_framework import status
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.utils import model_meta
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from djangoldp.endpoints.webfinger import WebFingerEndpoint, WebFingerError
from djangoldp.models import LDPSource, Model, Follower
from djangoldp.permissions import LDPPermissions
from djangoldp.filters import LocalObjectOnContainerPathBackend
from djangoldp.related import get_prefetch_fields
from djangoldp.utils import is_authenticated_user
from djangoldp.activities import ActivityQueueService, as_activitystream
from djangoldp.activities import ActivityPubService
from djangoldp.activities.errors import ActivityStreamDecodeError, ActivityStreamValidationError
import logging

logger = logging.getLogger('djangoldp')
get_user_model()._meta.rdf_context = {"get_full_name": "rdfs:label"}


def reorder_ordered_dict(odico):
    keys_order = ['@context', '@type', '@id']
    keys_order.reverse()

    for key in keys_order:
        if key in odico.keys():
            odico.move_to_end(key, False)

    return odico

def reorder_data(data):
    ''' 
    Reordering data before converting in JSONLDRenderer 
    Parsing all nested dict and converting in OrderedDict
    '''
    if isinstance(data, OrderedDict):
        data = reorder_ordered_dict(data)

        for key in data:
            if isinstance(data[key], dict):
                data[key] = OrderedDict(data[key])
            reorder_data(data[key])

    elif isinstance(data, list):
        for item in data:
            reorder_data(item)

    return data


# renders into JSONLD format by applying context to the data
# https://github.com/digitalbazaar/pyld
class JSONLDRenderer(JSONRenderer):
    media_type = 'application/ld+json'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if isinstance(data, dict):
            context = data.get("@context")
            if isinstance(context, list):
                data["@context"] = [settings.LDP_RDF_CONTEXT] + context
            elif isinstance(context, str) or isinstance(context, dict):
                data["@context"] = [settings.LDP_RDF_CONTEXT, context]
            else:
                data["@context"] = settings.LDP_RDF_CONTEXT

        data_ordered = reorder_data(data)

        return super(JSONLDRenderer, self).render(data, accepted_media_type, renderer_context)


# https://github.com/digitalbazaar/pyld
class JSONLDParser(JSONParser):
    media_type = 'application/ld+json'

    def parse(self, stream, media_type=None, parser_context=None):
        data = super(JSONLDParser, self).parse(stream, media_type, parser_context)
        # compact applies the context to the data and makes it a format which is easier to work with
        # see: http://json-ld.org/spec/latest/json-ld/#compacted-document-form
        try:
            return jsonld.compact(data, ctx=settings.LDP_RDF_CONTEXT)
        except jsonld.JsonLdError as e:
            raise ParseError(str(e.cause))


# an authentication class which exempts CSRF authentication
class NoCSRFAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class InboxView(APIView):
    """
    Receive linked data notifications
    """
    permission_classes = [AllowAny, ]

    def post(self, request, *args, **kwargs):
        '''
        receiver for inbox messages. See https://www.w3.org/TR/ldn/
        '''
        payload = request.body.decode("utf-8")

        try:
            activity = json.loads(payload, object_hook=as_activitystream)
            activity.validate()
        except ActivityStreamDecodeError:
            return Response('Activity type unsupported', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        except ActivityStreamValidationError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        try:
            self._handle_activity(activity, **kwargs)
        except IntegrityError:
            return Response({'Unable to save due to an IntegrityError in the receiver model'},
                            status=status.HTTP_200_OK)
        except ValueError as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)

        # save the activity and return 201
        obj = ActivityQueueService._save_sent_activity(activity.to_json(), local_id=request.path_info, success=True,
                                                       type=activity.type)

        response = Response({}, status=status.HTTP_201_CREATED)
        response['Location'] = obj.urlid

        return response

    def _handle_activity(self, activity, **kwargs):
        if activity.type == 'Add':
            self.handle_add_activity(activity, **kwargs)
        elif activity.type == 'Remove':
            self.handle_remove_activity(activity, **kwargs)
        elif activity.type == 'Delete':
            self.handle_delete_activity(activity, **kwargs)
        elif activity.type == 'Create' or activity.type == 'Update':
            self.handle_create_or_update_activity(activity, **kwargs)
        elif activity.type == 'Follow':
            self.handle_follow_activity(activity, **kwargs)

    def atomic_get_or_create_nested_backlinks(self, obj, object_model=None, update=False):
        '''
        a version of get_or_create_nested_backlinks in which all nested backlinks are created, or none of them are
        '''
        try:
            with transaction.atomic():
                return self._get_or_create_nested_backlinks(obj, object_model, update)
        except IntegrityError as e:
            logger.error(str(e))
            logger.warning(
                'received a backlink which you were not able to save because of a constraint on the model field.')
            raise e

    def _get_or_create_nested_backlinks(self, obj, object_model=None, update=False):
        '''
        recursively deconstructs a tree of nested objects, using get_or_create on each leaf/branch
        :param obj: Dict representation of the object
        :param object_model: The Model class of the object. Will be discovered if set to None
        :param update: if True will update retrieved objects with new data
        :raises Exception: if get_or_create fails on a branch, the creation will be reversed and the Exception re-thrown
        '''
        # store a list of the object's sub-items
        if object_model is None:
            object_model = Model.get_subclass_with_rdf_type(obj['@type'])
        if object_model is None:
            raise Http404('unable to store type ' + obj['@type'] + ', model with this rdf_type not found')
        branches = {}

        for item in obj.items():
            # TODO: parse other data types. Match the key to the field_name
            if isinstance(item[1], dict):
                item_value = item[1]
                item_model = Model.get_subclass_with_rdf_type(item_value['@type'])
                if item_model is None:
                    raise Http404(
                        'unable to store type ' + item_value['@type'] + ', model with this rdf_type not found')

                # push nested object tuple as a branch
                backlink = self._get_or_create_nested_backlinks(item_value, item_model)
                branches[item[0]] = backlink

        # get or create the backlink
        try:
            if obj['@id'] is None or not validators.url(obj['@id']):
                raise ValueError('received invalid urlid ' + str(obj['@id']))
            external = Model.get_or_create_external(object_model, obj['@id'], update=update, **branches)

            # creating followers, to inform distant resource of changes to local connection
            if Model.is_external(external):
                # this is handled with Followers, where each local child of the branch is followed by its external parent
                for item in obj.items():
                    urlid = item[1]
                    if isinstance(item[1], dict):
                        urlid = urlid['@id']
                    if not isinstance(urlid, str) or not validators.url(urlid):
                        continue

                    if not Model.is_external(urlid):
                        ActivityPubService.save_follower_for_target(external.urlid, urlid)

            return external

        # this will be raised when the object was local, but it didn't exist
        except ObjectDoesNotExist:
            raise Http404(Model.get_meta(object_model, 'label', 'Unknown Model') + ' ' + str(obj['@id']) + ' does not exist')

    # TODO: a fallback here? Saving the backlink as Object or similar
    def _get_subclass_with_rdf_type_or_404(self, rdf_type):
        model = Model.get_subclass_with_rdf_type(rdf_type)
        if model is None:
            raise Http404('unable to store type ' + rdf_type + ', model not found')
        return model

    def handle_add_activity(self, activity, **kwargs):
        '''
        handles Add Activities. See https://www.w3.org/ns/activitystreams
        Indicates that the actor has added the object to the target
        '''
        object_model = self._get_subclass_with_rdf_type_or_404(activity.object['@type'])
        target_model = self._get_subclass_with_rdf_type_or_404(activity.target['@type'])

        try:
            target = target_model.objects.get(urlid=activity.target['@id'])
        except target_model.DoesNotExist:
            return Response({}, status=status.HTTP_404_NOT_FOUND)

        # store backlink(s) in database
        backlink = self.atomic_get_or_create_nested_backlinks(activity.object, object_model)

        # add object to target
        target_info = model_meta.get_field_info(target_model)

        for field_name, relation_info in target_info.relations.items():
            if relation_info.related_model == object_model:
                attr = getattr(target, field_name)
                if not attr.filter(urlid=backlink.urlid).exists():
                    attr.add(backlink)
                    ActivityPubService.save_follower_for_target(backlink.urlid, target.urlid)

    def handle_remove_activity(self, activity, **kwargs):
        '''
        handles Remove Activities. See https://www.w3.org/ns/activitystreams
        Indicates that the actor has removed the object from the origin
        '''
        # TODO: Remove Activity may pass target instead
        object_model = self._get_subclass_with_rdf_type_or_404(activity.object['@type'])
        origin_model = self._get_subclass_with_rdf_type_or_404(activity.origin['@type'])

        # get the model reference to saved object
        try:
            origin = origin_model.objects.get(urlid=activity.origin['@id'])
            object_instance = object_model.objects.get(urlid=activity.object['@id'])
        except origin_model.DoesNotExist:
            raise Http404(activity.origin['@id'] + ' did not exist')
        except object_model.DoesNotExist:
            return

        # remove object from origin
        origin_info = model_meta.get_field_info(origin_model)

        for field_name, relation_info in origin_info.relations.items():
            if relation_info.related_model == object_model:
                attr = getattr(origin, field_name)
                if attr.filter(urlid=object_instance.urlid).exists():
                    attr.remove(object_instance)
                    ActivityPubService.remove_followers_for_resource(origin.urlid, object_instance.urlid)

    def handle_create_or_update_activity(self, activity, **kwargs):
        '''
        handles Create & Update Activities. See https://www.w3.org/ns/activitystreams
        '''
        object_model = self._get_subclass_with_rdf_type_or_404(activity.object['@type'])
        self.atomic_get_or_create_nested_backlinks(activity.object, object_model, update=True)

    def handle_delete_activity(self, activity, **kwargs):
        '''
        handles Remove Activities. See https://www.w3.org/ns/activitystreams
        Indicates that the actor has deleted the object
        '''
        object_model = self._get_subclass_with_rdf_type_or_404(activity.object['@type'])

        # get the model reference to saved object
        try:
            object_instance = object_model.objects.get(urlid=activity.object['@id'])
        except object_model.DoesNotExist:
            return

        # disable backlinks first - prevents a duplicate being sent back
        object_instance.allow_create_backlink = False
        object_instance.save()
        object_instance.delete()
        urlid = getattr(object_instance, 'urlid', None)
        if urlid is not None:
            for follower in Follower.objects.filter(follower=urlid):
                follower.delete()

    def handle_follow_activity(self, activity, **kwargs):
        '''
        handles Follow Activities. See https://www.w3.org/ns/activitystreams
        Indicates that the actor is following the object, and should receive Updates on what happens to it
        '''
        object_model = self._get_subclass_with_rdf_type_or_404(activity.object['@type'])

        # get the model reference to saved object
        try:
            object_instance = object_model.objects.get(urlid=activity.object['@id'])
        except object_model.DoesNotExist:
            raise Http404(activity.object['@id'] + ' did not exist')
        if Model.is_external(object_instance):
            raise Http404(activity.object['@id'] + ' is not local to this server')

        # get the inbox field from the actor
        if isinstance(activity.actor, str):
            inbox = activity.actor
        else:
            inbox = getattr(activity.actor, 'inbox', None)
            if inbox is None:
                inbox = getattr(activity.actor, 'id', getattr(activity.actor, '@id'))

        if not Follower.objects.filter(object=object_instance.urlid, inbox=inbox).exists():
            Follower.objects.create(object=object_instance.urlid, inbox=inbox)


class LDPViewSetGenerator(ModelViewSet):
    """An extension of ModelViewSet that generates automatically URLs for the model"""
    model = None
    nested_fields = []
    model_prefix = None
    list_actions = {'get': 'list', 'post': 'create'}
    detail_actions = {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lookup_field = LDPViewSetGenerator.get_lookup_arg(**kwargs)

    @classonlymethod
    def get_model(cls, **kwargs):
        '''gets the model in the arguments or in the viewset definition'''
        model = kwargs.get('model') or cls.model
        if isinstance(model, str):
            model = apps.get_model(model)
        return model

    @classonlymethod
    def get_lookup_arg(cls, **kwargs):
        return kwargs.get('lookup_url_kwarg') or cls.lookup_url_kwarg or kwargs.get('lookup_field') or \
               Model.get_meta(kwargs['model'], 'lookup_field', 'pk') or cls.lookup_field

    @classonlymethod
    def get_detail_expr(cls, lookup_field=None, **kwargs):
        '''builds the detail url based on the lookup_field'''
        lookup_field = lookup_field or cls.get_lookup_arg(**kwargs)
        lookup_group = r'\d' if lookup_field == 'pk' else r'[\w\-\.]'
        return r'(?P<{}>{}+)/'.format(lookup_field, lookup_group)

    @classonlymethod
    def build_nested_view_set(cls, view_set=None):
        '''returns the the view_set parameter mixed into the LDPNestedViewSet class'''
        if view_set is not None:
            class LDPNestedCustomViewSet(LDPNestedViewSet, view_set):
                pass

            return LDPNestedCustomViewSet

        return LDPNestedViewSet

    @classonlymethod
    def urls(cls, **kwargs):
        '''constructs urls list for model passed in kwargs'''
        kwargs['model'] = cls.get_model(**kwargs)
        model_name = kwargs['model']._meta.object_name.lower()
        if kwargs.get('model_prefix'):
            model_name = '{}-{}'.format(kwargs['model_prefix'], model_name)
        detail_expr = cls.get_detail_expr(**kwargs)

        urls = [
            re_path('^$', cls.as_view(cls.list_actions, **kwargs), name='{}-list'.format(model_name)),
            re_path('^' + detail_expr + '$', cls.as_view(cls.detail_actions, **kwargs),
                    name='{}-detail'.format(model_name)),
        ]

        # append nested fields to the urls list
        for field in kwargs.get('nested_fields') or cls.nested_fields:
            # the nested property may have a custom viewset defined
            try:
                related_field = kwargs['model']._meta.get_field(field)
                nested_model = related_field.related_model
            except FieldDoesNotExist:
                related_field = getattr(kwargs['model'], field).field
                nested_model = related_field.model

            if related_field.related_query_name:
                nested_related_name = related_field.related_query_name()
            else:
                nested_related_name = related_field.remote_field.name

            # urls should be called from _nested_ view set, which may need a custom view set mixed in
            view_set = None
            if hasattr(nested_model, 'get_view_set'):
                view_set = nested_model.get_view_set()
            nested_view_set = cls.build_nested_view_set(view_set)

            urls.append(re_path('^' + detail_expr + field + '/',
                                nested_view_set.urls(
                                    model=nested_model,
                                    model_prefix=kwargs['model']._meta.object_name.lower(), # prefix with parent name
                                    lookup_field=Model.get_meta(nested_model, 'lookup_field', 'pk'),
                                    lookup_url_kwarg=kwargs['model']._meta.object_name.lower() + '_id',
                                    exclude=(nested_related_name,) if related_field.one_to_many else (),
                                    permission_classes=Model.get_meta(nested_model, 'permission_classes', [LDPPermissions]),
                                    nested_field=field,
                                    fields=Model.get_meta(nested_model, 'serializer_fields', []),
                                    nested_fields=[],
                                    parent_model=kwargs['model'],
                                    parent_lookup_field=cls.get_lookup_arg(**kwargs),
                                    related_field=related_field,
                                    nested_related_name=nested_related_name)))

        return include(urls)


# LDPViewSetGenerator is a ModelViewSet (DRF) with methods to automatically generate model urls
class LDPViewSet(LDPViewSetGenerator):
    """An automatically generated viewset that serves models following the Linked Data Platform convention"""
    fields = None
    exclude = None
    renderer_classes = (JSONLDRenderer,)
    parser_classes = (JSONLDParser,)
    authentication_classes = (NoCSRFAuthentication,)
    filter_backends = [LocalObjectOnContainerPathBackend]
    prefetch_fields = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # attach filter backends based on permissions classes, to reduce the queryset based on these permissions
        # https://www.django-rest-framework.org/api-guide/filtering/#generic-filtering
        if self.permission_classes:
            filtered_classes = [p for p in self.permission_classes if hasattr(p, 'filter_backends') and p.filter_backends is not None]
            for p in filtered_classes:
                self.filter_backends = list(set(self.filter_backends).union(set(p.filter_backends)))

        self.serializer_class = self.build_read_serializer()
        self.write_serializer_class = self.build_write_serializer()

    def build_read_serializer(self):
        model_name = self.model._meta.object_name.lower()
        lookup_field = get_resolver().reverse_dict[model_name + '-detail'][0][0][1][0]
        meta_args = {'model': self.model, 'extra_kwargs': {
            '@id': {'lookup_field': lookup_field}},
                     'depth': getattr(self, 'depth', Model.get_meta(self.model, 'depth', 0)),
                     # 'depth': getattr(self, 'depth', 4),
                     'extra_fields': self.nested_fields}
        if self.fields:
            meta_args['fields'] = self.fields
        else:
            meta_args['exclude'] = Model.get_meta(self.model, 'serializer_fields_exclude') or ()
        
        return self.build_serializer(meta_args, 'Read')

    def build_write_serializer(self):
        model_name = self.model._meta.object_name.lower()
        lookup_field = get_resolver().reverse_dict[model_name + '-detail'][0][0][1][0]
        meta_args = {'model': self.model, 'extra_kwargs': {
            '@id': {'lookup_field': lookup_field}},
                     'depth': 10,
                     'extra_fields': self.nested_fields}
        if self.fields:
            meta_args['fields'] = self.fields
        else:
            meta_args['exclude'] = self.exclude or Model.get_meta(self.model, 'serializer_fields_exclude') or ()

        return self.build_serializer(meta_args, 'Write')

    def build_serializer(self, meta_args, name_prefix):
        # create the Meta class to associate to LDPSerializer, using meta_args param
        meta_class = type('Meta', (), meta_args)

        from djangoldp.serializers import LDPSerializer

        if self.serializer_class is None:
            self.serializer_class = LDPSerializer

        return type(LDPSerializer)(self.model._meta.object_name.lower() + name_prefix + 'Serializer',
                                   (self.serializer_class,),
                                   {'Meta': meta_class})

    def is_safe_create(self, user, validated_data, *args, **kwargs):
        '''
        A function which is checked before the create operation to confirm the validated data is safe to add
        returns True by default
        :return: True if the operation should be permitted, False to return a 403 response
        '''
        return True

    def check_model_permissions(self, request):
        """
        Check if the request should be permitted when the model-level permissions matter (generally just for creating an object)
        Raises an appropriate exception if the request is not permitted.
        """
        for permission in self.get_permissions():
            if hasattr(permission, 'has_container_permission') and not permission.has_container_permission(request, self):
                self.permission_denied(
                    request,
                    message=getattr(permission, 'message', None)
                )

    def create(self, request, *args, **kwargs):
        self.check_model_permissions(request)
        serializer = self.get_write_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not self.is_safe_create(request.user, serializer.validated_data):
            return Response({'detail': 'You do not have permission to perform this action'},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_create(serializer)
        response_serializer = self.get_serializer()
        data = response_serializer.to_representation(serializer.instance)
        headers = self.get_success_headers(data)
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_write_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        response_serializer = self.get_serializer()
        data = response_serializer.to_representation(serializer.instance)
        return Response(data)

    def get_write_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_write_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_write_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.write_serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.write_serializer_class is not None, (
                "'%s' should either include a `write_serializer_class` attribute, "
                "or override the `get_write_serializer_class()` method."
                % self.__class__.__name__
        )

        return self.write_serializer_class

    def perform_create(self, serializer, **kwargs):
        if hasattr(self.model._meta, 'auto_author') and isinstance(self.request.user, get_user_model()):
            # auto_author_field may be set (a field on user which should be made author - e.g. profile)
            auto_author_field = getattr(self.model._meta, 'auto_author_field', None)
            if auto_author_field is not None:
                kwargs[self.model._meta.auto_author] = getattr(self.request.user, auto_author_field, None)
            else:
                kwargs[self.model._meta.auto_author] = get_user_model().objects.get(pk=self.request.user.pk)
        return serializer.save(**kwargs)

    def perform_update(self, serializer):
        return serializer.save()

    def get_queryset(self, *args, **kwargs):
        if self.model:
            queryset = self.model.objects.all()
        else:
            queryset = super(LDPViewSet, self).get_queryset(*args, **kwargs)
        if self.prefetch_fields is None:
            depth = getattr(self, 'depth', Model.get_meta(self.model, 'depth', 0))
            self.prefetch_fields = get_prefetch_fields(self.model, self.get_serializer(), depth)
        return queryset.prefetch_related(*self.prefetch_fields)

    def dispatch(self, request, *args, **kwargs):
        '''overriden dispatch method to append some custom headers'''
        response = super(LDPViewSet, self).dispatch(request, *args, **kwargs)
        response["Accept-Post"] = "application/ld+json"

        if response.status_code in [201, 200] and '@id' in response.data:
            response["Location"] = str(response.data['@id'])
        else:
            pass

        if is_authenticated_user(request.user):
            try:
                response['User'] = request.user.webid()
            except AttributeError:
                pass
        return response


class LDPNestedViewSet(LDPViewSet):
    """
    A special case of LDPViewSet serving objects of a relation of a given object
    (e.g. members of a group, or skills of a user)
    """
    parent_model = None
    parent_lookup_field = None
    related_field = None
    nested_field = None
    nested_related_name = None

    def get_parent(self):
        return get_object_or_404(self.parent_model, **{self.parent_lookup_field: self.kwargs[self.parent_lookup_field]})

    def perform_create(self, serializer, **kwargs):
        kwargs[self.nested_related_name] = self.get_parent()
        super().perform_create(serializer, **kwargs)

    def get_queryset(self, *args, **kwargs):
        if self.related_field.many_to_many or self.related_field.one_to_many:
            return getattr(self.get_parent(), self.nested_field).all()
        if self.related_field.many_to_one or self.related_field.one_to_one:
            return [getattr(self.get_parent(), self.nested_field)]


class LDPAPIView(APIView):
    '''extends rest framework APIView to support Solid standards'''
    authentication_classes = (NoCSRFAuthentication,)

    def dispatch(self, request, *args, **kwargs):
        '''overriden dispatch method to append some custom headers'''
        response = super().dispatch(request, *args, **kwargs)
        
        if response.status_code in [201, 200] and isinstance(response.data, dict) and '@id' in response.data:
            response["Location"] = str(response.data['@id'])
        else:
            pass

        if is_authenticated_user(request.user):
            try:
                response['User'] = request.user.webid()
            except AttributeError:
                pass
        return response


class LDPSourceViewSet(LDPViewSet):
    model = LDPSource
    federation = None
    filter_backends = []

    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(federation=self.kwargs['federation'])


class WebFingerView(View):
    endpoint_class = WebFingerEndpoint

    def get(self, request, *args, **kwargs):
        return self.on_request(request)

    def on_request(self, request):
        endpoint = self.endpoint_class(request)
        try:
            endpoint.validate_params()

            return JsonResponse(endpoint.response())

        except WebFingerError as error:
            return JsonResponse(error.create_dict(), status=400)

    def post(self, request, *args, **kwargs):
        return self.on_request(request)
