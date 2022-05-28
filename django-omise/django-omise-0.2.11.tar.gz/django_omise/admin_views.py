from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib import messages

from django.urls import reverse
from django.views.generic import FormView

from django_omise.forms import IssueRefundForm
from django_omise.models.core import Charge
from django_omise.omise import omise


class IssueRefundView(UserPassesTestMixin, FormView):
    template_name = "admin/django_omise/charge/issue_refund_form.html"
    form_class = IssueRefundForm

    def test_func(self):
        return self.request.user.has_perm("django_omise.issue_refund")

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs["charge"] = self.get_object()
        return kwargs

    def get_object(self):
        return Charge.objects.get(id=self.kwargs["pk"])

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["charge"] = self.get_object()
        return context

    def get_success_url(self):
        return reverse(
            "admin:django_omise_charge_change",
            args=[
                self.get_object().pk,
            ],
        )

    def form_valid(self, form):
        refund_amount = form.cleaned_data["refund_amount"]
        charge = self.get_object()
        omise_charge = charge.get_omise_object()

        try:
            omise_charge.refund(amount=refund_amount)
        except omise.errors.FailedRefundError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

        messages.success(
            self.request,
            "Refund issued. This might take a few seconds to update. Try refreshing if you do not see the refund data.",
        )
        return super().form_valid(form)
