# Dependes
import time
import sys
# Code
def slowcode(s):
    for c in s + '\n':
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(1./10)
# Example
#
# slowcode("Test1223") - Printing your code with handwrite slow.
#