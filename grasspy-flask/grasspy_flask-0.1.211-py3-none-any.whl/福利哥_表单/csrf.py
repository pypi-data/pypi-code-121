从 flask_wtf 导入 *
从 汉化通用 导入 _反向注入

类 CSRF保护(CSRFProtect):

    套路 初始化应用(分身, 应用):
        分身.init_app(应用)

    套路 保护(分身):
        返回 分身.protect()
    
    套路 豁免(分身, 视图):
        返回 分身.exempt(视图)

_反向注入(CSRF保护, CSRFProtect)
