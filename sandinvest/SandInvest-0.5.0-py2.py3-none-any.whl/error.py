#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author : SandQuant
# @Email: market@sandquant.com
# Copyright © 2020-present SandQuant Group. All Rights Reserved.

class LoginError(Exception):

    def __str__(self):
        return "- 缺少登录信息，请使用：`si.register('account', 'password')`\n" \
               "- Missing Login Information, Please use: `si.register('account', 'password')`."


class RegisterError(Exception):

    def __str__(self):
        return "- 登录信息已经注销。\n" \
               "- Login Information is already unregister."


class RegisterWrongError(Exception):

    def __str__(self):
        return "\n" \
               "- 登录信息出错，请使用`si.register('account', 'password')`方法重新注册。 \n" \
               "- Login Information Fail, Please use: `si.register('account', 'password')` again."


class RunOutError(Exception):

    def __str__(self):
        return "- 今日已超出使用额度。 \n" \
               "- Usage limit has been exceeded today."


class ClientError(Exception):

    def __str__(self):
        return "\n" \
               "- 客户端访问出错。 \n" \
               "- Client access error."
