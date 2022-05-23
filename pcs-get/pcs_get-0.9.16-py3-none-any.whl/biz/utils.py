# -*- coding: utf-8 -*-
import os
import re

from .log import i


def detect_package():
    """
    检查当前目录的包名
    :rtype str
    """
    path = os.path.abspath(".")
    sep = os.path.sep
    if os.name == 'nt':
        pattern = r'.*\\src\\.*\\java\\(.*)'
    else:
        pattern = r'.*/src/.*/java/(.*)'
    r = re.match(pattern, path)
    if r and len(r.group(1)) > 0:
        return r.group(1).replace(sep, '.')
    return ""


def save_code_file(path, name, source, package, extension):
    """
    替换包名/格式化(TODO)/保存协议源码
    :type path str
    :type name str
    :type source str
    :type package str
    :type extension str
    """
    f_name = path + os.sep + name + "." + extension
    if extension == "kt":
        m = re.match(r'^package (.*?)\n', source)
        if m:
            curr_pkg = m.group(1)
            content = source.replace("package " + curr_pkg + "\n", "package " + package + "\n")
        else:
            content = source
    else:
        content = source.replace("MODIFY_HERE_TO_ADD_YOUR_PACKAGE_NAME", package)
    with open(f_name, 'w', encoding='UTF-8') as fp:
        fp.write(content)
    i(name + "." + extension + " up-to-date")


def detect_file_update_time(file_path):
    """
    读取本地源码文件的更新时间
    :type file_path str
    :rtype str
    """
    with open(file_path, 'r', encoding='UTF-8') as fp:
        p = r'.*update_time:(.*)\.'
        for line in fp.readlines():
            r = re.match(p, line.strip())
            if r and len(r.group(1)) > 0:
                return r.group(1)
    return ''


def detect_code_update_time(code):
    """
    读取源码中的更新时间
    :type code str
    :rtype str
    """
    p = r'.*update_time:(.*)\.'
    for line in code.splitlines():
        r = re.match(p, str(line).strip())
        if r and len(r.group(1)) > 0:
            return r.group(1)
    return ''


def get_file_extension(lang):
    """
    映射后台语言选项->本地源码文件扩展名
    :type lang str
    :rtype str
    """
    if lang == "kotlin":
        return "kt"
    return lang


def get_lang(extension):
    """
    映射本地源码文件扩展名->后台语言选项
    :type extension str
    :rtype str
    """
    if extension == "kt":
        return "kotlin"
    return extension


def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        pass
    return False


def encrypt(src):
    """
    简单加密字符串，避免明文存储
    :type src str
    :rtype str
    """
    output = ""
    for i in range(len(src)):
        char = src[i]
        if char.isalpha():
            if char.isupper():
                output = char.lower() + output
            elif char.islower():
                output = char.upper() + output
            else:
                output = char + output
        elif char.isdigit():
            num = (int(char) + 3) % 10
            output = str(num) + output
        else:
            output = char + output
    return output


def decrypt(src):
    """
    解密简单加密的字符串
    :type src str
    :rtype str
    """
    output = ""
    for i in range(len(src)):
        char = src[i]
        if char.isalpha():
            if char.isupper():
                output = char.lower() + output
            elif char.islower():
                output = char.upper() + output
            else:
                output = char + output
        elif char.isdigit():
            num = (int(char) - 3 + 10) % 10
            output = str(num) + output
        else:
            output = char + output
    return output
