#
# Created on Tue Dec 21 2021
#
# Copyright (c) 2021 Lenders Cooperative, a division of Summit Technology Group, Inc.
#
import json
import logging

from django.conf import settings

from .api_handler import ApiHandler
from .docusign_helper import process_docusign_webhook, extract_documents
from los_docusign.utils.validators import validate_payload

LOGGER = logging.getLogger("root")


class DocuSignClient:
    def __init__(self, access_token: str, timeout: int, tenant_schema: str):
        self.account_id = settings.DOCUSIGN_API_ACCOUNT_ID
        self.api_key = f"Bearer {access_token}"
        DEFAULT_TIMEOUT = 60
        if timeout:
            self.timeout = timeout
        else:
            self.timeout = DEFAULT_TIMEOUT
        self.tenant_schema = tenant_schema

    def generate_docusign_preview_url(self, params: dict, log_config: dict = None):
        LOGGER.info("Generating Docusign Preview Url")
        if not (
            "envelope_id" in params
            and params["envelope_id"] is not None
            or "authentication_method" in params
            and params["authentication_method"] is not None
            or "email" in params
            and params["email"] is not None
            or "user_name" not in params
            and params["user_name"] is not None
            or "client_user_id" not in params
            and params["client_user_id"] is not None
            or "return_url" not in params
            and params["return_url"] is not None
        ):
            LOGGER.error("Invalid input dict for generate_docusign_preview_url")
            raise Exception("Invalid input dict for generate_docusign_preview_url")

        envelope_id = params["envelope_id"]
        authentication_method = params["authenticationMethod"]
        email = params["email"]
        user_name = params["userName"]
        client_user_id = params["clientUserId"]
        return_url = params["returnUrl"]

        url = settings.DOCUSIGN_API_ENDPOINT

        preview_resource_path = f"{self.account_id}/envelopes/{envelope_id}/views/recipient"
        preview_url = url + preview_resource_path
        preview_data = {
            "authenticationMethod": authentication_method,
            "email": email,
            "userName": user_name,
            "clientUserId": client_user_id,
            "returnUrl": return_url,
        }
        LOGGER.info("Calling API Handler's send request for generate_docusign_preview_url")
        docusign_handler = ApiHandler(preview_url, self.api_key, self.tenant_schema, timeout=self.timeout)
        envelope_result = docusign_handler.send_request(
            method="POST", payload=json.dumps(preview_data), log_config=log_config, event="EMBEDDED_URL"
        )

        LOGGER.debug(
            f"generate_docusign_preview_url completed for envelope {envelope_id} with status; {envelope_result.status_code}. Preview Url Data: {envelope_result.text}"
        )
        return envelope_result

    def create_envelope(self, payload, log_config: dict = None):

        ## Validate necessary values from payload
        response = validate_payload(payload=payload)
        if response != "Success":
            if log_config:
                log_entry = log_config["model"](
                    loan=log_config["loan"],
                    requested_by=log_config["user"],
                    request_url=log_config["request_url"],
                    request_headers=log_config["request_headers"],
                    request_body=log_config["request_body"],
                    response_body=response,
                    request_time=log_config["timezone"].now(),
                    response_time=log_config["timezone"].now(),
                    tin=log_config["tin"],
                    request_ip=log_config["request_ip"],
                    response_code=log_config["response_code"],
                    event_type="ENVELOPE",
                    event="SENT",
                )
                log_entry.save()
            raise Exception(response)

        url = settings.DOCUSIGN_API_ENDPOINT

        resource_path = self.account_id + "/envelopes"
        envelope_url = url + resource_path
        LOGGER.info("Creating envelope for given payload")
        docusign_handler = ApiHandler(envelope_url, self.api_key, self.tenant_schema, timeout=self.timeout)
        envelope_result = docusign_handler.send_request(
            method="POST", payload=json.dumps(payload), log_config=log_config, add_custom_fields=True, event="SENT"
        )

        LOGGER.debug(
            f"create_envelope completed with status; {envelope_result.status_code}. Envelope Creation Data: {envelope_result.text}"
        )
        return envelope_result

    def download_docusign_document(self, params: dict, log_config: dict = None):
        LOGGER.info("Docusign Document Download")
        envelopeId = params["envelope_id"]
        # Value can be combined, archive
        document_download_option = params["doc_download_option"]

        account_id = settings.DOCUSIGN_API_ACCOUNT_ID
        headers = None
        if document_download_option == "archive":
            resource_path = f"{account_id}/envelopes/{envelopeId}/documents/archive"
            headers = {}
            headers["Accept"] = "application/zip, application/octet-stream"
        elif document_download_option == "combined":
            resource_path = f"{account_id}/envelopes/{envelopeId}/documents/combined"

        url = settings.DOCUSIGN_API_ENDPOINT
        doc_url = url + resource_path

        docusign_handler = ApiHandler(doc_url, self.api_key, self.tenant_schema, timeout=self.timeout)
        doc_download_result = docusign_handler.send_request(method="GET", log_config=log_config, event="DOWNLOAD_DOC")
        LOGGER.info(
            f"download_docusign_document completed with status: {doc_download_result.status_code} for envelope id: {envelopeId}"
        )
        return doc_download_result

    def process_docusign_notification(self, xml_string: str, log_config: dict = None):
        return process_docusign_webhook(xml_string, log_config)

    def extract_docusign_documents(self, xml_string: str):
        return extract_documents(xml_string)

    def update_envelope_and_resend(self, envelope_id, signers_data: dict, log_config: dict = None):
        url = settings.DOCUSIGN_API_ENDPOINT

        signer_payload = {}
        signers = []
        for signer in signers_data:
            signer_data = {}
            signer_data["recipientId"] = signer["recipientId"]
            signer_data["email"] = signer["email"]
            try:
                if signer["phone"]:
                    phoneAuthentication = {}
                    phoneAuthentication["recipMayProvideNumber"] = False
                    phoneAuthentication["validateRecipProvidedNumber"] = False
                    phoneAuthentication["recordVoicePrint"] = False
                    senderProvidedNumbers = []
                    senderProvidedNumbers.append(signer["phone"])
                    phoneAuthentication["senderProvidedNumbers"] = senderProvidedNumbers
                    signer_data["phoneAuthentication"] = phoneAuthentication
            except KeyError as e:
                pass
            signers.append(signer_data)
        signer_payload["signers"] = signers
        resource_path = self.account_id + f"/envelopes/{envelope_id}/recipients?resend_envelope=true"
        envelope_url = url + resource_path
        LOGGER.info(f"Resending envelope: {envelope_id}")

        docusign_handler = ApiHandler(envelope_url, self.api_key, self.tenant_schema, timeout=self.timeout)
        envelope_result = docusign_handler.send_request(
            method="PUT", payload=json.dumps(signer_payload), log_config=log_config, event="RESEND"
        )

        LOGGER.debug(
            f"update_envelope_and_resend completed with status; {envelope_result.status_code}. update_envelope_and_resend data: {envelope_result.text}"
        )
        return envelope_result

    def update_envelope_status(self, status_info: dict, log_config: dict = None):
        url = settings.DOCUSIGN_API_ENDPOINT

        status_update_payload = {}
        envelope_id = status_info["envelope_id"]
        status = status_info["status"]
        reason = status_info["reason"]

        if status.lower() == "voided":
            status_update_payload["voidedReason"] = reason

        status_update_payload["status"] = status

        resource_path = self.account_id + f"/envelopes/{envelope_id}"
        envelope_url = url + resource_path
        LOGGER.info(f"Updating envelope status to {status} for envelope : {envelope_id}")

        docusign_handler = ApiHandler(envelope_url, self.api_key, self.tenant_schema, timeout=self.timeout)
        envelope_result = docusign_handler.send_request(
            method="PUT",
            payload=json.dumps(status_update_payload),
            log_config=log_config,
            event="UPDATE_ENVELOPE_STATUS",
        )

        LOGGER.debug(
            f"update_envelope_status completed with status; {envelope_result.status_code}. update_envelope_status data: {envelope_result.text}"
        )
        return envelope_result
