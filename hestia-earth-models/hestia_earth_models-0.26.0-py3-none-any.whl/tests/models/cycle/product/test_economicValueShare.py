import json
from tests.utils import fixtures_path

from hestia_earth.models.cycle.product.economicValueShare import (
    MODEL, MODEL_KEY, run,
    _should_run_single_missing_evs, _should_run_default, _should_run_by_revenue
)

class_path = f"hestia_earth.models.{MODEL}.product.{MODEL_KEY}"
fixtures_folder = f"{fixtures_path}/{MODEL}/product/{MODEL_KEY}"


def test_should_run_single_missing_evs():
    cycle = {'dataCompleteness': {'products': True}}

    # if total value >= 100 => no run
    products = [{
        '@type': 'Product',
        'economicValueShare': 20
    }, {
        '@type': 'Product',
        'economicValueShare': 80
    }, {
        '@type': 'Product'
    }, {
        '@type': 'Product'
    }]
    assert not _should_run_single_missing_evs(cycle, products)

    # total < 100 => no run
    products[1]['economicValueShare'] = 70
    assert not _should_run_single_missing_evs(cycle, products)

    # with only 1 missing value => run
    del products[2]
    assert _should_run_single_missing_evs(cycle, products) is True


def test_should_run_by_revenue():
    cycle = {'dataCompleteness': {'products': True}}

    # if total value >= 100 => no run
    products = [{
        '@type': 'Product',
        'economicValueShare': 20
    }, {
        '@type': 'Product',
        'economicValueShare': 80
    }, {
        '@type': 'Product'
    }]
    assert not _should_run_by_revenue(cycle, products)

    # total < 100 => no run
    products[1]['economicValueShare'] = 70
    assert not _should_run_by_revenue(cycle, products)

    # all with revenue => run
    products[0]['revenue'] = 10
    products[1]['revenue'] = 10
    products[2]['revenue'] = 10
    assert _should_run_by_revenue(cycle, products) is True


def test_should_run_default():
    assert _should_run_default([{}]) is True


def test_run():
    with open(f"{fixtures_folder}/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


def test_run_complete_1_product_missing_evs():
    with open(f"{fixtures_folder}/complete-1-product-missing-evs/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/complete-1-product-missing-evs/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


def test_run_complete_all_revenue():
    with open(f"{fixtures_folder}/complete-all-revenue/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/complete-all-revenue/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


def test_run_complete_no_evs():
    with open(f"{fixtures_folder}/complete-no-evs/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/complete-no-evs/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


def test_run_incomplete_multiple_crops():
    with open(f"{fixtures_folder}/incomplete-multiple-crops/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/incomplete-multiple-crops/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


def test_run_incomplete_single_crop():
    with open(f"{fixtures_folder}/incomplete-single-crop/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/incomplete-single-crop/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected


def test_run_single_product():
    with open(f"{fixtures_folder}/single-product/cycle.jsonld", encoding='utf-8') as f:
        cycle = json.load(f)

    with open(f"{fixtures_folder}/single-product/result.jsonld", encoding='utf-8') as f:
        expected = json.load(f)

    value = run(cycle)
    assert value == expected
