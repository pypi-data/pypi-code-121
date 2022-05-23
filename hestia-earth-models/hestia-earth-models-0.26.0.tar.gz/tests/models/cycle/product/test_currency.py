import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.product.currency import MODEL, MODEL_KEY, run, _should_run_product

class_path = f"hestia_earth.models.{MODEL}.product.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/product/{MODEL_KEY}"


def test_should_run_product():
    product = {'currency': 'USD', 'price': 100}
    should_run = _should_run_product(product)
    assert not should_run

    product = {'currency': 'EUR'}
    should_run = _should_run_product(product)
    assert not should_run

    product = {'currency': 'EUR', 'price': 100}
    should_run = _should_run_product(product)
    assert should_run is True


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


def test_run_unhandled_currency():
    with open(f"{fixtures_folder}/unhandled-currency/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/unhandled-currency/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
