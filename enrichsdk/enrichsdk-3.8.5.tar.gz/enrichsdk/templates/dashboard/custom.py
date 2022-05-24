from django.urls import reverse
from enrichsdk.lib.customer import find_usecase

spec = {
    'name': 'APPNAMEApp',
    'description': "Custom application",
    'usecase': find_usecase(__file__),    
}

def get_spec():
    return spec
