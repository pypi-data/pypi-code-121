#
# Created on Tue Dec 21 2021
#
# Copyright (c) 2021 Lenders Cooperative, a division of Summit Technology Group, Inc.
#
import os
from urllib import request, response
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from django.core.exceptions import ValidationError


def validate_excel_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = [".xls", ".xlsx", ".csv"]
    if not ext.lower() in valid_extensions:
        raise ValidationError(u"Unsupported file extension. Must be Excel File")


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = [
        ".pdf",
        ".xls",
        ".xlsx",
        ".csv",
        ".doc",
        ".docx",
        ".jpg",
        ".jpeg",
        ".png",
    ]
    if not ext.lower() in valid_extensions:
        raise ValidationError(u"Unsupported file extension.")

def validate_payload(payload):
    request_payload = payload
    signers = request_payload["recipients"]["signers"]
    documents = request_payload["documents"]
    status = request_payload["status"]
    emailSubject = request_payload["emailSubject"]

    if status is None or status == "":
        response = "DocuSign Failure : Status is not set"
        return response
    if emailSubject is None or emailSubject == "":
        response = "DocuSign Failure : Email Subject is not set"
        return response

    for signer in signers:

        role = signer["roleName"]
        recipient_id = signer["recipientId"]
        recipient_type = signer["recipientType"]
        routingOrder = signer["routingOrder"]
        email = signer["email"]
        name = signer["name"]

        if "customFields" in signer:
            customfield = signer["customFields"]
            if customfield is None or customfield == "":
                response = "DocuSign Failure : Signer's custom details are incorrect."
                return response

        if role is None or role == "":
            response = "DocuSign Failure : Signer's Role is not set"
            return response
        elif recipient_id is None or recipient_id == "":
            response = "DocuSign Failure : Signer's Recipient Id is not present."
            return response
        elif recipient_type is None or recipient_type == "":
            response = "DocuSign Failure : Signer's Recipient Type is not present."
            return response
        elif routingOrder is None or routingOrder == "":
            response = "DocuSign Failure : Signer's Routing Order is not set."
            return response
        elif email is None or email == "":
            response = "DocuSign Failure : Signer's email is not set."
            return response
        elif name is None or name == "":
            response = "DocuSign Failure : Signer's Name is not set."
            return response

        if "idCheckConfigurationName" in signer and "phoneAuthentication" in signer:
            authentication = signer["idCheckConfigurationName"]
            phone = signer["phoneAuthentication"]["senderProvidedNumbers"]
            if authentication == "Phone Auth $":
                for phonenumber in phone:
                    phone_number = "+1" + phonenumber
                    try:
                        phone_number = phonenumbers.parse(phone_number, None)
                        if not phonenumbers.is_valid_number(phone_number):
                            response = "DocuSign Failure : Invalid phone number"
                            return response
                    except NumberParseException as e:
                        response = "DocuSign Failure : Phone Number must be 10 digits"
                        return response

            
    for document in documents:
        docName = document["name"]
        docExt = document["fileExtension"]
        docbase64 = document["documentBase64"]
        docId = document["documentId"]

        if docName is None or docName == "":
            response = "DocuSign Failure : Signer's Dcoument Name is not set."
            return response
        elif docExt is None or docExt == "":
            response = "DocuSign Failure : Signer's Document extension Order is not set."
            return response
        elif docbase64 is None or docbase64 == "":
            response = "DocuSign Failure : Signer's Document is not present."
            return response
        elif docId is None or docId == "":
            response = "DocuSign Failure : Signer's Document Id is not set."
            return response

    return "Success"