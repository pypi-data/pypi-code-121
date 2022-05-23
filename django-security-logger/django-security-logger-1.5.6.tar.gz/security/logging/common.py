import copy

from threading import local
from attrdict import AttrDict

from uuid import uuid4

from contextlib import ContextDecorator

from django.conf import settings as django_settings

from security.config import settings
from security.utils import get_object_triple


undefined = object()


class SecurityLogger(ContextDecorator, local):

    loggers = []
    logger_name = None
    store = True

    def __init__(self, id=None, parent_log=undefined, related_objects=None, slug=None, extra_data=None,
                 start=None, stop=None, error_message=None, time=None, release=None):
        self.id = id or (uuid4() if self.logger_name else None)
        self.parent = SecurityLogger.loggers[-1] if SecurityLogger.loggers else None

        self.related_objects = set()
        if related_objects:
            self.add_related_objects(*related_objects)

        self.start = start
        self.stop = stop
        self.error_message = error_message
        self.release = release or settings.RELEASE

        self.slug = slug
        if self.parent:
            self.related_objects |= self.parent.related_objects
            if not self.slug:
                self.slug = self.parent.slug
        parent_with_id = self._get_parent_with_id()
        self.parent_log = (
            '{}|{}'.format(parent_with_id.logger_name, parent_with_id.id) if parent_with_id else None
        ) if parent_log is undefined else parent_log

        self._extra_data = extra_data
        if self._extra_data is None:
            self._extra_data = self.parent.extra_data if self.parent else {}

        if self.store:
            SecurityLogger.loggers.append(self)

            if 'reversion' in django_settings.INSTALLED_APPS:
                from reversion.signals import post_revision_commit

                post_revision_commit.connect(self._post_revision_commit, weak=False)
        self.backend_logs = AttrDict()
        self.stream = None

    def _get_parent_with_id(self):
        parent = self.parent
        while parent and not parent.id:
            parent = parent.parent
        return parent

    @property
    def time(self):
        return (self.stop - self.start).total_seconds() if self.start and self.stop else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.store:
            self.close()

    def set_slug(self, slug):
        self.slug = slug

    def add_related_objects(self, *related_objects):
        self.related_objects |= set(get_object_triple(obj) for obj in related_objects)

    @property
    def extra_data(self):
        return copy.deepcopy(self._extra_data)

    def update_extra_data(self, data):
        self._extra_data.update(data)

    def close(self):
        if not SecurityLogger.loggers or SecurityLogger.loggers[-1] != self:
            raise RuntimeError('Log already finished')

        SecurityLogger.loggers.pop()
        if 'reversion' in django_settings.INSTALLED_APPS:
            from reversion.signals import post_revision_commit

            post_revision_commit.disconnect(self._post_revision_commit)

    def _post_revision_commit(self, **kwargs):
        """
        Called as a post save of revision model of the reversion library.
        If log context manager is active input logged request, command
        log or celery task run log is joined with revision via related objects.
        """
        reversion_data = self._extra_data['reversion'] = self._extra_data.get('reversion', {
            'revisions': [],
            'total_count': 0
        })
        if reversion_data['total_count'] < settings.LOG_MAX_REVISIONS_COUNT:
            reversion_data['revisions'].append({
                'id': kwargs['revision_id'] if 'revision_id' in kwargs else kwargs['revision'].id
            })
        reversion_data['total_count'] += 1

    def to_dict(self):
        return dict(
            extra_data=self.extra_data,
            time=self.time,
            **{k: v for k, v in self.__dict__.items() if k not in {
                'backend_logs', 'stream', 'store', 'logger_name', 'loggers', 'parent'
            } and not k.startswith('_')}
        )


def get_last_logger(name):
    for logger in SecurityLogger.loggers[::-1]:
        if logger.logger_name == name:
            return logger
    return None
