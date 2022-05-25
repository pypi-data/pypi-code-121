# -*- coding: utf-8 -*-

from marshmallow import fields, ValidationError

from docparser.config.excel.enums import BlockType


class CustomFields:
    """
    自定义字段类型
    """

    class BlockTypeField(fields.Field):
        """
        块类型枚举字段
        """

        def _serialize(self, value, attr, obj, **kwargs):
            try:
                if value is None:
                    return BlockType.text.name
                return value.name

            except ValueError as error:
                raise ValidationError("指定的类型值不在[text,table]范围内!") from error

        def _deserialize(self, value, attr, data, **kwargs):
            try:
                return BlockType[value]
            except ValueError as error:
                raise ValidationError("指定的类型值不在[0-1]范围内!") from error

    class TableModeField(fields.Field):
        """
        表格模式
        """

        def _serialize(self, value, attr, obj, **kwargs):
            if value is None:
                return TableMode.standard.name
            return value.name

        def _deserialize(self, value, attr, data, **kwargs):
            try:
                return TableMode[value]
            except ValueError as error:
                raise ValidationError("指定的类型值不在[standard,promiscuous,custom]范围内!") from error

    class HorizontalAlignModeField(fields.Field):
        """
        水平对齐方式
        """

        def _serialize(self, value, attr, obj, **kwargs):
            if value is None:
                return HorizontalAlignMode.right.name
            return value.name

        def _deserialize(self, value, attr, data, **kwargs):
            try:
                return HorizontalAlignMode[value]
            except ValueError as error:
                raise ValidationError("指定的类型值不在[left,center,right]范围内!") from error

    class VerticalAlignModeField(fields.Field):
        """
        水平对齐方式
        """

        def _serialize(self, value, attr, obj, **kwargs):
            if value is None:
                return VerticalAlignMode.middle.name
            return value.name

        def _deserialize(self, value, attr, data, **kwargs):
            try:
                return VerticalAlignMode[value]
            except ValueError as error:
                raise ValidationError("指定的类型值不在[top,middle,bottom]范围内!") from error

    class AnalyticalModeField(fields.Field):
        """
        解析模式枚举字段
        """

        def _serialize(self, value, attr, obj, **kwargs):
            try:
                if value is None:
                    return enums.AnalyticalMode.key_value
                return value.name
            except ValueError as error:
                raise ValidationError("<value:%s 指定的类型值不在[key_value,table]范围内.>" % value) from error

        def _deserialize(self, value, attr, data, **kwargs, ):
            try:
                return enums.AnalyticalMode[value]
            except ValueError as error:
                raise ValidationError("<value:%s 指定的类型值不在[key_value,table]范围内.>" % value) from error

    class FindModeField(fields.Field):
        """
        查找模式枚举字段
        """

        def _serialize(self, value, attr, obj, **kwargs):
            try:
                if value is None:
                    return enums.FindMode.default
                return value.name
            except ValueError as error:
                raise ValidationError("<value:[%s] 指定的类型值不在[default,vertical,horizontal]范围内.>" % value) from error

        def _deserialize(self, value, attr, data, **kwargs, ):
            try:
                return enums.FindMode[value]
            except ValueError as error:
                raise ValidationError("<value:[%s] 指定的类型值不在[default,vertical,horizontal]范围内.>" % value) from error

    class SeparatorModeField(fields.Field):
        """
        分割模式枚举字段
        """

        def _serialize(self, value, attr, obj, **kwargs):
            try:
                if value is None:
                    return enums.SeparatorMode.split
                return value.name
            except ValueError as error:
                raise ValidationError("<value:[%s] 指定的类型值不在[split,regex]范围内.>" % value) from error

        def _deserialize(self, value, attr, data, **kwargs, ):
            try:
                return enums.SeparatorMode[value]
            except ValueError as error:
                raise ValidationError("<value:[%s] 指定的类型值不在[split,regex]范围内.>" % value) from error

    class OverActionField(fields.Field):
        """
        匹配成功后的行为模式枚举字段
        """

        def _serialize(self, value, attr, obj, **kwargs):
            try:
                if value is None:
                    return enums.OverAction.default
                return value.name
            except ValueError as error:
                raise ValidationError("<value:[%s] 指定的类型值不在[default,skip,end]范围内.>" % value) from error

        def _deserialize(self, value, attr, data, **kwargs, ):
            try:
                return enums.OverAction[value]
            except ValueError as error:
                raise ValidationError("<value:[%s] 指定的类型值不在[default,skip,end]范围内.>" % value) from error

    class ActionTypeField(fields.Field):
        """
        赋值模式枚举字段
        """

        def _serialize(self, value, attr, obj, **kwargs):
            try:
                if value is None:
                    return enums.ActionType.add
                return value.name
            except ValueError as error:
                raise ValidationError("<value:[%s] 指定的类型值不在[default,append,cut,split]范围内.>" % value) from error

        def _deserialize(self, value, attr, data, **kwargs, ):
            try:
                return enums.ActionType[value]
            except ValueError as error:
                raise ValidationError("<value:[%s] 指定的类型值不在[default,append,cut,split]范围内.>" % value) from error

    class ActionKeyField(fields.Field):
        """
        数值型或者字符串型
        """

        def _serialize(self, value, attr, obj, **kwargs):
            try:
                if isinstance(value.name, int) or isinstance(value.name, str):
                    return value
                else:
                    raise ValidationError
            except ValueError as error:
                raise ValidationError("<value:[%s] 指定的类型值不在[int,str]范围内.>" % value) from error

        def _deserialize(self, value, attr, data, **kwargs, ):
            try:
                if isinstance(value, int) or isinstance(value, str):
                    return value
                else:
                    raise ValidationError
            except ValueError as error:
                raise ValidationError("<value:[%s] 指定的类型值不在[default,skip,end]范围内.>" % value) from error
