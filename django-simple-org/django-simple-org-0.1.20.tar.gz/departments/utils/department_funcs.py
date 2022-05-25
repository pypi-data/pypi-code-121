# -*- coding: utf-8 -*-
"""
@File        : department_funcs.py
@Author      : yu wen yang
@Time        : 2022/5/13 10:12 上午
@Description :
"""
import math

from django.db.models import Max
from django.db import transaction

from departments.common.config import BadRequestCode, ServerErrorCode
from departments.models import Department, DepartmentUserMap
from departments.forms.forms import (
    DepartmentForms,
)
from departments.utils.error_response import Resp


def get_departments(organization_id: int, department_name: str = None) -> dict:
    """
    通过组织id获取全量部门
    :param organization_id:
    :param department_name:部门名称, 默认为空
    :return:
    """
    # 没有搜索的情况, 直接获取全部
    if not department_name:
        instance = Department.objects.filter(
            organization_id=organization_id,
            path__isnull=True,
            is_deleted=False
        )
        items = list()

        for i in instance:
            items.append(i.department_tree())

    # 有搜索的情况
    else:
        # 查询到包含搜索关键字的部门
        departments = Department.objects.filter(
            organization_id=organization_id,
            name__contains=department_name,
            is_deleted=False
        )
        items = list()
        # 循环每一个部门
        for instance in departments:
            lst = list()
            # 如果有父级的话, 查询到每一个父级部门的内容append到返回列表中
            if instance.path:
                for i in instance.path:
                    dic = {}
                    obj = Department.objects.filter(pk=i).only("name").first()
                    dic["id"] = obj.id
                    dic["name"] = obj.name
                    dic["show_order"] = obj.show_order
                    lst.append(dic)
            # 最后把部门本身的内容也append到返回列表中
            lst.append({
                "id": instance.id,
                "name": instance.name,
                "show_order": instance.show_order
            })
            items.append(lst)

    return Resp(data=items)


def get_sub_department(organization_id: int, department_id=None) -> dict:
    """
    通过部门id获取部门下的子部门, 默认获取所有的一级部门
    :param organization_id: 组织id
    :param department_id: 部门id
    :return:
    """

    if not department_id:
        department_instance = Department.objects.filter(
            organization_id=organization_id, is_deleted=False, path__isnull=True
        )
        department_items = []
        for department in department_instance:
            department_items.append({
                "id": department.id,
                "name": department.name,
                "charger_id": department.charger_id,
                "path": department.path,

            })
        return Resp(data=department_items)

    instance = Department.objects.get(
        pk=department_id,
        organization_id=organization_id,
        is_deleted=False
    )
    department_path = instance.path if instance.path else list()
    department_path.append(department_id)
    department = Department.objects.filter(
        organization_id=organization_id,
        is_deleted=False,
        path=department_path
    )
    return Resp(data=[{"id": i.id, "name": i.name, "charger_id": i.charger_id, "path": i.path} for i in department])


@transaction.atomic
def create_department(data: dict) -> dict:
    """
    新建部门
    :param data:
    :return:
    """

    """
    1. 校验需要创建企业的数据, 判断数据合法性
    2. 构建新建部门path(如果父级部门有path, 将父级部门id加入父级path中;如果父级部门没有path, 则path=父级部门)
    3. 找到数据表中最大的排序数, 将这个数字加1并且创建新的部门.
    """
    # 校验数据
    checked = DepartmentForms(data)
    # 判断数据合法性
    if not checked.is_valid():
        return Resp(code=ServerErrorCode, msg="error", data=checked.errors)
    # 构造path
    parent_id = data.pop("parent_id")
    parent = Department.objects.get(pk=parent_id)
    if parent.path:
        path = parent.path
        path.append(parent.id)
    else:
        path = [parent.id]
    # 找到最大排序数
    show_order = Department.objects.aggregate(num=Max('show_order'))["num"]
    data["show_order"] = show_order + 1
    data["path"] = path
    # 查询当前添加的部门同一级别是否有重复
    same_level_department = Department.objects.filter(
        name=data["name"],
        path=path,
        organization_id=data["organization_id"]
    ).exists()

    # 如果当前部门下有这个部门
    if same_level_department:
        return Resp(code=ServerErrorCode, msg="error", data=f"[{data['name']}]在当前部门下已存在, 请使用其他名称")

    department_instance = Department.objects.create(**data)
    return Resp(data={'id': department_instance.pk})


def get_department_object(organization_id: int, pk: int):
    """
    获取部门详情
    :param organization_id: 组织id
    :param pk: 部门id
    :return:
    """
    try:
        instance = Department.objects.get(pk=pk, organization_id=organization_id, is_deleted=False)
        return Resp(
            data={"id": instance.id, "name": instance.name, "path": instance.path, "charger_id": instance.charger_id}
        )
    except Department.DoesNotExist:
        return Resp(code=ServerErrorCode, msg="error", data=f"the department can't be found  id: {pk}")


