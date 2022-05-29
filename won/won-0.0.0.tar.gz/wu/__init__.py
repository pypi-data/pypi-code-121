# this dir as module name，只要有__init__.py，那么那个目录就是module，比如放在上一级目录
# TODO
#这里重点讨论 orbitkit 文件夹，也就是我们的核心代码文件夹。python 和 java 不一样，并不是一个文件就是一个类，在 python 中一个文件中可以写多个类。我们推荐把希望向用户暴漏的类和方法都先导入到 __init__.py 中，并且用关键词 __all__ 进行限定。下面是我的一个 __init__.py 文件。
#这样用户在使用的时候可以清楚的知道哪些类和方法是可以使用的，也就是关键词 __all__ 所限定的类和方法。


from wu import wy
#另外，在写自己代码库的时候，即便我们可以使用相对导入，但是模块导入一定要从项目的根目录进行导入，这样可以避免一些在导入包的时候因路径不对而产生的问题。比如
# from orbitkit.file_extractor.dispatcher import FileDispatcher

name = 'orbitkit'

__version__ = '0.0.0'
VERSION = __version__

__all__ = [
    'wy',
]
