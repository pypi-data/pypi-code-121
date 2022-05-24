#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'help_ui.py'
__create_time__ = '2020/7/22 21:40'

from tkinter import filedialog, messagebox
from tkinter import *
from tkinter import ttk
from os.path import splitext
from yaml import full_load, FullLoader
import json
from sqlite3 import connect
from xiaobaiauto2.utils.xiaobaiauto2db import DB
from xiaobaiauto2.config.config import CASE_TYPE

_case_config = CASE_TYPE()
filetypes = _case_config.filepytes

class HELP_UI:
    def read_case_file(self):
        fr = filedialog.askopenfile(filetypes=filetypes)
        try:
            if fr is not None and splitext(fr.name)[1] in ['.txt', '.csv']:
                all_data = fr.buffer.readlines()
                for c in all_data:
                    _c = c.decode('utf-8').split(_case_config.caseSeparator)
                    self.newrow(_c[0], _c[1], _c[2], _c[3], _c[4])
            elif fr is not None and splitext(fr.name)[1] in ['.json', '.yaml']:
                all_data = fr.buffer.read().decode('utf-8')
                if splitext(fr.name)[1] == '.json':
                    case_data = list(json.loads(all_data).get('cases'))
                else:
                    case_data = full_load(open(fr.name, 'r', encoding='utf-8')).get('cases')
                for c in case_data:
                    try:
                        self.newrow(c[0], c[1], c[2], c[3], c[4])
                    except IndexError as e:
                        messagebox.showerror('错误', e)
        except UnicodeError as e:
            messagebox.showerror('错误', e)

    def save_case_file(self):
        if messagebox.askyesno('温馨提示：', '您是否保存数据？若不保存只导出模板文件'):
            fw = filedialog.asksaveasfile(filetypes=filetypes)
            if fw is not None:
                fwdata = open(fw.name, 'w', encoding='utf-8')
                if splitext(fw.name)[1] in ['.txt', '.csv']:
                    for i in range(self.cmd.__len__()):
                        fwdata.write("\r\n" + str(self.cmd[i]).replace('\r\n', '').replace('\n', '') + _case_config.caseSeparator +
                                     str(self.loc[i]).replace('\r\n', '').replace('\n', '') + _case_config.caseSeparator +
                                     str(self.data[i]).replace('\r\n', '').replace('\n', '') + _case_config.caseSeparator +
                                     str(self.contains_assert[i]).replace('\r\n', '').replace('\n', '') + _case_config.caseSeparator +
                                     str(self.equal_assert[i]).replace('\r\n', '').replace('\n', '') + _case_config.caseSeparator)
                elif splitext(fw.name)[1] in ['.yaml']:
                    _header = '---\r\ncases:\r\n'
                    _body = ''
                    _foot = '\n}'
                    for i in range(self.cmd.__len__()):
                        _body += f'''\r\n\t\t[
                            \r\t\t\t"%s"
                        ]''' % str(self.cmd[i]).replace(r'\r\n', '').replace(r'\n', '')
                        fwdata.write(_header + _body + _foot)
                fwdata.close()
        else:
            filedialog.asksaveasfilename(filetypes=filetypes)

    def treeview_sort_column(self, tv, col, reverse):  # Treeview、列名、排列方式
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
        l.sort(reverse=reverse)  # 排序方式
        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):  # 根据排序后索引移动
            tv.move(k, '', index)
        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))  # 重写标题，使之成为再点倒序的标题

    def set_cell_value(self, event):  # 双击进入编辑状态
        for item in self.data_treeview.selection():
            item_text = self.data_treeview.item(item, "values")
        column = self.data_treeview.identify_column(event.x)  # 列
        row = self.data_treeview.identify_row(event.y)  # 行
        cn = int(str(column).replace('#', ''))
        if row != '':
            rn = int(str(row).replace('I', ''))
            entryedit = Text(self.f_edit, width=int(self.columns_width[cn-1]/10), height=1)#  + (cn - 1) * 16, height=1)
            entryedit.place(x=16 + (cn - 1) * self.columns_width[cn-1], y=6 + rn * 20)
            treeview = self.data_treeview
            def saveedit():
                if entryedit.get(0.0, "end") != '\n':
                    treeview.set(item, column=column, value=entryedit.get(0.0, "end"))
                entryedit.destroy()
                okb.destroy()
            okb = ttk.Button(self.f_edit, text='OK', width=4, command=saveedit)
            okb.place(x=90 + (cn - 1) * self.columns_width[cn-1], y=2 + rn * 20)
        else:
            messagebox.showerror('错误', '还没有数据别点了！')

    def newrow(self, cmd='指令', loc='定位', data='数据', ccontains_assert='包含断言', equal_assert='相等断言'):
        self.cmd.append(cmd)
        self.loc.append(loc)
        self.data.append(data)
        self.contains_assert.append(ccontains_assert)
        self.equal_assert.append(equal_assert)
        self.data_treeview.insert('',
                                  len(self.cmd) - 1,
                                  values=(
                                      self.cmd[len(self.cmd) - 1],
                                      self.loc[len(self.loc) - 1],
                                      self.data[len(self.data) - 1],
                                      self.contains_assert[len(self.contains_assert) - 1],
                                      self.equal_assert[len(self.equal_assert) - 1],
                                  ))
        self.data_treeview.update()
        self.newb.place(x=120, y=(len(self.cmd) - 1) * 20 + 45)
        self.newb.update()

    def edit_case_ui(self, master):
        f_body = Frame(master=master, width=600)
        f_tool = Frame(master=f_body, )
        self.f_edit = Frame(master=f_body, width=600)
        Button(master=f_tool, text='导入用例', command=self.read_case_file).pack(side=LEFT, fill=Y)
        Button(master=f_tool, text='导出用例', command=self.save_case_file).pack(side=RIGHT, fill=Y)
        f_tool.pack(side=TOP, fill=X)
        # 添加 tableview
        # columns = ("CMD", "LOC", "DATA", "CONTAINS_ASSERT", "EQUAL_ASSERT")
        columns = ("指令", "定位", "数据", "包含断言", "相等断言")
        self.columns_width = [100, 200, 150, 150, 150]
        self.cmd = []
        self.loc = []
        self.data = []
        self.contains_assert = []
        self.equal_assert = []
        self.data_treeview = ttk.Treeview(self.f_edit, height=26, show="headings", columns=columns)  # 表格
        self.data_treeview.column("指令", width=self.columns_width[0], anchor='center')  # 表示列,不显示
        self.data_treeview.column("定位", width=self.columns_width[1], anchor='center')  # 表示列,不显示
        self.data_treeview.column("数据", width=self.columns_width[2], anchor='center')  # 表示列,不显示
        self.data_treeview.column("包含断言", width=self.columns_width[3], anchor='center')  # 表示列,不显示
        self.data_treeview.column("相等断言", width=self.columns_width[4], anchor='center')  # 表示列,不显示
        self.data_treeview.heading("指令", text="指令")  # 显示表头
        self.data_treeview.heading("定位", text="定位")  # 显示表头
        self.data_treeview.heading("数据", text="数据")  # 显示表头
        self.data_treeview.heading("包含断言", text="包含断言")  # 显示表头
        self.data_treeview.heading("相等断言", text="相等断言")  # 显示表头
        self.data_treeview.pack(side=LEFT, fill=BOTH)
        self.data_treeview.bind('<Double-1>', self.set_cell_value)  # 双击左键进入编辑
        self.newb = ttk.Button(self.f_edit, text='新建用例', width=20, command=self.newrow)
        self.newb.place(x=120, y=(len(self.cmd)) * 20 + 45)
        for col in columns:  # 绑定函数，使表头可排序
            self.data_treeview.heading(
                col, text=col, command=lambda _col=col: self.treeview_sort_column(self.data_treeview, _col, False))
        self.f_edit.pack()# side=BOTTOM, fill=X)
        f_body.pack()

    def vent_ui(self, master):
        '''环境检查'''
        pass

    def db_view(self, master):
        '''数据配置'''
        db = DB()
        db.select('select * from keyword')
        f_body = Frame(master=master, width=600)
        f_tool = Frame(master=f_body, )
        self.f_edit = Frame(master=f_body, width=600)
        Button(master=f_tool, text='导入关键词', command=self.read_case_file).pack(side=LEFT, fill=Y)
        Button(master=f_tool, text='导出关键词', command=self.save_case_file).pack(side=RIGHT, fill=Y)
        f_tool.pack(side=TOP, fill=X)
        # 添加 tableview
        # columns = ("CMD", "LOC", "DATA", "CONTAINS_ASSERT", "EQUAL_ASSERT")
        columns = ("编号", "命令", "关键词", "测试类型", "元素命令", "设备命令", "代码", "创建时间", "是否删除")
        self.columns_width = [100, 200, 150, 150, 150]
        self.cmd = []
        self.loc = []
        self.data = []
        self.contains_assert = []
        self.equal_assert = []
        self.data_treeview = ttk.Treeview(self.f_edit, height=26, show="headings", columns=columns)  # 表格
        self.data_treeview.column("指令", width=self.columns_width[0], anchor='center')  # 表示列,不显示
        self.data_treeview.column("定位", width=self.columns_width[1], anchor='center')  # 表示列,不显示
        self.data_treeview.column("数据", width=self.columns_width[2], anchor='center')  # 表示列,不显示
        self.data_treeview.column("包含断言", width=self.columns_width[3], anchor='center')  # 表示列,不显示
        self.data_treeview.column("相等断言", width=self.columns_width[4], anchor='center')  # 表示列,不显示
        self.data_treeview.heading("指令", text="指令")  # 显示表头
        self.data_treeview.heading("定位", text="定位")  # 显示表头
        self.data_treeview.heading("数据", text="数据")  # 显示表头
        self.data_treeview.heading("包含断言", text="包含断言")  # 显示表头
        self.data_treeview.heading("相等断言", text="相等断言")  # 显示表头
        self.data_treeview.pack(side=LEFT, fill=BOTH)
        self.data_treeview.bind('<Double-1>', self.set_cell_value)  # 双击左键进入编辑
        self.newb = ttk.Button(self.f_edit, text='新建用例', width=20, command=self.newrow)
        self.newb.place(x=120, y=(len(self.cmd)) * 20 + 45)
        for col in columns:  # 绑定函数，使表头可排序
            self.data_treeview.heading(
                col, text=col, command=lambda _col=col: self.treeview_sort_column(self.data_treeview, _col, False))
        self.f_edit.pack()  # side=BOTTOM, fill=X)
        f_body.pack()