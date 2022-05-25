#
# Created on Tue Dec 21 2021
#
# Copyright (c) 2021 Lenders Cooperative, a division of Summit Technology Group, Inc.
#
import base64
import hashlib
import hmac
import json
import logging
import re
from datetime import datetime, timedelta
from os import path
from xml.etree import cElementTree as ElementTree

from django.conf import settings
from django.http import Http404

# import sentry_sdk
from django.utils import timezone
from docusign_esign import ApiClient
from docusign_esign.client.api_exception import ApiException

from los_docusign.models import (
    DocusignEnvelopeAuditLog,
    DocusignEnvelopeStageData,
    DocusignOrgTemplate,
    DocuSignUserAuth,
)

from .XmlParser import XmlDictConfig

SCOPES = ["signature"]

LOGGER = logging.getLogger("root")


def get_docusign_user(organization_pk):
    try:
        # Try if the user is the available and has the docusign account
        docusign_user = DocuSignUserAuth.objects.get(organization_pk=organization_pk)
    except DocuSignUserAuth.DoesNotExist:
        # Else use the admin user
        # Tejas, isn't default_user supposed to be the default user we use as a
        # fallback?
        docusign_user = DocuSignUserAuth.objects.get(default_user=True)

    return docusign_user


def get_access_token(docusign_user, redirect_url=None):
    docusign_token_expiry = settings.DOCUSIGN_TOKEN_EXPIRY_IN_SECONDS

    if docusign_user.expires_at >= timezone.now():
        access_token = docusign_user.access_token
    else:
        token_response = _jwt_auth(docusign_user.docusign_api_username, redirect_url)
        # print(f"Token Response: {token_response}")
        try:
            if token_response["consent_url"]:
                return token_response
        except TypeError as e:
            pass
        access_token = token_response.access_token
        docusign_user.access_token = access_token
        docusign_user.expires_at = timezone.now() + timedelta(seconds=int(docusign_token_expiry))
        docusign_user.save()

    return access_token


def check_docusign_access_token(organization_pk, redirect_uri=None):
    docusign_user = get_docusign_user(organization_pk)
    token_response = _jwt_auth(docusign_user.docusign_api_username, redirect_uri)
    LOGGER.info("Checking DocuSign Access Token")
    if token_response and isinstance(token_response, dict):
        # return the consent_url here
        return token_response
    return None


def _jwt_auth(docusign_api_username, redirect_uri):
    """JSON Web Token authorization"""
    api_client = ApiClient()
    api_client.set_base_path(settings.DOCUSIGN_AUTHORIZATION_SERVER)
    use_scopes = SCOPES
    if "impersonation" not in use_scopes:
        use_scopes.append("impersonation")

    # Catch IO error
    try:
        private_key = _get_private_key().encode("ascii").decode("utf-8")

    except (OSError, IOError) as err:
        # sentry_sdk.capture_exception(Exception(f'OSError, IOError in Docusign JWT Auth'))
        return "error"

    try:
        jwtTokenResponse = api_client.request_jwt_user_token(
            client_id=str(settings.DOCUSIGN_CLIENT_ID),
            user_id=docusign_api_username,
            oauth_host_name=str(settings.DOCUSIGN_AUTHORIZATION_SERVER),
            private_key_bytes=private_key,
            expires_in=3600,
            scopes=use_scopes,
        )
    except ApiException as err:
        body = err.body.decode("utf8")
        # Grand explicit consent for the application
        if "consent_required" in body:
            use_scopes = SCOPES
            if "impersonation" not in use_scopes:
                use_scopes.append("impersonation")
            consent_scopes = " ".join(use_scopes)
            if redirect_uri is None:
                redirect_uri = settings.DOCUSIGN_REDIRECT_APP_URL
            consent_url = (
                f"https://{settings.DOCUSIGN_AUTHORIZATION_SERVER}/oauth/auth?response_type=code&"
                f"scope={consent_scopes}&client_id={settings.DOCUSIGN_CLIENT_ID}&redirect_uri={redirect_uri}"
            )
            consent_url_dict = {}
            consent_url_dict["consent_url"] = consent_url
            return consent_url_dict
        else:
            LOGGER.error(f"Error while getting the jwt token for docusign: {err}")
            raise

    return jwtTokenResponse


def _get_private_key():
    """
    Check that the private key present in the file and if it is, get it from the file.
    In the opposite way get it from config variable.
    """
    private_key_file = path.abspath(settings.DOCUSIGN_PRIVATE_KEY_FILE)
    if path.isfile(private_key_file):
        with open(private_key_file) as private_key_file:
            private_key = private_key_file.read()
    else:
        private_key = settings.DOCUSIGN_PRIVATE_KEY_FILE.encode().decode("unicode-escape")

    return private_key


