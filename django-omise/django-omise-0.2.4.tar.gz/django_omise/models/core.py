from .base import OmiseBaseModel, OmiseMetadata
from .choices import Currency, ChargeStatus, ChargeSourceType, SourceFlow
from .managers import NotDeletedManager

import uuid

from django.apps import apps
from django_omise.omise import omise

from django.conf import settings
from django.contrib.auth import get_user_model

from django.db import models

from django.urls import reverse_lazy, reverse
from django.utils.translation import gettext_lazy as _

from typing import TYPE_CHECKING, Optional, Dict

if TYPE_CHECKING:
    User = get_user_model()


class Customer(OmiseBaseModel, OmiseMetadata):

    """
    A card representing Omise Customer object.

    Official documentation: https://www.omise.co/customers-api
    """

    NON_DEFAULT_FIELDS = OmiseBaseModel.NON_DEFAULT_FIELDS + [
        "charges",
        "user",
        "charge_schedules",
    ]

    omise_class = omise.Customer

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="omise_customers",
    )

    deleted = models.BooleanField(
        default=False, help_text=_("Whether this customer was deleted.")
    )

    default_card = models.ForeignKey(
        "Card", on_delete=models.SET_NULL, blank=True, null=True, related_name="+"
    )

    description = models.TextField(blank=True)

    email = models.EmailField(blank=True)

    objects = NotDeletedManager()

    def __str__(self) -> str:
        if self.user:
            return f"Omise{self.__class__.__name__}: {str(self.user)}"
        return f"Omise{self.__class__.__name__}: {self.id}"

    def add_card(self, token: omise.Token) -> "Card":
        """
        Add a new card to the user

        :param token: The token retrieved from Omise API.

        :returns: A new card instance.
        """
        omise_customer = omise.Customer.retrieve(self.id)
        omise_customer.update(card=token.id)

        card = token.card

        new_card = Card.update_or_create_from_omise_object(
            omise_object=card,
        )

        new_card.customer = self
        new_card.save()

        return new_card

    @property
    def schedules(self):
        """
        Get a list of all charge schedules belonging to this customer.

        :returns: A list of django_omise.models.schedule.Schedule
        """
        schedule_model = apps.get_model(app_label="django_omise", model_name="Schedule")
        schedule_ids = self.charge_schedules.all().values_list("schedule", flat=True)
        schedules = schedule_model.objects.filter(pk__in=schedule_ids)
        return schedules

    def remove_card(self, card: "Card") -> None:
        """
        Remove the card from the customer.

        :param card: The card to be removed.

        :returns: None
        """
        self.cards.filter(id=card.id).delete()

    def charge_with_card(
        self,
        amount: int,
        currency: Currency.choices,
        card: "Card",
        return_uri: str = None,
        metadata: dict = None,
    ) -> "Charge":
        """
        Charge the customer with provided card.

        :returns: An instace of Charge object.
        """
        return Charge.charge(
            amount=amount,
            currency=currency,
            card=card,
            return_uri=return_uri,
            metadata=metadata,
        )

    @classmethod
    def get_or_create(cls, user: "User") -> "Customer":
        """
        Get or create django_omise customer.o

        :param user: The user model instance to create a customer.
        :returns: A tuple of Customer instance and whether the object is newly created.
        """
        livemode = settings.OMISE_LIVE_MODE

        try:
            return (
                Customer.objects.get(user=user, livemode=livemode, deleted=False),
                False,
            )
        except Customer.DoesNotExist:

            customer_attributes = {}

            if user.email:
                customer_attributes["email"] = user.email

            omise_customer = cls.omise_class.create(**customer_attributes)

            if omise_customer.livemode != livemode:
                raise ValueError(
                    f"The API livemode inconsistent. API livemode: {omise_customer.livemode}. settings.OMISE_LIVE_MODE: {livemode}"
                )

            return (
                Customer.objects.create(
                    id=omise_customer.id,
                    user=user,
                    livemode=omise_customer.livemode,
                ),
                True,
            )


class Card(OmiseBaseModel):
    """
    A class representing Omise's Card object.

    Official documentation: https://www.omise.co/cards-api
    """

    omise_class = omise.Card

    NON_DEFAULT_FIELDS = OmiseBaseModel.NON_DEFAULT_FIELDS + [
        "charges",
        "customer",
        "charge_schedules",
    ]

    customer = models.ForeignKey(
        Customer,
        blank=True,
        null=True,
        related_name="cards",
        on_delete=models.PROTECT,
    )

    name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=255, blank=True)

    postal_code = models.CharField(max_length=255, blank=True)
    state = models.CharField(max_length=255, blank=True)
    street1 = models.CharField(max_length=255, blank=True)
    street2 = models.CharField(max_length=255, blank=True)
    tokenization_method = models.CharField(max_length=255, blank=True)
    first_digits = models.CharField(max_length=6, blank=True)
    last_digits = models.CharField(max_length=4)
    bank = models.CharField(max_length=255, blank=True)
    brand = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=255, blank=True)

    expiration_month = models.CharField(max_length=2, blank=True)
    expiration_year = models.CharField(max_length=4, blank=True)

    fingerprint = models.TextField(blank=True)

    financing = models.CharField(max_length=10, blank=True)

    deleted = models.BooleanField(
        default=False, help_text=_("Whethe this card was deleted.")
    )

    objects = NotDeletedManager()

    def __str__(self) -> str:
        return f"Omise{self.__class__.__name__}: {self.last_digits}"

    def delete(self):
        omise_customer = self.customer.get_omise_object()
        card = omise_customer.cards.retrieve(self.id)
        card.destroy()

        self.deleted = True
        self.save()


