# -*- coding:utf-8 -*-

import difflib
import codecs
from robot.api import logger
from robot.api.deco import keyword
import sys
import os
import importlib

# reload(sys)
importlib.reload(sys)
sys.setdefaultencoding('utf-8')

class Diff(object):
    """用来比较两个对象的库。

    ``Diff`` 是Gbase的内部库，用来比较两个对象
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        self.sequence_matcher = difflib.SequenceMatcher()
        self.differ = difflib.HtmlDiff()

    @keyword(u'比较字符串序列')
    def diff_strings(self, strings1, strings2):
        """比较两个容器类对象，如字符串，列表，元组等。
        显示对比结果，并友好的显示在html格式的log文件中
        如果两个对象不同，抛出ValueError异常。

        strings1: 第一个待比较对象.
        strings2: 第二个待比较对象.

        逻辑: 一个元素一个元素的比较两个容器对象的内容，
        显示对比的结果和匹配度。如果发现不同，抛出ValueError异常

        示例:
        | 比较序列 | ['hello world', 'hello python!'] | ['Hello World', 'Helloo Python'] |
        """
        self.sequence_matcher.set_seqs(strings1, strings2)
        logger.info(self.differ.make_table(strings1, strings2)
                    + self.differ._legend, html=True)
        logger.info('Match ratio is {0}'.format(self.sequence_matcher.ratio()))
        if self.sequence_matcher.ratio() < 1:
            raise ValueError ('These two things are different.')

    @keyword(u'比较文件')
    def diff_files(self, file1, file2, encoding = 'utf-8'):
        """比较两个文件。

        file1:第一个文件. file2:第二个文件.
        两个文件以带绝对路径的全文件名称传入

        逻辑: 以指定encoding编码方式(默认utf-8)打开两个文件，按行进行对比，并显示对比结果和匹配度。
        如果发现不同，抛出ValueError异常

        示例:
        | 比较文件 | /opt/file1_name | /opt/file2_name |
        """

        file1_size = os.path.getsize(file1)
        file2_size = os.path.getsize(file2)
        if file1_size != file2_size:
            raise ValueError('Files [%s] and [%s] differ.' % (file1, file2))

        try:
            with codecs.open(file1, 'r', encoding) as f1:
                with codecs.open(file2, 'r', encoding) as f2:
                    string1 = f1.readlines()
                    string2 = f2.readlines()
            self.diff_strings(string1, string2)
        except UnicodeDecodeError:
            with open(file1, 'rb') as f1:
                with open(file2, 'rb') as f2:
                    bytes1 = f1.readlines()
                    bytes2 = f2.readlines()
            self.sequence_matcher.set_seqs(bytes1, bytes2)
            if self.sequence_matcher.ratio() < 1:
                raise ValueError('Binary files [%s] and [%s] differ.' % (file1, file2))

    @keyword(u'比较二进制文件')
    def diff_binary_files(self, file1, file2):
        """
        比较两个二进制文件的内容，如不相同，抛出ValueError
        Args:
            file1: 待比较的第一个二进制文件(带全路径)
            file2: 待比较的第二个二进制文件(带全路径)
        示例：
        | 比较二进制文件 | /opt/file_name1 | /opt/file_name2 |
        """
        with open(file1, 'rb') as file1:
            with open(file2, 'rb') as file2:
                string1 = file1.readlines()
                string2 = file2.readlines()
        self.diff_strings(string1, string2)

    @keyword(u'列表中所有项目应该一致')
    def all_items_in_list_should_equal(self, the_list):
        """
        比较一个列表中的所有项目，如果有与其他项目不同的项目则抛出ValueError

        Args:
            the_list: 包含用户内容的列表对象

        Returns: None

        示例：
        | ${the_list} | Create List | 1 | 2| 1 |
        | 列表中所有项目应该一致 | ${the_list} |

        ==>

        ValueError: Item [2] and [1] differ.
        """
        if len(the_list) == 0:
            return

        first_item = the_list[0]
        for item in the_list[1:]:
            if item != first_item:
                raise ValueError('Item [%s] and [%s] differ.' % (item, first_item))

    def _log_diff_files(self, dcmp, diff_result_list):
        for name in dcmp.diff_files:
            diff_result_list.append("diff file %s found in %s and %s" % (name, dcmp.left,
                  dcmp.right))
        # for sub_dcmp in dcmp.subdirs.values():
        for sub_dcmp in list(dcmp.subdirs.values()):
            self.print_diff_files(sub_dcmp)

    @keyword(u'目录中的公共文件应该相同')
    def diff_directories(self, dir1, dir2):
        """
        比较两个目录中的文件是否完全相同，要注意：这个关键字只比较两个文件夹中的公共文件。
        如果不同则抛出 ValueError 异常
        Args:
            dir1: 目录1
            dir2: 目录2
        """
        from filecmp import dircmp
        dcmp = dircmp(dir1, dir2)

        diff_result_list = []
        self._log_diff_files(dcmp, diff_result_list)

        if len(dcmp.diff_files):
            raise ValueError('Files in directories [%s] and [%s] differ:\n\t%s' % (dir1, dir2, '\n\t'.join(diff_result_list)))

a = '/home/gbase/workspace/8a_Test/robotframework/src/robot/REDOLOG_192.168.103.100_org'
b = '/home/gbase/workspace/8a_Test/robotframework/src/robot/REDOLOG_192.168.103.100_modified'

a = 'd:\\Robot_OO\REDOLOG_192.168.103.100_after_restart'
b = 'd:\\Robot_OO\REDOLOG_192.168.103.100_modified'

if __name__ == '__main__':
    ud = Diff()

    #ud.diff_files(a, b)
    #ud.diff_binary_files(a, b)
    #ud.all_items_in_list_should_equal([1, 1, 1])
    ud.diff_directories('/home/guobin/testdir/a', '/home/guobin/testdir/b')
