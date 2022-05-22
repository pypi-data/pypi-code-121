from django.urls import path, include

from .views import (
    omise_webhook_view,
    charge_status_json,
    ManagePaymentMethodsView,
    PaymentMethodDeleteView,
    OmiseReturnURIView,
    CheckoutView,
    PromptpayCheckoutView,
    OmiseAccountAndCapabilityJsonView,
)

app_name = "django_omise"

urlpatterns = [
    path(
        "omise_account/",
        OmiseAccountAndCapabilityJsonView.as_view(),
        name="omise_account",
    ),
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("return/<uuid:uid>/", OmiseReturnURIView.as_view(), name="return_uri"),
    path("webhook/", omise_webhook_view, name="webhook"),
    path(
        "promptpay_checkout/<pk>/",
        PromptpayCheckoutView.as_view(),
        name="promptpay_checkout",
    ),
    path("charge_status/", charge_status_json, name="charge_status_json"),
    path(
        "payment_methods/",
        include(
            [
                path(
                    "",
                    ManagePaymentMethodsView.as_view(),
                    name="manage_payment_methods",
                ),
                path(
                    "delete/<pk>/",
                    PaymentMethodDeleteView.as_view(),
                    name="delete_payment_method",
                ),
            ]
        ),
    ),
]