class Charge(OmiseBaseModel, OmiseMetadata):
    """
    A class representing Omise Charge object.

    Official documentation: https://www.omise.co/charges-api
    """

    omise_class = omise.Charge

    status = models.CharField(
        max_length=10,
        choices=ChargeStatus.choices,
        help_text=_("Status of this charge."),
    )

    amount = models.IntegerField(
        help_text="Charge amount in the smallest unit of charge currency"
    )
    authorize_uri = models.CharField(
        max_length=255,
        help_text=_("URI for payment authorization (e.g. 3-D Secure)."),
        blank=True,
    )

    authorized = models.BooleanField(
        blank=True, null=True, help_text=_("Whether charge has been authorized.")
    )
    capturable = models.BooleanField(
        blank=True,
        null=True,
        help_text=_("Whether charge is able to be captured (paid)."),
    )
    capture = models.BooleanField(
        blank=True,
        null=True,
        help_text=_("Whether charge is set to be automatically captured (paid)."),
    )

    card = models.ForeignKey(
        Card,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="charges",
        help_text=_("Card that was charged (if card was charged)."),
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
    )

    customer = models.ForeignKey(
        Customer,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="charges",
        help_text=_("Customer associated with charge."),
    )

    description = models.TextField(blank=True)
    disputable = models.BooleanField(blank=True, null=True)

    expired = models.BooleanField(
        blank=True, null=True, help_text=_("Whether this charge has expired.")
    )

    expired_at = models.DateTimeField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    failure_code = models.CharField(max_length=255, blank=True)
    failure_message = models.TextField(blank=True)

    fee = models.IntegerField()
    fee_vat = models.IntegerField()

    funding_amount = models.IntegerField(
        blank=True,
        null=True,
        help_text=_(
            "For multi-currency charges, amount after exchange into account funding currency."
        ),
    )

    funding_currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
    )

    interest = models.IntegerField(
        blank=True,
        null=True,
        help_text=_(
            "Interest paid by customer or merchant over the course of an installment term."
        ),
    )

    interest_vat = models.IntegerField(
        blank=True,
        null=True,
        help_text=_("Value-added Tax (VAT) applied to interest."),
    )

    ip = models.CharField(
        max_length=255,
        blank=True,
        help_text=_(
            "IP address provided to Omise at charge creation. May be IPv4 or IPv6."
        ),
    )

    net = models.IntegerField(
        help_text=_("funding_amount after fees, interest, and VAT deducted.")
    )

    paid = models.BooleanField(help_text=_("Whether charge has been captured (paid)."))
    paid_at = models.DateTimeField(blank=True, null=True)
    refundable = models.BooleanField(
        help_text=_("Whether charge is able to be refunded.")
    )

    refunded_amount = models.IntegerField(
        blank=True,
        null=True,
        help_text=_("Refunded amount in smallest unit of currency."),
    )

    return_uri = models.TextField(
        blank=True,
        help_text=_(
            "URI to which customer is redirected after 3-D Secure card authorization or other redirect-based authorization."
        ),
    )

    reversed = models.BooleanField(
        blank=True,
        null=True,
        help_text=_("Whether charge authorization is able to be reversed."),
    )

    schedule = models.ForeignKey(
        "django_omise.Schedule",
        on_delete=models.PROTECT,
        related_name="charges",
        blank=True,
        null=True,
    )

    source = models.ForeignKey(
        "Source",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="charges",
    )

    voided = models.BooleanField(
        blank=True,
        null=True,
        help_text=_(
            "Whether, in the case of a refund, charge was voided instead. Charges are voided if refund is processed before settlement time."
        ),
    )

    zero_interest_installments = models.BooleanField(
        blank=True,
        null=True,
        help_text=_(
            "Whether merchant absorbs the interest for installment payments; must match value in associated source."
        ),
    )

    @property
    def human_amount(self) -> float:
        if not self.pk:
            return 0
        if self.currency == Currency.JPY:
            return f"{self.amount:,.2f}"
        return f"{self.amount / 100:,.2f}"

    @classmethod
    def charge(
        cls,
        amount: int,
        currency: Currency.choices,
        token: Optional[omise.Token] = None,
        card: Optional[Card] = None,
        source: Optional[Dict] = None,
        return_uri: str = None,
        metadata: dict = None,
    ) -> "Charge":
        """
        Charge the customer with provided payment_method.

        :param amount: The amount to charge in the smallest unit.
        :param currency: The currency to charge.
        :param token: The token to charge.
        :param card: The card to charge.
        :param source: The source to charge.
        :param return_uri optional: The return uri.
        :param metadata optional: The charge metadata.
        :returns: An instace of Charge object.
        """
        if [token, card, source].count(None) == 3:
            raise ValueError("At least a token, a card, or a source is required")

        if [token, card, source].count(None) != 2:
            raise ValueError("Only one of token, card, or source must be specified")

        uid = uuid.uuid4()

        host = settings.OMISE_CHARGE_RETURN_HOST
        if return_uri is None:
            return_uri = f'https://{host}{reverse("django_omise:return_uri", kwargs={"uid": uid})}'

        if metadata is None:
            metadata = {}

        charge_details = {}

        if token is not None:
            if type(token) == str:
                charge_details["card"] = token
            else:
                charge_details["card"] = token.id

        if card is not None:
            charge_details["card"] = card.id
            charge_details["customer"] = card.customer.id

        if source is not None:
            charge_details["source"] = source

        charge = omise.Charge.create(
            amount=int(amount),
            currency=currency,
            metadata=metadata,
            return_uri=return_uri,
            **charge_details,
        )

        return cls.update_or_create_from_omise_object(omise_object=charge, uid=uid)


