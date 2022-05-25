import copy, fractions, math

VALID = '''A valid polynomial defined here is in the form ax^n1bx^n2 + ... + 
ax^n + bx^n-1 + ... + ax + bx + c, you can set any number of variables here, 
just to make sure when you want to show a power use '^' and use + or - between 
every term. Note that the coefficient of every term should be placed at the
beginning of term, if you want to  create a polynomial like 3x2y which
means 6xy actually, then use brackets like 3x(2y) or (3x)2y or (3x)(2y).
Whitespaces between terms is not necessary. Some examples of valid 
polynomials here: 2x; 2xy+3x+3; 2x^2y-3+y; 2x^2x + xy + y^3 
xyz+3x^2+6x; 3; 2x + 5y + x^-2 + 6, some invalid polynomials example: 3x**y; 
2x**2 + 3; 2x^2x^3; 5x**3 + xy**6
Feel free to leave the polynomial unmerged in every term, 
because my program will automatically do it when it analyze your polynomial. To
merge through all of the terms just do a.standardize() where a is a polynomial object.'''


def separate(co):
    number = 1
    func = ''
    for t in range(len(co) - 1, -1, -1):
        if co[t].isdigit():
            number = int(co[:t + 1])
            break
        elif co[t] == '-' and not co[t + 1].isdigit():
            number = -1
            break
        else:
            func = co[t] + func
    return number, func


def div(temp, temp2, ind, ind2):
    if len(temp.varname) > 1:
        divide = polynomial([[temp.polydict[var][ind][1]]
                             for var in temp.varname],
                            [[temp.polydict[var][ind][0]]
                             for var in temp.varname], temp.varname)
    else:
        divide = polynomial(
            [temp.polydict[var][ind][1] for var in temp.varname],
            [temp.polydict[var][ind][0] for var in temp.varname], temp.varname)
    if len(temp2.varname) > 1:
        divisor = polynomial([[temp2.polydict[var][ind2][1]]
                              for var in temp2.varname],
                             [[temp2.polydict[var][ind2][0]]
                              for var in temp2.varname], temp2.varname)
    else:
        divisor = polynomial(
            [temp2.polydict[var][ind2][1] for var in temp2.varname],
            [temp2.polydict[var][ind2][0]
             for var in temp2.varname], temp2.varname)
    return divide, divisor


