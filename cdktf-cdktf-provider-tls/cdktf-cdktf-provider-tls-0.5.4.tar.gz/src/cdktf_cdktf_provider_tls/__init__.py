'''
# Terraform CDK tls Provider ~> 3.1

This repo builds and publishes the Terraform tls Provider bindings for [cdktf](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-tls](https://www.npmjs.com/package/@cdktf/provider-tls).

`npm install @cdktf/provider-tls`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-tls](https://pypi.org/project/cdktf-cdktf-provider-tls).

`pipenv install cdktf-cdktf-provider-tls`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Tls](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Tls).

`dotnet add package HashiCorp.Cdktf.Providers.Tls`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-tls](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-tls).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-tls</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)

## Versioning

This project is explicitly not tracking the Terraform tls Provider version 1:1. In fact, it always tracks `latest` of `~> 3.1` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform tls Provider](https://github.com/terraform-providers/terraform-provider-tls)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped. While the Terraform Engine and the Terraform tls Provider are relatively stable, the Terraform CDK is in an early stage. Therefore, it's likely that there will be breaking changes.

## Features / Issues / Bugs

Please report bugs and issues to the [terraform cdk](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### projen

This is mostly based on [projen](https://github.com/eladb/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on projen

There's a custom [project builder](https://github.com/hashicorp/cdktf-provider-project) which encapsulate the common settings for all `cdktf` providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [Repository Manager](https://github.com/hashicorp/cdktf-repository-manager/)
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import cdktf
import constructs


class CertRequest(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.CertRequest",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/tls/r/cert_request tls_cert_request}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        private_key_pem: builtins.str,
        dns_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        key_algorithm: typing.Optional[builtins.str] = None,
        subject: typing.Optional["CertRequestSubject"] = None,
        uris: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/tls/r/cert_request tls_cert_request} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param private_key_pem: Private key in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format, that the certificate will belong to. This can be read from a separate file using the ```file`` <https://www.terraform.io/language/functions/file>`_ interpolation function. Only an irreversible secure hash of the private key will be stored in the Terraform state. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#private_key_pem CertRequest#private_key_pem}
        :param dns_names: List of DNS names for which a certificate is being requested (i.e. certificate subjects). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#dns_names CertRequest#dns_names}
        :param ip_addresses: List of IP addresses for which a certificate is being requested (i.e. certificate subjects). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#ip_addresses CertRequest#ip_addresses}
        :param key_algorithm: Name of the algorithm used when generating the private key provided in ``private_key_pem``. **NOTE**: this is deprecated and ignored, as the key algorithm is now inferred from the key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#key_algorithm CertRequest#key_algorithm}
        :param subject: subject block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#subject CertRequest#subject}
        :param uris: List of URIs for which a certificate is being requested (i.e. certificate subjects). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#uris CertRequest#uris}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = CertRequestConfig(
            private_key_pem=private_key_pem,
            dns_names=dns_names,
            ip_addresses=ip_addresses,
            key_algorithm=key_algorithm,
            subject=subject,
            uris=uris,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putSubject")
    def put_subject(
        self,
        *,
        common_name: typing.Optional[builtins.str] = None,
        country: typing.Optional[builtins.str] = None,
        locality: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        organizational_unit: typing.Optional[builtins.str] = None,
        postal_code: typing.Optional[builtins.str] = None,
        province: typing.Optional[builtins.str] = None,
        serial_number: typing.Optional[builtins.str] = None,
        street_address: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param common_name: Distinguished name: ``CN``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#common_name CertRequest#common_name}
        :param country: Distinguished name: ``C``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#country CertRequest#country}
        :param locality: Distinguished name: ``L``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#locality CertRequest#locality}
        :param organization: Distinguished name: ``O``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#organization CertRequest#organization}
        :param organizational_unit: Distinguished name: ``OU``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#organizational_unit CertRequest#organizational_unit}
        :param postal_code: Distinguished name: ``PC``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#postal_code CertRequest#postal_code}
        :param province: Distinguished name: ``ST``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#province CertRequest#province}
        :param serial_number: Distinguished name: ``SERIALNUMBER``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#serial_number CertRequest#serial_number}
        :param street_address: Distinguished name: ``STREET``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#street_address CertRequest#street_address}
        '''
        value = CertRequestSubject(
            common_name=common_name,
            country=country,
            locality=locality,
            organization=organization,
            organizational_unit=organizational_unit,
            postal_code=postal_code,
            province=province,
            serial_number=serial_number,
            street_address=street_address,
        )

        return typing.cast(None, jsii.invoke(self, "putSubject", [value]))

    @jsii.member(jsii_name="resetDnsNames")
    def reset_dns_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsNames", []))

    @jsii.member(jsii_name="resetIpAddresses")
    def reset_ip_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpAddresses", []))

    @jsii.member(jsii_name="resetKeyAlgorithm")
    def reset_key_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyAlgorithm", []))

    @jsii.member(jsii_name="resetSubject")
    def reset_subject(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubject", []))

    @jsii.member(jsii_name="resetUris")
    def reset_uris(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUris", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certRequestPem")
    def cert_request_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certRequestPem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subject")
    def subject(self) -> "CertRequestSubjectOutputReference":
        return typing.cast("CertRequestSubjectOutputReference", jsii.get(self, "subject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsNamesInput")
    def dns_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsNamesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddressesInput")
    def ip_addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipAddressesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyAlgorithmInput")
    def key_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyAlgorithmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyPemInput")
    def private_key_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyPemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subjectInput")
    def subject_input(self) -> typing.Optional["CertRequestSubject"]:
        return typing.cast(typing.Optional["CertRequestSubject"], jsii.get(self, "subjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urisInput")
    def uris_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "urisInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsNames")
    def dns_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsNames"))

    @dns_names.setter
    def dns_names(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "dnsNames", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipAddresses"))

    @ip_addresses.setter
    def ip_addresses(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "ipAddresses", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyAlgorithm")
    def key_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyAlgorithm"))

    @key_algorithm.setter
    def key_algorithm(self, value: builtins.str) -> None:
        jsii.set(self, "keyAlgorithm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyPem")
    def private_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyPem"))

    @private_key_pem.setter
    def private_key_pem(self, value: builtins.str) -> None:
        jsii.set(self, "privateKeyPem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uris")
    def uris(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "uris"))

    @uris.setter
    def uris(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "uris", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.CertRequestConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "private_key_pem": "privateKeyPem",
        "dns_names": "dnsNames",
        "ip_addresses": "ipAddresses",
        "key_algorithm": "keyAlgorithm",
        "subject": "subject",
        "uris": "uris",
    },
)
class CertRequestConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        private_key_pem: builtins.str,
        dns_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        key_algorithm: typing.Optional[builtins.str] = None,
        subject: typing.Optional["CertRequestSubject"] = None,
        uris: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param private_key_pem: Private key in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format, that the certificate will belong to. This can be read from a separate file using the ```file`` <https://www.terraform.io/language/functions/file>`_ interpolation function. Only an irreversible secure hash of the private key will be stored in the Terraform state. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#private_key_pem CertRequest#private_key_pem}
        :param dns_names: List of DNS names for which a certificate is being requested (i.e. certificate subjects). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#dns_names CertRequest#dns_names}
        :param ip_addresses: List of IP addresses for which a certificate is being requested (i.e. certificate subjects). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#ip_addresses CertRequest#ip_addresses}
        :param key_algorithm: Name of the algorithm used when generating the private key provided in ``private_key_pem``. **NOTE**: this is deprecated and ignored, as the key algorithm is now inferred from the key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#key_algorithm CertRequest#key_algorithm}
        :param subject: subject block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#subject CertRequest#subject}
        :param uris: List of URIs for which a certificate is being requested (i.e. certificate subjects). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#uris CertRequest#uris}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(subject, dict):
            subject = CertRequestSubject(**subject)
        self._values: typing.Dict[str, typing.Any] = {
            "private_key_pem": private_key_pem,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if dns_names is not None:
            self._values["dns_names"] = dns_names
        if ip_addresses is not None:
            self._values["ip_addresses"] = ip_addresses
        if key_algorithm is not None:
            self._values["key_algorithm"] = key_algorithm
        if subject is not None:
            self._values["subject"] = subject
        if uris is not None:
            self._values["uris"] = uris

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def private_key_pem(self) -> builtins.str:
        '''Private key in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format, that the certificate will belong to. This can be read from a separate file using the ```file`` <https://www.terraform.io/language/functions/file>`_ interpolation function. Only an irreversible secure hash of the private key will be stored in the Terraform state.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#private_key_pem CertRequest#private_key_pem}
        '''
        result = self._values.get("private_key_pem")
        assert result is not None, "Required property 'private_key_pem' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def dns_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of DNS names for which a certificate is being requested (i.e. certificate subjects).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#dns_names CertRequest#dns_names}
        '''
        result = self._values.get("dns_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def ip_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of IP addresses for which a certificate is being requested (i.e. certificate subjects).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#ip_addresses CertRequest#ip_addresses}
        '''
        result = self._values.get("ip_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def key_algorithm(self) -> typing.Optional[builtins.str]:
        '''Name of the algorithm used when generating the private key provided in ``private_key_pem``.

        **NOTE**: this is deprecated and ignored, as the key algorithm is now inferred from the key.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#key_algorithm CertRequest#key_algorithm}
        '''
        result = self._values.get("key_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subject(self) -> typing.Optional["CertRequestSubject"]:
        '''subject block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#subject CertRequest#subject}
        '''
        result = self._values.get("subject")
        return typing.cast(typing.Optional["CertRequestSubject"], result)

    @builtins.property
    def uris(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of URIs for which a certificate is being requested (i.e. certificate subjects).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#uris CertRequest#uris}
        '''
        result = self._values.get("uris")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertRequestConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.CertRequestSubject",
    jsii_struct_bases=[],
    name_mapping={
        "common_name": "commonName",
        "country": "country",
        "locality": "locality",
        "organization": "organization",
        "organizational_unit": "organizationalUnit",
        "postal_code": "postalCode",
        "province": "province",
        "serial_number": "serialNumber",
        "street_address": "streetAddress",
    },
)
class CertRequestSubject:
    def __init__(
        self,
        *,
        common_name: typing.Optional[builtins.str] = None,
        country: typing.Optional[builtins.str] = None,
        locality: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        organizational_unit: typing.Optional[builtins.str] = None,
        postal_code: typing.Optional[builtins.str] = None,
        province: typing.Optional[builtins.str] = None,
        serial_number: typing.Optional[builtins.str] = None,
        street_address: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param common_name: Distinguished name: ``CN``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#common_name CertRequest#common_name}
        :param country: Distinguished name: ``C``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#country CertRequest#country}
        :param locality: Distinguished name: ``L``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#locality CertRequest#locality}
        :param organization: Distinguished name: ``O``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#organization CertRequest#organization}
        :param organizational_unit: Distinguished name: ``OU``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#organizational_unit CertRequest#organizational_unit}
        :param postal_code: Distinguished name: ``PC``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#postal_code CertRequest#postal_code}
        :param province: Distinguished name: ``ST``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#province CertRequest#province}
        :param serial_number: Distinguished name: ``SERIALNUMBER``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#serial_number CertRequest#serial_number}
        :param street_address: Distinguished name: ``STREET``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#street_address CertRequest#street_address}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if common_name is not None:
            self._values["common_name"] = common_name
        if country is not None:
            self._values["country"] = country
        if locality is not None:
            self._values["locality"] = locality
        if organization is not None:
            self._values["organization"] = organization
        if organizational_unit is not None:
            self._values["organizational_unit"] = organizational_unit
        if postal_code is not None:
            self._values["postal_code"] = postal_code
        if province is not None:
            self._values["province"] = province
        if serial_number is not None:
            self._values["serial_number"] = serial_number
        if street_address is not None:
            self._values["street_address"] = street_address

    @builtins.property
    def common_name(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``CN``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#common_name CertRequest#common_name}
        '''
        result = self._values.get("common_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def country(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``C``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#country CertRequest#country}
        '''
        result = self._values.get("country")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def locality(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``L``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#locality CertRequest#locality}
        '''
        result = self._values.get("locality")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``O``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#organization CertRequest#organization}
        '''
        result = self._values.get("organization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organizational_unit(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``OU``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#organizational_unit CertRequest#organizational_unit}
        '''
        result = self._values.get("organizational_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postal_code(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``PC``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#postal_code CertRequest#postal_code}
        '''
        result = self._values.get("postal_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def province(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``ST``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#province CertRequest#province}
        '''
        result = self._values.get("province")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def serial_number(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``SERIALNUMBER``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#serial_number CertRequest#serial_number}
        '''
        result = self._values.get("serial_number")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def street_address(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Distinguished name: ``STREET``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/cert_request#street_address CertRequest#street_address}
        '''
        result = self._values.get("street_address")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertRequestSubject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertRequestSubjectOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.CertRequestSubjectOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCommonName")
    def reset_common_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommonName", []))

    @jsii.member(jsii_name="resetCountry")
    def reset_country(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCountry", []))

    @jsii.member(jsii_name="resetLocality")
    def reset_locality(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocality", []))

    @jsii.member(jsii_name="resetOrganization")
    def reset_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganization", []))

    @jsii.member(jsii_name="resetOrganizationalUnit")
    def reset_organizational_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizationalUnit", []))

    @jsii.member(jsii_name="resetPostalCode")
    def reset_postal_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostalCode", []))

    @jsii.member(jsii_name="resetProvince")
    def reset_province(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvince", []))

    @jsii.member(jsii_name="resetSerialNumber")
    def reset_serial_number(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSerialNumber", []))

    @jsii.member(jsii_name="resetStreetAddress")
    def reset_street_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStreetAddress", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commonNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="countryInput")
    def country_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "countryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="localityInput")
    def locality_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitInput")
    def organizational_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationalUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationInput")
    def organization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postalCodeInput")
    def postal_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postalCodeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provinceInput")
    def province_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "provinceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serialNumberInput")
    def serial_number_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serialNumberInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streetAddressInput")
    def street_address_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "streetAddressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @common_name.setter
    def common_name(self, value: builtins.str) -> None:
        jsii.set(self, "commonName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="country")
    def country(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "country"))

    @country.setter
    def country(self, value: builtins.str) -> None:
        jsii.set(self, "country", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locality")
    def locality(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "locality"))

    @locality.setter
    def locality(self, value: builtins.str) -> None:
        jsii.set(self, "locality", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organization")
    def organization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organization"))

    @organization.setter
    def organization(self, value: builtins.str) -> None:
        jsii.set(self, "organization", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnit")
    def organizational_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnit"))

    @organizational_unit.setter
    def organizational_unit(self, value: builtins.str) -> None:
        jsii.set(self, "organizationalUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postalCode")
    def postal_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postalCode"))

    @postal_code.setter
    def postal_code(self, value: builtins.str) -> None:
        jsii.set(self, "postalCode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="province")
    def province(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "province"))

    @province.setter
    def province(self, value: builtins.str) -> None:
        jsii.set(self, "province", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serialNumber")
    def serial_number(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serialNumber"))

    @serial_number.setter
    def serial_number(self, value: builtins.str) -> None:
        jsii.set(self, "serialNumber", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streetAddress")
    def street_address(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "streetAddress"))

    @street_address.setter
    def street_address(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "streetAddress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CertRequestSubject]:
        return typing.cast(typing.Optional[CertRequestSubject], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[CertRequestSubject]) -> None:
        jsii.set(self, "internalValue", value)


class DataTlsCertificate(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.DataTlsCertificate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/tls/d/certificate tls_certificate}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        content: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        verify_chain: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/tls/d/certificate tls_certificate} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param content: The content of the certificate in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/certificate#content DataTlsCertificate#content}
        :param url: URL of the endpoint to get the certificates from. Accepted schemes are: ``https``, ``tls``. For scheme ``https://`` it will use the HTTP protocol and apply the ``proxy`` configuration of the provider, if set. For scheme ``tls://`` it will instead use a secure TCP socket. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/certificate#url DataTlsCertificate#url}
        :param verify_chain: Whether to verify the certificate chain while parsing it or not (default: ``true``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/certificate#verify_chain DataTlsCertificate#verify_chain}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataTlsCertificateConfig(
            content=content,
            url=url,
            verify_chain=verify_chain,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetContent")
    def reset_content(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetContent", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetVerifyChain")
    def reset_verify_chain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVerifyChain", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certificates")
    def certificates(self) -> "DataTlsCertificateCertificatesList":
        return typing.cast("DataTlsCertificateCertificatesList", jsii.get(self, "certificates"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="contentInput")
    def content_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "contentInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verifyChainInput")
    def verify_chain_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "verifyChainInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="content")
    def content(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "content"))

    @content.setter
    def content(self, value: builtins.str) -> None:
        jsii.set(self, "content", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        jsii.set(self, "url", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="verifyChain")
    def verify_chain(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "verifyChain"))

    @verify_chain.setter
    def verify_chain(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "verifyChain", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.DataTlsCertificateCertificates",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataTlsCertificateCertificates:
    def __init__(self) -> None:
        self._values: typing.Dict[str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataTlsCertificateCertificates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataTlsCertificateCertificatesList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.DataTlsCertificateCertificatesList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataTlsCertificateCertificatesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        return typing.cast("DataTlsCertificateCertificatesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        jsii.set(self, "terraformAttribute", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        jsii.set(self, "terraformResource", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        jsii.set(self, "wrapsSet", value)


class DataTlsCertificateCertificatesOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.DataTlsCertificateCertificatesOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certPem")
    def cert_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certPem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isCa")
    def is_ca(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "isCa"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="issuer")
    def issuer(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuer"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notAfter")
    def not_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notAfter"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="notBefore")
    def not_before(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notBefore"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyAlgorithm")
    def public_key_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyAlgorithm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serialNumber")
    def serial_number(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serialNumber"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="sha1Fingerprint")
    def sha1_fingerprint(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sha1Fingerprint"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="signatureAlgorithm")
    def signature_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "signatureAlgorithm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subject")
    def subject(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="version")
    def version(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "version"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataTlsCertificateCertificates]:
        return typing.cast(typing.Optional[DataTlsCertificateCertificates], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataTlsCertificateCertificates],
    ) -> None:
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.DataTlsCertificateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "content": "content",
        "url": "url",
        "verify_chain": "verifyChain",
    },
)
class DataTlsCertificateConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        content: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        verify_chain: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param content: The content of the certificate in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/certificate#content DataTlsCertificate#content}
        :param url: URL of the endpoint to get the certificates from. Accepted schemes are: ``https``, ``tls``. For scheme ``https://`` it will use the HTTP protocol and apply the ``proxy`` configuration of the provider, if set. For scheme ``tls://`` it will instead use a secure TCP socket. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/certificate#url DataTlsCertificate#url}
        :param verify_chain: Whether to verify the certificate chain while parsing it or not (default: ``true``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/certificate#verify_chain DataTlsCertificate#verify_chain}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if content is not None:
            self._values["content"] = content
        if url is not None:
            self._values["url"] = url
        if verify_chain is not None:
            self._values["verify_chain"] = verify_chain

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def content(self) -> typing.Optional[builtins.str]:
        '''The content of the certificate in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/certificate#content DataTlsCertificate#content}
        '''
        result = self._values.get("content")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''URL of the endpoint to get the certificates from.

        Accepted schemes are: ``https``, ``tls``. For scheme ``https://`` it will use the HTTP protocol and apply the ``proxy`` configuration of the provider, if set. For scheme ``tls://`` it will instead use a secure TCP socket.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/certificate#url DataTlsCertificate#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def verify_chain(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Whether to verify the certificate chain while parsing it or not (default: ``true``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/certificate#verify_chain DataTlsCertificate#verify_chain}
        '''
        result = self._values.get("verify_chain")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataTlsCertificateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataTlsPublicKey(
    cdktf.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.DataTlsPublicKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/tls/d/public_key tls_public_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        private_key_openssh: typing.Optional[builtins.str] = None,
        private_key_pem: typing.Optional[builtins.str] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/tls/d/public_key tls_public_key} Data Source.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param private_key_openssh: The private key (in `OpenSSH PEM (RFC 4716) <https://datatracker.ietf.org/doc/html/rfc4716>`_ format) to extract the public key from. Currently-supported algorithms for keys are ``RSA``, ``ECDSA`` and ``ED25519``. This is *mutually exclusive* with ``private_key_pem``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/public_key#private_key_openssh DataTlsPublicKey#private_key_openssh}
        :param private_key_pem: The private key (in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format) to extract the public key from. Currently-supported algorithms for keys are ``RSA``, ``ECDSA`` and ``ED25519``. This is *mutually exclusive* with ``private_key_openssh``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/public_key#private_key_pem DataTlsPublicKey#private_key_pem}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = DataTlsPublicKeyConfig(
            private_key_openssh=private_key_openssh,
            private_key_pem=private_key_pem,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetPrivateKeyOpenssh")
    def reset_private_key_openssh(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateKeyOpenssh", []))

    @jsii.member(jsii_name="resetPrivateKeyPem")
    def reset_private_key_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateKeyPem", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="algorithm")
    def algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "algorithm"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyFingerprintMd5")
    def public_key_fingerprint_md5(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyFingerprintMd5"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyFingerprintSha256")
    def public_key_fingerprint_sha256(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyFingerprintSha256"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyOpenssh")
    def public_key_openssh(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyOpenssh"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyPem")
    def public_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyPem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyOpensshInput")
    def private_key_openssh_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyOpensshInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyPemInput")
    def private_key_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyPemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyOpenssh")
    def private_key_openssh(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyOpenssh"))

    @private_key_openssh.setter
    def private_key_openssh(self, value: builtins.str) -> None:
        jsii.set(self, "privateKeyOpenssh", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyPem")
    def private_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyPem"))

    @private_key_pem.setter
    def private_key_pem(self, value: builtins.str) -> None:
        jsii.set(self, "privateKeyPem", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.DataTlsPublicKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "private_key_openssh": "privateKeyOpenssh",
        "private_key_pem": "privateKeyPem",
    },
)
class DataTlsPublicKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        private_key_openssh: typing.Optional[builtins.str] = None,
        private_key_pem: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param private_key_openssh: The private key (in `OpenSSH PEM (RFC 4716) <https://datatracker.ietf.org/doc/html/rfc4716>`_ format) to extract the public key from. Currently-supported algorithms for keys are ``RSA``, ``ECDSA`` and ``ED25519``. This is *mutually exclusive* with ``private_key_pem``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/public_key#private_key_openssh DataTlsPublicKey#private_key_openssh}
        :param private_key_pem: The private key (in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format) to extract the public key from. Currently-supported algorithms for keys are ``RSA``, ``ECDSA`` and ``ED25519``. This is *mutually exclusive* with ``private_key_openssh``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/public_key#private_key_pem DataTlsPublicKey#private_key_pem}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {}
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if private_key_openssh is not None:
            self._values["private_key_openssh"] = private_key_openssh
        if private_key_pem is not None:
            self._values["private_key_pem"] = private_key_pem

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def private_key_openssh(self) -> typing.Optional[builtins.str]:
        '''The private key (in  `OpenSSH PEM (RFC 4716) <https://datatracker.ietf.org/doc/html/rfc4716>`_ format) to extract the public key from. Currently-supported algorithms for keys are ``RSA``, ``ECDSA`` and ``ED25519``. This is *mutually exclusive* with ``private_key_pem``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/public_key#private_key_openssh DataTlsPublicKey#private_key_openssh}
        '''
        result = self._values.get("private_key_openssh")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def private_key_pem(self) -> typing.Optional[builtins.str]:
        '''The private key (in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format) to extract the public key from. Currently-supported algorithms for keys are ``RSA``, ``ECDSA`` and ``ED25519``. This is *mutually exclusive* with ``private_key_openssh``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/d/public_key#private_key_pem DataTlsPublicKey#private_key_pem}
        '''
        result = self._values.get("private_key_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataTlsPublicKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LocallySignedCert(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.LocallySignedCert",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert tls_locally_signed_cert}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        allowed_uses: typing.Sequence[builtins.str],
        ca_cert_pem: builtins.str,
        ca_private_key_pem: builtins.str,
        cert_request_pem: builtins.str,
        validity_period_hours: jsii.Number,
        ca_key_algorithm: typing.Optional[builtins.str] = None,
        early_renewal_hours: typing.Optional[jsii.Number] = None,
        is_ca_certificate: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        set_subject_key_id: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert tls_locally_signed_cert} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param allowed_uses: List of key usages allowed for the issued certificate. Values are defined in `RFC 5280 <https://datatracker.ietf.org/doc/html/rfc5280>`_ and combine flags defined by both `Key Usages <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.3>`_ and `Extended Key Usages <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.12>`_. Accepted values: ``any_extended``, ``cert_signing``, ``client_auth``, ``code_signing``, ``content_commitment``, ``crl_signing``, ``data_encipherment``, ``decipher_only``, ``digital_signature``, ``email_protection``, ``encipher_only``, ``ipsec_end_system``, ``ipsec_tunnel``, ``ipsec_user``, ``key_agreement``, ``key_encipherment``, ``microsoft_commercial_code_signing``, ``microsoft_kernel_code_signing``, ``microsoft_server_gated_crypto``, ``netscape_server_gated_crypto``, ``ocsp_signing``, ``server_auth``, ``timestamping``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#allowed_uses LocallySignedCert#allowed_uses}
        :param ca_cert_pem: Certificate data of the Certificate Authority (CA) in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_cert_pem LocallySignedCert#ca_cert_pem}
        :param ca_private_key_pem: Private key of the Certificate Authority (CA) used to sign the certificate, in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_private_key_pem LocallySignedCert#ca_private_key_pem}
        :param cert_request_pem: Certificate request data in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#cert_request_pem LocallySignedCert#cert_request_pem}
        :param validity_period_hours: Number of hours, after initial issuing, that the certificate will remain valid for. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#validity_period_hours LocallySignedCert#validity_period_hours}
        :param ca_key_algorithm: Name of the algorithm used when generating the private key provided in ``ca_private_key_pem``. **NOTE**: this is deprecated and ignored, as the key algorithm is now inferred from the key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_key_algorithm LocallySignedCert#ca_key_algorithm}
        :param early_renewal_hours: The resource will consider the certificate to have expired the given number of hours before its actual expiry time. This can be useful to deploy an updated certificate in advance of the expiration of the current certificate. However, the old certificate remains valid until its true expiration time, since this resource does not (and cannot) support certificate revocation. Also, this advance update can only be performed should the Terraform configuration be applied during the early renewal period. (default: ``0``) Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#early_renewal_hours LocallySignedCert#early_renewal_hours}
        :param is_ca_certificate: Is the generated certificate representing a Certificate Authority (CA) (default: ``false``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#is_ca_certificate LocallySignedCert#is_ca_certificate}
        :param set_subject_key_id: Should the generated certificate include a `subject key identifier <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.2>`_ (default: ``false``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#set_subject_key_id LocallySignedCert#set_subject_key_id}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = LocallySignedCertConfig(
            allowed_uses=allowed_uses,
            ca_cert_pem=ca_cert_pem,
            ca_private_key_pem=ca_private_key_pem,
            cert_request_pem=cert_request_pem,
            validity_period_hours=validity_period_hours,
            ca_key_algorithm=ca_key_algorithm,
            early_renewal_hours=early_renewal_hours,
            is_ca_certificate=is_ca_certificate,
            set_subject_key_id=set_subject_key_id,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetCaKeyAlgorithm")
    def reset_ca_key_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaKeyAlgorithm", []))

    @jsii.member(jsii_name="resetEarlyRenewalHours")
    def reset_early_renewal_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEarlyRenewalHours", []))

    @jsii.member(jsii_name="resetIsCaCertificate")
    def reset_is_ca_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsCaCertificate", []))

    @jsii.member(jsii_name="resetSetSubjectKeyId")
    def reset_set_subject_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSetSubjectKeyId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certPem")
    def cert_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certPem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readyForRenewal")
    def ready_for_renewal(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "readyForRenewal"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityEndTime")
    def validity_end_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "validityEndTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityStartTime")
    def validity_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "validityStartTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedUsesInput")
    def allowed_uses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedUsesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caCertPemInput")
    def ca_cert_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caCertPemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caKeyAlgorithmInput")
    def ca_key_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caKeyAlgorithmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caPrivateKeyPemInput")
    def ca_private_key_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caPrivateKeyPemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certRequestPemInput")
    def cert_request_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certRequestPemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="earlyRenewalHoursInput")
    def early_renewal_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "earlyRenewalHoursInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isCaCertificateInput")
    def is_ca_certificate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "isCaCertificateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="setSubjectKeyIdInput")
    def set_subject_key_id_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "setSubjectKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityPeriodHoursInput")
    def validity_period_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "validityPeriodHoursInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedUses")
    def allowed_uses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedUses"))

    @allowed_uses.setter
    def allowed_uses(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "allowedUses", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caCertPem")
    def ca_cert_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caCertPem"))

    @ca_cert_pem.setter
    def ca_cert_pem(self, value: builtins.str) -> None:
        jsii.set(self, "caCertPem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caKeyAlgorithm")
    def ca_key_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caKeyAlgorithm"))

    @ca_key_algorithm.setter
    def ca_key_algorithm(self, value: builtins.str) -> None:
        jsii.set(self, "caKeyAlgorithm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="caPrivateKeyPem")
    def ca_private_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caPrivateKeyPem"))

    @ca_private_key_pem.setter
    def ca_private_key_pem(self, value: builtins.str) -> None:
        jsii.set(self, "caPrivateKeyPem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certRequestPem")
    def cert_request_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certRequestPem"))

    @cert_request_pem.setter
    def cert_request_pem(self, value: builtins.str) -> None:
        jsii.set(self, "certRequestPem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="earlyRenewalHours")
    def early_renewal_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "earlyRenewalHours"))

    @early_renewal_hours.setter
    def early_renewal_hours(self, value: jsii.Number) -> None:
        jsii.set(self, "earlyRenewalHours", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isCaCertificate")
    def is_ca_certificate(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "isCaCertificate"))

    @is_ca_certificate.setter
    def is_ca_certificate(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "isCaCertificate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="setSubjectKeyId")
    def set_subject_key_id(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "setSubjectKeyId"))

    @set_subject_key_id.setter
    def set_subject_key_id(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "setSubjectKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityPeriodHours")
    def validity_period_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "validityPeriodHours"))

    @validity_period_hours.setter
    def validity_period_hours(self, value: jsii.Number) -> None:
        jsii.set(self, "validityPeriodHours", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.LocallySignedCertConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "allowed_uses": "allowedUses",
        "ca_cert_pem": "caCertPem",
        "ca_private_key_pem": "caPrivateKeyPem",
        "cert_request_pem": "certRequestPem",
        "validity_period_hours": "validityPeriodHours",
        "ca_key_algorithm": "caKeyAlgorithm",
        "early_renewal_hours": "earlyRenewalHours",
        "is_ca_certificate": "isCaCertificate",
        "set_subject_key_id": "setSubjectKeyId",
    },
)
class LocallySignedCertConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        allowed_uses: typing.Sequence[builtins.str],
        ca_cert_pem: builtins.str,
        ca_private_key_pem: builtins.str,
        cert_request_pem: builtins.str,
        validity_period_hours: jsii.Number,
        ca_key_algorithm: typing.Optional[builtins.str] = None,
        early_renewal_hours: typing.Optional[jsii.Number] = None,
        is_ca_certificate: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        set_subject_key_id: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param allowed_uses: List of key usages allowed for the issued certificate. Values are defined in `RFC 5280 <https://datatracker.ietf.org/doc/html/rfc5280>`_ and combine flags defined by both `Key Usages <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.3>`_ and `Extended Key Usages <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.12>`_. Accepted values: ``any_extended``, ``cert_signing``, ``client_auth``, ``code_signing``, ``content_commitment``, ``crl_signing``, ``data_encipherment``, ``decipher_only``, ``digital_signature``, ``email_protection``, ``encipher_only``, ``ipsec_end_system``, ``ipsec_tunnel``, ``ipsec_user``, ``key_agreement``, ``key_encipherment``, ``microsoft_commercial_code_signing``, ``microsoft_kernel_code_signing``, ``microsoft_server_gated_crypto``, ``netscape_server_gated_crypto``, ``ocsp_signing``, ``server_auth``, ``timestamping``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#allowed_uses LocallySignedCert#allowed_uses}
        :param ca_cert_pem: Certificate data of the Certificate Authority (CA) in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_cert_pem LocallySignedCert#ca_cert_pem}
        :param ca_private_key_pem: Private key of the Certificate Authority (CA) used to sign the certificate, in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_private_key_pem LocallySignedCert#ca_private_key_pem}
        :param cert_request_pem: Certificate request data in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#cert_request_pem LocallySignedCert#cert_request_pem}
        :param validity_period_hours: Number of hours, after initial issuing, that the certificate will remain valid for. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#validity_period_hours LocallySignedCert#validity_period_hours}
        :param ca_key_algorithm: Name of the algorithm used when generating the private key provided in ``ca_private_key_pem``. **NOTE**: this is deprecated and ignored, as the key algorithm is now inferred from the key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_key_algorithm LocallySignedCert#ca_key_algorithm}
        :param early_renewal_hours: The resource will consider the certificate to have expired the given number of hours before its actual expiry time. This can be useful to deploy an updated certificate in advance of the expiration of the current certificate. However, the old certificate remains valid until its true expiration time, since this resource does not (and cannot) support certificate revocation. Also, this advance update can only be performed should the Terraform configuration be applied during the early renewal period. (default: ``0``) Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#early_renewal_hours LocallySignedCert#early_renewal_hours}
        :param is_ca_certificate: Is the generated certificate representing a Certificate Authority (CA) (default: ``false``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#is_ca_certificate LocallySignedCert#is_ca_certificate}
        :param set_subject_key_id: Should the generated certificate include a `subject key identifier <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.2>`_ (default: ``false``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#set_subject_key_id LocallySignedCert#set_subject_key_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "allowed_uses": allowed_uses,
            "ca_cert_pem": ca_cert_pem,
            "ca_private_key_pem": ca_private_key_pem,
            "cert_request_pem": cert_request_pem,
            "validity_period_hours": validity_period_hours,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if ca_key_algorithm is not None:
            self._values["ca_key_algorithm"] = ca_key_algorithm
        if early_renewal_hours is not None:
            self._values["early_renewal_hours"] = early_renewal_hours
        if is_ca_certificate is not None:
            self._values["is_ca_certificate"] = is_ca_certificate
        if set_subject_key_id is not None:
            self._values["set_subject_key_id"] = set_subject_key_id

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def allowed_uses(self) -> typing.List[builtins.str]:
        '''List of key usages allowed for the issued certificate.

        Values are defined in `RFC 5280 <https://datatracker.ietf.org/doc/html/rfc5280>`_ and combine flags defined by both `Key Usages <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.3>`_ and `Extended Key Usages <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.12>`_. Accepted values: ``any_extended``, ``cert_signing``, ``client_auth``, ``code_signing``, ``content_commitment``, ``crl_signing``, ``data_encipherment``, ``decipher_only``, ``digital_signature``, ``email_protection``, ``encipher_only``, ``ipsec_end_system``, ``ipsec_tunnel``, ``ipsec_user``, ``key_agreement``, ``key_encipherment``, ``microsoft_commercial_code_signing``, ``microsoft_kernel_code_signing``, ``microsoft_server_gated_crypto``, ``netscape_server_gated_crypto``, ``ocsp_signing``, ``server_auth``, ``timestamping``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#allowed_uses LocallySignedCert#allowed_uses}
        '''
        result = self._values.get("allowed_uses")
        assert result is not None, "Required property 'allowed_uses' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def ca_cert_pem(self) -> builtins.str:
        '''Certificate data of the Certificate Authority (CA) in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_cert_pem LocallySignedCert#ca_cert_pem}
        '''
        result = self._values.get("ca_cert_pem")
        assert result is not None, "Required property 'ca_cert_pem' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ca_private_key_pem(self) -> builtins.str:
        '''Private key of the Certificate Authority (CA) used to sign the certificate, in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_private_key_pem LocallySignedCert#ca_private_key_pem}
        '''
        result = self._values.get("ca_private_key_pem")
        assert result is not None, "Required property 'ca_private_key_pem' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cert_request_pem(self) -> builtins.str:
        '''Certificate request data in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#cert_request_pem LocallySignedCert#cert_request_pem}
        '''
        result = self._values.get("cert_request_pem")
        assert result is not None, "Required property 'cert_request_pem' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def validity_period_hours(self) -> jsii.Number:
        '''Number of hours, after initial issuing, that the certificate will remain valid for.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#validity_period_hours LocallySignedCert#validity_period_hours}
        '''
        result = self._values.get("validity_period_hours")
        assert result is not None, "Required property 'validity_period_hours' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def ca_key_algorithm(self) -> typing.Optional[builtins.str]:
        '''Name of the algorithm used when generating the private key provided in ``ca_private_key_pem``.

        **NOTE**: this is deprecated and ignored, as the key algorithm is now inferred from the key.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#ca_key_algorithm LocallySignedCert#ca_key_algorithm}
        '''
        result = self._values.get("ca_key_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def early_renewal_hours(self) -> typing.Optional[jsii.Number]:
        '''The resource will consider the certificate to have expired the given number of hours before its actual expiry time.

        This can be useful to deploy an updated certificate in advance of the expiration of the current certificate. However, the old certificate remains valid until its true expiration time, since this resource does not (and cannot) support certificate revocation. Also, this advance update can only be performed should the Terraform configuration be applied during the early renewal period. (default: ``0``)

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#early_renewal_hours LocallySignedCert#early_renewal_hours}
        '''
        result = self._values.get("early_renewal_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def is_ca_certificate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Is the generated certificate representing a Certificate Authority (CA) (default: ``false``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#is_ca_certificate LocallySignedCert#is_ca_certificate}
        '''
        result = self._values.get("is_ca_certificate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def set_subject_key_id(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Should the generated certificate include a `subject key identifier <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.2>`_ (default: ``false``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/locally_signed_cert#set_subject_key_id LocallySignedCert#set_subject_key_id}
        '''
        result = self._values.get("set_subject_key_id")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LocallySignedCertConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PrivateKey(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.PrivateKey",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/tls/r/private_key tls_private_key}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        algorithm: builtins.str,
        ecdsa_curve: typing.Optional[builtins.str] = None,
        rsa_bits: typing.Optional[jsii.Number] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/tls/r/private_key tls_private_key} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param algorithm: Name of the algorithm to use when generating the private key. Currently-supported values are ``RSA``, ``ECDSA`` and ``ED25519``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#algorithm PrivateKey#algorithm}
        :param ecdsa_curve: When ``algorithm`` is ``ECDSA``, the name of the elliptic curve to use. Currently-supported values are ``P224``, ``P256``, ``P384`` or ``P521`` (default: ``P224``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#ecdsa_curve PrivateKey#ecdsa_curve}
        :param rsa_bits: When ``algorithm`` is ``RSA``, the size of the generated RSA key, in bits (default: ``2048``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#rsa_bits PrivateKey#rsa_bits}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = PrivateKeyConfig(
            algorithm=algorithm,
            ecdsa_curve=ecdsa_curve,
            rsa_bits=rsa_bits,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetEcdsaCurve")
    def reset_ecdsa_curve(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEcdsaCurve", []))

    @jsii.member(jsii_name="resetRsaBits")
    def reset_rsa_bits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRsaBits", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyOpenssh")
    def private_key_openssh(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyOpenssh"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyPem")
    def private_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyPem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyFingerprintMd5")
    def public_key_fingerprint_md5(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyFingerprintMd5"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyFingerprintSha256")
    def public_key_fingerprint_sha256(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyFingerprintSha256"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyOpenssh")
    def public_key_openssh(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyOpenssh"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="publicKeyPem")
    def public_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "publicKeyPem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="algorithmInput")
    def algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "algorithmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ecdsaCurveInput")
    def ecdsa_curve_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ecdsaCurveInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rsaBitsInput")
    def rsa_bits_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "rsaBitsInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="algorithm")
    def algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "algorithm"))

    @algorithm.setter
    def algorithm(self, value: builtins.str) -> None:
        jsii.set(self, "algorithm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ecdsaCurve")
    def ecdsa_curve(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ecdsaCurve"))

    @ecdsa_curve.setter
    def ecdsa_curve(self, value: builtins.str) -> None:
        jsii.set(self, "ecdsaCurve", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="rsaBits")
    def rsa_bits(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "rsaBits"))

    @rsa_bits.setter
    def rsa_bits(self, value: jsii.Number) -> None:
        jsii.set(self, "rsaBits", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.PrivateKeyConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "algorithm": "algorithm",
        "ecdsa_curve": "ecdsaCurve",
        "rsa_bits": "rsaBits",
    },
)
class PrivateKeyConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        algorithm: builtins.str,
        ecdsa_curve: typing.Optional[builtins.str] = None,
        rsa_bits: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param algorithm: Name of the algorithm to use when generating the private key. Currently-supported values are ``RSA``, ``ECDSA`` and ``ED25519``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#algorithm PrivateKey#algorithm}
        :param ecdsa_curve: When ``algorithm`` is ``ECDSA``, the name of the elliptic curve to use. Currently-supported values are ``P224``, ``P256``, ``P384`` or ``P521`` (default: ``P224``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#ecdsa_curve PrivateKey#ecdsa_curve}
        :param rsa_bits: When ``algorithm`` is ``RSA``, the size of the generated RSA key, in bits (default: ``2048``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#rsa_bits PrivateKey#rsa_bits}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        self._values: typing.Dict[str, typing.Any] = {
            "algorithm": algorithm,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if ecdsa_curve is not None:
            self._values["ecdsa_curve"] = ecdsa_curve
        if rsa_bits is not None:
            self._values["rsa_bits"] = rsa_bits

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def algorithm(self) -> builtins.str:
        '''Name of the algorithm to use when generating the private key. Currently-supported values are ``RSA``, ``ECDSA`` and ``ED25519``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#algorithm PrivateKey#algorithm}
        '''
        result = self._values.get("algorithm")
        assert result is not None, "Required property 'algorithm' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ecdsa_curve(self) -> typing.Optional[builtins.str]:
        '''When ``algorithm`` is ``ECDSA``, the name of the elliptic curve to use.

        Currently-supported values are ``P224``, ``P256``, ``P384`` or ``P521`` (default: ``P224``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#ecdsa_curve PrivateKey#ecdsa_curve}
        '''
        result = self._values.get("ecdsa_curve")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def rsa_bits(self) -> typing.Optional[jsii.Number]:
        '''When ``algorithm`` is ``RSA``, the size of the generated RSA key, in bits (default: ``2048``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/private_key#rsa_bits PrivateKey#rsa_bits}
        '''
        result = self._values.get("rsa_bits")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PrivateKeyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SelfSignedCert(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.SelfSignedCert",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert tls_self_signed_cert}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        allowed_uses: typing.Sequence[builtins.str],
        private_key_pem: builtins.str,
        validity_period_hours: jsii.Number,
        dns_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        early_renewal_hours: typing.Optional[jsii.Number] = None,
        ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        is_ca_certificate: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        key_algorithm: typing.Optional[builtins.str] = None,
        set_authority_key_id: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        set_subject_key_id: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        subject: typing.Optional["SelfSignedCertSubject"] = None,
        uris: typing.Optional[typing.Sequence[builtins.str]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert tls_self_signed_cert} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param allowed_uses: List of key usages allowed for the issued certificate. Values are defined in `RFC 5280 <https://datatracker.ietf.org/doc/html/rfc5280>`_ and combine flags defined by both `Key Usages <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.3>`_ and `Extended Key Usages <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.12>`_. Accepted values: ``any_extended``, ``cert_signing``, ``client_auth``, ``code_signing``, ``content_commitment``, ``crl_signing``, ``data_encipherment``, ``decipher_only``, ``digital_signature``, ``email_protection``, ``encipher_only``, ``ipsec_end_system``, ``ipsec_tunnel``, ``ipsec_user``, ``key_agreement``, ``key_encipherment``, ``microsoft_commercial_code_signing``, ``microsoft_kernel_code_signing``, ``microsoft_server_gated_crypto``, ``netscape_server_gated_crypto``, ``ocsp_signing``, ``server_auth``, ``timestamping``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#allowed_uses SelfSignedCert#allowed_uses}
        :param private_key_pem: Private key in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format, that the certificate will belong to. This can be read from a separate file using the ```file`` <https://www.terraform.io/language/functions/file>`_ interpolation function. Only an irreversible secure hash of the private key will be stored in the Terraform state. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#private_key_pem SelfSignedCert#private_key_pem}
        :param validity_period_hours: Number of hours, after initial issuing, that the certificate will remain valid for. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#validity_period_hours SelfSignedCert#validity_period_hours}
        :param dns_names: List of DNS names for which a certificate is being requested (i.e. certificate subjects). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#dns_names SelfSignedCert#dns_names}
        :param early_renewal_hours: The resource will consider the certificate to have expired the given number of hours before its actual expiry time. This can be useful to deploy an updated certificate in advance of the expiration of the current certificate. However, the old certificate remains valid until its true expiration time, since this resource does not (and cannot) support certificate revocation. Also, this advance update can only be performed should the Terraform configuration be applied during the early renewal period. (default: ``0``) Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#early_renewal_hours SelfSignedCert#early_renewal_hours}
        :param ip_addresses: List of IP addresses for which a certificate is being requested (i.e. certificate subjects). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#ip_addresses SelfSignedCert#ip_addresses}
        :param is_ca_certificate: Is the generated certificate representing a Certificate Authority (CA) (default: ``false``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#is_ca_certificate SelfSignedCert#is_ca_certificate}
        :param key_algorithm: Name of the algorithm used when generating the private key provided in ``private_key_pem``. **NOTE**: this is deprecated and ignored, as the key algorithm is now inferred from the key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#key_algorithm SelfSignedCert#key_algorithm}
        :param set_authority_key_id: Should the generated certificate include an `authority key identifier <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.1>`_: for self-signed certificates this is the same value as the `subject key identifier <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.2>`_ (default: ``false``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#set_authority_key_id SelfSignedCert#set_authority_key_id}
        :param set_subject_key_id: Should the generated certificate include a `subject key identifier <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.2>`_ (default: ``false``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#set_subject_key_id SelfSignedCert#set_subject_key_id}
        :param subject: subject block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#subject SelfSignedCert#subject}
        :param uris: List of URIs for which a certificate is being requested (i.e. certificate subjects). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#uris SelfSignedCert#uris}
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        '''
        config = SelfSignedCertConfig(
            allowed_uses=allowed_uses,
            private_key_pem=private_key_pem,
            validity_period_hours=validity_period_hours,
            dns_names=dns_names,
            early_renewal_hours=early_renewal_hours,
            ip_addresses=ip_addresses,
            is_ca_certificate=is_ca_certificate,
            key_algorithm=key_algorithm,
            set_authority_key_id=set_authority_key_id,
            set_subject_key_id=set_subject_key_id,
            subject=subject,
            uris=uris,
            count=count,
            depends_on=depends_on,
            lifecycle=lifecycle,
            provider=provider,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="putSubject")
    def put_subject(
        self,
        *,
        common_name: typing.Optional[builtins.str] = None,
        country: typing.Optional[builtins.str] = None,
        locality: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        organizational_unit: typing.Optional[builtins.str] = None,
        postal_code: typing.Optional[builtins.str] = None,
        province: typing.Optional[builtins.str] = None,
        serial_number: typing.Optional[builtins.str] = None,
        street_address: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param common_name: Distinguished name: ``CN``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#common_name SelfSignedCert#common_name}
        :param country: Distinguished name: ``C``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#country SelfSignedCert#country}
        :param locality: Distinguished name: ``L``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#locality SelfSignedCert#locality}
        :param organization: Distinguished name: ``O``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#organization SelfSignedCert#organization}
        :param organizational_unit: Distinguished name: ``OU``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#organizational_unit SelfSignedCert#organizational_unit}
        :param postal_code: Distinguished name: ``PC``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#postal_code SelfSignedCert#postal_code}
        :param province: Distinguished name: ``ST``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#province SelfSignedCert#province}
        :param serial_number: Distinguished name: ``SERIALNUMBER``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#serial_number SelfSignedCert#serial_number}
        :param street_address: Distinguished name: ``STREET``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#street_address SelfSignedCert#street_address}
        '''
        value = SelfSignedCertSubject(
            common_name=common_name,
            country=country,
            locality=locality,
            organization=organization,
            organizational_unit=organizational_unit,
            postal_code=postal_code,
            province=province,
            serial_number=serial_number,
            street_address=street_address,
        )

        return typing.cast(None, jsii.invoke(self, "putSubject", [value]))

    @jsii.member(jsii_name="resetDnsNames")
    def reset_dns_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsNames", []))

    @jsii.member(jsii_name="resetEarlyRenewalHours")
    def reset_early_renewal_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEarlyRenewalHours", []))

    @jsii.member(jsii_name="resetIpAddresses")
    def reset_ip_addresses(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpAddresses", []))

    @jsii.member(jsii_name="resetIsCaCertificate")
    def reset_is_ca_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsCaCertificate", []))

    @jsii.member(jsii_name="resetKeyAlgorithm")
    def reset_key_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyAlgorithm", []))

    @jsii.member(jsii_name="resetSetAuthorityKeyId")
    def reset_set_authority_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSetAuthorityKeyId", []))

    @jsii.member(jsii_name="resetSetSubjectKeyId")
    def reset_set_subject_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSetSubjectKeyId", []))

    @jsii.member(jsii_name="resetSubject")
    def reset_subject(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubject", []))

    @jsii.member(jsii_name="resetUris")
    def reset_uris(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUris", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="certPem")
    def cert_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certPem"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="readyForRenewal")
    def ready_for_renewal(self) -> cdktf.IResolvable:
        return typing.cast(cdktf.IResolvable, jsii.get(self, "readyForRenewal"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subject")
    def subject(self) -> "SelfSignedCertSubjectOutputReference":
        return typing.cast("SelfSignedCertSubjectOutputReference", jsii.get(self, "subject"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityEndTime")
    def validity_end_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "validityEndTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityStartTime")
    def validity_start_time(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "validityStartTime"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedUsesInput")
    def allowed_uses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowedUsesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsNamesInput")
    def dns_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsNamesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="earlyRenewalHoursInput")
    def early_renewal_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "earlyRenewalHoursInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddressesInput")
    def ip_addresses_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ipAddressesInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isCaCertificateInput")
    def is_ca_certificate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "isCaCertificateInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyAlgorithmInput")
    def key_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyAlgorithmInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyPemInput")
    def private_key_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyPemInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="setAuthorityKeyIdInput")
    def set_authority_key_id_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "setAuthorityKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="setSubjectKeyIdInput")
    def set_subject_key_id_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "setSubjectKeyIdInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="subjectInput")
    def subject_input(self) -> typing.Optional["SelfSignedCertSubject"]:
        return typing.cast(typing.Optional["SelfSignedCertSubject"], jsii.get(self, "subjectInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="urisInput")
    def uris_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "urisInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityPeriodHoursInput")
    def validity_period_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "validityPeriodHoursInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="allowedUses")
    def allowed_uses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allowedUses"))

    @allowed_uses.setter
    def allowed_uses(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "allowedUses", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="dnsNames")
    def dns_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsNames"))

    @dns_names.setter
    def dns_names(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "dnsNames", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="earlyRenewalHours")
    def early_renewal_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "earlyRenewalHours"))

    @early_renewal_hours.setter
    def early_renewal_hours(self, value: jsii.Number) -> None:
        jsii.set(self, "earlyRenewalHours", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ipAddresses"))

    @ip_addresses.setter
    def ip_addresses(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "ipAddresses", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="isCaCertificate")
    def is_ca_certificate(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "isCaCertificate"))

    @is_ca_certificate.setter
    def is_ca_certificate(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "isCaCertificate", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="keyAlgorithm")
    def key_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyAlgorithm"))

    @key_algorithm.setter
    def key_algorithm(self, value: builtins.str) -> None:
        jsii.set(self, "keyAlgorithm", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="privateKeyPem")
    def private_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyPem"))

    @private_key_pem.setter
    def private_key_pem(self, value: builtins.str) -> None:
        jsii.set(self, "privateKeyPem", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="setAuthorityKeyId")
    def set_authority_key_id(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "setAuthorityKeyId"))

    @set_authority_key_id.setter
    def set_authority_key_id(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "setAuthorityKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="setSubjectKeyId")
    def set_subject_key_id(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "setSubjectKeyId"))

    @set_subject_key_id.setter
    def set_subject_key_id(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        jsii.set(self, "setSubjectKeyId", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="uris")
    def uris(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "uris"))

    @uris.setter
    def uris(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "uris", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="validityPeriodHours")
    def validity_period_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "validityPeriodHours"))

    @validity_period_hours.setter
    def validity_period_hours(self, value: jsii.Number) -> None:
        jsii.set(self, "validityPeriodHours", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.SelfSignedCertConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "count": "count",
        "depends_on": "dependsOn",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "allowed_uses": "allowedUses",
        "private_key_pem": "privateKeyPem",
        "validity_period_hours": "validityPeriodHours",
        "dns_names": "dnsNames",
        "early_renewal_hours": "earlyRenewalHours",
        "ip_addresses": "ipAddresses",
        "is_ca_certificate": "isCaCertificate",
        "key_algorithm": "keyAlgorithm",
        "set_authority_key_id": "setAuthorityKeyId",
        "set_subject_key_id": "setSubjectKeyId",
        "subject": "subject",
        "uris": "uris",
    },
)
class SelfSignedCertConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        lifecycle: typing.Optional[cdktf.TerraformResourceLifecycle] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        allowed_uses: typing.Sequence[builtins.str],
        private_key_pem: builtins.str,
        validity_period_hours: jsii.Number,
        dns_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        early_renewal_hours: typing.Optional[jsii.Number] = None,
        ip_addresses: typing.Optional[typing.Sequence[builtins.str]] = None,
        is_ca_certificate: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        key_algorithm: typing.Optional[builtins.str] = None,
        set_authority_key_id: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        set_subject_key_id: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        subject: typing.Optional["SelfSignedCertSubject"] = None,
        uris: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param count: 
        :param depends_on: 
        :param lifecycle: 
        :param provider: 
        :param allowed_uses: List of key usages allowed for the issued certificate. Values are defined in `RFC 5280 <https://datatracker.ietf.org/doc/html/rfc5280>`_ and combine flags defined by both `Key Usages <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.3>`_ and `Extended Key Usages <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.12>`_. Accepted values: ``any_extended``, ``cert_signing``, ``client_auth``, ``code_signing``, ``content_commitment``, ``crl_signing``, ``data_encipherment``, ``decipher_only``, ``digital_signature``, ``email_protection``, ``encipher_only``, ``ipsec_end_system``, ``ipsec_tunnel``, ``ipsec_user``, ``key_agreement``, ``key_encipherment``, ``microsoft_commercial_code_signing``, ``microsoft_kernel_code_signing``, ``microsoft_server_gated_crypto``, ``netscape_server_gated_crypto``, ``ocsp_signing``, ``server_auth``, ``timestamping``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#allowed_uses SelfSignedCert#allowed_uses}
        :param private_key_pem: Private key in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format, that the certificate will belong to. This can be read from a separate file using the ```file`` <https://www.terraform.io/language/functions/file>`_ interpolation function. Only an irreversible secure hash of the private key will be stored in the Terraform state. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#private_key_pem SelfSignedCert#private_key_pem}
        :param validity_period_hours: Number of hours, after initial issuing, that the certificate will remain valid for. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#validity_period_hours SelfSignedCert#validity_period_hours}
        :param dns_names: List of DNS names for which a certificate is being requested (i.e. certificate subjects). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#dns_names SelfSignedCert#dns_names}
        :param early_renewal_hours: The resource will consider the certificate to have expired the given number of hours before its actual expiry time. This can be useful to deploy an updated certificate in advance of the expiration of the current certificate. However, the old certificate remains valid until its true expiration time, since this resource does not (and cannot) support certificate revocation. Also, this advance update can only be performed should the Terraform configuration be applied during the early renewal period. (default: ``0``) Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#early_renewal_hours SelfSignedCert#early_renewal_hours}
        :param ip_addresses: List of IP addresses for which a certificate is being requested (i.e. certificate subjects). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#ip_addresses SelfSignedCert#ip_addresses}
        :param is_ca_certificate: Is the generated certificate representing a Certificate Authority (CA) (default: ``false``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#is_ca_certificate SelfSignedCert#is_ca_certificate}
        :param key_algorithm: Name of the algorithm used when generating the private key provided in ``private_key_pem``. **NOTE**: this is deprecated and ignored, as the key algorithm is now inferred from the key. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#key_algorithm SelfSignedCert#key_algorithm}
        :param set_authority_key_id: Should the generated certificate include an `authority key identifier <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.1>`_: for self-signed certificates this is the same value as the `subject key identifier <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.2>`_ (default: ``false``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#set_authority_key_id SelfSignedCert#set_authority_key_id}
        :param set_subject_key_id: Should the generated certificate include a `subject key identifier <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.2>`_ (default: ``false``). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#set_subject_key_id SelfSignedCert#set_subject_key_id}
        :param subject: subject block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#subject SelfSignedCert#subject}
        :param uris: List of URIs for which a certificate is being requested (i.e. certificate subjects). Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#uris SelfSignedCert#uris}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = cdktf.TerraformResourceLifecycle(**lifecycle)
        if isinstance(subject, dict):
            subject = SelfSignedCertSubject(**subject)
        self._values: typing.Dict[str, typing.Any] = {
            "allowed_uses": allowed_uses,
            "private_key_pem": private_key_pem,
            "validity_period_hours": validity_period_hours,
        }
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if dns_names is not None:
            self._values["dns_names"] = dns_names
        if early_renewal_hours is not None:
            self._values["early_renewal_hours"] = early_renewal_hours
        if ip_addresses is not None:
            self._values["ip_addresses"] = ip_addresses
        if is_ca_certificate is not None:
            self._values["is_ca_certificate"] = is_ca_certificate
        if key_algorithm is not None:
            self._values["key_algorithm"] = key_algorithm
        if set_authority_key_id is not None:
            self._values["set_authority_key_id"] = set_authority_key_id
        if set_subject_key_id is not None:
            self._values["set_subject_key_id"] = set_subject_key_id
        if subject is not None:
            self._values["subject"] = subject
        if uris is not None:
            self._values["uris"] = uris

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def allowed_uses(self) -> typing.List[builtins.str]:
        '''List of key usages allowed for the issued certificate.

        Values are defined in `RFC 5280 <https://datatracker.ietf.org/doc/html/rfc5280>`_ and combine flags defined by both `Key Usages <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.3>`_ and `Extended Key Usages <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.12>`_. Accepted values: ``any_extended``, ``cert_signing``, ``client_auth``, ``code_signing``, ``content_commitment``, ``crl_signing``, ``data_encipherment``, ``decipher_only``, ``digital_signature``, ``email_protection``, ``encipher_only``, ``ipsec_end_system``, ``ipsec_tunnel``, ``ipsec_user``, ``key_agreement``, ``key_encipherment``, ``microsoft_commercial_code_signing``, ``microsoft_kernel_code_signing``, ``microsoft_server_gated_crypto``, ``netscape_server_gated_crypto``, ``ocsp_signing``, ``server_auth``, ``timestamping``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#allowed_uses SelfSignedCert#allowed_uses}
        '''
        result = self._values.get("allowed_uses")
        assert result is not None, "Required property 'allowed_uses' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def private_key_pem(self) -> builtins.str:
        '''Private key in `PEM (RFC 1421) <https://datatracker.ietf.org/doc/html/rfc1421>`_ format, that the certificate will belong to. This can be read from a separate file using the ```file`` <https://www.terraform.io/language/functions/file>`_ interpolation function. Only an irreversible secure hash of the private key will be stored in the Terraform state.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#private_key_pem SelfSignedCert#private_key_pem}
        '''
        result = self._values.get("private_key_pem")
        assert result is not None, "Required property 'private_key_pem' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def validity_period_hours(self) -> jsii.Number:
        '''Number of hours, after initial issuing, that the certificate will remain valid for.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#validity_period_hours SelfSignedCert#validity_period_hours}
        '''
        result = self._values.get("validity_period_hours")
        assert result is not None, "Required property 'validity_period_hours' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def dns_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of DNS names for which a certificate is being requested (i.e. certificate subjects).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#dns_names SelfSignedCert#dns_names}
        '''
        result = self._values.get("dns_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def early_renewal_hours(self) -> typing.Optional[jsii.Number]:
        '''The resource will consider the certificate to have expired the given number of hours before its actual expiry time.

        This can be useful to deploy an updated certificate in advance of the expiration of the current certificate. However, the old certificate remains valid until its true expiration time, since this resource does not (and cannot) support certificate revocation. Also, this advance update can only be performed should the Terraform configuration be applied during the early renewal period. (default: ``0``)

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#early_renewal_hours SelfSignedCert#early_renewal_hours}
        '''
        result = self._values.get("early_renewal_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ip_addresses(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of IP addresses for which a certificate is being requested (i.e. certificate subjects).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#ip_addresses SelfSignedCert#ip_addresses}
        '''
        result = self._values.get("ip_addresses")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def is_ca_certificate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Is the generated certificate representing a Certificate Authority (CA) (default: ``false``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#is_ca_certificate SelfSignedCert#is_ca_certificate}
        '''
        result = self._values.get("is_ca_certificate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def key_algorithm(self) -> typing.Optional[builtins.str]:
        '''Name of the algorithm used when generating the private key provided in ``private_key_pem``.

        **NOTE**: this is deprecated and ignored, as the key algorithm is now inferred from the key.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#key_algorithm SelfSignedCert#key_algorithm}
        '''
        result = self._values.get("key_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def set_authority_key_id(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Should the generated certificate include an `authority key identifier <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.1>`_: for self-signed certificates this is the same value as the `subject key identifier <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.2>`_ (default: ``false``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#set_authority_key_id SelfSignedCert#set_authority_key_id}
        '''
        result = self._values.get("set_authority_key_id")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def set_subject_key_id(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Should the generated certificate include a `subject key identifier <https://datatracker.ietf.org/doc/html/rfc5280#section-4.2.1.2>`_ (default: ``false``).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#set_subject_key_id SelfSignedCert#set_subject_key_id}
        '''
        result = self._values.get("set_subject_key_id")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def subject(self) -> typing.Optional["SelfSignedCertSubject"]:
        '''subject block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#subject SelfSignedCert#subject}
        '''
        result = self._values.get("subject")
        return typing.cast(typing.Optional["SelfSignedCertSubject"], result)

    @builtins.property
    def uris(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of URIs for which a certificate is being requested (i.e. certificate subjects).

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#uris SelfSignedCert#uris}
        '''
        result = self._values.get("uris")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SelfSignedCertConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.SelfSignedCertSubject",
    jsii_struct_bases=[],
    name_mapping={
        "common_name": "commonName",
        "country": "country",
        "locality": "locality",
        "organization": "organization",
        "organizational_unit": "organizationalUnit",
        "postal_code": "postalCode",
        "province": "province",
        "serial_number": "serialNumber",
        "street_address": "streetAddress",
    },
)
class SelfSignedCertSubject:
    def __init__(
        self,
        *,
        common_name: typing.Optional[builtins.str] = None,
        country: typing.Optional[builtins.str] = None,
        locality: typing.Optional[builtins.str] = None,
        organization: typing.Optional[builtins.str] = None,
        organizational_unit: typing.Optional[builtins.str] = None,
        postal_code: typing.Optional[builtins.str] = None,
        province: typing.Optional[builtins.str] = None,
        serial_number: typing.Optional[builtins.str] = None,
        street_address: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param common_name: Distinguished name: ``CN``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#common_name SelfSignedCert#common_name}
        :param country: Distinguished name: ``C``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#country SelfSignedCert#country}
        :param locality: Distinguished name: ``L``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#locality SelfSignedCert#locality}
        :param organization: Distinguished name: ``O``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#organization SelfSignedCert#organization}
        :param organizational_unit: Distinguished name: ``OU``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#organizational_unit SelfSignedCert#organizational_unit}
        :param postal_code: Distinguished name: ``PC``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#postal_code SelfSignedCert#postal_code}
        :param province: Distinguished name: ``ST``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#province SelfSignedCert#province}
        :param serial_number: Distinguished name: ``SERIALNUMBER``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#serial_number SelfSignedCert#serial_number}
        :param street_address: Distinguished name: ``STREET``. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#street_address SelfSignedCert#street_address}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if common_name is not None:
            self._values["common_name"] = common_name
        if country is not None:
            self._values["country"] = country
        if locality is not None:
            self._values["locality"] = locality
        if organization is not None:
            self._values["organization"] = organization
        if organizational_unit is not None:
            self._values["organizational_unit"] = organizational_unit
        if postal_code is not None:
            self._values["postal_code"] = postal_code
        if province is not None:
            self._values["province"] = province
        if serial_number is not None:
            self._values["serial_number"] = serial_number
        if street_address is not None:
            self._values["street_address"] = street_address

    @builtins.property
    def common_name(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``CN``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#common_name SelfSignedCert#common_name}
        '''
        result = self._values.get("common_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def country(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``C``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#country SelfSignedCert#country}
        '''
        result = self._values.get("country")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def locality(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``L``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#locality SelfSignedCert#locality}
        '''
        result = self._values.get("locality")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organization(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``O``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#organization SelfSignedCert#organization}
        '''
        result = self._values.get("organization")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def organizational_unit(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``OU``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#organizational_unit SelfSignedCert#organizational_unit}
        '''
        result = self._values.get("organizational_unit")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def postal_code(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``PC``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#postal_code SelfSignedCert#postal_code}
        '''
        result = self._values.get("postal_code")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def province(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``ST``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#province SelfSignedCert#province}
        '''
        result = self._values.get("province")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def serial_number(self) -> typing.Optional[builtins.str]:
        '''Distinguished name: ``SERIALNUMBER``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#serial_number SelfSignedCert#serial_number}
        '''
        result = self._values.get("serial_number")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def street_address(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Distinguished name: ``STREET``.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls/r/self_signed_cert#street_address SelfSignedCert#street_address}
        '''
        result = self._values.get("street_address")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "SelfSignedCertSubject(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class SelfSignedCertSubjectOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.SelfSignedCertSubjectOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCommonName")
    def reset_common_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommonName", []))

    @jsii.member(jsii_name="resetCountry")
    def reset_country(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCountry", []))

    @jsii.member(jsii_name="resetLocality")
    def reset_locality(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocality", []))

    @jsii.member(jsii_name="resetOrganization")
    def reset_organization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganization", []))

    @jsii.member(jsii_name="resetOrganizationalUnit")
    def reset_organizational_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOrganizationalUnit", []))

    @jsii.member(jsii_name="resetPostalCode")
    def reset_postal_code(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostalCode", []))

    @jsii.member(jsii_name="resetProvince")
    def reset_province(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvince", []))

    @jsii.member(jsii_name="resetSerialNumber")
    def reset_serial_number(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSerialNumber", []))

    @jsii.member(jsii_name="resetStreetAddress")
    def reset_street_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStreetAddress", []))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commonNameInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="countryInput")
    def country_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "countryInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="localityInput")
    def locality_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localityInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnitInput")
    def organizational_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationalUnitInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationInput")
    def organization_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "organizationInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postalCodeInput")
    def postal_code_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "postalCodeInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="provinceInput")
    def province_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "provinceInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serialNumberInput")
    def serial_number_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serialNumberInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streetAddressInput")
    def street_address_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "streetAddressInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @common_name.setter
    def common_name(self, value: builtins.str) -> None:
        jsii.set(self, "commonName", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="country")
    def country(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "country"))

    @country.setter
    def country(self, value: builtins.str) -> None:
        jsii.set(self, "country", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="locality")
    def locality(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "locality"))

    @locality.setter
    def locality(self, value: builtins.str) -> None:
        jsii.set(self, "locality", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organization")
    def organization(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organization"))

    @organization.setter
    def organization(self, value: builtins.str) -> None:
        jsii.set(self, "organization", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="organizationalUnit")
    def organizational_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "organizationalUnit"))

    @organizational_unit.setter
    def organizational_unit(self, value: builtins.str) -> None:
        jsii.set(self, "organizationalUnit", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="postalCode")
    def postal_code(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "postalCode"))

    @postal_code.setter
    def postal_code(self, value: builtins.str) -> None:
        jsii.set(self, "postalCode", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="province")
    def province(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "province"))

    @province.setter
    def province(self, value: builtins.str) -> None:
        jsii.set(self, "province", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="serialNumber")
    def serial_number(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serialNumber"))

    @serial_number.setter
    def serial_number(self, value: builtins.str) -> None:
        jsii.set(self, "serialNumber", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="streetAddress")
    def street_address(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "streetAddress"))

    @street_address.setter
    def street_address(self, value: typing.List[builtins.str]) -> None:
        jsii.set(self, "streetAddress", value)

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[SelfSignedCertSubject]:
        return typing.cast(typing.Optional[SelfSignedCertSubject], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[SelfSignedCertSubject]) -> None:
        jsii.set(self, "internalValue", value)


class TlsProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-tls.TlsProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/tls tls}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/tls tls} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls#alias TlsProvider#alias}
        '''
        config = TlsProviderConfig(alias=alias)

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty # type: ignore[misc]
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property # type: ignore[misc]
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "alias", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-tls.TlsProviderConfig",
    jsii_struct_bases=[],
    name_mapping={"alias": "alias"},
)
class TlsProviderConfig:
    def __init__(self, *, alias: typing.Optional[builtins.str] = None) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls#alias TlsProvider#alias}
        '''
        self._values: typing.Dict[str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/tls#alias TlsProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "TlsProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "CertRequest",
    "CertRequestConfig",
    "CertRequestSubject",
    "CertRequestSubjectOutputReference",
    "DataTlsCertificate",
    "DataTlsCertificateCertificates",
    "DataTlsCertificateCertificatesList",
    "DataTlsCertificateCertificatesOutputReference",
    "DataTlsCertificateConfig",
    "DataTlsPublicKey",
    "DataTlsPublicKeyConfig",
    "LocallySignedCert",
    "LocallySignedCertConfig",
    "PrivateKey",
    "PrivateKeyConfig",
    "SelfSignedCert",
    "SelfSignedCertConfig",
    "SelfSignedCertSubject",
    "SelfSignedCertSubjectOutputReference",
    "TlsProvider",
    "TlsProviderConfig",
]

publication.publish()
