# -*- coding: utf-8 -*-
"""
 @Time: 2019/5/28 13:47
"""

import time
import os
import sys

text = "家开发部"
print(type(text))

# text = text.encode(encoding="utf-8", errors='strict')
text = text.encode(encoding="utf-8", errors='ignore')
# text = text.encode(encoding="utf-8",)
print(type(text))
print(isinstance(text, bytes))


text = text.decode(encoding="utf-8")
print(type(text))

print(text)

print(isinstance(text, str))
print(isinstance(text, bytes))