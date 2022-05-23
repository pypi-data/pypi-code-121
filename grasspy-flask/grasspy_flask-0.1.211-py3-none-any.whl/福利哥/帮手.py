从 flask.helpers 导入 *

套路 构造url(端点, **值々):
    """依据给定的端点使用所提供的方法生成一个 URL.
    """
    如果 端点 == '静态':
        端点 = 'static'
        如果 '文件名' 在 值々:
            值々['filename'] = 值々.弹出('文件名')  # 改进这种汉化静态路由的方法？
    返回 url_for(端点, **值々)

套路 获取模板属性(模板名称, 属性名称):
    返回 get_template_attribute(模板名称, 属性名称)

套路 闪现(消息, 类别="消息"):
    flash(消息, 类别)

套路 获取闪现消息々(带类别=假, 类别过滤器=()):
    返回 get_flashed_messages(with_categories=带类别, category_filter=类别过滤器)

套路 带上下文的流(生成器或函数):
    返回 stream_with_context(生成器或函数)

套路 制作响应(*参数々):
    返回 make_response(*参数々)

套路 发送文件(
    路径或文件,
    mime类型=空,
    作为附件=假,
    下载名称=空,
    附件文件名=空,
    条件式=真,
    etag=真,
    添加etag=空,
    最后修改时间=空,
    最大年龄=空,
    缓存超时=空,
):
    返回 send_file(
        路径或文件,
        mimetype=mime类型,
        as_attachment=作为附件,
        download_name=下载名称,
        attachment_filename=附件文件名,
        conditional=条件式,
        etag=etag,
        add_etags=添加etag,
        last_modified=最后修改时间,
        max_age=最大年龄,
        cache_timeout=缓存超时,
    )

套路 从目录发送(目录, 路径, 文件名=空, **关键词参数々):
    返回 send_from_directory(目录, 路径, filename=文件名, **关键词参数々)