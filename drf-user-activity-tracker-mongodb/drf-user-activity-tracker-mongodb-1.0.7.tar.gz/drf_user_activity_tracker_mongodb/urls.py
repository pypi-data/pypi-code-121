from django.urls import path
from drf_user_activity_tracker_mongodb.views import ActivityLogView

app_name = "activity_log"


urlpatterns = [
    path('history/', ActivityLogView.as_view(), name='history')
]


