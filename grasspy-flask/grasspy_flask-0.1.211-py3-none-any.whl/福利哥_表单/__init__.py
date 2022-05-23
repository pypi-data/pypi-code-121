从 汉化通用 导入 _反向注入
从 flask_wtf 导入 Form, FlaskForm
从 .csrf 导入 CSRF保护

# 利用猴子补丁增加对 '验证_<字段名>' 的处理
def __validate(self, extra_validators=None):
    """Validate the form by calling ``validate`` on each field.
    Returns ``True`` if validation passes.

    If the form defines a ``validate_<fieldname>`` method, it is
    appended as an extra validator for the field's ``validate``.

    :param extra_validators: A dict mapping field names to lists of
        extra validator methods to run. Extra validators run after
        validators passed when creating the field. If the form has
        ``validate_<fieldname>``, it is the last extra validator.
    """
    if extra_validators is not None:
        extra = extra_validators.copy()
    else:
        extra = {}

    for name in self._fields:
        inline = getattr(self.__class__, f"validate_{name}", None)
        if inline is not None:
            extra.setdefault(name, []).append(inline)
        inline_zw = getattr(self.__class__, f"验证_{name}", None)
        if inline_zw is not None:
            extra.setdefault(name, []).append(inline_zw)

    return super(Form, self).validate(extra)

Form.validate = __validate


类 〇表单(Form):
    """声明式表单基类"""

    # populate_obj
    # process

    套路 验证通过(分身, 额外验证器々=空):
        """调用每个字段的验证方法以验证表单.
        若验证通过则返回真.
        """
        返回 分身.validate(额外验证器々)

    @属性
    套路 数据(分身):
        返回 分身.data
    
    @属性
    套路 错误々(分身):
        返回 分身.errors

_反向注入(〇表单, Form)


类 〇福利哥表单(FlaskForm):
    
    套路 是提交(分身):
        返回 分身.is_submitted()

    套路 提交并验证通过(分身):
        """只有提交表单才会调用验证方法, 验证通过则返回真"""
        返回 分身.is_submitted() 且 分身.validate()

    套路 隐藏标签(分身, *字段々):
        """通过一次调用渲染表单的隐藏字段"""
        返回 分身.hidden_tag(*字段々)

_反向注入(〇福利哥表单, FlaskForm)