import pytest

from sym.flow.cli.models.service import BaseService
from sym.flow.cli.models.user import CSVMatcher, Identity


class TestCSVMatcher:
    def test_dict_init(self):
        matcher = {"email": "user@symops.io"}
        service = BaseService(slug="sym", external_id="cloud")
        csv_matcher = CSVMatcher.from_dict(service=service, matcher=matcher)
        assert csv_matcher.value == "user@symops.io"
        assert csv_matcher.to_dict() == matcher

    def test_unknown_mapping(self):
        service = BaseService(slug="twitter", external_id="cloud")
        value = '{"some_unknown_service":"user@sus.io"}'
        matcher = CSVMatcher(service=service, value=value)
        assert matcher.to_dict() == {"some_unknown_service": "user@sus.io"}

    def test_invalid_unknown_mapping(self):
        service = BaseService(slug="twitter", external_id="cloud")
        value = "this is not json"
        matcher = CSVMatcher(service=service, value=value)
        with pytest.raises(ValueError, match="should be valid json"):
            matcher.to_dict() == {"some_unknown_service": "user@sus.io"}


class TestIdentity:
    def test_regular_init(self):
        matcher = {"email": "user@symops.io"}
        service = BaseService(slug="google", external_id="symops.io")
        identity = Identity(matcher=matcher, service=service)
        assert identity.to_csv() == matcher["email"]

    def test_from_csv(self):
        matcher = {"email": "user@symops.io"}
        identity = Identity.from_csv(
            service_key="google:symops.io", matcher_value=matcher["email"]
        )
        assert identity.to_csv() == matcher["email"]

    def test_parse_service_key(self):
        service_type, external_id = Identity.parse_service_key("google:symops.io")
        assert service_type == "google"
        assert external_id == "symops.io"

    def test_equality(self):
        assert Identity.parse_service_key(
            "slack:symops.io"
        ) != Identity.parse_service_key("google:symops.io")
        assert Identity.parse_service_key(
            "google:symops.io"
        ) == Identity.parse_service_key("google:symops.io")
