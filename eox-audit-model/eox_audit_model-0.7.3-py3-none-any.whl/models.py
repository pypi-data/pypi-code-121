"""eox-audit-model models file.

Contain all the models and required functions.

Classes:
    AuditModel: Main model to execute audit actions.
    AuditNote: Complementary model which allows to relate text fields with an audit model.

Functions:
    get_current_domain: Return the domain for the current request.
    get_current_performer: Return the username for the current user.
"""
import inspect
import traceback
import uuid

from crum import get_current_request, get_current_user
from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from ipware import ip

from eox_audit_model.constants import Status
from eox_audit_model.context_managers import capture_logs
from eox_audit_model.exceptions import EoxAuditModelInvalidMethod, EoxAuditModelInvalidParameters
from eox_audit_model.tasks import create_audit_register  # pylint: disable=cyclic-import, useless-suppression


def get_current_site():
    """Allow to get the current site for the request.

    If there is no site, it will be create.

    Returns:
        Site: Django site model.
    """
    request = get_current_request()
    domain = request.META['HTTP_HOST'] if request else 'Missing domain.'
    site, _ = Site.objects.get_or_create(
        domain=domain,
    )

    return site.id


def get_current_ip():
    """Allow to get the current ip for the request.

    Returns:
        String: Current ip.
    """
    request = get_current_request()

    if not request:
        return 'Missing ip.'

    try:
        # Works with django-ipware lower than 3.0.0
        get_ip = getattr(ip, 'get_ip')

        return get_ip(request)
    except AttributeError:
        get_client_ip = getattr(ip, 'get_client_ip')

    return get_client_ip(request)[0]


def get_current_performer():
    """Allow to get the username for the current user.

    Returns:
        String: Current username.
    """
    user = get_current_user()

    return user.username if user else 'Missing user.'


class AuditModel(models.Model):
    """AuditModel.

    Attributes:
        action: The name of the action, which initializes the process, for example, api student update.
        audit_date_stamp: Creation date.
        input_parameters: String representation of the input values.
        capture_logs. logs generated in the execution.
        traceback_log: traceback if there is an exception.
        method_name: Audited method.
        output_parameters: String representation of the returned value.
        performer: Username of the user who is executing the current request.
        site_domain: Domain get from the current request.
        status: Success or fail. that depends on audited method.
        ip: Current ip.

    Methods:
        execute_action: Allow to audit the execution for the given method.
    """

    key = models.UUIDField(
        unique=True,
        editable=False,
        default=uuid.uuid4,
        verbose_name="Public identifier",
    )
    action = models.CharField(max_length=150)
    audit_date_stamp = models.DateTimeField(auto_now_add=True, editable=False)
    input_parameters = models.TextField(null=True, blank=True)
    captured_logs = models.TextField(null=True, blank=True)
    traceback_log = models.TextField(null=True, blank=True)
    method_name = models.CharField(max_length=150)
    output_parameters = models.TextField(null=True, blank=True)
    performer = models.CharField(max_length=150, default=get_current_performer)
    site = models.ForeignKey(Site, default=get_current_site, on_delete=models.SET_NULL, null=True)
    status = models.PositiveIntegerField(choices=Status.choices(), default=Status.SUCCESS)
    ip = models.CharField(max_length=150, default=get_current_ip)

    @classmethod
    def execute_action(cls, action, method, parameters, notes=None):
        """Execute the given a method and create an entry log for the process.

        Example:
            AuditModel.execute_action(
                action='Add en view info',
                method=add,
                parameters={
                    'args': (arg1, arg2), # Positional arguments
                    'kwargs': {'a': 5, 'b': 0}, # keyword arguments.
                },
                notes=[
                        {
                            'title': 'Test notes',
                            'description': 'this is a field designed to store custom information',
                        },
                    ]
            )

        Args:
            action: The name of the action to identify the process.
            method: The method, which will be executed.
            parameters: The method parameters.
            notes: some extra notes, that must have the following structure.

                notes = [
                    {
                        'title': 'This is called in a tests environment',
                        'Description': 'Ignore this error message since....',
                    },
                    {
                        'title': 'Another note',
                        'Description': 'Another description....',
                    },
                    ...
                ]

        Returns:
            The same parameters that the method returns.
        """
        if not (inspect.isfunction(method) or inspect.ismethod(method)):
            raise EoxAuditModelInvalidMethod('Method is not callable.')

        if not isinstance(parameters, dict):
            raise EoxAuditModelInvalidParameters('Parameters must be a dict instance.')

        result = {}
        status = Status.SUCCESS
        args = parameters.get('args', ())
        kwargs = parameters.get('kwargs', {})

        try:
            with capture_logs() as logs:
                result = method(*args, **kwargs)

            return result
        except Exception as error:
            status = Status.FAIL
            raise error
        finally:
            if getattr(settings, 'ALLOW_EOX_AUDIT_MODEL', True):
                create_audit_register.delay(
                    action=action,
                    status=status,
                    method_name=getattr(method, '__name__', 'Missing method name'),
                    captured_logs='\n'.join(logs.formatted_records),
                    traceback_log=traceback.format_exc(),
                    input_parameters=parameters,
                    output_parameters=result.__repr__(),
                    site_id=get_current_site(),
                    performer=get_current_performer(),
                    ip=get_current_ip(),
                    notes=notes,
                )


class AuditNote(models.Model):
    """AuditNote model.

    This model allows to store custom information related
    with an AuditModel procedure.

    Attributes:
        audit_register: ForeignKey for Audit model.
        title: CharField note title.
        created: DateTimeField for the creation date.
        description: TextField note content.
    """

    audit_register = models.ForeignKey(AuditModel, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now=True)
    description = models.TextField(max_length=500, blank=True)
