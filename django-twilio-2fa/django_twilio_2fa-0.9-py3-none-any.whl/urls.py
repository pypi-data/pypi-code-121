from django.urls import path, include
from .views import *


app_name = "twilio_2fa"


urlpatterns = [
    path(
        "",
        Twilio2FAIndexView.as_view(),
        name="index",
    ),
    path(
        "register",
        Twilio2FARegisterView.as_view(),
        name="register"
    ),
    path(
        "change",
        Twilio2FAChangeView.as_view(),
        name="change"
    ),
    path(
        "start",
        Twilio2FAStartView.as_view(),
        name="start"
    ),
    path(
        "verify",
        Twilio2FAVerifyView.as_view(),
        name="verify"
    ),
    path(
        "success",
        Twilio2FASuccessView.as_view(),
        name="success"
    ),
    path(
        "failed",
        Twilio2FAFailedView.as_view(),
        name="failed"
    )
]
