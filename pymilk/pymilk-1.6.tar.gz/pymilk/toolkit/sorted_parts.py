
class sorted_parts():

    def __init__(self, value, order=True):
        self.value = value
        self.order = order

    def __lt__(self, obj):
        if self.order:
            return self.lt(self.value, obj.value)
        return not self.lt(self.value, obj.value)
    
    def lt(self, a, b):
        try:
            if type(a) in (tuple, dict, set):  a = list(a)
            if type(b) in (tuple, dict, set):  b = list(b)
            try:
                return a < b
            except: pass
            if not a or not b: return bool(a) < bool(b)
            if a is True: a = 1
            elif a is False: a = 0
            elif a is None: a = 0
            if b is True: b = 1
            elif b is False: b = 0
            elif b is None: b = 0
            ta = type(a)
            tb = type(b)
            if ta in (float, int, str) and tb in (float, int, str): return str(a) < str(b)
            try:
                for x, y in zip(a, b):
                    if x == y:
                        continue
                    return self.lt(x, y)
                return len(a) < len(b)
            except: pass
        except:
            pass
        return False
