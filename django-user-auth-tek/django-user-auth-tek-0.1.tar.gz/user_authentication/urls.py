from rest_framework.routers import SimpleRouter
from users.API import (
    otp_api,
    user_api,
    update_password_api
)

# Create a router and register our viewsets with it.
router = SimpleRouter(trailing_slash=False)
router.register("verify", otp_api.OTPViewset, 'verify')
router.register("signup", user_api.UserRegistrationViewSet, 'signup'),
router.register("signin", user_api.UserLoginViewSet, 'signin'),
router.register("profile", user_api.UserProfileViewSet, 'profile'),
router.register("user", user_api.UserViewSet, "user"),
router.register("reset-password", update_password_api.UpdatePassowrdViewSet, "reset-password")
router.register("change-password", update_password_api.ChangePasswordViewSet, "change-password")

urlpatterns = router.urls