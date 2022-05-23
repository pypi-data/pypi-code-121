# acceptance_test_example

import os
import sys

#testdir = os.path.dirname(__file__)
#testdir = os.path.realpath(__file__)
testdir = os.getcwd()
srcdir = '../..'
src_path =  os.path.abspath(os.path.join(testdir, srcdir))
sys.path.insert(0, os.path.abspath(src_path))

import unittest

from behave import *

import time

@given('we have behave installed')
def step_impl(context):
    pass

@when('we implement a test')
def step_impl(context):
    assert True is not False

@then('behave will test it for us!')
def step_impl(context):
    assert context.failed is False


# ----------------------
@given('a set up')
def step_impl(context):
    pass

@when('we run the test')
def step_impl(context):
    time.sleep(2)

@then('it will eventually pass')
def step_impl(context):
    pass

@when('we run the current test')
def step_impl(context):
    pass

@then('it will pass')
def step_impl(context):
    pass

# ---------------------
@given('a starting point two')
def step_impl(context):
    pass

@given('a starting point three')
def step_impl(context):
    pass

@when('we multiply by three')
def step_impl(context):
    time.sleep(2)

@when('we multiply by two')
def step_impl(context):
    time.sleep(2)

@then('the product will be six')
def step_impl(context):
    pass

# ----------------------------------

@given('a lot of data')
def step_impl(context):
     context.s = context.text

@when('we add more data')
def step_impl(context):
    context.s += context.text

@then('we have even more data')
def step_impl(context):
     assert (context.s == context.text)


# ----------------------------------

@given('a table')
def step_impl(context):
    context.t = context.table

@when('we calculate the total value')
def step_impl(context):
    context.total_value = 0
    for row in context.t:
        fruit, value, items = row
        context.total_value += int(value) * int(items)

@when('we calculate the total items')
def step_impl(context):
    context.total_items = 0
    for row in context.t:
        fruit, value, items = row
        context.total_items += int(items)

@then('we get the totals')
def step_impl(context):
    expected_results = context.table

    expected_totals = {}
    for total, value in expected_results:
       expected_totals[total] = int(value)

    # generally a bad idea to test 2 things in one test
    assert (context.total_value == expected_totals['value'] )
    assert (context.total_items == expected_totals['items'] )


# ------------------------------
@given('a value "{v}"')
def step_impl(context, v):
    context.v = int(v)

@when('squared')
def step_impl(context):
    context.r = context.v * context.v

@then ('the result is "{r}"' )
def step_impl(context, r):
    r = int(r)
    assert( context.r == r)
