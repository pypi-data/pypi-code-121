# acceptance_test_mh

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
import mh


# we put is required starting state
@given('we have installed mh')
def step_impl(context):
    import mh

# an action is taken
@when('we get the version')
def step_impl(context):
    context.version = mh.__version__

# the result is correct
@then('we have a version')
def step_impl(context):
    assert type(context.version) is type('')

# -----------------------------------------
@when('we get a mh variable')
def step_impl(context):
    context.v = mh.EG_VAR2

@then('we get the correct value')
def step_impl(context):
    assert (context.v == 'ABCD')

# -----------------------------------------
@when('we call a mh function')
def step_impl(context):
    context.r = mh.testFunction()

@then('we get the correct return')
def step_impl(context):
    assert (context.r == 'OK' )
# -----------------------------------------
@when('we create a mh object')
def step_impl(context):
    context.x = mh.Mh()


@then('we will have an mh object')
def step_impl(context):
    assert type(context.x) is type(mh.Mh())

# -----------------------------------------
@given('we have an mh object')
def step_impl(context):
    context.x = mh.Mh()

@when('we call a function')
def step_impl(context):
    context.y = context.x.runMh()

@then('we get the correct result')
def step_impl(context):
    assert ( context.y == 100 )


