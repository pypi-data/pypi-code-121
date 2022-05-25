from typing import Optional

import pytest

from sym.sdk.resource import (
    SRN,
    InvalidSlugError,
    InvalidSRNError,
    MultipleErrors,
    SymResource,
    TrailingSeparatorError,
)


class MockSymResource(SymResource):
    """This is a test class for SymResource behavior."""


class TestResource:
    def test_sym_resource_fails_on_malformed_srn(self):
        self._test_bad("foo", InvalidSRNError)
        self._test_bad("foo:bar", InvalidSRNError)
        self._test_bad("foo:bar:baz", InvalidSRNError)
        self._test_bad("foo:bar:baz:boz", InvalidSRNError)
        self._test_bad("foo:bar:baz:lates:", TrailingSeparatorError, match="trailing separator.")
        self._test_bad("foo:bar:baz:1.0:", InvalidSRNError)
        self._test_bad("foo:bar:baz:1.0.0::", InvalidSRNError)
        self._test_bad("foo:bar:baz:latest:1.0.0:", TrailingSeparatorError)
        self._test_bad("foo:bar:baz:1.3000.0:something", InvalidSRNError)
        self._test_bad("foo:bar:baz:something", InvalidSRNError)
        self._test_bad("foo:bar:baz:latestsomething", InvalidSRNError)
        self._test_bad("foo:bar:baz:latest:", TrailingSeparatorError)
        self._test_bad("foo!foobar:bar:baz:latest:foo", InvalidSlugError, match="org")
        self._test_bad("sym:flow:something::", InvalidSRNError)
        self._test_bad("foo!foobar:bar:baz:1000.0.2000:foo", MultipleErrors, match="version")
        self._test_bad("sym:integration:missing-type:1.0.0", InvalidSRNError)
        self._test_bad("sym:integration:missing-type:1.0.0:1234-5667", InvalidSRNError)
        self._test_bad("sym:integration::empty-type:1.0.0", InvalidSlugError, match="type")

    def _test_bad(self, srn, exc, match: str = None):
        if match:
            with pytest.raises(exc, match=match):
                SRN.parse(srn)
        else:
            with pytest.raises(exc):
                SRN.parse(srn)

    def test_sym_srn_succeeds_on_valid_srn(self):
        self._test_good(
            "sym:foo-bar:12345-11233:0.1.0:stuff",
            "sym",
            "foo-bar",
            None,
            "12345-11233",
            "0.1.0",
            "stuff",
        )
        self._test_good(
            "foo:bar:baz:1.300.0:something", "foo", "bar", None, "baz", "1.300.0", "something"
        )
        self._test_good("foo:bar:baz:latest", "foo", "bar", None, "baz", "latest", None)
        self._test_good("foo_foo:bar:baz:latest", "foo_foo", "bar", None, "baz", "latest", None)
        self._test_good(
            "sym:template:approval:1.0.0", "sym", "template", None, "approval", "1.0.0", None
        )
        self._test_good(
            "sym:template:approval:1.0.0:e97af6b3-0249-4855-971f-4e1dd188773a",
            "sym",
            "template",
            None,
            "approval",
            "1.0.0",
            "e97af6b3-0249-4855-971f-4e1dd188773a",
        )
        self._test_good(
            "sym:template:approval:1.0.0",
            "sym",
            "template",
            None,
            "approval",
            "1.0.0",
            None,
        )
        self._test_good(
            "sym:integration:slack:my-integration:latest",
            "sym",
            "integration",
            "slack",
            "my-integration",
            "latest",
            None,
        )

    def _test_good(
        self,
        raw,
        org: str,
        model: str,
        model_type: Optional[str],
        slug: str,
        version: str,
        identifier: Optional[str],
    ):
        srn = SRN.parse(raw)
        assert srn.organization == org
        assert srn.model == model
        assert srn.type == model_type
        assert srn.slug == slug
        assert srn.version == version
        assert srn.identifier == identifier

    def test_srn_copy_should_succeed_without_identifier(self):
        srn_string = "foo:bar:baz:1.0.0"

        srn = SRN.parse(srn_string)

        assert str(srn.copy(version="latest")) == "foo:bar:baz:latest"
        assert str(srn.copy(organization="myorg")) == "myorg:bar:baz:1.0.0"

    def test_srn_str_should_produce_an_identical_srn(self):
        text = "sym:template:approval:1.0.0"
        srn = SRN.parse(text)

        srn_str = str(srn)
        srn2 = SRN.parse(srn_str)

        assert srn == srn2
        assert str(srn) == str(srn2)
        assert text == srn_str

    def test_sym_resource_srn_getattr_fallback(self):
        srn = SRN.parse("test:mock:slug:latest:12345")
        resource = MockSymResource(srn=srn)

        assert resource.srn == srn
        assert resource.name == srn.slug
        assert resource.organization == srn.organization
        assert resource.identifier == srn.identifier

    def test_sym_resource_srn_getattr_errors(self):
        srn = SRN.parse("test:mock:slug:latest:12345")
        resource = MockSymResource(srn=srn)

        # Ensure a normal missing attribute errors properly.
        with pytest.raises(AttributeError, match="no attribute 'nope'"):
            resource.nope

        # Delete the attributes so the __getattr__ override should fall back,
        # but we want to ensure it doesn't infinitely recurse.
        delattr(resource, "_srn")
        with pytest.raises(AttributeError, match="no attribute 'srn"):
            resource.srn

    def test_srn_type(self):
        for model in SRN._MODELS_WITH_TYPES:
            # Check that type is parsed properly
            srn = SRN.parse(f"sym:{model}:type:slug:latest")
            assert srn.type == "type"

            # Check that type is enforced
            with pytest.raises(InvalidSRNError):
                SRN.parse(f"sym:{model}:slug:latest")

            with pytest.raises(InvalidSRNError):
                SRN.parse(f"sym:{model}:slug:latest:identifier")

    def test_srn_copy_with_types(self):
        integration_srn = SRN.parse("test:integration:slack:slug:latest:12345")
        assert integration_srn.type == "slack"

        # Cannot copy from a typed resource to an untyped resource.
        with pytest.raises(InvalidSRNError, match="cannot have a type component"):
            integration_srn.copy(model="flow")

        flow_srn = SRN.parse("test:flow:slug:latest:12345")
        assert str(flow_srn) == "test:flow:slug:latest:12345"
        assert flow_srn.type is None

        # The type must be passed in if copying from an untyped resource to a typed resource.
        with pytest.raises(InvalidSRNError, match="type"):
            flow_srn.copy(model="integration")

        copied_integration_srn = flow_srn.copy(model="integration", type="slack")
        assert str(copied_integration_srn) == "test:integration:slack:slug:latest:12345"
        assert copied_integration_srn.type == "slack"

    def test_srn_init(self):
        SRN("test", "flow", None, "slug", "latest", "12345")

        with pytest.raises(InvalidSRNError, match="type"):
            SRN("test", "integration", None, "slug", "1.0.0")

        with pytest.raises(InvalidSRNError, match="cannot have a type"):
            SRN("test", "flow", "invalid-type", "slug", "latest")

    def test_requires_type(self):
        for model in SRN._MODELS_WITH_TYPES:
            assert SRN.requires_type(model)

        assert not SRN.requires_type("flow")

    def test_eq(self):
        srn1 = SRN.parse("test:flow:slug:latest:12345")
        srn2 = SRN.parse("test:flow:slug:latest:12345")

        assert srn1 == srn2
        assert srn1 == "test:flow:slug:latest:12345"

        assert not srn1 == "test:flow:slug:latest"
        assert not srn1 == "test:flow:other-slug:latest:12345"
        assert not srn1 == SRN.parse("test:flow:other-slug:latest:12345")

        assert not srn1 == 1
        assert not srn1 == "something"
