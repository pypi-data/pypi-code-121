import fast_jieba
import rjieba
import jieba
import time


# time cost decorator
def time_cost(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print('{} Time cost: {}'.format(func.__name__, end - start))
    return wrapper


@time_cost
def run_jieba():
    for i in range(1000):
        words = list(jieba.cut(f'No.{i} 我来到北京清华大学'))


@time_cost
def run_rjieba():
    for i in range(1000):
        words = rjieba.cut(f'No.{i} 我来到北京清华大学')


@time_cost
def run_fast_jieba():
    for i in range(1000):
        words = fast_jieba.cut(f'No.{i} 我来到北京清华大学')


@time_cost
def run_fast_jieba_batch():
    words = fast_jieba.batch_cut([f'No.{i} 我来到北京清华大学' for i in range(1000)])


run_jieba()
run_rjieba()
run_fast_jieba()
run_fast_jieba_batch()
