def print_hello(port):
    print('==> Deploying bloggart:')
    print('http://localhost:' + str(port) + "/")


def readlist(path):
    if (path == ''):
        return []
    lines = [line.strip() for line in open(path, 'r', encoding=FILE_ENCODE).readlines()]
    return lines

def trans_reserve(line):
    reserved_chars = '''?&|!{}[]()^~*:\\"'+-.+'''
    replace = ['\\' + l for l in reserved_chars]
    trans = dict(zip(reserved_chars, replace))
    result = ''
    for char in line:
        if char in trans:
            result += trans[char]
        else:
            result += char
    return result

# 71. 简化路径
# 作者：LeetCode-Solution
# 链接：https://leetcode-cn.com/problems/simplify-path/solution/jian-hua-lu-jing-by-leetcode-solution-aucq/
# 来源：力扣（LeetCode）
def simplifyPath(path: str) -> str:
    names = path.split("/")
    stack = list()
    for name in names:
        if name == "..":
            if stack:
                stack.pop()
        elif name and name != ".":
            stack.append(name)
    return "/".join(stack)


