from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response

from drf_user_activity_tracker_mongodb.utils import MyCollection
from drf_user_activity_tracker_mongodb.serializers import ActivityLogSerializer, ActivityLogAdminSerializer


class ActivityLogView(GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ActivityLogSerializer

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.request.user.is_superuser:
            serializer = ActivityLogAdminSerializer
        return serializer

    def get(self, request):
        if not self.request.user.is_superuser:
            response = MyCollection().list(user_id=self.request.user.id, api=True)
        else:
            response = MyCollection().list(api=True)

        serializer = self.get_serializer(instance=response, many=True)
        return Response(serializer.data)


