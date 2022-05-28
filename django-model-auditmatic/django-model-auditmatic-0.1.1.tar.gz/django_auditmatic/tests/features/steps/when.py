"""
when steps
"""
from behave import use_step_matcher, when  # pylint: disable=E0611

from django_auditmatic.install.audit_permission import install_audit_permission
from django_auditmatic.utils.generate import (
    generate_function,
    generate_install_hstore,
    generate_table,
    generate_trigger,
)

use_step_matcher("parse")


@when("the function sql is generated")
def __generate_function_sql(context):
    """
    :type context: behave.runner.Context
    """
    context.statement_generated = generate_function(context.audit_name)


@when("the trigger sql is generated")
def __generate_trigger_sql(context):
    """
    :type context: behave.runner.Context
    """
    context.statement_generated = generate_trigger(
        context.audit_name, context.table_name, "UPDATE"
    )


@when("the table sql is generated")
def __generate_table_sql(context):
    """
    :type context: behave.runner.Context
    """
    context.statement_generated = generate_table(context.audit_name)


@when("the hstore sql is generated")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    context.statement_generated = generate_install_hstore()


@when("the permission validator is called with the user model")
def permission_validator_called_with_user(context):
    """
    :type context: behave.runner.Context
    """
    context.result = context.user.has_perm("auth.can_audit_user")


@when("the audit permission is installed")
def audit_permission_installed(context):
    """
    :type context: behave.runner.Context
    """
    install_audit_permission()
