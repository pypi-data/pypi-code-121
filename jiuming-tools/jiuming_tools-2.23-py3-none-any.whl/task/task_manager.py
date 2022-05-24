import datetime
import time

import click

from src.config.peewee_config import MyTask


def create(name, content, level):
    t = MyTask(name=name, content=content, level=level, over=False, create_time=time.time(),
               update_time=time.time())
    t.save()
    click.echo("创建{}任务成功!".format(t.name))


def list(model, date, search):
    expressions = None
    if str(model).upper() == 'FALSE':
        expressions = (MyTask.over == False)
    elif str(model).upper() == 'TRUE':
        expressions = (MyTask.over == True)

    if date is not None:
        expressions = expressions & MyTask.create_time >= date

    if search is not None:
        search = '%{}%'.format(search)
        expressions = expressions & (MyTask.name ** search | MyTask.content ** search)

    t_list = MyTask.select().where(expressions)
    for t in t_list:
        s = """
id:{}
名称:{}
内容:{}
等级:{}  
是否完成:{}  
完成时间:{}    
创建时间:{}
修改时间:{}
        """.format(t.id, t.name, t.content, t.level, t.over, t.over_time, t.create_time, t.update_time)
        click.echo(s)


def select():
    f_task_list = MyTask.select().where(MyTask.over == False)
    i_id_map = {}
    for i, t in enumerate(f_task_list):
        i_id_map[str(i)] = t.id
        click.echo("{},id:{},name:{}".format(i, t.id, t.name))
    r = click.prompt(
        "选择任务编号:",
        type=click.Choice(i_id_map.keys()),
        show_default=False,
    )
    return i_id_map[r]


def select_over():
    over(select())


def over(id):
    MyTask.update({MyTask.over: True, MyTask.over_time: time.time()}).where(MyTask.id == id).execute()
    click.echo("{}任务已完成!".format(id))


def select_remove():
    remove(select())


def remove(id):
    MyTask.delete_by_id(id)
    click.echo("{}任务已删除!".format(id))
