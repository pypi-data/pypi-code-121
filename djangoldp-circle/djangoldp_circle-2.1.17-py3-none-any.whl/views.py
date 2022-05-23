from django.http import Http404
from django.contrib.auth import get_user_model
from django.conf import settings

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from djangoldp.filters import LocalObjectFilterBackend
from djangoldp.views import LDPViewSet, JSONLDParser, JSONLDRenderer
from djangoldp.serializers import LDPSerializer
from djangoldp.models import Model


class CircleMembersViewset(LDPViewSet):

    def get_parent(self):
        raise NotImplementedError("get_parent not implemented in CircleMembersViewset")

    def is_safe_create(self, user, validated_data, *args, **kwargs):
        from djangoldp_circle.models import Circle, CircleMember

        try:
            if 'circle' in validated_data.keys():
                circle = Circle.objects.get(urlid=validated_data['circle']['urlid'])
            else:
                circle = self.get_parent()

            # public circles any user can add
            if circle.status == 'Public':
                return True

            # other circles any circle member can add a user
            if circle.members.filter(user=user).exists():
                return True
        except Circle.DoesNotExist:
            return True
        except (KeyError, AttributeError):
            raise Http404('circle not specified with urlid')

        return False


class CirclesRequestableViewset(LDPViewSet):
    '''Viewset for accessing all Restricted circles'''

    filter_backends = [LocalObjectFilterBackend]

    def __init__(self, **kwargs):
        from djangoldp_circle.models import Circle

        kwargs['model'] = Circle
        kwargs['nested_fields'] = Circle.nested.fields()
        super().__init__(**kwargs)

    def get_queryset(self):
        return super().get_queryset().exclude(members__user=self.request.user.id)\
            .exclude(access_requests__user=self.request.user.id)\
            .filter(status="Restricted")


class CirclesJoinableViewset(LDPViewSet):
    '''Viewset for accessing all Public circles'''

    filter_backends = [LocalObjectFilterBackend]

    def __init__(self, **kwargs):
        from djangoldp_circle.models import Circle

        kwargs['model'] = Circle
        kwargs['nested_fields'] = Circle.nested.fields()
        super().__init__(**kwargs)

    def get_queryset(self):
        return super().get_queryset().exclude(members__user=self.request.user.id)\
            .filter(status="Public")

class CircleAccessRequestFilteredByUserViewSet(LDPViewSet):
    '''Viewset for accessing all AccessRequests linked to me'''

    filter_backends = [LocalObjectFilterBackend]

    def __init__(self, **kwargs):
        from djangoldp_circle.models import CircleAccessRequest

        kwargs['model'] = CircleAccessRequest
        kwargs['nested_fields'] = CircleAccessRequest.nested.fields()
        super().__init__(**kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user.id)

class CircleAccessRequestServerNotificationView(APIView):
    '''
    A view to handle notifying users about changes in Circle Access Requests from distant servers
    '''
    permission_classes = (AllowAny,)
    parser_classes = (JSONLDParser,)
    renderer_classes = (JSONLDRenderer,)

    def get(self, request):
        try:
            from djangoldp_notification.models import Notification
            from djangoldp_circle.models import CircleAccessRequest
            from djangoldp_circle.serializers import CircleAccessRequestModelSerializer

            data = request.data

            if 'object' in data and 'status' in data['object']:
                object_urlid = data['object']['@id'] \
                    if (not isinstance(data['object'], str) and '@id' in data['object']) \
                     else data['object']

                # create a backlinked version of the CircleAccessRequest passed, if one does not exist
                # we save this with all the fields we will need for the notification email later
                if not isinstance(data['object'], str):
                    try:
                        ar = CircleAccessRequest.objects.get(urlid=object_urlid)
                    except CircleAccessRequest.DoesNotExist:
                        ar = CircleAccessRequest(urlid=object_urlid)

                    serializer = CircleAccessRequestModelSerializer(ar, data=data['object'])

                    if not serializer.is_valid():
                        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    
                    serializer.save()
                
                # save the notification itself, which will trigger the user to be notified
                summary = data['summary'] if 'summary' in data else ''

                # notifying the administrator that a CircleAccessRequest was created
                if data['object']['status'] == "Pending" and 'target' in data:
                    recipient = get_user_model().objects.filter(urlid=data['target'])
                    
                    if not recipient.exists() or Model.is_external(recipient):
                        return Response("The recipient user is not local to this server", status=status.HTTP_404_NOT_FOUND)

                    Notification.objects.create(user=recipient[0], object=object_urlid, author=data['author'], type=data['type'], summary=summary)
                
                # notifying the user that a response was made to their request
                elif 'user' in data['object'] and '@id' in data['object']['user']:
                    recipient = get_user_model().objects.filter(urlid=data['object']['user']['@id'])

                    if not recipient.exists() or Model.is_external(recipient):
                        return Response("The recipient user is not local to this server", status=status.HTTP_404_NOT_FOUND)

                    Notification.objects.create(user=recipient[0], object=object_urlid, author=data['author'], type=data['type'], summary=summary)
                
                return Response(status=status.HTTP_201_CREATED)

        except ImportError:
            return Response("Notifications are not supported by this server", status=status.HTTP_404_NOT_FOUND)
