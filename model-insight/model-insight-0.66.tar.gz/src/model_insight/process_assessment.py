# -*- coding: utf-8 -*-
"""
Created on April 13,  2022

@author: wang Haihua
"""

from importlib_metadata import entry_points
import time
import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
plt.rcParams.update({'font.family': 'SimHei', 'mathtext.fontset': 'stix'})

###########################################################################################
###############################     1 Record        ###############################
###########################################################################################

####***************************     1.1 Process Assessment       ****************************###



def process_assess(merge=False,file_name=''):
    """Record the performance of students based on class and homework

    Parameters
    ----------
    merge    : indicates whether the user wants to merge the current inputs to an existing file(.xlsx)
    file_name: if the user set the merge==True, the function will merge the current record in the file named file_name
        
    Yields
    ------
    A DataFrame object contain the records of students' performance value

    """    
    indicators = ['姓名','日期','课次', '活动主体', '活动类型', '活动内容', '数学内容', '数学', '模型内容', '模型', '编程内容', '编程',
              '写作内容', '写作', '合作', '分析内容', '分析总成就','分析(教师辅助)','建模内容', '建模总成就','建模(教师辅助)',
              '求解内容', '求解总成就','求解(教师辅助)', '解释内容','解释总成就','解释(教师辅助)', '验证内容', '验证总成就','验证(教师辅助)', 
              '汇报内容', '汇报总成就','汇报(教师辅助)']
    description = {'姓名':'请输入学生的 \U0001F466 \033[1m 姓名 \033[0m \U0001F467 \n',
               '日期':'请输入上课的 \U0001F4C6 日期 \U0001F4C6，格式为YY/MM/DD \n',
               '课次':'请输入上课的 \U0001F36D 课次 \U0001F36D，输入阿拉伯数字1-30 \n', 
               '活动主体':'请输入活动主体，1代表-学生，2代表-老师 \n', 
               '活动类型':'请输入活动类型，\n 110-学生课堂案例分析 \U0001F31E \U0001F31C 111-学生课后案例分析  \n 120-学生课堂理论学习 \U0001F31E \U0001F31C 121-学生课后理论学习 \n 130 学生课堂写作   \U0001F31E \U0001F31C 131 学生课后写作 \n', 
               '活动内容':'请输入活动内容的简单描述 \n', 
               '数学内容':'关于\U0001F449 数学 \U0001F448 内容的简单描述 \n', 
               '数学':'数学知识内容的等级(1-初中,3-高中,5-大学) \n', 
               '模型内容':'关于\U0001F449 模型 \U0001F448 内容的简单描述 \n',
               '模型':'模型内容的等级 \n 10-初等,\n 3-常规高等(31评价、32优化、33变化、34预测、35解释、36模拟),\n 50-其他 \n', 
               '编程内容':'关于\U0001F449 编程 \U0001F448 内容的简单描述 \n', 
               '编程':'编程内容的等级 \n 10-基础,\n 3-重要第三方库(31Numpy、32Matplotlib、33Pandas),\n 5-模型第三方库(51Model-Insight、52Pulp、53Scipy、54Sklearn、55Statsmodel、56其他) \n',
               '写作内容':'关于\U0001F449 写作 \U0001F448 内容的简单描述 \n', 
               '写作':'写作内容的等级 \n 1-基础学术论文, \n 3-通用建模论文, \n 5-特定模型论文(51评价、52优化、53变化、54预测、55解释、56模拟、57其他) \n', 
               '合作':'合作人数 \n', 
               '分析内容':'简要描述 \U0001F440 分析内容 \U0001F440 \n', 
               '分析总成就':'分析总成就(0-5) \n',
               '分析(教师辅助)':'教师辅助分析得分(0-5) \U0001F511 \n',
               '建模内容':'简要描述 \U0001F44A 建模内容 \U0001F44A \n', 
               '建模总成就':'建模总成就(0-5) \n', 
               '建模(教师辅助)':'教师辅助建模得分(0-5) \U0001F511 \n',
               '求解内容':'简要描述 \U0001F4D0 求解内容 \U0001F4D0 \n', 
               '求解总成就':'求解总成就(0-5) \n',
               '求解(教师辅助)':'教师辅助求解得分(0-5) \U0001F511 \n',
               '解释内容':'简要描述 \U0001F913 解释内容 \U0001F913 \n',
               '解释总成就':'解释总成就(0-5) \n', 
               '解释(教师辅助)':'教师辅助解释得分(0-5) \U0001F511 \n',
               '验证内容':'简要描述 \U0001F98A 建模内容 \U0001F98A \n', 
               '验证总成就':'验证总成就(0-5) \n', 
               '验证(教师辅助)':'教师辅助解验证得分(0-5) \U0001F511 \n',
               '汇报内容':'简要描述 \U0001F3E8 建模内容 \U0001F3E8 \n', 
               '汇报总成就':'汇报总成就(0-5) \n',
               '汇报(教师辅助)':'教师辅助解汇报得分(0-5) \U0001F511 \n'}
    record_dict = {i:[] for i in indicators}
    print('欢迎进入课程评价记录系统!'+'\U0001F9D0'*3)
    print('Loading...\n',end='')
    print('如果你不希望继续输入，可以在输入框中 输入 exit 即可退出')
    flag_continue = 1
    while flag_continue:
        for i in range(20):
            print('\U0001F680',end='',flush=True)
            time.sleep(0.1)
        print('\n')
        for i in record_dict.keys():
            info = input(description[i])
            if len(info)==0:
                record_dict[i].append(None)
            elif info == 'exit':
                flag_continue = 0
                print('终止本次输入')
                record_dict = {i:[] for i in indicators}
                break
            else:
                record_dict[i].append(info)
        whether_continue = input('是否继续输入下一条记录,1-是，2-否')
        if whether_continue == '1':
            pass
        else:
            flag_continue = 0
    for i in range(7):
        print('\U0001F947',end='',flush=True)
        print('\U0001F948',end='',flush=True)
        print('\U0001F949',end='',flush=True)
        time.sleep(0.1)   
    print('\n')
    print('                    \U0001F44C录入完成\U0001F44C                    ')
    df = pd.DataFrame(record_dict)
    if merge:
        data = pd.read_excel(file_name)
        return data.append(df)