def populate_text_tabs(text_tabs_forms, text_tabs_data: dict):
    # Need to populate all the text tabs with the values
    for textTabsInfo in text_tabs_forms:
        tab_label = textTabsInfo["tabLabel"]
        try:
            textTabsInfo["value"] = text_tabs_data.get(tab_label)
        except KeyError as e:
            print(f"Key not found {e}")


def get_docusign_template(organization_pk, template_name=None):
    docusign_payload = None
    try:
        docusign_template = DocusignOrgTemplate.objects.get(
            organization_model="organization",
            docusign_template__template_type=template_name,
            organization_pk=organization_pk,
        ).docusign_template
    except DocusignOrgTemplate.DoesNotExist:
        dsua = DocuSignUserAuth.objects.get(default_user=True)
        docusign_template = DocusignOrgTemplate.objects.get(
            object_pk=dsua.object_pk, docusign_template__template_type=template_name
        ).docusign_template

    docusign_payload = docusign_template.docusign_payload
    if docusign_payload is None:
        print("Payload Not found for org. Check database..return")
        LOGGER.error(f"Payload Not found for org {organization_pk}. Check database..return")
        return

    # resp = json.loads(docusign_payload)
    return docusign_payload


def _read_response_webhook(xml_string):

    root = ElementTree.XML(xml_string)
    request_data_dict = XmlDictConfig(root)
    m = re.search("{http://www.docusign.net/API/(.+?)}EnvelopeStatus", str(request_data_dict))
    api_version = None
    if m:
        api_version = m.group(1)
    else:
        # sentry_sdk.capture_exception(Exception(f'Failed to retrieve API Version for the DocuSign Webhook: {str(request_data_dict)}'))
        raise Http404

    docusign_schema = "{http://www.docusign.net/API/" + api_version + "}"

    # Since we are not using any of the data sent back by DocuSign, we clear those fields which potentially causes json.dumps to fail to parse Decimal Values which are set by the Parser
    recipient_signers = request_data_dict[f"{docusign_schema}EnvelopeStatus"][f"{docusign_schema}RecipientStatuses"][
        f"{docusign_schema}RecipientStatus"
    ]

    if not isinstance(recipient_signers, list):
        recipient_signers = [recipient_signers]

    for recipients in recipient_signers:
        recipients[f"{docusign_schema}TabStatuses"] = None
        recipients[f"{docusign_schema}FormData"] = None

    line = re.sub(
        r"({http://www.docusign.net/API/[0-9].[0-9]})",
        "",
        json.dumps(request_data_dict),
    )
    docusign_data_dict = json.loads(line)

    return docusign_data_dict


def process_docusign_webhook(xml_string, log_config, event=None, event_type="WEBHOOK"):
    # request_data_dict = request.data

    docusign_data_dict = _read_response_webhook(xml_string)

    envelopeId = docusign_data_dict["EnvelopeStatus"]["EnvelopeID"]

    try:
        envelope_stage_data = DocusignEnvelopeStageData.objects.get(envelope_id=envelopeId)
    except DocusignEnvelopeStageData.DoesNotExist:
        LOGGER.error(f"Envelope id  {envelopeId} not found in system")
        raise Exception(f"Envelope id  {envelopeId} not found in system")

    return _extract_envelope_information(envelope_stage_data, docusign_data_dict, log_config, event, event_type)


def extract_documents(xml_string):
    root = ElementTree.XML(xml_string)
    request_data_dict = XmlDictConfig(root)
    line = re.sub(
        r"({http://www.docusign.net/API/[0-9].[0-9]})",
        "",
        json.dumps(request_data_dict),
    )
    docusign_data_dict = json.loads(line)
    documents = []
    document_pdfs = docusign_data_dict["DocumentPDFs"]["DocumentPDF"]
    if isinstance(document_pdfs, list):
        for document_pdf in document_pdfs:
            document = {}
            document["name"] = document_pdf["Name"]
            document["pdf_bytes"] = document_pdf["PDFBytes"]
            try:
                document["document_id"] = document_pdf["DocumentID"]
            except KeyError as e:
                document["document_id"] = None
            document["document_type"] = document_pdf["DocumentType"]
            documents.append(document)
    else:
        document = {}
        document["name"] = document_pdfs["Name"]
        document["pdf_bytes"] = document_pdfs["PDFBytes"]
        try:
            document["document_id"] = document_pdfs["DocumentID"]
        except KeyError as e:
            document["document_id"] = None
        document["document_type"] = document_pdfs["DocumentType"]
        documents.append(document)
    return documents


