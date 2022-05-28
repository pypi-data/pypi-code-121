import logging
from os import environ
from time import sleep

import pytest
from python_eloqua_wrapper import EloquaSession

LOGGER = logging.getLogger(__name__)


def get_eloqua_session():
    return EloquaSession(
        username=environ['ELOQUA_USER'],
        password=environ['ELOQUA_PASSWORD'],
        company=environ['ELOQUA_COMPANY'])


@pytest.fixture()
def eloqua_bulk_wait():
    LOGGER.info("Waiting to ensure Eloqua had time to update the records via BULK")
    sleep(20)


@pytest.fixture()
def create_delete_contacts(map_external_input):
    LOGGER.info("Creating contacts in Eloqua...")
    contact_ids = []
    for contact in map_external_input:
        response = get_eloqua_session().post(url='/api/REST/1.0/data/contact', json=contact)
        response.raise_for_status()
        contact.update({'id': response.json().get('id')})
        contact_id = response.json().get('id')
        contact_ids.append(contact_id)
    yield contact_ids
    LOGGER.info("Deleting contacts from Eloqua...")
    for contact_id in contact_ids:
        response = get_eloqua_session().delete(url=f'/api/REST/1.0/data/contact/{contact_id}')
        response.raise_for_status()


@pytest.fixture()
def contact_field_map():
    response = get_eloqua_session().get('/api/REST/1.0/assets/contact/fields?depth=complete', timeout=30)
    response.raise_for_status()
    return response.json()['elements']


@pytest.fixture()
def create_contact_field_map(contact_field_map):
    return {
        contact_field['internalName']: contact_field['id']
        for contact_field in contact_field_map}


@pytest.fixture()
def retrieved_contact_field_map(contact_field_map):
    result = {contact_field['id']: contact_field['internalName'] for contact_field in contact_field_map}
    return result


def map_retrieved_contact_record(record, retrieved_contact_field_map):
    field_map = {retrieved_contact_field_map[field['id']]: field.get('value', "") for field in record['fieldValues']}
    field_map['C_EmailAddress'] = record.get("emailAddress", "")
    field_map['C_FirstName'] = record.get("firstName", "")
    field_map['C_LastName'] = record.get("lastName", "")
    field_map['C_MobilePhone'] = record.get("mobilePhone", "")
    field_map['C_Country'] = record.get("country", "")
    field_map['C_Address1'] = record.get("address1", "")
    field_map['C_Address2'] = record.get("address2", "")
    field_map['C_Address3'] = record.get("address3", "")
    field_map['C_City'] = record.get("city", "")
    field_map['C_State_Prov'] = record.get("province", "")
    field_map['C_Zip_Postal'] = record.get("postalCode", "")
    field_map['C_Company'] = record.get("accountName", "")
    field_map['C_BusPhone'] = record.get("businessPhone", "")
    field_map['C_Title'] = record.get("title", "")
    field_map['isBounced'] = record.get("isBounceback", ""),
    field_map['isSubscribed'] = record.get("isSubscribed", "")
    return field_map


@pytest.fixture()
def retrieve_contacts_for_validation(create_delete_contacts, retrieved_contact_field_map):
    contacts = []
    for contact_id in create_delete_contacts:
        response = get_eloqua_session().get(url=f'/api/REST/1.0/data/contact/{contact_id}')
        response.raise_for_status()
        contacts.append(map_retrieved_contact_record(response.json(), retrieved_contact_field_map))
    return contacts
