# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import sys

from contrast.extern.wrapt import CallableObjectProxy, register_post_import_hook

from contrast.agent.assess.policy.preshift import Preshift
from contrast.agent.assess.policy.analysis import _analyze
from contrast.agent.policy import patch_manager
from contrast.agent.policy.loader import Policy
from contrast.utils.decorators import fail_quietly
from contrast.utils.patch_utils import build_and_apply_patch


@fail_quietly("Failed to apply assess xpath-injection")
def apply_assess(location, self, retval, args, kwargs):
    policy = Policy()
    patch_policy = policy.policy_by_name.get(location)
    if patch_policy is None:
        return

    preshift = Preshift(self, args, kwargs)
    _analyze(patch_policy, preshift, self, retval, (self,) + args, kwargs)


def apply_call(class_name, orig_func, self, args, kwargs):
    result = None
    try:
        result = orig_func(*args, **kwargs)
    finally:
        location = f"lxml.etree.{class_name}.__call__"
        apply_assess(location, self, result, args, kwargs)
    return result


class ContrastXPathEvaluatorProxy(CallableObjectProxy):
    """
    Proxy class that wraps instances returned by XPathEvaluator factory

    We instrument the relevant classes directly, but since the factory is implemented
    as a C extension, the instances that it returns are the original type instead of
    our replacement. In order to cover all of our bases, we need both the replacement
    subclass and a proxied class that we return from the instrumented factory.
    """

    def __call__(__cs_self, *args, **kwargs):
        self_obj = __cs_self.__wrapped__
        orig_func = __cs_self.__wrapped__.__call__
        return apply_call(
            self_obj.__class__.__name__, orig_func, self_obj, args, kwargs
        )


def create_instrumented_xpath_element_evaluator(XPathElementEvaluator):
    """
    Generate instrumented subclass of XPathElementEvaluator

    We can't simply declare this at module level since we can't guarantee that lxml
    will be installed. We need to wait until the import hook is fired to know whether
    it's safe to make a reference to the original type.
    """

    class ContrastXPathElementEvaluator(XPathElementEvaluator):
        def __call__(__cs_self, *args, **kwargs):
            orig_func = super().__call__
            return apply_call(
                XPathElementEvaluator.__name__, orig_func, __cs_self, args, kwargs
            )

    return ContrastXPathElementEvaluator


def create_instrumented_xpath_document_evaluator(x_path_document_evaluator):
    """
    Generate instrumented subclass of XPathDocumentEvaluator

    See docstring for create_instrumented_xpath_element_evaluator above.
    """

    class ContrastXPathDocumentEvaluator(x_path_document_evaluator):
        def __call__(__cs_self, *args, **kwargs):
            orig_func = super().__call__
            return apply_call(
                x_path_document_evaluator.__name__, orig_func, __cs_self, args, kwargs
            )

    return ContrastXPathDocumentEvaluator


def create_instrumented_xpath(x_path):
    """
    Generate instrumented subclass of XPath

    We can't simply declare this at module level since we can't guarantee that lxml
    will be installed. We need to wait until the import hook is fired to know whether
    it's safe to make a reference to the original type.
    """

    class ContrastXPath(x_path):
        def __init__(__cs_self, *args, **kwargs):
            try:
                super().__init__(*args, **kwargs)
            finally:
                apply_assess("lxml.etree.XPath.__init__", __cs_self, None, args, kwargs)

    return ContrastXPath


def build_x_path_eval_patch(orig_func, _):
    def x_path_evaluator(*args, **kwargs):
        """
        Instrumented version of XPathEvaluator factory
        """
        evaluator = orig_func(*args, **kwargs)
        return ContrastXPathEvaluatorProxy(evaluator)

    return x_path_evaluator


def patch_etree(etree_module):
    build_and_apply_patch(etree_module, "XPathEvaluator", build_x_path_eval_patch)

    new_xpath = create_instrumented_xpath(etree_module.XPath)
    patch_manager.patch(etree_module, "XPath", new_xpath)

    new_element_evaluator = create_instrumented_xpath_element_evaluator(
        etree_module.XPathElementEvaluator
    )
    patch_manager.patch(etree_module, "XPathElementEvaluator", new_element_evaluator)

    new_document_evaluator = create_instrumented_xpath_document_evaluator(
        etree_module.XPathDocumentEvaluator
    )
    patch_manager.patch(etree_module, "XPathDocumentEvaluator", new_document_evaluator)


def register_patches():
    register_post_import_hook(patch_etree, "lxml.etree")


def reverse_patches():
    module = sys.modules.get("lxml.etree")
    if not module:
        return

    patch_manager.reverse_patches_by_owner(module)