def multco(a):
    result = 1
    result2 = ''
    if all(x == 0 for x in a):
        return 0
    for i in a:
        if i != 0:
            if isinstance(i, str):
                if any(
                        x in i for x in
                    ['sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'log', 'ln']):
                    for t in range(len(i) - 1, -1, -1):
                        if i[t].isdigit():
                            now = eval(i[:t + 1])
                            if isinstance(now, float):
                                now = fractions.Fraction(
                                    now).limit_denominator()
                            result *= now
                            break
                        elif i[t] == '-' and not i[t + 1].isdigit():
                            result *= -1
                            break
                        else:
                            result2 = i[t] + result2
            else:
                result *= i
    if result == 1:
        if result2 == '':
            return 1
        else:
            return f'{result2}'
        return result2
    elif result == -1:
        if result2 == '':
            return -1
        else:
            return f'-{result2}'
    else:
        if result2 == '':
            return result
        else:
            return f'{result}{result2}'


class polynomial:
    def __init__(self,
                 colist,
                 powerlist,
                 varname=['x'],
                 root=1,
                 equation=None,
                 single=True):
        if len(colist) != len(powerlist):
            raise ValueError(
                'the number of coefficients should equal to the number of powers'
            )
        if len(varname) > 1 or single is False:
            if not all(
                    all(isinstance(x, list) for x in m)
                    for m in [colist, powerlist]) or any(
                        len(x) != len(varname)
                        for x in [colist, powerlist]) or len(
                            set([len(y) for y in colist + powerlist])) != 1:
                raise ValueError(
                    'to build up a multi-variable polynomial, you should set coefficient list and power list as a list of every variable\'s list in order, and every variable should have same length of coefficient list and power list'
                )
            self.colist = colist
            self.powerlist = powerlist
        else:
            colist = [colist]
            powerlist = [powerlist]
            self.colist = colist
            self.powerlist = powerlist
        self.varname = varname
        self.equation = equation
        self.root = root
        self.fraction = []
        self.polydict = {
            varname[var]: [[powerlist[var][i], colist[var][i]]
                           for i in range(len(colist[0]))]
            for var in range(len(varname))
        }

    def __str__(self):
        result = ''
        if all(x[i] == 0 for i in range(len(self.colist[0]))
               for x in self.powerlist) and all(
                   x[i] == 0 for i in range(len(self.colist[0]))
                   for x in self.colist):
            return '0'
        varname = self.varname
        colist = self.colist
        powerlist = self.powerlist
        step = len(colist[0])
        for i in range(step):
            temp = ''
            coefficient = multco([x[i] for x in colist])
            if coefficient not in [1, -1]:
                if coefficient == 0:
                    continue
                else:
                    temp += f'{coefficient}'
            else:
                if all(powerlist[x][i] == 0 or (
                        powerlist[x][i] != 0 and colist[x][i] == 0)
                       for x in range(len(powerlist))):
                    if coefficient == -1:
                        temp += '-1'
                    else:
                        temp += f'{coefficient}'
                else:
                    if coefficient == -1:
                        temp += '-'
            for j in range(len(varname)):
                var = varname[j]
                power = powerlist[j][i]
                if power != 0 and colist[j][i] != 0:
                    if power == 1:
                        temp += f'{var}'
                    else:
                        temp += f'{var}^{power}'
            result += temp + ' + '
        for k in self.fraction:
            result += str(k) + ' + '
        result = result[:-3]
        if self.root != 1:
            result = f'({result})^{self.root}'
        if self.equation != None:
            result += f' = {self.equation.__str__()}'
        return result

    __repr__ = __str__

    def __contains__(self, obj):
        return obj in self.split()

    def __len__(self):
        return len(self.colist[0])

    def split(self):
        # split term by term to a list of polynomials
        temp = copy.deepcopy(self)
        pre = [polynomial([[temp.colist[x][i]]\
                           for x in range(len(temp.colist))],\
                          [[temp.powerlist[x][i]] for x in\
                           range(len(temp.powerlist))],temp.varname, single = False)\
                for i in range(len(temp.colist[0]))]
        return [poly(f'{x}') for x in pre]

    def __getitem__(self, ind):
        temp = copy.deepcopy(self)
        if isinstance(ind, slice):
            if ind == slice(None, None):
                return self.split()
            start, stop = ind.start, ind.stop
            if ind.start is None:
                start = 0
            if ind.stop is None:
                stop = len(temp.colist[0])
            return sums([polynomial([[temp.colist[x][i]]\
                           for x in range(len(temp.colist))],\
                          [[temp.powerlist[x][i]] for x in\
                           range(len(temp.powerlist))],temp.varname, single = False) for i in range(start, stop)])
        return polynomial([[temp.colist[x][ind]]\
                           for x in range(len(temp.colist))],\
                          [[temp.powerlist[x][ind]] for x in\
                           range(len(temp.powerlist))],temp.varname, single = False)

    def __neg__(self):
        temp = copy.deepcopy(self)
        temp *= -1
        return temp

    def __mul__(self, other):
        if isinstance(other, str):
            other = poly(other)
        if any(isinstance(other, x) for x in [int, float, fractions.Fraction]):
            if other == 0:
                return poly('0')
            result = copy.deepcopy(self)
            result.fraction = [x * other for x in result.fraction]
            result.colist[0] = [
                i * other if not isinstance(i, str) else
                f'{separate(i)[0]*other}{separate(i)[1]}'
                for i in result.colist[0]
            ]
            for i in range(len(result.colist[0])):
                co = result.colist[0][i]
                if not isinstance(co, str):
                    f = fractions.Fraction(co).limit_denominator().__float__()
                    result.colist[0][i] = int(f) if f.is_integer() else f
            return result
        elif isinstance(other, polynomial):
            if other == poly('0'):
                return poly('0')
            temp = copy.deepcopy(self)
            temp2 = copy.deepcopy(other)
            temp.standardize()
            temp2.standardize()
            temp.fraction = [x * temp2 for x in temp.fraction]
            if len(self.polydict[self.varname[0]]) == 1 and len(
                    other.polydict[other.varname[0]]) == 1:
                if len(temp.varname) == 1:
                    if temp.powerlist[0][0] == 0:
                        return temp.colist[0][0] * temp2
                if len(temp2.varname) == 1:
                    if temp2.powerlist[0][0] == 0:
                        return temp * temp2.colist[0][0]
                tempco = multco([x[0] for x in temp.colist])
                temp2co = multco([y[0] for y in temp2.colist])

                if all(not isinstance(x, str) for x in [tempco, temp2co]):
                    co = tempco * temp2co
                else:
                    if isinstance(tempco, str):
                        tempco, temp2co = temp2co, tempco
                    co = (str(tempco) if tempco not in [1, -1] else
                          ('' if tempco == 1 else '-')) + str(temp2co)
                    if not isinstance(tempco, str):
                        temp, temp2 = temp2, temp
                temp.colist = [[1] for i in range(len(temp.colist))]
                temp2.colist = [[1] for i in range(len(temp2.colist))]
                return poly(
                    ('' if temp.__str__() != '-1' else '-') + str(co) +
                    (temp.__str__() if temp.__str__() not in [1, -1] else '') +
                    temp2.__str__())
            else:
                result = poly('0')
                if len(temp2.varname) == 1:
                    if temp2.powerlist[0][0] == 0:
                        return temp * temp2.colist[0][0]
                for i in range(len(temp.colist[0])):
                    if len(temp.varname) == 1:
                        term1 = polynomial([temp.colist[0][i]],
                                           [temp.powerlist[0][i]],
                                           temp.varname)
                    else:
                        if all(x[i] == 0 for x in temp.powerlist):
                            term1 = poly(
                                str(multco([x[i] for x in temp.colist])))
                        else:
                            term1 = polynomial([[x[i]] for x in temp.colist],
                                               [[y[i]]
                                                for y in temp.powerlist],
                                               temp.varname)
                    for j in range(len(temp2.colist[0])):
                        if len(temp2.varname) == 1:
                            term2 = polynomial([temp2.colist[0][j]],
                                               [temp2.powerlist[0][j]],
                                               temp2.varname)
                        else:
                            if all(x[j] == 0 for x in temp2.powerlist):
                                term2 = poly(
                                    str(multco([x[j] for x in temp2.colist])))
                            else:
                                term2 = polynomial([[q[j]]
                                                    for q in temp2.colist],
                                                   [[t[j]]
                                                    for t in temp2.powerlist],
                                                   temp2.varname)
                        result += term1 * term2
                return result

        else:
            return 'polynomial multiplication object can only take numbers or polynomials'

    def __rmul__(self, other):
        return self * other

    def merge(self):
        '''Merge terms with same powers of the polynomial. Return a new polynomial after standarlization.'''
        temp = self.copy()
        temp.standardize()
        return temp

    def simp(self):
        temp = self.copy()
        temp.simplify()
        return temp

    def copy(self):
        return copy.deepcopy(self)

    def __eq__(self, other):
        if not isinstance(other, polynomial):
            other = poly(str(other))
            return self == other
        else:
            temp1 = copy.deepcopy(self)
            temp2 = copy.deepcopy(other)
            temp1.standardize()
            temp2.standardize()
            if (temp1 - temp2
                ).__str__() == '0' and temp1.fraction == temp2.fraction:
                return True
            else:
                return False

    def __add__(self, other):
        if type(other) in [int, float, fractions.Fraction, str]:
            other = poly(str(other))
            return self + other
        elif isinstance(other, fract):
            temp = copy.deepcopy(self)
            temp.fraction.append(other)
            return temp
        #if not isinstance(other, polynomial):
        #return 'polynomial addition only takes between polynomial objects, you could use poly(a) to simply \
#transform a into a polynomial object if a is a valid polynomial. To see what is a valid polynomial defined \
#here, type "print(VALID)" and press enter if you import polynomial as *, or if you import polynomial as something, \
#type "print(something.VALID)" and press enter.'
        else:
            temp = copy.deepcopy(self)
            temp2 = copy.deepcopy(other)
            if temp.powerlist == [[0]] and temp.colist == [[0]]:
                return temp2
            if temp2.powerlist == [[0]] and temp2.colist == [[0]]:
                return temp
            for t in range(len(temp.colist[0])):
                temp.colist[0][t] = multco(
                    [temp.colist[i][t] for i in range(len(temp.colist))])
                for x in range(1, len(temp.colist)):
                    temp.colist[x][t] = 1
            for x in temp2.varname:
                if x not in temp.varname:
                    temp.varname.append(x)
                    temp.colist.append([1 for i in range(len(temp.colist[0]))])
                    temp.powerlist.append(
                        [0 for i in range(len(temp.colist[0]))])
            for y in temp.varname:
                if y not in temp2.varname:
                    temp2.varname.append(y)
                    temp2.colist.append(
                        [1 for i in range(len(temp2.colist[0]))])
                    temp2.powerlist.append(
                        [0 for i in range(len(temp2.colist[0]))])
            terms = [{
                temp.varname[i]: temp.powerlist[i][j]
                for i in range(len(temp.powerlist))
            } for j in range(len(temp.powerlist[0]))]
            power = temp2.powerlist
            co = temp2.colist
            t = 0
            while t < len(co[0]):
                term = {
                    temp2.varname[i]: power[i][t]
                    for i in range(len(power))
                }
                nowco = multco([q[t] for q in co])
                if term in terms:
                    ind = terms.index(term)
                    temp.colist[0][ind] += nowco
                    if temp.colist[0][ind] == 0:
                        del terms[ind]
                        j = 0
                        while j < len(temp.colist):
                            del temp.powerlist[j][ind]
                            del temp.colist[j][ind]
                            j += 1
                else:
                    for h in range(len(temp.powerlist)):
                        temp.powerlist[h].append(term[temp.varname[h]])
                        if h == 0:
                            temp.colist[h].append(nowco)
                        else:
                            temp.colist[h].append(1)
                t += 1
            if len(temp.colist[0]) == 0 and len(temp.powerlist[0]) == 0:
                temp.colist[0].append(0)
                temp.powerlist[0].append(0)
            var = 0
            while var < len(temp.varname):
                if all(x == 0 for x in temp.powerlist[var]):
                    co = temp.colist[0]
                    del temp.varname[var]
                    del temp.powerlist[var]
                    del temp.colist[var]
                    if len(temp.colist) != 0:
                        temp.colist[0] = co
                    else:
                        temp.colist.append(co)
                    continue
                var += 1
            if len(temp.varname) == 0:
                temp.varname = ['x']
                temp.powerlist = [[0]]
                temp.colist = [[0]] if len(temp.colist) == 0 else temp.colist
                temp.updatedict()
            else:
                temp.polydict = {
                    temp.varname[var]:
                    [[temp.powerlist[var][i], temp.colist[var][i]]
                     for i in range(len(temp.colist[0]))]
                    for var in range(len(temp.varname))
                }
            return temp

    def __radd__(self, other):
        return poly(str(other)) + self

    def __sub__(self, other):
        if isinstance(other, str):
            other = poly(other)
            return self - other
        #if not isinstance(other, polynomial):
        #return 'polynomial subtraction only takes between polynomial objects, you could use poly(a) to simply \


#transform a into a polynomial object if a is a valid polynomial. To see what is a valid polynomial defined \
#here, type "print(VALID)" and press enter if you import polynomial as *, or if you import polynomial as something, \
#type "print(something.VALID)" and press enter.'
        else:
            return self + other * -1

    def __rsub__(self, other):
        return poly(str(other)) - self

    def __invert__(self):
        return self.recipro()

    def recipro(self):
        temp = copy.deepcopy(self)
        if len(temp.colist[0]) == 1:
            for k in range(len(temp.powerlist)):
                temp.powerlist[k] = [t * -1 for t in temp.powerlist[k]]
            number = fractions.Fraction(
                1 / temp.colist[0][0]).limit_denominator().__float__()
            temp.colist[0][0] = int(number) if number.is_integer() else number
        else:
            return fract(poly('1'), copy.deepcopy(self))
        return temp

    def __truediv__(self, other):
        temp = copy.deepcopy(self)
        if type(other) in [int, float, fractions.Fraction]:
            rec = fractions.Fraction(1 / other).limit_denominator()
            rec = int(rec) if rec.__float__().is_integer() else rec
            temp *= rec
            return temp
        elif isinstance(other, str):
            other = poly(other)
            return self / other
        elif isinstance(other, polynomial):
            if temp.powerlist == [[0]] and temp.colist == [[0]]:
                return poly('0')
            # if the remainder of division is 0, return the division result polynomial only,
            # otherwise return a list with 2 elements, one is the division result polynomial
            # and the another one is the remainder term
            temp2 = copy.deepcopy(other)
            if all(x not in temp2.varname for x in temp.varname):
                return fract(temp, temp2)
            else:
                if len(temp.colist[0]) == len(temp2.colist[0]) == 1:
                    quo = temp * (temp2.recipro())
                    for g in range(len(quo.colist)):
                        for h in range(len(quo.colist[g])):
                            if isinstance(quo.colist[g][h], float):
                                if quo.colist[g][h].is_integer():
                                    quo.colist[g][h] = int(quo.colist[g][h])
                                else:
                                    quo.colist[g][h] = fractions.Fraction(
                                        quo.colist[g][h]).limit_denominator()
                    quo.standardize()
                    return quo
                else:
                    remainder = copy.deepcopy(temp)
                    found = False
                    for i in range(len(temp.colist[0])):
                        if i != 0:
                            temp.insert(0, temp.pop(i))
                        for j in range(len(temp2.colist[0])):
                            divide, divisor = div(temp, temp2, 0, j)
                            if not all(
                                    x not in poly(divisor.__str__()).varname
                                    for x in poly(divide.__str__()).varname):
                                found = True
                                break
                        if found:
                            break
                    if not found:
                        return fract(temp, temp2)
                    #while all(x not in poly(divisor.__str__()).varname for x in poly(divide.__str__()).varname):
                    #print(temp, temp2)
                    #temp.standardize(True)
                    #divide, divisor = div(temp, temp2)
                    #if all(x not in poly(divisor.__str__()).varname for x in poly(divide.__str__()).varname):
                    #temp2.standardize(True)
                    #divide, divisor = div(temp, temp2)
                    #else:
                    #break
                    result = ''
                    while not any(
                            any(r < 0 for r in x)
                            for x in (divide / divisor).powerlist):
                        multi = divide / divisor
                        for g in range(len(multi.colist)):
                            for h in range(len(multi.colist[g])):
                                if isinstance(multi.colist[g][h], float):
                                    if multi.colist[g][h].is_integer():
                                        multi.colist[g][h] = int(
                                            multi.colist[g][h])
                                    else:
                                        multi.colist[g][
                                            h] = fractions.Fraction(
                                                multi.colist[g]
                                                [h]).limit_denominator()
                        rep = multi.__str__()
                        result += rep + ' + '
                        remainder = poly(remainder.mono())
                        remainder -= temp2 * multi
                        remainder.standardize()
                        for g in range(len(remainder.colist)):
                            for h in range(len(remainder.colist[g])):
                                if isinstance(remainder.colist[g][h], float):
                                    if remainder.colist[g][h].is_integer():
                                        remainder.colist[g][h] = int(
                                            remainder.colist[g][h])
                                    else:
                                        remainder.colist[g][
                                            h] = fractions.Fraction(
                                                remainder.colist[g]
                                                [h]).limit_denominator()
                        if len(remainder.varname) > 1:
                            divide = polynomial(
                                [[remainder.polydict[var][0][1]]
                                 for var in remainder.varname],
                                [[remainder.polydict[var][0][0]]
                                 for var in remainder.varname],
                                remainder.varname)
                        else:
                            divide = polynomial([
                                remainder.polydict[var][0][1]
                                for var in remainder.varname
                            ], [
                                remainder.polydict[var][0][0]
                                for var in remainder.varname
                            ], remainder.varname)
                        divide = copy.deepcopy(divide)
                        divide.standardize()
                        if isinstance(divide / divisor, fract):
                            break
                        if remainder.__str__() == '0':
                            break
                    if result == '':
                        remain = divide / divisor
                        left = (temp - remain * divisor) / divisor
                        return [
                            f'quotient: {remain}',
                            'remainder: ' + left.mono() if isinstance(
                                left, polynomial) else left.__str__()
                        ]
                    if result[-2] == '+':
                        result = result[:-3]
                    if remainder.__str__() == '0':
                        return topoly(result)
                    else:
                        return [
                            'quotient: ' + result.replace(' + -', ' - '),
                            'remainder: ' + remainder.mono()
                        ]
        else:
            return 'polynomial division only takes number or polynomials to be a divisor'

    def __floordiv__(self, other):
        return concat([x / other for x in self.split()])

    def __rtruediv__(self, other):
        return ~(self // other)

    def __pow__(self, number):
        if number == 0:
            return 1
        temp = copy.deepcopy(self)
        number *= temp.root
        if isinstance(number, float) and number.is_integer():
            number = int(number)
        if isinstance(number, float) or isinstance(number, fractions.Fraction):
            temp.root = number
            return temp
        else:
            temp.root = 1
            if number < 0:
                return 1 / temp**(abs(number))
            else:
                for i in range(number - 1):
                    temp *= self
                return temp

    def __xor__(self, number):
        return self.__pow__(number)

    def cat(self, other, mode='+'):
        if mode == '+':
            return concat(self, other)
        elif mode == '-':
            other = -topoly(other)
            return concat(self, other)
        else:
            return concat(self, other)

    def diff(self, var=None, times=1):
        if len(self.varname) > 1:
            if var == None:
                return 'please notify which variables to differentiate'
            else:
                if var not in self.varname:
                    return 'the variable to differentiate does not exist in the given function'
                else:
                    temp = copy.deepcopy(self)
                    varind = temp.varname.index(var)
                    co = [x[1] for x in temp.polydict[var]]
                    powers = [x[0] for x in temp.polydict[var]]
                    if times == 1:
                        t = 0
                        while t < len(co):
                            nowco = co[t]
                            power = powers[t]
                            if power == 0:
                                for y in range(len(temp.colist)):
                                    del temp.powerlist[y][t]
                                    del temp.colist[y][t]
                                del co[t]
                                del powers[t]
                                continue
                            if any(
                                    isinstance(nowco, x)
                                    for x in [int, float, fractions.Fraction]):
                                temp.colist[varind][t] *= temp.powerlist[
                                    varind][t]
                                temp.powerlist[varind][t] -= 1
                            else:
                                number, func = separate(nowco)
                                if func == 'sin':
                                    temp.colist[varind][t] = f'{number}cos'
                                elif func == 'cos':
                                    number *= -1
                                    temp.colist[varind][t] = f'{number}sin'

                            t += 1
                        temp = poly(temp.mono())
                        temp.updatedict()
                        if temp.colist[0] == [0]:
                            return poly('0')
                        return temp
                    else:
                        for x in range(times):
                            temp = temp.diff(var, times=1)
                        return temp

        else:
            if var != None and var not in self.varname:
                return 'the variable to differentiate does not exist in the given function'
            else:
                temp = copy.deepcopy(self)
                if times == 1:
                    for t in range(len(temp.colist[0])):
                        nowco = temp.colist[0][t]
                        power = temp.powerlist[0][t]
                        if any(
                                isinstance(nowco, x)
                                for x in [int, float, fractions.Fraction]):
                            temp.colist[0][t] *= temp.powerlist[0][t]
                            temp.powerlist[0][t] -= 1
                        else:
                            number, func = separate(nowco)
                            if func == 'sin':
                                temp.colist[0][t] = f'{number}cos'
                            elif func == 'cos':
                                number *= -1
                                temp.colist[0][t] = f'{number}sin'
                    if temp.colist[0] == [0]:
                        return poly('0')
                    return temp
                else:
                    for x in range(times):
                        temp = temp.diff(var, times=1)
                    return temp

    def integral(self, var):
        pass

    def __iter__(self):
        self.count = 0
        return self

    def __next__(self):
        if self.count == len(self.colist[0]):
            raise StopIteration
        else:
            result = self[self.count]
            self.count += 1
            return result

    def simplify(self, is_poly=False):
        # simplify a polynomial to a result as simple as possible
        # this function deals with many cases, including powers,
        # fractions and trigonometric polynomials, and so on.
        # this funcion will only return a string showing the simplified
        # result of the polynomial, if you want to return a polynomial,
        # set the parameter "is_poly" to True.
        result = ''
        # first step, extract the common coefficients
        polylist = self.split()
        wholevar = self.varname
        commonlist = []
        afterlist = []
        commons = []
        for var in wholevar:
            hasvar = []
            k = 0
            while k < len(polylist):
                current = polylist[k]
                if var in current.varname:
                    hasvar.append(k)
                k += 1
            if len(hasvar) > 1:
                commonterm = [polylist[x] for x in hasvar]
                commonlist.append(commonterm)
                new = sums(commonterm)
                common = poly(f'{var}')
                commons.append(common)
                after = poly(new / common)
                found = True
                while found:
                    found = False
                    for v in wholevar:
                        if all(v in x.varname for x in after.split()):
                            found = True
                            new2 = poly(f'{v}')
                            after = poly(after / new2)
                            commons[-1] *= new2
                    if not found:
                        break

                polylist = [
                    polylist[k] for k in range(len(polylist))
                    if k not in hasvar
                ]
                if after not in afterlist:
                    afterlist.append(after)
                else:
                    ind = afterlist.index(after)
                    combine1 = commons.pop(ind)
                    combine2 = commons.pop()
                    upgrade = sums([combine1, combine2])
                    commons.append(upgrade)
        for h in range(len(commons)):
            com = commons[h]
            com2 = f'({com})' if len(com.colist[0]) > 1 else com
            result += f'{com2}({afterlist[h]}) + '
        if len(polylist) != 0:
            result += sums(polylist).mono()
        else:
            result = result[:-3]
        return result

    def standardize(self, swap=False):
        ''' Merge terms with same power and sort the terms with order of decreasing powers.
        Return the polynomial representation in standard form defined above.'''
        t = 0
        while t < len(self.colist[0]):
            power = [x[t] for x in self.powerlist]
            self.colist[0][t] = multco([i[t] for i in self.colist])
            j = 1
            while j < len(self.colist):
                self.colist[j][t] = 1
                j += 1
            m = 0
            while m < len(self.colist[0]):
                if m != t:
                    power2 = [x[m] for x in self.powerlist]
                    nowco = multco([i[m] for i in self.colist])
                    if power2 == power:
                        self.colist[0][t] += nowco
                        g = 0
                        while g < len(self.colist):
                            del self.powerlist[g][m]
                            del self.colist[g][m]
                            g += 1
                        if m < t:
                            t -= 1
                m += 1
            if self.colist[0][t] == 0:
                q = 0
                while q < len(self.colist):
                    del self.powerlist[q][t]
                    del self.colist[q][t]
                    q += 1
            t += 1
        if len(self.colist[0]) == 0 and len(self.powerlist[0]) == 0:
            self.colist[0].append(0)
            self.powerlist[0].append(0)
        var = 0
        while var < len(self.varname):
            if all(x == 0 for x in self.powerlist[var]) or len(
                    self.powerlist[var]) == 0:
                co = self.colist[0]
                del self.varname[var]
                del self.powerlist[var]
                del self.colist[var]
                if len(self.colist) != 0:
                    self.colist[0] = co
                else:
                    self.colist.append(co)
                continue
            var += 1
        if len(self.varname) == 0:
            self.varname = ['x']
            self.powerlist = [[0]]
            self.colist = [[0]] if len(self.colist) == 0 else self.colist
        else:
            if len(
                    set([
                        sum([x[r] for x in self.powerlist])
                        for r in range(len(self.colist[0]))
                    ])) != 1 or swap == True:
                terms = [(i, sum([x[i] for x in self.powerlist]))
                         for i in range(len(self.colist[0]))]
                terms = sorted(terms, key=lambda x: x[1], reverse=True)
                for i in range(len(self.colist)):
                    self.colist[i] = [
                        self.colist[i][terms[k][0]] for k in range(len(terms))
                    ]
                    self.powerlist[i] = [
                        self.powerlist[i][terms[k][0]]
                        for k in range(len(terms))
                    ]
        self.updatedict()

    def val(self, *var):
        # The variable list var accept 1 or more variables to evaluate the value of
        # polynomial, the order is the same as the polynomial's varname list.
        if len(var) == 0:
            return self
        elif len(var) == 1 and isinstance(var[0], list):
            temp = copy.deepcopy(self)
            var = var[0]
            M = len(temp.colist)
            for i in range(len(var)):
                value = var[i]
                if value != None:
                    N = len(temp.colist[i])
                    if value == 0:
                        k = 0
                        while k < N:
                            if temp.powerlist[i][k] != 0:
                                for t in range(M):
                                    del temp.colist[t][k]
                                    del temp.powerlist[t][k]
                                N -= 1
                                continue
                            k += 1
                    else:
                        temp.colist[i] = [
                            temp.colist[i][j] * (value**temp.powerlist[i][j])
                            for j in range(N)
                        ]
                    temp.powerlist[i] = [0 for k in range(N)]
            temp.updatedict()
            saveroot = 1
            if temp.root != 1:
                saveroot = temp.root
                temp.root = 1
            temp2 = sums(temp.split())
            if temp2.powerlist == [[0]]:
                temp2 = eval(temp2.mono())
            return temp2**saveroot
        elif len(var) > len(self.varname):
            return f'this polynomial only have {len(self.varname)} variables but {len(var)} is given'
        else:
            var = list(var)
            return self.val(var)

    def mono(self):
        represent = self.__str__()
        represent = represent.replace(' + -', ' - ')
        return represent

    def updatedict(self):
        varname = self.varname
        colist = self.colist
        powerlist = self.powerlist
        self.polydict = {
            varname[var]: [[powerlist[var][i], colist[var][i]]
                           for i in range(len(colist[0]))]
            for var in range(len(varname))
        }

    def __setitem__(self, ind, new):
        pre = self.split()
        if not isinstance(new, polynomial):
            new = poly(str(new))
        pre[ind] = new
        temp = concat(pre)
        self.colist, self.powerlist, self.varname, self.polydict = temp.colist, temp.powerlist, temp.varname, temp.polydict

    def __delitem__(self, ind):
        pre = self.split()
        del pre[ind]
        temp = sums(pre)
        self.colist, self.powerlist, self.varname, self.polydict = temp.colist, temp.powerlist, temp.varname, temp.polydict

    def pop(self, ind=None):
        if ind is None:
            result = self.split().pop()
            del self[-1]
            return result
        else:
            result = self.split().pop(ind)
            del self[ind]
            return result

    def insert(self, ind, new):
        pre = self.split()
        if not isinstance(new, polynomial):
            new = poly(str(new))
        pre.insert(ind, new)
        temp = concat(pre)
        self.colist, self.powerlist, self.varname, self.polydict = temp.colist, temp.powerlist, temp.varname, temp.polydict

    def reverse(self):
        pre = self.split()
        pre.reverse()
        return sums(pre)

    def append(self, new):
        pre = self.split()
        if not isinstance(new, polynomial):
            new = poly(str(new))
        pre.append(new)
        temp = concat(pre)
        self.colist, self.powerlist, self.varname, self.polydict = temp.colist, temp.powerlist, temp.varname, temp.polydict

    def swap(self, ind1, ind2):
        self[ind1], self[ind2] = self[ind2], self[ind1]

    def __call__(self, *x, mode='val'):
        if mode == 'val':
            return self.val(*x)
        elif mode == 'standardize':
            self.standardize()


def rounding(num, dec=None, tostr=False):
    if dec is None or isinstance(num, int):
        return num
    if isinstance(num, fractions.Fraction):
        num = float(num)
    numstr = str(num)
    ind = numstr.index('.')
    if dec == 0:
        intpart = eval(numstr[:ind])
        return intpart + 1 if eval(numstr[ind + 1]) >= 5 else intpart
    tol = len(numstr) - ind - 1
    if tol < dec:
        return f'{num:.{dec}f}' if tostr else num
    elif tol == dec:
        return num
    else:
        if eval(numstr[ind + dec + 1]) >= 5:
            temp = str(num + 10**-dec)[:ind + dec + 1]
            result = eval(temp)
            resultstr = str(result)
            if len(resultstr) - resultstr.index('.') - 1 == dec:
                return result
            else:
                return f'{result:.{dec}f}' if tostr else result

        else:
            return eval(numstr[:ind + dec + 1])


class Func:
    def __init__(self, poly_obj, title='f'):
        poly_obj = topoly(poly_obj)
        self.func = poly_obj
        self.title = title

    def __str__(self):
        # represents like f(x, y) = x^2 + y^2 + 3xy
        varlist = (x for x in self.func.varname)
        return f'{self.title}({", ".join(self.func.varname)}) = {self.func}'

    __repr__ = __str__

    def sample(self, start, stop, unit, digit=None, formated=False):
        # sample a set of points of the function from a range (start to stop)
        # split into number of unit, digit is the digits after the decimal point,
        # if formated is set to True, the result will be shown in terms of fractions
        each = (stop - start) / unit
        points = [(rounding(start + i * each,
                            digit), rounding(self.val(start + i * each),
                                             digit)) for i in range(unit + 1)]
        return points

    def samples(self, start, stop, unit, digit=None, formated=False):
        # this function is for variables more than 1 case
        # start, stop must be tuples or lists, unit should be a number (the number
        # of the values that each variable picks should be the same)
        numvars = len(self.func.varname)
        each = [(stop[i] - start[i]) / unit for i in range(numvars)]
        points = [
            ([rounding(start[k] + i * each[k], digit) for k in range(numvars)],
             rounding(
                 self.val([start[k] + i * each[k]
                           for k in range(numvars)]), digit))
            for i in range(unit + 1)
        ]
        return points

    def draw(self, start, stop, unit, digit):
        # draw  the function's graph in a standard point sets form
        pass

    def domain(self):
        pass

    def codomain(self):
        pass

    def solveat(self, number):
        # find the solutions of the equation built as
        # function = number (number could be either numbers or polynomials)
        pass

    def val(self, *values):
        return self.func.val(*values)

    def __call__(self, *values):
        return self.val(*values)


def func(poly_obj, title='f'):
    return Func(poly_obj, title)


def topoly(x):
    if not isinstance(x, polynomial):
        return poly(str(x))
    else:
        return x


def ft(a):
    if '/' not in a:
        return 'a fraction must contain at least one "/"'
    ind = a.index('/')
    num = poly(a[:ind])
    deno = poly(a[ind + 1:])
    if deno == poly('1'):
        return num
    return fract(num, deno)


class fract:
    def __init__(self, num, deno):
        if not isinstance(num, polynomial):
            num = poly(str(num))
        if not isinstance(deno, polynomial):
            deno = poly(str(deno))
        self.num = num
        self.deno = deno

    def __str__(self):
        numstr = f'({self.num.__str__()})' if len(
            self.num.colist[0]) > 1 else self.num.__str__()
        denostr = f'({self.deno.__str__()})' if len(
            self.deno.colist[0]) > 1 else self.deno.__str__()
        result = f'{numstr}/{denostr}'
        return result

    __repr__ = __str__

    def comp(self):
        return self.num / self.deno

    def __mul__(self, other):
        if isinstance(other, fract):
            temp = copy.deepcopy(self)
            temp2 = copy.deepcopy(other)
            result = fract(temp.num * other.num, temp.deno * other.deno)
            if result.num == poly('0'):
                return 0
            if result.deno == poly('1'):
                return result.num
            return result
        other = topoly(other)
        temp = copy.deepcopy(self)
        temp.num *= other
        if temp.num == poly('0'):
            return 0
        if temp.deno == poly('1'):
            return temp.num
        return temp

    def __rmul__(self, other):
        return self * other

    def __pow__(self, number):
        if number == 0:
            return 1
        if number < 0:
            return 1 / self**(abs(number))
        temp = copy.deepcopy(self)
        for i in range(number - 1):
            temp *= self
        return temp

    def __xor__(self, number):
        return self.__pow__(number)

    def __add__(self, other):
        if isinstance(other, fract):
            temp = copy.deepcopy(self)
            temp2 = copy.deepcopy(other)
            if temp.deno == temp2.deno:
                result = fract(temp.num + temp2.num, temp.deno)
            else:
                result = fract(temp.num * temp2.deno + temp2.num * temp.deno,
                               temp.deno * temp2.deno)
            if result.num == poly('0'):
                return 0
            if result.deno == poly('1'):
                return result.num
            return result
        other = topoly(other)
        temp = copy.deepcopy(self)
        temp2 = copy.deepcopy(other)
        temp2.fraction.append(self)
        return temp2

    def __sub__(self, other):
        if isinstance(other, fract):
            result = self + other * (-1)
            if result.num == poly('0'):
                return 0
            if result.deno == poly('1'):
                return result.num
            return result
        other = topoly(other)
        return self + other * (-1)

    def __neg__(self):
        temp = copy.deepcopy(self)
        temp.num *= -1
        return temp

    def __truediv__(self, other):
        if isinstance(other, fract):
            temp, temp2 = copy.deepcopy(self), copy.deepcopy(other)
            if self.deno == other.deno:
                temp.deno = temp2.num
            else:
                temp.num *= temp2.deno
                temp.deno *= temp2.num
            if temp.deno == poly('1'):
                return temp.num
            return temp
        else:
            other = topoly(other)
            temp = copy.deepcopy(self)
            temp.deno *= other
            if temp.deno == poly('1'):
                return temp.num
            return temp

    def __eq__(self, other):
        if not isinstance(other, fract):
            other = ft(str(other))
        return self.num == other.num and self.deno == other.deno

    def recipro(self):
        temp = copy.deepcopy(self)
        temp.num, temp.deno = temp.deno, temp.num
        if temp.deno == poly('1'):
            return temp.num
        return temp

    def __invert__(self):
        return self.recipro()

    def __rtruediv__(self, other):
        return ~(self / other)

    def __radd__(self, other):
        return self + other

    def __rsub__(self, other):
        return -(self - other)

    def val(self, *values):
        temp = copy.deepcopy(self)
        wholevar = temp.num.varname + [
            x for x in temp.deno.varname if x not in temp.num.varname
        ]
        numstart, numend = wholevar.index(
            temp.num.varname[0]), wholevar.index(temp.num.varname[-1]) + 1
        numvar = list(values[numstart:numend])
        denostart, denoend = wholevar.index(
            temp.deno.varname[0]), wholevar.index(temp.deno.varname[-1]) + 1
        denovar = list(values[denostart:denoend])
        return temp.num.val(numvar) / temp.deno.val(denovar)


E = 2.718281828459045


def log(num, base=E, precision=None):
    if precision is None:
        precision = 5 * num
    if base == E:
        y = (num - 1) / (num + 1)
        se = seq([lambda n: 1 / (2 * n + 1), lambda n: 2 * n], [1, y],
                 types=[None, 'exp'])
        result = 2 * y * sum([se.at(x) for x in range(precision)])
        return float(fractions.Fraction(result).limit_denominator())
    else:
        if base == 1:
            return None
        result = log(num) / log(base)
        return float(fractions.Fraction(result).limit_denominator())


theta = 'theta'
r = 'r'
polar = 'polar'
radian = 'radian'
degree = 'degree'


class cfunc:
    # complex-valued functions, let z = x+iy (x,y in R),
    # then f(z) = u(x,y) + iv(x,y) is a complex-valued function,
    # where u and v are real-valued functions.
    def __init__(self, u, v):
        # here u and v could be polynomials or functions

        if len(u.colist) == 1:
            u.colist.append([1])
        if len(u.powerlist) == 1:
            u.powerlist.append([0])
        if len(v.colist) == 1:
            if v.varname[0] == u.varname[0]:
                v.colist.append([1])
            else:
                v.colist.insert(0, [1])
        if len(v.powerlist) == 1:
            if v.varname[0] == u.varname[0]:
                v.powerlist.append([0])
            else:
                v.powerlist.insert(0, [0])
        u.varname = ['x', 'y']
        v.varname = ['x', 'y']
        u.updatedict()
        v.updatedict()
        self.u = u
        self.v = v

    def CR(self):
        # check if the function satisfies Cauchy-Riemann equations
        return self.u.diff('x') == self.v.diff('y') and self.u.diff(
            'y') == -self.v.diff('x')

    def __str__(self):
        return f'f(x+iy) = {self.u} + i*({self.v})'

    __repr__ = __str__


class comp:
    # complex number
    def __init__(self, re=None, im=None, letter='i'):
        if im is None:
            if isinstance(re, str):
                re1 = None
                im1 = None
                re = re.replace(' ', '')
                reco = 1
                for k in range(len(re)):
                    if re[k] in ['+', '-']:
                        if k == 0:
                            continue
                        re1 = eval(re[:k]) * reco
                        try:
                            im1 = eval(re[k:-1])
                        except:
                            if re[k] == '-':
                                im1 = -1
                            else:
                                im1 = 1
                        break
                if re1 is None:
                    if re[-1].isalpha():
                        re1 = 0
                        try:
                            im1 = eval(re[:-1])
                        except:
                            if re[0] == '-':
                                im1 = -1
                            else:
                                im1 = 1
                    else:
                        re1 = eval(re)
                        im1 = 0
                self.re = re1
                self.im = im1
                self.letter = re[-1]
            else:
                self.re = re
                self.im = 0
                self.letter = letter
        else:
            self.re = re
            self.im = im
            self.letter = letter

    def __call__(self, mode=r, ty=radian):
        if mode == r:
            return math.sqrt(self.re**2 + self.im**2)
        elif mode == theta:
            a = self.re
            b = self.im
            if a == 0:
                return math.radians(90) if ty == radian else 90
            elif a > 0:
                return math.atan(b / a) if ty == radian else math.degrees(
                    math.atan(b / a))
            else:
                return math.atan(b / a) + math.radians(
                    180) if ty == radian else math.degrees(math.atan(b /
                                                                     a)) + 180
        elif mode == polar:
            return f'{self()}e^i{self(theta)}'

    def __str__(self):
        if self.re == 0 and self.im == 0:
            return '0'
        return f'''{self.re if self.re != 0 else ""}{" + " if self.re != 0
               and self.im != 0 else ""}{self.im if self.im not in
               [0,1,-1] else 
               dict({0:"", 1: "", -1:"-"})[self.im]}{self.letter 
               if self.im != 0 else ""}'''

    def __abs__(self):
        return math.sqrt(self.re**2 + self.im**2)

    def __getitem__(self, ind):
        if ind == 0:
            return self.re
        elif ind == 1:
            return self.im

    def __setitem__(self, ind, value):
        if ind == 0:
            self.re = value
        elif ind == 1:
            self.im = value

    def letter(self, new):
        self.letter = new

    __repr__ = __str__

    def __add__(self, other):
        if not isinstance(other, comp):
            return comp(self.re + other, self.im, self.letter)
        return comp(self.re + other.re, self.im + other.im, self.letter)

    def __sub__(self, other):
        return self + -other

    def __neg__(self):
        return comp(-self.re, -self.im, self.letter)

    def __mul__(self, other):
        if not isinstance(other, comp):
            return comp(self.re * other, self.im * other, self.letter)
        return comp(self.re * other.re - self.im * other.im,
                    self.re * other.im + self.im * other.re, self.letter)

    def __pow__(self, num):
        if num == 0:
            return 1
        else:
            if num > 0:
                temp = self
                for i in range(num - 1):
                    temp *= self
                return temp
            else:
                return 1 / (self**-num)

    def __xor__(self, num):
        return self.__pow__(num)

    def __rpow__(self, other):
        first = other**self.re
        base = other**self.im
        second = comp(math.cos(math.log(base)), math.sin(math.log(base)),
                      self.letter)
        return first * second

    def __eq__(self, other):
        if isinstance(other, comp):
            return self.re == other.re and self.im == other.im
        else:
            return self.im == 0 and self.re == other

    def __radd__(self, other):
        return self + other

    def __rmul__(self, other):
        return self * other

    def __rsub__(self, other):
        return -(self - other)

    def __rxor__(self, other):
        return self.__rpow__(other)

    def repro(self):
        a = self.re
        b = self.im
        return comp(a / (a**2 + b**2), -b / (a**2 + b**2), self.letter)

    def __truediv__(self, other):
        if not isinstance(other, comp):
            return comp(self.re / other, self.im / other, self.letter)
        return self * other.repro()

    def __rtruediv__(self, other):
        return (self / other).repro()

    def conj(self):
        return comp(self.re, -self.im, self.letter)

    def __invert__(self):
        return self.conj()

    def point(self, ty=tuple):
        if ty == tuple:
            return (self.re, self.im)
        elif ty == list:
            return [self.re, self.im]
        elif ty == dict:
            return {'x': self.re, 'y': self.im}


def c(num):
    # transform a string of number to a complex number
    re = 0
    im = 0
    num = num.replace(' ', '')
    for k in range(len(num)):
        if not num[k].isdigit():
            re = eval(num[:k])
            im_part = num[k:-1]
            if len(im_part) == 1:
                im_part += '1'
            im = eval(im_part)
            break
    return comp(re, im, num[-1])


def findside(a, t, mode='right'):
    # t must be an index that a[t] == '(' when mode is 'right'
    # or a[t] == ')' when mode is 'left'
    if mode == 'right':
        left = 1
        right = 0
        result = None
        num = a.count('(')
        for i in range(t + 1, len(a)):
            if a[i] == '(':
                left += 1
            elif a[i] == ')':
                right += 1
            if left == right:
                result = i
                break
        if left == num:
            ind1 = a[result:].find('+') + result - 1
            if ind1 == -1:
                ind1 = result
            ind2 = a[result:].find('-') + result - 1
            if ind2 == -1:
                ind2 = ind1
            return max(result, min(ind1, ind2))
        return result
    if mode == 'left':
        left = 0
        right = 1
        result = None
        num = a.count('(')
        for i in range(t - 1, -1, -1):
            if a[i] == '(':
                left += 1
            elif a[i] == ')':
                right += 1
            if left == right:
                result = i
                break
        if left == num:
            ind1 = a[:result].rfind('+') + 1
            if ind1 == 0:
                ind1 = result
            ind2 = a[:result:].rfind('-') + 1
            if ind2 == 0:
                ind2 = ind1
            return min(result, max(ind1, ind2))
        return result


def leftbracket(a):
    if '(' in a:
        if a[0] != '(':
            a = '(' + a
            ind = a[1:].find('(') + 1
            if '+' in a:
                ind1 = a.find('+')
            else:
                ind1 = ind
            if '-' in a:
                ind2 = a.find('-')
            else:
                ind2 = ind1
            indmin = min(ind, ind1, ind2)
            a = a[:indmin] + ')' + a[indmin:]
    return a


def bracket(a):
    t = 0
    while t < len(a):
        if t > 0:
            if a[t] == '(':
                if a[t - 1] not in ['+', '-', '(', ')']:
                    ind1 = a[:t].rfind('+') + 1
                    if ind1 == 0:
                        ind1 = 0
                    ind2 = a[:t].rfind('-') + 1
                    if ind2 == 0:
                        ind2 = ind1
                    ind3 = a[:t].rfind(')')
                    if ind3 == -1:
                        ind3 = ind2
                    indleft = a[:t].rfind('(')
                    if indleft <= max(ind1, ind2):
                        ind = max(ind1, ind2, ind3)
                        a = a[:ind] + '(' + a[ind:]
                        t += 1
                        side = findside(a, t)
                        a = a[:side + 1] + ')' + a[side + 1:]
                        a = a[:t] + ')' + a[t:]
                        a = a[:ind + 1] + '(' + a[ind + 1:]
                        t = side + 2
                        t += 2
                        continue
            elif a[t] == ')':
                if t + 1 < len(a):
                    if a[t + 1] not in ['+', '-', '(', ')']:
                        ind1 = a[t:].find('+') + t - 1
                        if ind1 == t - 2:
                            ind1 = len(a)
                        ind2 = a[t:].find('-') + t - 1
                        if ind2 == t - 2:
                            ind2 = ind1
                        ind3 = a[t:].find('(') + t - 1
                        if ind3 == t - 2:
                            ind3 = ind2
                        indright = a[t + 1:].find(')') + t + 1
                        if indright >= min(ind1 + 1,
                                           ind2 + 1) or indright == t:
                            ind = min(ind1, ind2, ind3)
                            a = a[:ind + 1] + ')' + a[ind + 1:]
                            side = findside(a, t, 'left')
                            if side != 0:
                                side -= 1
                            a = a[:side + 1] + '(' + a[side + 1:]
                            a = a[:t + 2] + '(' + a[t + 2:]
                            a = a[:ind + 3] + ')' + a[ind + 3:]
                            t = ind + 3
                            t += 2
                            continue

        t += 1
    return a


def poly(a, root=1):
    # please solve the issue that poly('(2x)x') or poly('3x(2x)') cannot be analyzed 2019.8.20 13:49
    ''' Analyze the structure of given string of polynomial and construct
        a polynomial object with handful attributes and data. Return the
        constructed polynomial object if the given string is a valid form
        of polynomial, otherwise return the reason why it is invalid. '''
    if not isinstance(a, str):
        return a
    try:
        result = float(a)
        if not result.is_integer():
            return polynomial(colist=[result], powerlist=[0])
    except:
        pass
    a = a.replace(' ', '').replace('*', '').replace('+-', '-')
    if '(' in a:
        a = bracket(a)
        t = 0
        while t < len(a):
            if a[t] == '(':
                if t != 0:
                    start1 = t
                    start2 = 0
                    if a[t - 1] not in ['+', '-']:
                        operator1 = '*'
                    else:
                        operator1 = a[t - 1]
                        start1 -= 1
                    side = findside(a, t)
                    if side + 1 < len(a):
                        if side + 1 == len(a) - 1:
                            operator2 = ''
                        else:
                            if a[side + 1] not in ['+', '-']:
                                operator2 = '*'
                            else:
                                operator2 = a[side + 1]
                                start2 += 1
                    else:
                        operator2 = ''
                    if operator2 == '':
                        after = ''
                    else:
                        after = f'poly("{a[side+1+start2:]}")'
                    return eval(
                        f'poly("{a[:start1]}") {operator1} poly("{a[t+1:side]}") {operator2} {after}'
                    )
                start2 = 0
                side = findside(a, t)
                if side + 1 < len(a):
                    if side + 1 == len(a) - 1:
                        operator2 = ''
                    else:
                        if a[side + 1] not in ['+', '-']:
                            operator2 = '*'
                        else:
                            operator2 = a[side + 1]
                            start2 += 1
                else:
                    operator2 = ''
                if operator2 == '':
                    after = ''
                else:
                    after = f'poly("{a[side+1+start2:]}")'
                return eval(f'poly("{a[t+1:side]}") {operator2} {after}')
            t += 1
    if a[0] != '-':
        a = '+' + a
    a += '+'
    varname = []
    equation = None
    special = []
    varind = []
    opeind = []
    nonexp = []
    newope = False
    i = 0
    while i < len(a):
        if a[i].isalpha() and a[i] not in varname:
            if i + 2 in range(len(a)):
                if a[i:i +
                     3] in ['sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'log']:
                    special.append(i)
                    i += 3
                    continue
            varname.append(a[i])
        i += 1
    varnumber = len(varname)
    if varnumber == 0:
        coefficient = a[1:-1] if a[0] != '-' else a[:-1]
        try:
            coefficient = eval(coefficient)
        except:
            return 'this is considered to be a polynomial with only constant term, but some of the terms is not considered as a constant or the operation is not + or -, note that the operation * or / is not allowed here, only + and - is considered to be valid, if you want to show multiply as *, just put them together, for example, xy means x*y, and to show division you can multiply by its reciprocal, for example, you can write xy^-1 instead of x/y, which is in more general form.'
        colist = [coefficient]
        powerlist = [0]
        varname = ['x']
    else:
        colist = [[] for t in range(varnumber)]
        powerlist = [[] for t in range(varnumber)]
        for k in range(len(a)):
            if a[k] in ['+', '-']:
                valid = True
                if k - 1 in range(len(a)):
                    if a[k - 1] == '^':
                        valid = False
                if valid:
                    nonco = None
                    for m in range(k, len(a)):
                        if a[m] in ['+', '-'] and m != k:
                            nonco = m
                            break
                    if nonco != None and all(x not in varname
                                             for x in a[k:nonco]):
                        coefficient = a[k:nonco]
                        try:
                            coefficient = eval(coefficient)
                        except:
                            return 'the constant term is not a number'
                        colist[0].append(coefficient)
                        for t in range(1, len(colist)):
                            colist[t].append(1)
                        for h in powerlist:
                            h.append(0)
                        continue
                    most = max([len(q) for q in powerlist])
                    for j in powerlist:
                        if len(j) < most:
                            j.append(0)
                    found = False
                    for m in range(k, len(a)):
                        if a[m] in varname:
                            found = True
                            ind = m
                            ind2 = varname.index(a[m])
                            break
                    if found:
                        coefficient = a[k + 1:m] if a[k] == '+' else a[k:m]
                        if coefficient == '':
                            for r in range(len(colist)):
                                colist[r].append(1)
                        elif coefficient == '-':
                            colist[0].append(-1)
                            for r in range(1, len(colist)):
                                colist[r].append(1)
                        else:
                            try:
                                coefficient = eval(coefficient)
                            except:
                                pass
                            colist[ind2].append(coefficient)
                            for r in range(len(colist)):
                                if r != ind2:
                                    colist[r].append(1)
            elif a[k] == '^':
                ind1 = (a[k:].find('+') + k) if a[k:].find('+') != -1 else -1
                if k + 2 in range(len(a)):
                    large = True
                    if a[k + 1:k + 3] == '-1':
                        if k + 3 in range(len(a)):
                            if a[k + 3].isdigit():
                                large = False
                        if large:
                            whichvar = varname.index(a[k - 1])
                            if len(powerlist[whichvar]) == len(
                                    colist[whichvar]):
                                powerlist[whichvar][-1] -= 1
                            else:
                                powerlist[whichvar].append(-1)
                            continue
                        else:
                            ind2 = (a[k +
                                      2:].find('-')) + k + 2 if a[k + 2:].find(
                                          '-') != -1 else ind1
                    else:
                        ind2 = (a[k + 2:].find('-')) + k + 2 if a[k + 2:].find(
                            '-') != -1 else ind1
                found = False
                for m in range(k, len(a)):
                    if a[m] in varname:
                        found = True
                        ind3 = m
                        break
                if not found:
                    ind3 = -1
                if ind1 == -1 and ind2 == -1:
                    return 'invalid representation of polynomial, the power does not carry anything'
                else:
                    if ind1 == -1:
                        ind = ind2
                    elif ind2 == -1:
                        ind = ind1
                    else:
                        ind = min(ind1, ind2)
                    if ind3 != -1 and ind3 < ind:
                        ind = ind3
                    power = a[k + 1:ind]
                    try:
                        power = eval(power)
                    except:
                        return 'construction is not successful because the power is not a number'
                    whichvar = varname.index(a[k - 1])
                    if len(colist[whichvar]) == len(powerlist[whichvar]):
                        powerlist[whichvar][-1] += power
                    else:
                        powerlist[whichvar].append(power)
            elif a[k] in varname:
                if k + 1 in range(len(a)):
                    if a[k + 1] != '^':
                        whichvar = varname.index(a[k])
                        if len(colist[whichvar]) == len(powerlist[whichvar]):
                            powerlist[whichvar][-1] += 1
                        else:
                            powerlist[whichvar].append(1)
                else:
                    whichvar = varname.index(a[k])
                    if len(colist[whichvar]) == len(powerlist[whichvar]):
                        powerlist[whichvar][-1] += 1
                    else:
                        powerlist[whichvar].append(1)
    if varnumber == 1:
        colist = colist[0]
        powerlist = powerlist[0]
    return polynomial(colist, powerlist, varname, root, equation)


def standardize(a):
    a.standardize()


def updatedict(a):
    a.updatedict()


def concat(*po):
    if len(po) == 0:
        return poly('0')
    else:
        if len(po) == 1 and isinstance(po[0], list):
            if len(po[0]) == 0:
                return poly('0')
            elif not all((isinstance(x, polynomial) or isinstance(x, fract))
                         for x in po[0]):
                for k in range(len(po[0])):
                    if not isinstance(po[0][k], polynomial):
                        if not isinstance(po[0][k], fract):
                            po[0][k] = poly(str(po[0][k]))
                return concat(po[0])
            else:
                fraction = []
                result = ''
                for i in po[0]:
                    if isinstance(i, fract):
                        fraction.append(i)
                    else:
                        current = str(i)
                        if current[0] == '-':
                            result += '-' + current[1:]
                        else:
                            result += '+' + current
                if result[0] == '+':
                    result = result[1:]
                result = topoly(result)
                result.fraction = fraction
                return result
        else:
            po = list(po)
            return concat(po)


def sums(*po):
    if len(po) == 0:
        return poly('0')
    else:
        if len(po) == 1 and isinstance(po[0], list):
            po = po[0]
            if len(po) == 0:
                return poly('0')
            else:
                for k in range(len(po)):
                    if isinstance(po[k], str):
                        po[k] = poly(po[k])
                temp = poly('0')
                fraction = []
                for i in po:
                    if isinstance(i, fract):
                        fraction.append(i)
                    else:
                        temp += i
                if type(temp) == polynomial:
                    temp.fraction = fraction
                return temp
        else:
            po = list(po)
            return sums(po)


def mult(*po):
    if len(po) == 0:
        return poly('0')
    else:
        if len(po) == 1 and isinstance(po[0], list):
            if len(po[0]) == 0:
                return poly('0')
            else:
                po1 = [poly(k) if type(k) == str else k for k in po[0]]
                temp = po1[0]
                for i in po1[1:]:
                    temp *= i
                return temp
        else:
            po = list(po)
            return mult(po)


def cat(self, other, mode='+'):
    return self.cat(other, mode)


def simplify(a, to_poly=False):
    a = topoly(a)
    return a.simplify(to_poly)


def isls(a):
    return type(a) in [list, tuple, set]


def polyls(a, standard=None):
    if standard is None:
        return a if isls(a) else [a]
    return a + [a[-1] for i in range(standard - len(a))] if isls(a) else [
        a for i in range(standard)
    ]


def cby(obj, func, dr=0):
    if dr == 0:
        temp = obj[0]
        for k in obj[1:]:
            temp = func(temp, k)
    else:
        temp = obj[-1]
        for k in range(len(obj) - 2, -1, -1):
            temp = func(temp, obj[k])
    return temp


def fib(n):
    a, b = 0, 1
    for i in range(n):
        a, b = b, a + b
    return b


# this is a fibonacci sequence lambda function written in one line
fib2 = lambda n, alist=[0, 1]: ([
    alist.__setitem__(1, alist[0] + alist[1]) or alist.__setitem__(
        0, alist[1] - alist[0]) for i in range(n)
], alist.copy(), alist.__setitem__(0, 0) or alist.__setitem__(1, 1))[1][1]
fibseq = lambda n: [(lambda n, alist=[0, 1]: ([
    alist.__setitem__(1, alist[0] + alist[1]) or alist.__setitem__(
        0, alist[1] - alist[0]) for i in range(n)
], alist.copy(), alist.__setitem__(0, 0) or alist.__setitem__(1, 1))[1][1])(i)
                    for i in range(n)]


class formula:
    def __init__(self, init, func, hasn=False):
        self.init = init
        self.func = func if type(func) != str else tofunc(func)
        self.length = 1 if (not isls(init)) else len(init)
        self.hasn = hasn
        # if hasn is True, this formula will treat the last variable in
        # func as n when doing calculations
    def ls(self, num):
        init = self.init
        func = self.func
        N = self.length

        result = [i for i in init] if isls(init) else [init]
        if num + 1 <= N:
            return result[:num + 1]
        M = num + 2 - N
        if not self.hasn:
            for i in range(1, M):
                result.append(func(*result[-N:]))
        else:
            count1 = N - 1
            for i in range(1, M):
                result.append(func(*result[-N:], count1))
                count1 += 1
        return result

    def __call__(self, num):
        return self.ls(num)[-1]

    def sums(self, num):
        return sum(self.ls(num))

    def mult(self, num):
        return mult(self.ls(num))

    def combine(self, func, num):
        return cby(self.ls(num), func)

    def __repr__(self):
        return str(self.ls(10))[1:-1] + ', ...'

    def __contains__(self, x):
        i = 0
        while True:
            value = self(i)
            if value == x:
                return True
            elif value > x:
                return False
            i += 1

    def find(self, x):
        i = 0
        while True:
            value = self(i)
            if value == x:
                return i
            elif value > x:
                return -1
            i += 1

    def number(self, x):
        result = self.find(x)
        return result + 1 if result != -1 else -1

    def converge(self, tol=1e-20, number=1000, ind=0):
        for i in range(number):
            current = self(i)
            if abs(self(i + 1) - current) < tol:
                return current if ind == 0 else (current, i)
        return 'this series diverges in the given tolerance and number of terms.'

    def isconverge(self, tol=1e-20, number=1000):
        for i in range(number):
            current = self(i)
            if abs(self(i + 1) - current) < tol:
                return True
        return False


def fac(num):
    if num == 0:
        return 1
    return mult([i for i in range(1, num + 1)])


class seq:
    def __init__(self,
                 rules,
                 obj=None,
                 start=0,
                 stop=None,
                 types=None,
                 way='sum',
                 symbol=None,
                 name=None,
                 coefway='mult'):
        obj = polyls(obj)
        obj = [
            poly(x) if type(x) == str else (1 if x is None else x) for x in obj
        ]
        self.obj = obj
        N = len(obj)
        rules = polyls(rules, N)
        self.rules = [tofunc(i) if type(i) == str else i for i in rules]
        self.start = polyls(start, N)
        self.stop = polyls(stop, N)
        self.types = polyls(types, N)

        if symbol is None:
            if way == 'sum':
                symbol = '+'
            elif way == 'mult':
                symbol = '*'
            else:
                symbol = '+'
        self.way = tofunc(
            way) if type(way) == str and way not in ['sum', 'mult'] else way
        self.coefway = tofunc(coefway) if type(
            coefway) == str and coefway not in ['sum', 'mult'] else coefway
        self.symbol = symbol
        self.name = name

    def __matmul__(self, num):
        return self.show(num)

    def __len__(self):
        return len(self.obj)

    def __and__(self, value, ind=None):
        new = copy.deepcopy(self)
        if ind is None:
            value = polyls(value, len(new.obj))
            value = [poly(x) if type(x) == str else x for x in value]
            new.obj = value
        else:
            if type(value) == str:
                value = poly(value)
            new.obj[ind] = value
        return new

    def at(self, num):
        obj, types, rules, start, coefway = self.obj, self.types, self.rules, self.start, self.coefway
        if coefway == 'mult':
            result = mult([
                self.objat(obj[i], rules[i], start[i] + num, types[i])
                for i in range(len(self))
            ])
        elif coefway == 'sum':
            result = sums([
                self.objat(obj[i], rules[i], start[i] + num, types[i])
                for i in range(len(self))
            ])
        else:
            result = coefway(*[
                self.objat(obj[i], rules[i], start[i] + num, types[i])
                for i in range(len(self))
            ])
        if type(result) != polynomial:
            return result
        if result.powerlist == [[0]]:
            return eval(str(result))
        else:
            return result

    def indat(self, ind, num):
        return self.objat(self.obj[ind], self.rules[ind],
                          self.start[ind] + num, self.types[ind])

    def objat(self, obj, rules, num, types):
        if types is None:
            return obj * rules(num)
        elif types == 'exp':
            return obj**(rules(num))
        elif types == 'coef':
            return rules(num) * obj
        elif types == 'self':
            return rules(obj, num)
        else:
            return obj * rules(num)

    def __repr__(self):
        return f' {self.symbol} '.join([str(self.at(x))
                                        for x in range(5)] + ['...'])

    def show(self, num):
        return f' {self.symbol} '.join([str(self.at(x))
                                        for x in range(num)] + ['...'])

    def __call__(self, num):
        if self.way == 'sum':
            return sum([self.at(x) for x in range(num)])
        elif self.way == 'mult':
            return mult([self.at(x) for x in range(num)])
        else:
            return cby([self.at(x) for x in range(num)], self.way)

    def __getitem__(self, ind):
        return self.at(ind)

    def ls(self, num, ind=None):
        if ind is None:
            return [self.at(x) for x in range(num)]
        else:
            return [self.indat(ind, x) for x in range(num)]

    def __contains__(self, x):
        i = 0
        while True:
            value = self[i]
            if value == x:
                return True
            elif value > x:
                return False
            i += 1

    def find(self, x):
        i = 0
        while True:
            value = self[i]
            if value == x:
                return i
            elif value > x:
                return -1
            i += 1

    def number(self, x):
        result = self.find(x)
        return result + 1 if result != -1 else -1

    def converge(self, tol=1e-20, number=1000, ind=0, only=0):
        # check if the series converges to a number
        # within a given tolerance and times.

        # tol: if the difference between a current result
        # and next result is less than tol, then this series
        # converges, return current result

        # number: the maximum number of times to check if the
        # series converges

        # ind: if ind is 0, only returns the number this series
        # converges to, if ind is not 0, returns the number with
        # the index when it satisfies the tol (if this series does
        # converge within the given number of times)

        # only: is only is 0, then does not make the sum
        # (or the way of combination defined by users) of
        # the terms, just consider if the terms itself
        # converges to a number or not.
        if only == 0:
            for i in range(number):
                current = self(i)
                if abs(self(i + 1) - current) < tol:
                    return current if ind == 0 else (current, i)
            return 'this series diverges in the given tolerance and number of terms.'
        else:
            for i in range(number):
                current = self[i]
                if abs(self[i + 1] - current) < tol:
                    return current if ind == 0 else (current, i)
            return 'this series diverges in the given tolerance and number of terms.'

    def isconverge(self, tol=1e-20, number=1000, only=0):
        if only == 0:
            for i in range(number):
                current = self(i)
                if abs(self(i + 1) - current) < tol:
                    return True
            return False
        else:
            for i in range(number):
                current = self[i]
                if abs(self[i + 1] - current) < tol:
                    return True
            return False


def variables(var, separator=' '):
    if ' ' not in var and len(var) > 1:
        return [poly(i) for i in list(var)]
    else:
        return [poly(i) for i in var.split(separator)]


def tofunc(a):
    # transfrom a string in format '[var1, var2, ...] (-> or | or :) [expressions]'
    # to a function lambda [var1, var2, ...] : [expressions]
    for separator in ['=', '->', '|', ':']:
        if separator in a:
            result = a.split(separator)
            return eval(f'lambda {result[0]} : {result[1]}')
    return 'no valid separator was found'


def factorize(a, merge=False):
    if a == 0:
        if not merge:
            return [0]
        else:
            return ['0^1']
    elif a < 0:
        temp = factorize(-a, merge)
        if not merge:
            return [-temp[0]] + temp[1:]
        else:
            return ['-' + temp[0]] + temp[1:]
    else:
        result = [1]
        last = 3
        while True:
            k = divmod(a, 2)
            if k[1] == 0:
                result.append(2)
                a = k[0]
            else:
                break
        while a != 1:
            found = 0
            N = int(math.sqrt(a)) + 1
            for i in range(last, N, 2):
                current = divmod(a, i)
                if current[1] == 0:
                    result.append(i)
                    a = current[0]
                    found = 1
                    last = i
                    break
            if found == 0:
                result.append(a)
                break
        if merge:
            q = set(result)
            merged = [f'{j}^{result.count(j)}' for j in q]
            return merged
        else:
            return result


def factorize_show(a, merge=False):
    if a == 0:
        print('find a factor: 0')
        if not merge:
            return [0]
        else:
            return ['0^1']
    elif a < 0:
        result = [-1]
        print('find a factor: -1', flush=True)
        temp = factorize_show(-a, merge)
        if not merge:
            return [-temp[0]] + temp[1:]
        else:
            return ['-' + temp[0]] + temp[1:]
    else:
        result = [1]
        print('find a factor: 1', flush=True)
        last = 3
        while True:
            k = divmod(a, 2)
            if k[1] == 0:
                result.append(2)
                a = k[0]
                print('find a factor: 2', flush=True)
            else:
                break
        while a != 1:
            found = 0
            N = int(math.sqrt(a)) + 1
            for i in range(last, N, 2):
                current = divmod(a, i)
                if current[1] == 0:
                    result.append(i)
                    a = current[0]
                    found = 1
                    last = i
                    print(f'find a factor: {i}', flush=True)
                    break
            if found == 0:
                result.append(a)
                print(f'find a factor: {a}', flush=True)
                break
        if merge:
            q = set(result)
            merged = [f'{j}^{result.count(j)}' for j in q]
            return merged
        else:
            return result


P = p = poly