@transaction.atomic
def update_department(pk: int, data: dict):
    """
    修改部门内容
    :param pk:
    :param data:
    :return:
    """
    checked = DepartmentForms(data)
    # 判断数据合法性
    if not checked.is_valid():
        return Resp(code=ServerErrorCode, msg="error", data=checked.errors)
    organization_id = data["organization_id"]
    try:
        instance = Department.objects.get(pk=pk, organization_id=organization_id, is_deleted=False)
        parent_id = data["parent_id"]
        self_path = instance.id

        # 查询当前部门的子级部门(path包含当前部门id的部门)
        son_departments = Department.objects.filter(
            path__contains=[self_path, ]
        ).values_list("id", flat=True)

        # 如果父部门选择了自己或者自己的子级部门抛出异常
        if int(parent_id) == self_path or int(parent_id) in list(son_departments):
            raise ValueError("该父部门不可选择")

        parent = Department.objects.get(organization_id=organization_id, pk=parent_id)
        if parent.path:
            path = parent.path
            path.append(parent.id)
        else:
            path = [parent.id]

        instance.path = path
        instance.name = data["name"]
        instance.charger_id = data["charger_id"]
        instance.save()
        return Resp(data="修改成功")
    except Exception as err:
        raise ValueError(f"{str(err)}  id: {pk}")


@transaction.atomic
def delete_department(organization_id: int, pk: int):
    """
    删除部门
    :param organization_id:
    :param pk:
    :return:
    """
    instance = Department.objects.filter(organization_id=organization_id, pk=pk).first()
    if instance.path:
        path = instance.path
    else:
        raise ValueError("一级部门不允许删除")
    path.append(instance.id)
    dic = {f"path__0_{len(path)}": path}
    departments = list(Department.objects.filter(**dic).values_list("id", flat=True))
    print(departments)
    departments.append(instance.id)
    if DepartmentUserMap.objects.filter(department_id__in=departments).exists():
        raise ValueError("当前部门或子部门下还有用户, 无法删除!")
    Department.objects.filter(id__in=departments).delete()
    return Resp(data="删除成功")


@transaction.atomic
def add_department_user_map(organization_id: int, department_id: int, user_ids: list):
    """
    添加部门-用户的映射关系
    :param organization_id:
    :param department_id:
    :param user_ids:
    :return:
    """
    if not Department.objects.filter(
            organization_id=organization_id, pk=department_id
    ).exists():
        return Resp(code=BadRequestCode, msg="error", data="当前组织没有该部门")

    department_user_list = [
        DepartmentUserMap(department_id=department_id, user_id=user) for user in user_ids
    ]
    try:
        DepartmentUserMap.objects.bulk_create(department_user_list)
    except Exception as err:
        raise Exception(err)
    return Resp(data="添加成功")


# def get_department_user(organization_id: int, department_id: int, page: int, size: int):
def get_department_user(organization_id: int, department_id: int):
    """
    通过部门获取用户
    :param organization_id: 组织id
    :param department_id: 部门id
    :param page: 页码
    :param size: 每页数量
    :return:
    """
    user_ids = DepartmentUserMap.objects.filter(
        department__organization_id=organization_id,
        department__is_deleted=False,
        department_id=department_id
    ).order_by("-id").values_list("user_id", flat=True)
    return Resp(data=list(user_ids))
    # total = user_ids.count()
    # max_page = math.ceil(total / size)
    # items = [
    #     item for item in user_ids.order_by("-id").values_list("user_id", flat=True)[(page-1)*size: page*size]
    # ] if page <= max_page else []
    #
    # return Resp(data={
    #     "total": total,
    #     "page_range": [i for i in range(1, max_page+1)],
    #     "current_page": page,
    #     "list": items
    # })


@transaction.atomic
def delete_department_user_map(organization_id: int, department_id: int, user_ids: list):
    """
    添加部门-用户的映射关系
    :param organization_id:
    :param department_id:
    :param user_ids:
    :return:
    """
    if not Department.objects.filter(
            organization_id=organization_id, pk=department_id
    ).exists():
        return Resp(code=BadRequestCode, msg="error", data="当前组织没有该部门")

    DepartmentUserMap.objects.filter(
        department__organization_id=organization_id,
        user_id__in=user_ids
    ).delete()

    return Resp(data="移除成功")


def mv_show_order(organization_id: int, data: dict):
    """
    修改部门show_order
    :param organization_id:  组织id
    :param data:  [{"id": 5, "show_order": 4}, {"id": 7, "show_order": 5}] --> [{"id": 5, "show_order": 5}, {"id": 7, "show_order": 4}]
    :return:
    """
    for item in data:
        Department.objects.filter(id=item["id"], organization_id=organization_id).update(show_order=item["show_order"])

    return Resp()
