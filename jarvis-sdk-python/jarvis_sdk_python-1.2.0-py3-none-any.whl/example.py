"""
This file contains examples of Identify API usage.
"""

from jarvis_sdk.cmd import IdentityClient


def introspect_token_example():
    token = "JWT TOKEN"
    client = IdentityClient()
    token_info = client.introspect_token(token)
    if token_info is not None:
        print("Token info")
        print("Tenant: " + token_info.subject.tenantId)
        print("Customer: " + token_info.customerId)
        print("App space: " + token_info.appSpaceId)
        print("Application: " + token_info.applicationId)
        print("Subject: " + token_info.subject.id)
        print("Expire time: " + str(token_info.expireTime))


def verify_digital_twin_email_example():
    token = "VERIFICATION TOKEN FROM TEMPORAL"
    client = IdentityClient()
    digital_twin_info = client.verify_digital_twin_email(token)
    if digital_twin_info is not None:
        print("Digital twin info")
        print("Tenant: " + digital_twin_info.tenantId)
        print("Digital twin: " + digital_twin_info.id)

def digital_twin_by_token():
    token = "JWT TOKEN"
    client = IdentityClient()
    digital_twin = client.get_digital_twin_by_token(token, ["email"])
    if digital_twin is not None:
        if "digitalTwin" in digital_twin:
            print(digital_twin["digitalTwin"])
        if "tokenInfo" in digital_twin:
            print("\nToken info:")
            print(digital_twin["tokenInfo"])

def digital_twin():
    dt_id = "DIGITAL TWIN ID"
    tenant_id = "TENANT ID"
    client = IdentityClient()
    digital_twin = client.get_digital_twin(dt_id, tenant_id, ["email", "address"])
    print("Digital Twin info")
    if digital_twin is not None:
        if "digitalTwin" in digital_twin:
            print(digital_twin["digitalTwin"])
        if "tokenInfo" in digital_twin:
            print("\nToken info:")
            print(digital_twin["tokenInfo"])

def enrich_token():
    token = "JWT TOKEN"
    claims = {
        "string_claim": "string_value",
        "number_claim": 42,
        "bool_claim": True,
        "null_claim": None,
        "map_claim": {
            "key": "value",
        },
        "array_claim": [
            "string_value",
        ]
    }
    client = IdentityClient()
    response = client.enrich_token(token, claims, claims)
    if response is not None:
        print("Successfully enriched token")
    else:
        print("Invalid token")
