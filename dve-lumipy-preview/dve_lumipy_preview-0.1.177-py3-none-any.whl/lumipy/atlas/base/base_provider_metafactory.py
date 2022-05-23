from abc import ABCMeta, abstractmethod
from typing import List, Callable
from inspect import Parameter, Signature

from lumipy.common.string_utils import handle_available_string, to_snake_case
from lumipy.atlas.base.base_provider_factory import BaseProviderFactory
from lumipy.query.expression.sql_value_type import lumi_data_type_to_py_type, SqlValType
from lumipy.query.expression.variable.table_variable import TableVariable
from lumipy.client import Client
from lumipy.atlas.field_metadata import FieldMetadata
from datetime import datetime


class BaseProviderMetafactory(ABCMeta):

    def __new__(
            mcs,
            table_name: str,
            description: str,
            provider_type: str,
            category: str,
            last_ping_at: datetime,
            documentation: str,
            fields: List[FieldMetadata],
            client: Client
    ):

        class_name = table_name.replace('.', '') + 'Factory'
        mcs._class_name = class_name

        class_attrs = {
            '_class_name': class_name,
            '_table_name': table_name,
            '_description': handle_available_string(description),
            '_provider_type': provider_type,
            '_category': category,
            '_last_ping_at': last_ping_at,
            '_documentation': handle_available_string(documentation),
            '_fields': fields,
            '_client': client,
            '__call__': mcs._create_call_fn(
                table_name, description, provider_type, category, last_ping_at, documentation, fields, client
            ),
            '__init__': mcs._create_init_fn(
                table_name, description, provider_type, category, last_ping_at, documentation, fields, client
            ),
            '__doc__': ""  # Set to empty so it's not in the tooltips
        }

        return super().__new__(mcs, class_name, (BaseProviderFactory,), class_attrs)

    def __init__(cls, *args, **kwargs):
        super().__init__(cls._class_name, (BaseProviderFactory,), {})

    @classmethod
    def _create_init_fn(mcs, table_name, description, provider_type, category, last_ping_at, documentation, fields, client) -> Callable:
        """Function that creates an overload method for a provider metadata subclass.
        The new method simply gives the values given to the metaclass ctor to the super().__init__.
        This is to prevent the base class docstring from showing up in the jupyter tooltips.

        Returns:
            Callable: the new constructor.
        """
        def __init__(self):
            # noinspection PyArgumentList
            super(type(self), self).__init__(
                table_name,
                description,
                provider_type,
                category,
                last_ping_at,
                documentation,
                fields,
                client
            )

        __init__.__doc__ = ''  # Set to empty so it's not in the tooltips
        return __init__

    @staticmethod
    def _generate_call_signature(pmeta: List[FieldMetadata], return_type: type, add_with_vars=False, add_limit=False):
        params = [Parameter('self', Parameter.POSITIONAL_OR_KEYWORD)]

        def create_fn_param(x):
            if x.data_type in lumi_data_type_to_py_type.keys():
                cls = lumi_data_type_to_py_type[x.data_type]
                return Parameter(x.name, Parameter.POSITIONAL_OR_KEYWORD, annotation=cls)
            elif x.data_type == SqlValType.Table:
                return Parameter(x.name, Parameter.POSITIONAL_OR_KEYWORD, annotation=TableVariable)
            else:
                return Parameter(x.name, Parameter.POSITIONAL_OR_KEYWORD)

        params += [create_fn_param(p) for p in pmeta]
        if add_limit:
            params.append(Parameter('apply_limit', Parameter.POSITIONAL_OR_KEYWORD, annotation=int))
        if add_with_vars:
            params.append(Parameter('with_vars', Parameter.VAR_POSITIONAL))

        return Signature(params, return_annotation=return_type)

    @staticmethod
    def _generate_call_docstring(
            pmeta: List[FieldMetadata], signature: Signature, table_name, description, documentation
    ):

        return_type = signature.return_annotation
        type_name = return_type.__name__
        type_descr = to_snake_case(type_name).replace('_', ' ')
        params = [p for p in signature.parameters.values() if p.name != 'self']
        ps = {p.name: p for p in pmeta}

        def arg_line(x):
            if x.name == 'with_vars':
                return ''
            if x.name == 'apply_limit':
                return f"    apply_limit (int): limit to apply to the direct provider call"

            return f"    {x.name} ({x.annotation.__name__}): {handle_available_string(ps[x.name].description)}"

        doc = f'Create a {type_name} instance for the {table_name} provider.\n\n'
        doc += f"Provider Description:\n    {description}\n\n"
        doc += f"Provider Documentation:\n    {documentation}\n\n"
        if len(params) > 0:
            doc += f"Args: \n"
            doc += '\n'.join(map(arg_line, params))
        doc += '\n\n'
        doc += f'Returns:\n'
        doc += f'    {type_name}: the {type_descr} instance for the {table_name} '
        doc += 'provider with the given parameter values.'

        return doc

    @classmethod
    @abstractmethod
    def _create_call_fn(
            mcs, table_name, description, provider_type, category, last_ping_at, documentation, fields, client
    ) -> Callable:
        raise NotImplementedError()
