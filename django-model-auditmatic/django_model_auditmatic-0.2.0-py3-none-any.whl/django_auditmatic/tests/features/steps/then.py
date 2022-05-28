"""
then steps
"""
from django.contrib.auth.models import User

from behave import then, use_step_matcher  # pylint: disable=E0611

from django_auditmatic.permission import get_audit_permission

use_step_matcher("parse")


@then("the statement generated should contain the audit name")
def generated_statement_contains_audit_name(context):
    """
    :type context: behave.runner.Context
    """
    context.test.assertTrue(context.audit_name in context.statement_generated)


@then("the statement generated should contain the table name")
def generated_statement_contains_table_name(context):
    """
    :type context: behave.runner.Context
    """
    context.test.assertTrue(context.audit_name in context.statement_generated)


@then("the statement generated should contain hstore")
def generated_statement_contains_hstore(context):
    """
    :type context: behave.runner.Context
    """
    context.test.assertTrue("hstore" in context.statement_generated)


@then("result is True")
def result_is_true(context):
    """
    :type context: behave.runner.Context
    """
    assert context.result


@then("the user model has an audit permission")
def user_model_has_audit_permission(context):
    """
    :type context: behave.runner.Context
    """
    permission = get_audit_permission(User)
    assert permission is not None


@then("result is False")
def result_is_false(context):
    """
    :type context: behave.runner.Context
    """
    assert not bool(context.result)
