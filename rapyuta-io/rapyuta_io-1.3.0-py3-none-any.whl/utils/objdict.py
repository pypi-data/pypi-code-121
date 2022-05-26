# encoding: utf-8

from __future__ import absolute_import
from rapyuta_io.utils.error import OperationNotAllowedError
import six


class ObjDict(dict):
    def __contains__(self, k):
        try:
            return hasattr(self, k) or dict.__contains__(self, k)
        except:  # Not tested: in which situations can this happen?
            return False

    # only called if k not found in normal places
    def __getattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            return object.__getattribute__(self, k)
        except AttributeError:
            try:
                return self[k]
            except KeyError:
                raise AttributeError(k)

    def __setattr__(self, k, v):
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                self[k] = v
            except OperationNotAllowedError:
                raise OperationNotAllowedError
            except:  # Not tested: in which situations can this happen?
                raise AttributeError(k)
        else:  # Not tested: in which situations can this happen?
            object.__setattr__(self, k, v)

    def __delattr__(self, k):
        try:
            # Throws exception if not in prototype chain
            object.__getattribute__(self, k)
        except AttributeError:
            try:
                del self[k]
            except KeyError:
                raise AttributeError(k)
            except OperationNotAllowedError:
                raise OperationNotAllowedError
        else:  # Not tested: in which situations can this happen?
            object.__delattr__(self, k)

    def to_dict(self):
        return to_dict(self)

    @staticmethod
    def from_dict(d):
        return to_objdict(d)


class ImmutableKeyDict(ObjDict):
    def __setitem__(self, key, value):
        if key not in self and not (key == 'device_id'):
            raise OperationNotAllowedError
        super(ObjDict, self).__setitem__(key, value)

    def __delitem__(self, key):
        raise OperationNotAllowedError


def to_objdict(x):
    if isinstance(x, dict):
        return ObjDict((k, to_objdict(v)) for k, v in six.iteritems(x))
    elif isinstance(x, (list, tuple)):
        return type(x)(to_objdict(v) for v in x)
    else:
        return x


def to_dict(x):
    if isinstance(x, dict):
        return dict((k, to_dict(v)) for k, v in six.iteritems(x))
    elif isinstance(x, (list, tuple)):
        return type(x)(to_dict(v) for v in x)
    else:
        return x
