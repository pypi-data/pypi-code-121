# 2022.4.2
import fire

def run(paras):
	''' test list '''
	print (type(paras), paras, flush=True)

if __name__ == '__main__':
	fire.Fire()

'''
D:\root\cikuu\pypi\util>python fire-test.py run  one
<class 'str'> one

D:\root\cikuu\pypi\util>python fire-test.py run  one,two
<class 'tuple'> ('one', 'two')

D:\root\cikuu\pypi\util>python fire-test.py run  one,
<class 'tuple'> ('one',)

D:\root\cikuu\pypi\util>python fire-test.py run  {"one":"two"}
<class 'dict'> {'one': 'two'}

'''