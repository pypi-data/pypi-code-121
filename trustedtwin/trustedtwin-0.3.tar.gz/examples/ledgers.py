"""Examples of API call for Ledgers operations"""
from time import sleep

from trustedtwin import RestService

client = RestService(auth='$my_private_token')

# creation of a new Twin
twin = client.twins.create()
twin_uuid = twin['creation_certificate']['uuid']

other_twin = client.twins.create()
other_twin_uuid = other_twin['creation_certificate']['uuid']


entries = {
    "key1": {
        "value": "123",
        "visibility": "true"
    },
    "key2": {
        "value": "321",
        "visibility": None          # limited visibility only to account members aka private
    }
}

twin_ledger = client.ledgers.add_twin_ledger_entry(twin=twin_uuid, entries=entries)
ledger_entries = twin_ledger['entries']

# accessing params in ledger:
key1_value = ledger_entries['key1']['value']
key1_visibility = ledger_entries['key1']['visibility']
key1_created = ledger_entries['key1']['entry_created_ts']
key1_updated = ledger_entries['key1']['entry_updated_ts']
key1_val_changed = ledger_entries['key1']['value_changed_ts']

# ledger's params:
ledger_created = twin_ledger['entry_created_ts']
ledger_updated = twin_ledger['entry_updated_ts']
ledger_val_changed = twin_ledger['value_changed_ts']

# update ledger:
to_update_ledger = {
    "key1": {
        "value": "new_value"
    },
    "key2": {
        "visibility": 'true'
    }
}

updated_ledger = client.ledgers.update_twin_ledger_entry(twin=twin_uuid, entries=to_update_ledger)
print(updated_ledger['entries']['key1']['value'] == 'new_value')
print(updated_ledger['entries']['key2']['visibility'] == 'true')

# get ledger
personal_ledger = client.ledgers.get_twin_ledger_entry(twin_uuid)     # by default returns personal ledger

# we can access foreign ledger (if contains public entries)
# foreign_ledger = client.ledgers.get_twin_ledger_entry(twin_uuid, ledger_created='other-ledger-uuid')

# we can create reference to entries in ledgers of other twins
# important: references between entries within the same ledger are not acceptable
other_twin_ledger_entries = {
    "key3": {
        "value": "referred val",
        "visibility": "true"
    }
}
other_ledger = client.ledgers.add_twin_ledger_entry(twin=other_twin_uuid, entries=other_twin_ledger_entries)
other_ledger_uuid = 'uuid-of-a-ledger'     # equals to Account ID

twin_2_ref_entry = {
    "referring_key": {
        "ref": {
            "source": "twin://" + other_twin_uuid + "/" + other_ledger_uuid + "/key3"
        }
    }
}

# twin.referring_key -> other_twin.key3
response = client.ledgers.add_twin_ledger_entry(twin=twin_uuid, entries=twin_2_ref_entry)
print(response['entries']['referring_key']['ref']['status'] == 'not_found')
# during initialisation the reference, it's status is set to 'not_found' as it not exists yet.
# when references propagates and is defined properly, then status

sleep(2)    # some time is needed to propagation
response = client.ledgers.get_twin_ledger_entry(twin=twin_uuid)
print(response['entries']['referring_key']['ref']['status'] == 'ok')

# delete entry
client.ledgers.delete_twin_ledger_entry(twin=twin_uuid, entries=['referring_key'])
response = client.ledgers.get_twin_ledger_entry(twin=twin_uuid)
print(response['entries'].get('referring_key') is None)

# delete all entries in a ledger:
client.ledgers.delete_twin_ledger_entry(twin=twin_uuid)
response = client.ledgers.get_twin_ledger_entry(twin=twin_uuid)
print(response['entries'] == {})
