# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from collections import OrderedDict

from contrast.agent.protect.rule.cmdi_rule import CmdInjection
from contrast.agent.protect.rule.deserialization_rule import Deserialization
from contrast.agent.protect.rule.http_method_tampering import MethodTampering
from contrast.agent.protect.rule.malformed_header import MalformedHeader
from contrast.agent.protect.rule.nosqli_rule import NoSqlInjection
from contrast.agent.protect.rule.path_traversal_rule import PathTraversal
from contrast.agent.protect.rule.sqli_rule import SqlInjection
from contrast.agent.protect.rule.ssrf_rule import Ssrf
from contrast.agent.protect.rule.unsafe_file_upload_rule import UnsafeFileUpload
from contrast.agent.protect.rule.xss_rule import Xss
from contrast.agent.protect.rule.xxe_rule import Xxe


def build_protect_rules():
    """
    Build a dict with rules with prefilter rules first.
    We want prefilter rules first so they get evaluated / trigger first.

    :return: an ordered dict of protect rules
    """
    rules = OrderedDict(
        {
            UnsafeFileUpload.RULE_NAME: UnsafeFileUpload(),
            CmdInjection.RULE_NAME: CmdInjection(),
            Deserialization.RULE_NAME: Deserialization(),
            # Turned off until TS can handle rule information
            MalformedHeader.RULE_NAME: MalformedHeader(),
            MethodTampering.RULE_NAME: MethodTampering(),
            NoSqlInjection.RULE_NAME: NoSqlInjection(),
            # Padding Oracle rule is currently disabled - CONTRAST-35352
            # PaddingOracle.RULE_NAME: PaddingOracle(),
            PathTraversal.RULE_NAME: PathTraversal(),
            SqlInjection.RULE_NAME: SqlInjection(),
            Ssrf.RULE_NAME: Ssrf(),
            Xss.RULE_NAME: Xss(),
            Xxe.RULE_NAME: Xxe(),
        }
    )

    return rules