class Source(OmiseBaseModel):
    """
    A class representing Omise Source object.

    Official documentation: https://www.omise.co/sources-api
    """

    omise_class = omise.Source

    NON_DEFAULT_FIELDS = OmiseBaseModel.NON_DEFAULT_FIELDS + [
        "charges",
    ]

    amount = models.IntegerField(
        help_text=_("Source amount in smallest unit of source currency")
    )

    bank = models.CharField(max_length=255, blank=True)

    barcode = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Source amount in smallest unit of source currency"),
    )

    charge_status = models.CharField(
        max_length=10,
        choices=ChargeStatus.choices,
        help_text=_("Status of charge created using this source (if any)"),
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
    )

    email = models.CharField(
        max_length=255, blank=True, help_text=_("The payer's email")
    )

    flow = models.CharField(
        max_length=50,
        help_text=_(
            "The payment flow payers need to go through to complete the payment. One of redirect, offline, or app_redirect"
        ),
        choices=SourceFlow.choices,
    )

    installment_term = models.IntegerField(
        blank=True, null=True, help_text=_("Installment term in months")
    )
    mobile_number = models.CharField(max_length=50, blank=True)
    name = models.CharField(max_length=255, blank=True, help_text=_("Payer's name"))
    phone_number = models.CharField(max_length=50, blank=True)
    platform_type = models.CharField(
        max_length=50,
        blank=True,
        help_text=_(
            "Platform from which payer is making a payment. One of WEB, IOS, or ANDROID"
        ),
    )

    receipt_amount = models.IntegerField(blank=True, null=True)
    store_id = models.CharField(max_length=255, blank=True)
    store_name = models.CharField(max_length=255, blank=True)
    terminal_id = models.CharField(max_length=255, blank=True)

    type = models.CharField(max_length=255, choices=ChargeSourceType.choices)

    zero_interest_installments = models.BooleanField(blank=True, null=True)

    @property
    def source_type_name(self):
        source_types = {
            "internet_banking_bay": _("Internet Banking Krungsri Bank"),
            "internet_banking_bbl": _("Internet Banking Bangkok Bank"),
            "internet_banking_ktb": _("Internet Banking Krungthai Bank"),
            "internet_banking_scb": _("Internet Banking SCB Bank"),
            ChargeSourceType.PROMPTPAY: ChargeSourceType.PROMPTPAY.label,
            ChargeSourceType.RABBIT_LINEPAY: ChargeSourceType.RABBIT_LINEPAY.label,
            ChargeSourceType.TRUEMONEY_WALLET: ChargeSourceType.TRUEMONEY_WALLET.label,
        }
        return source_types[self.type]

    @property
    def human_amount(self) -> float:
        if not self.pk:
            return 0
        if self.currency == Currency.JPY:
            return f"{self.amount:,.2f}"
        return f"{self.amount / 100:,.2f}"


class Refund(OmiseBaseModel, OmiseMetadata):

    charge = models.ForeignKey(
        Charge,
        related_name="refunds",
        on_delete=models.PROTECT,
    )

    amount = models.IntegerField(
        help_text="Refund amount in smallest unit of charge currency.",
    )

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
    )

    funding_amount = models.IntegerField(
        blank=True,
        null=True,
        help_text=_(
            "For multi-currency charges, amount after exchange into account funding currency."
        ),
    )

    funding_currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
    )

    voided = models.BooleanField()

    @property
    def human_amount(self) -> float:
        if not self.pk:
            return 0
        if self.currency == Currency.JPY:
            return f"{self.amount:,.2f}"
        return f"{self.amount / 100:,.2f}"