def _extract_envelope_information(
    envelope_stage_data, docusign_data_dict, log_config=None, event=None, event_type="WEBHOOK"
):
    try:
        envelopeId = docusign_data_dict["EnvelopeStatus"]["EnvelopeID"]
        recipients = docusign_data_dict["EnvelopeStatus"]["RecipientStatuses"]["RecipientStatus"]
        envelope_status = docusign_data_dict["EnvelopeStatus"]["Status"]
        envelope_status = str(envelope_status).lower()
        envelope_output = {}

        if not isinstance(recipients, list):
            recipients = [recipients]

        recipient_failed_delivery = False
        recipient_failed_authentication = False
        recipients_data = []
        for recipient in recipients:
            recipient_data = {}

            recipient_status = recipient["Status"]
            email = recipient["Email"]
            username = recipient["UserName"]
            recipient_id = recipient["RecipientId"]
            sent_time = recipient.get("Sent", None)
            routing_order = recipient["RoutingOrder"]

            try:
                custom_fields = recipient["CustomFields"]
            except KeyError as e:
                custom_fields = None

            recipient_auth_status = recipient.get("RecipientAuthenticationStatus", None)
            recipient_id_question_status = None
            recipient_id_lookup_status = None
            recipient_phone_auth_status = None

            if recipient_auth_status:
                recipient_idquestion_result = recipient_auth_status.get("IDQuestionsResult", None)

                recipient_id_lookup_result = recipient_auth_status.get("IDLookupResult", None)

                recipient_phone_auth_result = recipient_auth_status.get("PhoneAuthResult", None)

                if recipient_idquestion_result:
                    recipient_id_question_status = recipient_idquestion_result["Status"]
                    recipient_id_question_status = str(recipient_id_question_status).lower()
                if recipient_id_lookup_result:
                    recipient_id_lookup_status = recipient_id_lookup_result["Status"]
                    recipient_id_lookup_status = str(recipient_id_lookup_status).lower()

                if recipient_phone_auth_result:
                    recipient_phone_auth_status = recipient_phone_auth_result["Status"]
                    recipient_phone_auth_status = str(recipient_phone_auth_status).lower()

                if "failed" in (
                    recipient_id_lookup_status,
                    recipient_id_question_status,
                    recipient_phone_auth_status,
                ):
                    recipient_status = "authentication failed"
                    recipient_failed_authentication = True

            recipient_status = str(recipient_status).lower()

            if recipient_status in ["autoresponded"]:
                recipient_failed_delivery = True

            recipient_data["recipient_id"] = recipient_id
            recipient_data["email"] = email
            recipient_data["name"] = username
            recipient_data["status"] = recipient_status
            recipient_data["sent_time"] = sent_time
            recipient_data["routing_order"] = routing_order
            if custom_fields:
                recipient_data["custom_fields"] = custom_fields

            recipient_data["phone_auth"] = {}
            if recipient_auth_status is not None:
                phone_auth = {}
                current_status = envelope_stage_data.current_status
                if current_status is None:
                    if recipient_phone_auth_status:
                        phone_auth["status"] = recipient_phone_auth_status
                        phone_auth["last_event_time"] = recipient_phone_auth_result["EventTimestamp"]
                        if recipient_phone_auth_status == "passed":
                            phone_auth["fail_count"] = 0
                        else:
                            phone_auth["fail_count"] = 1
                    recipient_data["phone_auth"] = phone_auth
                else:
                    recipient_status = current_status["recipients"]
                    for recipient in recipient_status:
                        phone_auth = recipient["phone_auth"]
                        if (
                            recipient["email"] == recipient_data["email"]
                            and recipient["name"] == recipient_data["name"]
                            and recipient["custom_fields"]["CustomField"] in custom_fields["CustomField"]
                        ):
                            # Currently not relying on the recipient id as we do store the sent recipient id and we receive the Docusign internal recipient id
                            if phone_auth is {}:
                                phone_auth["fail_count"] = None
                                phone_auth["status"] = None
                                phone_auth["last_event_time"] = None

                            if recipient_phone_auth_status:
                                if recipient_phone_auth_status == "passed":
                                    phone_auth["fail_count"] = 0
                                else:
                                    if phone_auth.get("fail_count", None):
                                        fail_count = phone_auth["fail_count"]
                                        fail_count = fail_count + 1
                                        phone_auth["fail_count"] = fail_count
                                    else:
                                        fail_count = 1
                                        phone_auth["fail_count"] = fail_count
                                        phone_auth["status"] = recipient_phone_auth_status
                                        phone_auth["last_event_time"] = recipient_phone_auth_result["EventTimestamp"]
                            recipient_data["phone_auth"] = phone_auth
                            break

            recipients_data.append(recipient_data)
            # envelope_output["recipients"].append(recipient_data)

        # Let's not overwrite the status of authentication failed if the recipient failed authentication.
        # We need this to know if the receipient failed authentication and later on completed the application
        # Assigning the envelope status value to recipient status as the for multiple signers,
        # Env status will be updated to "Completed" only when all signers sign.

        if not envelope_stage_data.recipient_status == "authentication failed":
            envelope_stage_data.recipient_status = envelope_status

        if "failed" in (
            recipient_id_lookup_status,
            recipient_id_question_status,
            recipient_phone_auth_status,
        ):
            envelope_stage_data.recipient_status = "authentication failed"
            envelope_stage_data.recipient_auth_info = recipient_auth_status
            recipient_status = "authentication failed"

        if recipient_failed_delivery:
            recipient_status = "autoresponded"

        if recipient_failed_authentication:
            recipient_status = "authentication failed"

        event_value = envelope_status

        if recipient_status == "authentication failed" and envelope_status == "sent":
            event_value = "authentication failed"

        if recipient_status == "autoresponded" and envelope_status == "sent":
            event_value = "autoresponded"

        # TODO: Need to understand how can we log this in the DocuSignEnvelopeAuditLog, since we do not have the content type?
        # log = DocusignEnvelopeAuditLog(
        #     content_type=envelope_stage_data.content_type,
        #     object_pk=envelope_stage_data.object_pk,
        #     event_received_at=datetime.now(),
        #     envelope_id=envelope_stage_data.envelope_id,
        #     event_type="WEBHOOK",
        #     event_value=event_value,
        #     remote_addr="0.0.0.0",
        #     recipient_details=recipients_data,
        # )
        # log.save()

        if log_config:
            log_entry = log_config["model"](
                loan=log_config["loan"],
                requested_by=log_config["user"],
                request_url=log_config["request_url"],
                request_headers=log_config["request_headers"],
                request_body=log_config["request_body"],
                request_time=log_config["timezone"].now(),
                response_time=log_config["timezone"].now(),
                tin=log_config["tin"],
                request_ip=log_config["request_ip"],
                response_code=log_config["response_code"],
                event_type=event_type,
                event=event_value,
            )
            log_entry.save()

        if event_value == "authentication failed":
            envelope_status = "authentication failed"

        envelope_output = {
            "envelopeId": envelopeId,
            "envelope_status": envelope_status,
            "recipients": recipients_data,
        }
        envelope_stage_data.envelope_status = envelope_status
        envelope_stage_data.current_status = envelope_output
        envelope_stage_data.recipient_status = recipient_status
        # envelope_stage_data.updated_at = timezone.now()
        envelope_stage_data.save()

        print(f"END process_docusign_notification: {envelopeId}")
        LOGGER.debug(f"END process_docusign_notification: {envelopeId}")

    except Exception as e:
        LOGGER.error(f"Exception while extracting status from Webhook notification: {e}")
        if log_config:
            log_entry = log_config["model"](
                loan=log_config["loan"],
                requested_by=log_config["user"],
                request_url=log_config["request_url"],
                request_headers=log_config["request_headers"],
                request_body=log_config["request_body"],
                response_body=str(e),
                request_time=log_config["timezone"].now(),
                response_time=log_config["timezone"].now(),
                tin=log_config["tin"],
                request_ip=log_config["request_ip"],
                response_code=log_config["response_code"],
                event_type=event_type,
                event=event_value,
            )
            log_entry.save()
        raise Exception("Exception while extracting status from Webhook notification!") from e
    return envelope_output


def ComputeHash(secret, payload):
    hashBytes = hmac.new(secret, msg=payload, digestmod=hashlib.sha256).digest()
    base64Hash = base64.b64encode(hashBytes)
    return base64Hash


def HashIsValid(secret, payload, verify):
    return hmac.compare_digest(verify, ComputeHash(secret, payload))


def validate_received_webhook(secret, payload, verify):
    return HashIsValid(secret=secret.encode(), payload=payload, verify=verify.encode())
