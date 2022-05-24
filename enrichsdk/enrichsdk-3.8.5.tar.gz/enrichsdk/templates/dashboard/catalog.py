from enrichsdk.lib.customer import find_usecase

def get_spec():

    return {
        "name": "Catalog",
        "description": "Catalog",
        "usecase": find_usecase(__file__),
    }
