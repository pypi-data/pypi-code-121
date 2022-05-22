from .forms import CheckoutWithCardsForm, CheckoutForm
from .models.core import Customer, Charge, Card
from .models.choices import Currency, ChargeStatus, SourceFlow, ChargeSourceType
from .omise import omise

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import FormView

from typing import Dict, Optional


class CheckoutMixin(FormView):
    form_class = CheckoutForm

    def charge(self, charge_type_details: Dict) -> Charge:
        """
        Created a charge with selected payment method.

        :param charge_type_details: Dict of charge type details.
                                    E.g. {'card': core.Card}
                                    or {'token': omise.Token}
                                    or {'source': {'type': 'internet_banking_bbl'}}

        :returns: A new Charge instance.
        """
        charge_details = self.get_charge_details()
        charge_kwargs = self.get_charge_kwargs()

        amount = charge_details["amount"]
        currency = charge_details["currency"]

        charge = Charge.charge(
            amount=amount,
            currency=currency,
            **charge_type_details,
            **charge_kwargs,
        )

        return charge

    def get_form_kwargs(self, *args, **kwargs) -> Dict:
        """
        Overwrite this method to provide data for the form.

        :returns: A dictionary in the form of {'user': auth.User, 'amount': int, 'currency': Currency}
        """
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs["user"] = self.request.user
        return {**kwargs, **self.get_charge_details()}

    def get_charge_details(self) -> Dict[int, Currency]:
        """
        Overwrite this method to provide the charge amount and currency.

        Read more on the amount and currency here https://www.omise.co/currency-and-amount

        :returns: Dictionary of charge amount in the smallest unit (int) and the 3-digit currency code. {"amount": int, "currency": str}
        """
        raise NotImplementedError("Must rewrite get_charge_details method.")

    def get_omise_customer(self) -> Optional[Customer]:
        """
        Get the user to charge. Neccessary for charging with existing card.
        Overwrite this method to provide different way to obtain the customer instance.

        :returns: An instance of Customer if the user is logged in. None otherwise.
        """
        user = self.request.user

        if user.is_authenticated == False:
            return None

        customer, created = Customer.get_or_create(user=self.request.user)
        return customer

    def get_charge_kwargs(self) -> Dict:
        """
        Overwrite this method to add charge parameters.

        E.g. You could return {'metadata': {'successful_url': ..., 'failed_url': ...}} to redirect to specific view
        when a user complete actions from pending charges.

        :return: A dictionary of charge parameters
        """
        return dict()

    def form_valid(self, form):

        charge_type_details = form.get_charge_type_details()

        try:
            charge = self.charge(charge_type_details=charge_type_details)
        except omise.errors.InvalidChargeError as e:
            messages.error(
                self.request,
                f"Payment failed: {str(e)}",
            )
            return super().form_invalid(form)

        self.process_charge_and_form(charge, form)

        if charge.status == ChargeStatus.FAILED:
            messages.error(
                self.request,
                f"Payment failed: {charge.failure_message}",
            )
            return super().form_invalid(form)

        if charge.status == ChargeStatus.PENDING:
            if not charge.source:
                return redirect(charge.authorize_uri)

            if charge.source.flow != SourceFlow.OFFLINE:
                return redirect(charge.authorize_uri)

            if charge.source.type == ChargeSourceType.PROMPTPAY:
                return redirect(
                    reverse(
                        "django_omise:promptpay_checkout",
                        kwargs={"pk": charge.id},
                    )
                )

        if charge.status == ChargeStatus.SUCCESSFUL:
            messages.success(self.request, _("Payment successful."))

        return super().form_valid(form)

    def process_charge_and_form(self, charge: Charge, form):
        """
        Overwrite this method to process the new charge object with the form.

        :params charge: The new Charge object.
        :params form: The form instance
        """
        pass


class CheckoutWithCardsMixin(FormView):
    form_class = CheckoutWithCardsForm

    def charge_with_card(self, card: Card) -> Charge:
        """
        Charge the user with selected card.

        :returns: An instance of Charge object
        """
        customer = self.get_omise_customer()
        charge_details = self.get_charge_details()
        charge = customer.charge_with_card(
            amount=charge_details["amount"],
            currency=charge_details["currency"],
            card=card,
            **self.get_charge_kwargs(),
        )

        return charge

    def get_charge_details(self) -> Dict[int, Currency]:
        """
        Overwrite this method to provide the charge amount and currency.

        Read more on the amount and currency here https://www.omise.co/currency-and-amount

        :returns: Dictionary of charge amount in the smallest unit (int) and the 3-digit currency code. {"amount": int, "currency": str}
        """

    def get_omise_customer(self) -> Customer:
        """
        Overwrite this method to provide the customer instance to charge.

        :returns: An instance of Customer
        """
        if self.request.user.is_authenticated:
            customer, created = Customer.get_or_create(user=self.request.user)
            return customer

    def get_charge_kwargs(self) -> Dict:
        """
        Overwrite this method to add charge parameters.

        :return: A dictionary of charge parameters
        """
        return dict()

    def form_valid(self, form):

        selected_card = form.cleaned_data["card"]

        try:
            charge = self.charge_with_card(card=selected_card)
        except omise.errors.InvalidChargeError as e:
            messages.error(
                self.request,
                f"Payment failed: {str(e)}",
            )
            return super().form_invalid(form)

        self.process_new_charge(charge)

        if charge.status == ChargeStatus.FAILED:
            messages.error(
                self.request,
                f"Payment failed: {charge.failure_message}",
            )
            return super().form_invalid(form)

        if charge.status == ChargeStatus.PENDING:
            return redirect(charge.authorize_uri)

        if charge.status == ChargeStatus.SUCCESSFUL:
            messages.success(self.request, _("Payment successful."))

        return super().form_valid(form)

    def process_new_charge(self, charge: Charge):
        """
        Overwrite this method to process the new charge object.

        :params charge: The new Charge object.
        """
        pass
