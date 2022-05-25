from faker import Faker
from datetime import datetime, timedelta
import random

faker = Faker("es_CA")


def random_ref():
    return str(random.randint(0, 99999))


def subscription_request_create_data(odoo_env):
    return {
        'partner_id': 0,
        'already_cooperator': False,
        'is_company': False,
        'firstname': faker.first_name(),
        'lastname': faker.last_name(),
        'email': faker.email(),
        'ordered_parts': 1,
        "share_product_id": odoo_env.browse_ref(
            "easy_my_coop.product_template_share_type_2_demo"
        ).product_variant_id.id,
        'address': faker.street_address(),
        'city': faker.city(),
        'zip_code': faker.postcode(),
        'country_id': odoo_env.ref('base.es'),
        'date': datetime.now() - timedelta(days=12),
        'company_id': 1,
        'source': 'manual',
        'lang': random.choice(["es_ES", "ca_ES"]),
        'sponsor_id': False,
        'vat': faker.vat_id(),
        'discovery_channel_id': odoo_env.browse_ref(
            'somconnexio.other_cooperatives'
        ).id,
        'iban': faker.iban(),
        'state': 'draft',
    }


def partner_create_data(odoo_env):
    return {
        'parent_id': False,
        'name': faker.name(),
        'email': faker.email(),
        'street': faker.street_address(),
        'street2': faker.street_address(),
        'city': faker.city(),
        'zip_code': faker.postcode(),
        'country_id': odoo_env.ref('base.es'),
        'state_id': odoo_env.ref('base.state_es_b'),
        'customer': True,
        'ref': random_ref(),
        'lang': random.choice(["es_ES", "ca_ES"]),
    }
