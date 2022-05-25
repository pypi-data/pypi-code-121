# -*- coding: utf-8 -*-
"""
@File        : department.py
@Author      : yu wen yang
@Time        : 2022/4/28 2:25 下午
@Description :
"""
from django.db import transaction

from departments.common.config import ServerErrorCode, BadRequestCode
from departments.utils.error_response import Resp
from departments.utils.department_funcs import (
    get_departments,
    get_sub_department,
    create_department,
    get_department_object,
    update_department,
    delete_department,
    add_department_user_map,
    get_department_user,
    delete_department_user_map,
    mv_show_order,
    get_all_chargers
)


class DepartmentViewSet(object):

    def __init__(self, organization_id: int):
        if not isinstance(organization_id, int):
            raise TypeError(f"organization_id is failed type ")
        self.organization_id = organization_id

    def retrieve(self, pk: int):
        return get_department_object(self.organization_id, pk)

    def list(self, type_: str, department_id: int = None, department_name: str = None):
        """
        获取部门列表.有两种方式. 1: 一次性获取; 2: 获取下一级部门.
        :param type_: 获取部门的方式, all: 一次性获取, sub: 获取下一级部门
        :param department_id: type_=sub时的部门id
        :param department_name: 部门名称(搜索用)
        :return:
        """
        if type_ == "all":
            return get_departments(self.organization_id, department_name)
        elif type_ == "sub":
            return get_sub_department(self.organization_id, department_id)
        else:
            return Resp(code=ServerErrorCode, msg="error", data="failed params")

    def create(self, data: dict):
        """
        创建部门
        :param data: {"name": "部门名称", "parent_id": "上一级部门id"}
        :return:
        """
        data["organization_id"] = self.organization_id
        return create_department(data)

    def update(self, pk: int, data: dict):
        data["organization_id"] = self.organization_id
        try:
            return update_department(pk, data)
        except Exception as err:
            return Resp(code=ServerErrorCode, msg="error", data=str(err))

    def delete(self, pk: int):
        return delete_department(self.organization_id, pk)

    @transaction.atomic
    def move_show_order(self, data: list):
        """
        移动顺序

        :param data: [{"id": 1, "show_order": 0}, {"id": 2, "show_order": 1}]
        :return:
        """
        if len(data) > 2:
            return Resp(code=BadRequestCode, msg="参数错误")
        return mv_show_order(self.organization_id, data)

    # def department_user_list(self, department_id: int, page: int = 1, size: int = 20):
    def department_user_list(self, department_id: int, page: int = 1, size: int = 20):
        """
        通过部门获取部门下的用户
        :param department_id: 部门id
        :param page: 页码
        :param size: 每页数量
        :return:
        """
        # return get_department_user(self.organization_id, department_id, page, size)
        return get_department_user(self.organization_id, department_id)

    def create_department_user(self, department_id: int, user_ids: list):
        """
        部门中添加用户
        :param department_id:
        :param user_ids:
        :return:
        """
        try:
            return add_department_user_map(self.organization_id, department_id, user_ids)
        except Exception as err:
            return Resp(code=BadRequestCode, msg="error", data=str(err))

    def delete_department_user(self, department_id: int, user_ids: list):
        """
        部门移除用户
        :param department_id:
        :param user_ids:
        :return:
        """
        return delete_department_user_map(self.organization_id, department_id, user_ids)

    def get_chargers(self):
        """
        获取部门负责人列表
        :return:
        """
        return get_all_chargers(self.organization_id)

