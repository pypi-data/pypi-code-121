#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
# author:fanfanfeng
# contact: 544855237@qq.com
# datetime:2022/2/14 下午11:31
'''

def get_list_start_position(main_list,sub_list,start = 0):
    '''
    找出sub_list在main_list里面的起始位置
    :param main_list:
    :param sub_list:
    :param start:main_list开始搜索的起始位置
    :return: 包含的下标（start_position,end_position）
    '''

    positions = []
    len1 = len(main_list)
    len2 = len(sub_list)
    if main_list == [] or sub_list == []:
        return -1
    for index in range(start,len1 - len2 + 1):
        if main_list[index] == sub_list[0] and main_list[index:index + len2] == sub_list:
            positions.append(index)
            positions.append(index + len2 -1)
            break


    return positions


def check_list_same(listA,listB):
    '''
    判断两个list是否相同
    :param listA:
    :param listB:
    :return: 1相同，0不相同
    '''
    the_same = True
    for itemA,itemB in zip(listA,listB):
        if itemA != itemB:
            the_same = False
            break
    return the_same
