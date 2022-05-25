# -*- coding: utf-8 -*-
"""
@File        : request_test.py
@Author      : yu wen yang
@Time        : 2022/5/10 1:23 下午
@Description :
"""
import json
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_simple_departments.settings')
django.setup()
if __name__ == '__main__':

    from departments.views.department import create_department, DepartmentViewSet


    def response(func):
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            print(json.loads(res.content))
        return wrapper

    # 创建部门
    @response
    def create_department_():
        post_data = {
            "name": "python",
            "parent_id": 2,
            "charger_id": None,
            "organization_id": 1
        }
        res = create_department(post_data)
        return res


    # obj = DepartmentViewSet(1)
    # print(obj.list("sub", 2))
    # print(obj.list("all"))
    # print(obj.list("all", department_name="o"))
    # print(obj.create({"name": "前端o99", "parent_id": 2}))
    # print(obj.retrieve(3))
    # print(obj.update(18, {"name": "前端99", "parent_id": 2, "charger_id": None}))
    # print(obj.delete(2))
    # print(obj.move_show_order([{"id": 5, "show_order": 5}, {"id": 7, "show_order": 4}]))
    # print(obj.create_department_user(5, [1, 2, 3]))
    # print(obj.department_user_list(5,))
    # print(obj.delete_department_user(5, [11]))
    # print(obj.get_chargers())



