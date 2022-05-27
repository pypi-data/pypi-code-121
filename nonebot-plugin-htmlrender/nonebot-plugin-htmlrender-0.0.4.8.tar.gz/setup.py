# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['nonebot_plugin_htmlrender']

package_data = \
{'': ['*'], 'nonebot_plugin_htmlrender': ['templates/*', 'templates/katex/*']}

install_requires = \
['Pygments>=2.10.0,<3.0.0',
 'aiofiles>=0.8.0,<0.9.0',
 'jinja2>=3.0.3,<4.0.0',
 'markdown>=3.3.6,<4.0.0',
 'nonebot2>=2.0.0-beta.1,<3.0.0',
 'playwright>=1.17.2,<2.0.0',
 'pymdown-extensions>=9.1,<10.0',
 'python-markdown-math>=0.8,<0.9',
 'uvicorn>=0.17.6,<0.18.0']

setup_kwargs = {
    'name': 'nonebot-plugin-htmlrender',
    'version': '0.0.4.8',
    'description': '通过浏览器渲染图片',
    'long_description': '# nonebot-plugin-htmlrender\n\n- 通过浏览器渲染图片\n- 可通过查看`example`参考使用实例\n\n# ✨ 功能\n\n- 通过 html 和浏览器生成图片\n- 支持`纯文本` `markdown` 和 `jinja2` 模板输入\n- 通过 CSS 来控制样式\n\n# 使用\n\n参考[example/plugins/render/**init**.py](example/plugins/render/__init__.py)\n\n## markdown 转 图片\n\n- 使用 `GitHub-light` 样式\n- 支持绝大部分 md 语法\n- 代码高亮\n- latex 数学公式 （感谢@[MeetWq](https://github.com/MeetWq)）\n  - 使用 `$$...$$` 来输入独立公式\n  - 使用 `$...$` 来输入行内公式\n- 图片需要使用外部连接并使用`html`格式 否则文末会超出截图范围\n- 图片可使用 md 语法 路径可为 `绝对路径`(建议), 或 `相对于template_path` 的路径\n\n## 模板 转 图片\n\n- 使用 jinja2 模板引擎\n- 页面参数可自定义\n\n# 🌰 栗子\n\n[example.md](docs/example.md)\n\n## 文本转图片（同时文本里面可以包括 html 图片）\n\n![](docs/text2pic.png)\n\n## markdown 转图片（同时文本里面可以包括 html 图片）\n\n![](docs/md2pic.png)\n\n## 纯 html 转图片\n\n![](docs/html2pic.png)\n\n## jinja2 模板转图片\n\n![](docs/template2pic.png)\n\n# 特别感谢\n\n- [MeetWq](https://github.com/MeetWq) 提供数学公式支持代码和代码高亮\n\n# 常见疑难杂症\n\n## `playwright._impl._api_types.Error:` 初次运行时报错\n\n- 一般为缺少必要的运行环境，如中文字体等\n\n### Ubuntu 使用 `apt`\n\n- 参考[Dao-bot Dockerfile](https://github.com/kexue-z/Dao-bot/blob/a7b35d6877b24b2bbd72039195bd1b3afebb5cf6/Dockerfile#L12-L15)\n\n```sh\napt update && apt install -y locales locales-all fonts-noto libnss3-dev libxss1 libasound2 libxrandr2 libatk1.0-0 libgtk-3-0 libgbm-dev libxshmfence1\n```\n\n- 然后设置 ENV local\n\n```sh\nLANG zh_CN.UTF-8\nLANGUAGE zh_CN.UTF-8\nLC_ALL zh_CN.UTF-8\n```\n\n### CentOS 使用 `yum`\n\n- ~~小心 CentOS~~\n- 参考[CentOS Dockerfile](https://github.com/kumaraditya303/playwright-centos/blob/master/Dockerfile)\n- 添加中文字体库\n- ~~最佳解决办法~~\n  - 使用 Docker 然后用 Python 镜像 按照上面 Ubuntu 的写 `dockerfile`\n\n下面这个依赖运行一下 也许就可以用了\n\n```sh\ndnf install -y alsa-lib at-spi2-atk at-spi2-core atk cairo cups-libs dbus-libs expat flac-libs gdk-pixbuf2 glib2 glibc gtk3 libX11 libXcomposite libXdamage libXext libXfixes libXrandr libXtst libcanberra-gtk3 libdrm libgcc libstdc++ libxcb libxkbcommon libxshmfence libxslt mesa-libgbm nspr nss nss-util pango policycoreutils policycoreutils-python-utils zlib cairo-gobject centos-indexhtml dbus-glib fontconfig freetype gtk2 libXcursor libXi libXrender libXt liberation-fonts-common liberation-sans-fonts libffi mozilla-filesystem p11-kit-trust pipewire-libs harfbuzz-icu libglvnd-glx libglvnd-egl libnotify opus woff2 gstreamer1-plugins-base gstreamer1-plugins-bad-free openjpeg2 libwebp enchant libsecret hyphen libglvnd-gles\n```\n',
    'author': 'kexue',
    'author_email': 'xana278@foxmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7.3,<4.0.0',
}


setup(**setup_kwargs)
