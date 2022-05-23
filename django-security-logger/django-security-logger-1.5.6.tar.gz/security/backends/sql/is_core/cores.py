from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _

from pyston.utils.decorators import filter_class, order_by

from is_core.utils.decorators import short_description

from is_core.main import DjangoUiRestCore
from is_core.generic_views.inlines.inline_table_views import DjangoInlineTableView

from security.backends.common.is_core import (
    LogCoreMixin, ChildLogTableViewMixin, InputRequestLogCoreMixin, OutputRequestLogCoreMixin,
    CommandLogCoreMixin, CeleryTaskInvocationLogInlineTableViewMixin, CeleryTaskRunLogInlineTableViewMixin,
    CeleryTaskRunLogCoreMixin, CeleryTaskInvocationLogCoreMixin, BaseRelatedLogsView, RelatedLogInlineTableViewMixin
)
from security.backends.sql.models import (
    CommandLog, InputRequestLog, OutputRequestLog, CeleryTaskInvocationLog, CeleryTaskRunLog, get_log_from_key,
    get_log_key
)

from .filters import UsernameUserFilter, RelatedObjectsFilter


class ChildLogTableView(ChildLogTableViewMixin, DjangoInlineTableView):

    def _get_log_key(self, log):
        return get_log_key(log)


class OutputRequestLogInlineTableView(ChildLogTableView):

    model = OutputRequestLog


class CommandLogInlineTableView(ChildLogTableView):

    model = CommandLog


class CeleryTaskInvocationLogInlineTableView(ChildLogTableView):

    model = CeleryTaskInvocationLog


class LogCore(LogCoreMixin, DjangoUiRestCore):

    abstract = True

    output_request_inline_table_view = OutputRequestLogInlineTableView
    command_inline_table_view = CommandLogInlineTableView
    celery_task_invocation_inline_table_view = CeleryTaskInvocationLogInlineTableView

    display_related_objects_filter = RelatedObjectsFilter

    def _get_parent_log_obj(self, obj):
        return get_log_from_key(obj.parent_log) if obj.parent_log else None

    def _get_related_objects(self, obj):
        related_object_instances = []
        for related_object in obj.related_objects.all():
            try:
                related_object_instances.append(related_object.object)
            except (ObjectDoesNotExist, AttributeError):
                pass
        return related_object_instances


class InputRequestLogCore(InputRequestLogCoreMixin, LogCore):

    abstract = True
    model = InputRequestLog

    @short_description(_('user'))
    @filter_class(UsernameUserFilter)
    @order_by('user_id')
    def user(self, obj):
        return obj.user


class OutputRequestLogCore(OutputRequestLogCoreMixin, LogCore):

    abstract = True
    model = OutputRequestLog


class CommandLogCore(CommandLogCoreMixin, LogCore):

    abstract = True
    model = CommandLog


class CeleryRunCeleryTaskInvocationLogInlineTableView(CeleryTaskInvocationLogInlineTableViewMixin,
                                                      DjangoInlineTableView):

    model = CeleryTaskInvocationLog


class CeleryTaskRunLogCore(CeleryTaskRunLogCoreMixin, LogCore):

    abstract = True
    model = CeleryTaskRunLog

    celery_task_invocation_inline_table_view = CeleryRunCeleryTaskInvocationLogInlineTableView


class CeleryTaskRunLogInlineTableView(CeleryTaskRunLogInlineTableViewMixin, DjangoInlineTableView):

    model = CeleryTaskRunLog


class CeleryTaskInvocationLogCore(CeleryTaskInvocationLogCoreMixin, LogCore):

    abstract = True
    model = CeleryTaskInvocationLog

    celery_task_run_inline_table_view = CeleryTaskRunLogInlineTableView


class RelatedInputRequestLogInlineTableView(RelatedLogInlineTableViewMixin, DjangoInlineTableView):

    model = InputRequestLog


class RelatedOutputRequestLogInlineTableView(RelatedLogInlineTableViewMixin, DjangoInlineTableView):

    model = OutputRequestLog


class RelatedCommandLogInlineTableView(RelatedLogInlineTableViewMixin, DjangoInlineTableView):

    model = CommandLog


class RelatedCeleryTaskInvocationLogInlineTableView(RelatedLogInlineTableViewMixin, DjangoInlineTableView):

    model = CeleryTaskInvocationLog


class RelatedCeleryTaskRunLogInlineTableView(RelatedLogInlineTableViewMixin, DjangoInlineTableView):

    model = CeleryTaskRunLog


class RelatedLogsView(BaseRelatedLogsView):

    input_request_inline_view = RelatedInputRequestLogInlineTableView
    output_request_inline_view = RelatedOutputRequestLogInlineTableView
    command_inline_view = RelatedCommandLogInlineTableView
    celery_task_run_inline_view = RelatedCeleryTaskInvocationLogInlineTableView
    celery_task_invocation_inline_view = RelatedCeleryTaskRunLogInlineTableView
