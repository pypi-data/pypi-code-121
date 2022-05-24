"""
来自于 PEP572

在 python 3.8 中获取正式支持

https://docs.python.org/3/whatsnew/3.8.html

:= (由于它与海象的眼睛和象牙很像，因此被亲切地称为“海象操作员” )

"""

# 在此示例中，赋值表达式有助于避免调用 len()两次：
import re
import string

a = "adahfhoifoigoiwfhoiwg"
if (n := len(a)) > 10:
    print(f"List is too long ({n} elements, expected <= 10)")

# 在正则表达式匹配期间会产生类似的好处，其中需要两次匹配对象，一次是测试是否发生匹配，另一次是提取子组：
discount = 0.0
advertisement = "a 50% discount"
if mo := re.search(r'(\d+)% discount', advertisement):
    discount = float(mo.group(1)) / 100.0
    print(discount)


# 该运算符还对while循环有用，该循环计算一个值来测试循环终止，然后在循环主体中再次需要相同的值：
# Loop over fixed length blocks
f = open("./__init__.py", 'rb')
while len(block := f.read(256)) != 0:
    print(len(block))

# 另一个具有启发性的用例出现在列表理解中，其中表达式主体中还需要在过滤条件下计算出的值：
allowed_names = list(string.ascii_letters)
names = list(string.ascii_letters)
print([clean_name for name in names if (clean_name := name) in allowed_names])