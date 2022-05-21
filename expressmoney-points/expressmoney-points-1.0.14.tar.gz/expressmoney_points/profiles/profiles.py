__all__ = ('UserProfilePoint', 'UserProfileObjectPoint', 'RussianProfilePoint', 'RussianProfileObjectPoint')

from expressmoney.api import *

SERVICE = 'profiles'


class UserProfileCreateContract(Contract):
    user_id = serializers.IntegerField(min_value=1)
    department = serializers.IntegerField(min_value=1)
    ip = serializers.IPAddressField()
    http_referer = serializers.URLField()


class UserProfileReadContract(UserProfileCreateContract):
    created = serializers.DateTimeField()
    country = serializers.CharField(max_length=2)


class ProfileUpdateContract(Contract):
    first_name = serializers.CharField(max_length=32)
    last_name = serializers.CharField(max_length=32)
    middle_name = serializers.CharField(max_length=32)


class ProfileCreateContract(ProfileUpdateContract):
    NONE = 'NONE'
    PASSPORT = "PP"
    DRIVING_LICENCE = "DL"
    INSURANCE = "INSURANCE"
    TAX_ID = "TAX_ID"
    GOVERNMENT_ID_TYPE_CHOICES = (
        (NONE, gettext_lazy('None')),
        (PASSPORT, gettext_lazy("Passport")),
        (DRIVING_LICENCE, gettext_lazy("Driving licence")),
        (TAX_ID, gettext_lazy("Tax ID")),
        (INSURANCE, gettext_lazy('SNILS')),
    )

    birth_date = serializers.DateField()
    # Address
    postal_code = serializers.CharField(max_length=16, allow_blank=True)
    state = serializers.CharField(max_length=32, allow_blank=True)
    city = serializers.CharField(max_length=32, allow_blank=True)
    street = serializers.CharField(max_length=32, allow_blank=True)
    street_house = serializers.CharField(max_length=8, allow_blank=True)
    street_building = serializers.CharField(max_length=4, allow_blank=True)
    street_lane = serializers.CharField(max_length=16, allow_blank=True)
    street_apartment = serializers.CharField(max_length=8, allow_blank=True)
    address = serializers.CharField(max_length=256, allow_blank=True)
    address_optional = serializers.CharField(max_length=64, allow_blank=True)
    po_box = serializers.CharField(max_length=8, allow_blank=True)
    # Government ID
    government_id_type = serializers.ChoiceField(choices=GOVERNMENT_ID_TYPE_CHOICES, default=NONE)
    government_id_number = serializers.CharField(max_length=16, allow_blank=True)
    government_id_date = serializers.DateField(allow_null=True, required=False)


class ProfileReadContract(ProfileCreateContract):
    created = serializers.DateTimeField()
    updated = serializers.DateTimeField()
    # Underwriting
    is_identified = serializers.BooleanField()
    is_verified = serializers.BooleanField()
    credit_score = serializers.DecimalField(max_digits=3, decimal_places=2, allow_null=True)
    credit_score_created = serializers.DateTimeField(allow_null=True)
    # Address
    address_code = serializers.CharField(max_length=64, allow_blank=True)
    address_coordinates = serializers.CharField(max_length=64, allow_blank=True)
    # property
    is_default = serializers.BooleanField(allow_null=True)


class RussianProfileUpdateContract(ProfileUpdateContract):
    passport_serial = serializers.CharField(max_length=4)
    passport_number = serializers.CharField(max_length=6)


class RussianProfileCreateContract(ProfileCreateContract):
    passport_serial = serializers.CharField(max_length=4)
    passport_number = serializers.CharField(max_length=6)
    passport_issue_name = serializers.CharField(max_length=256, allow_blank=True)
    passport_code = serializers.CharField(max_length=16)
    passport_date = serializers.DateField()
    income = serializers.IntegerField(allow_null=True, required=False)


class RussianProfileReadContract(ProfileReadContract, ):
    passport_serial = serializers.CharField(max_length=4)
    passport_number = serializers.CharField(max_length=6)
    passport_issue_name = serializers.CharField(max_length=256, allow_blank=True)
    passport_code = serializers.CharField(max_length=16)
    passport_date = serializers.DateField()
    income = serializers.IntegerField(allow_null=True)
    income_region = serializers.IntegerField(allow_null=True)
    court_address = serializers.CharField(max_length=256, allow_blank=True)
    fias_region = serializers.CharField(max_length=256, allow_blank=True)


class RussianProfileID(ID):
    _service = SERVICE
    _app = 'profiles'
    _view_set = 'russian_profile'


class UserProfileID(ID):
    _service = SERVICE
    _app = 'profiles'
    _view_set = 'user_profile'


class UserProfilePoint(CreatePointMixin, ContractPoint):
    _point_id = UserProfileID()
    _create_contract = UserProfileCreateContract


class UserProfileObjectPoint(RetrievePointMixin, ContractObjectPoint):
    _point_id = UserProfileID()
    _read_contract = UserProfileReadContract


class RussianProfilePoint(CreatePointMixin, ContractPoint):
    _point_id = RussianProfileID()
    _create_contract = RussianProfileCreateContract


class RussianProfileObjectPoint(RetrievePointMixin, UpdatePointMixin, ContractObjectPoint):
    _point_id = RussianProfileID()
    _read_contract = RussianProfileReadContract
    _update_contract = RussianProfileUpdateContract
