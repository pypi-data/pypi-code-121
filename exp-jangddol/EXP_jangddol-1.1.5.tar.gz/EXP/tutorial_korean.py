from exp import Shvar
from exp_plot import superplt
import uncertainties
from uncertainties import ufloat
from uncertainties.umath import *
import matplotlib.pyplot as plt
import numpy as np

# 이 파일은 Shvar 라이브러리의 튜토리얼입니다.
# 이 튜토리얼은 python IDE인 spyder를 기준으로 작성되었습니다.
# 혹여나 다른 IDE로 작동하시는 분은 설정에 유의해주시기 바랍니다.

# 이 튜토리얼은 각 함수마다 셀이 나뉘어져 있습니다.
    # spyder를 기준으로 ctrl+Enter를 하면 선택되어있는 셀만 실행할 수 있습니다.
    # 반드시 셀 순서를 지켜서 실행해주시기 바랍니다.

# 목차
    # 1. 세팅
    # 2. 변수설정
    # 3. 백업 & 백업 파일 불러오기
    # 4. 피팅
    # 5. plot 출력
    # 6. 변수간의 계산
    # 7. class variable 상세 내용
    

# 1. 세팅
    # exp.py와 exp_plot.py를 한 파일 안에 두어야 합니다.
    # 추가적인 세팅 없이 사용하고 싶으시다면, 다른 라이브러리가 저장되는 경로에 다른 라이브러리와 동일한 방법으로 저장해 주시면 되겠습니다.
    # 예시 : C:\Users\jang9\AppData\Local\Programs\Python\Python39\Lib\site-packages
    # 그렇지 않고 다른 파일에 해당 파일들을 저장하시는 경우, IDE의 세부설정에 들어가서 path에 추가해주시기 바랍니다.
    # 이 라이브러리를 사용할때는 이 파일이 import하고 있는 라이브러리 6개를 기본으로 import하고 시작해주시기 바랍니다.


# 2. 변수설정
    # Shvar 클래스의 오브젝트를 선언하고 싶다면 다음과 같이 코드를 작성합니다.
# %% 클래스 오브젝트 선언

A = Shvar()

# %%
    # 이렇게 되면 A는 모종의 상자처럼 작동하게 되며, 이 안에 알맞는 데이터를 넣음으로써, 자유자재로 운용할 수 있게 됩니다.
    
    # Shvar 클래스에서 사용할 수 있는 타입은 다음이 있습니다.
        # 1. data의 리스트를 넣어서 ufloat 하나를 만드는 타입 (setufdata)
        # 2. data의 리스트의 리스트를 넣어서 ufloat의 리스트를 만드는 타입 (setufdatalist)
        # 3. ufloat을 넣거나 meanvalue와 uncertainty를 넣어서 ufloat 하나를 만드는 타입 (simpleuf)
        # 4. ufloat의 리스트를 넣거나 meanvalue의 리스트와 uncertianty의 리스트를 넣어서 ufloat의 리스트를 만드는 타입 (simpleuflist)
        # 5. 수 하나를 넣는 타입 (simplescalar)
        # 6. 수의 리스트를 넣는 타입 (simplescalarlist)
        # 7. 두 개의 리스트를 묶어서 넣는 타입 (linear_rel)
    # 시험삼아 setufdata를 이용해 Shvar 클래스 변수를 생성해보겠습니다.
# %% setufdata 예시

Measure = [11.2, 10.8, 10.0, 11.5, 10.5]
A.setufdata(Measure)
print(A.uf)

# %%
    # setufdata 함수를 통해 Shvar 클래스 오브젝트(A)에 어떤 리스트를 넣어주면, 자동으로 평균과 uncertainty를 구해 저장을 해둡니다.
    # 다음은 Shvar 클래스 오브젝트(A)에 저장되어있는 자주 사용할 variable입니다.

# %% class variable 예시

print("measured value :", A.uf)
print("meanvalue :", A.mean)
print("uncertainty :", A.SE)
print("Original Data :", A.origin)

# %%
    # 이런 class variable은 다음과 같이 한꺼번에 출력하는 것이 가능합니다.

# %%

A.printfull()

# %%
    # 위 함수를 사용해 출력되는 class variable은 유의미한 값을 가진 variable만 출력됩니다.
    # 타입에 따라 출력되는 variable이 다양합니다.

    # 위에서 Measure를 측정값으로 봤을 때, 눈금에 의한 uncertainty도 고려를 해주어야 합니다.
    # 눈금 간격이 0.1이었을 때, 그로 인한 오차는 눈금간격의 1/20 이므로, 다음과 같이 설정해 주어, 눈금에 의한 uncertainty도 고려를 해줄 수 있습니다. (무시한 경우와 큰 차이는 안 날 수 있습니다.)

# %%

A.setufdata(Measure, ec=0.1 * 0.05)
A.printfull()

# %%
    # 다음은 setufdatalist, simpleuf, simpleuflist, simplescalar, simplescalarlist의 예시입니다.

# %%

print('\nsetufdatalist case')
Measurelist = [[x + i for x in Measure] for i in range(10)]
A = Shvar()
A.setufdatalist(Measurelist)
A.printfull()

print('\nsimpleuf case - 1')
Mass = ufloat(10, 0.1)
A = Shvar()
A.simpleuf(Mass)
A.printfull()

print('\nsimpleuf case - 2')
Mass_mean = 10
Mass_error = 0.1
A = Shvar()
A.simpleuf(Mass_mean, Mass_error)
A.printfull()

print('\nsimpleuflist case - 1')
Mass_list = [ufloat(10 + i, 0.1) for i in range(10)]
A = Shvar()
A.simpleuflist(Mass_list)
A.printfull()

print('\nsimpleuflist case - 2')
Mass_mean_list = range(10)
Mass_error_list = [0.1 for i in range(10)]
A = Shvar()
A.simpleuflist(Mass_mean_list, Mass_error_list)
A.printfull()

print('simplescalar case')
PI = 3.14
A = Shvar()
A.simplescalar(PI)
A.printfull()

print('\nsimplescalarlist case')
NUMBER = range(6)
A = Shvar()
A.simplescalarlist(NUMBER)
A.printfull()

# %%

# 3. 백업 & 백업 불러오기
    # 설정한 변수들의 백업 파일은 자동으로 생성되며, exp.py 와 exp_plot.py를 저장한 경로에서 var라는 파일안에 txt파일로 저장되게 됩니다.
    # 저장 시점은 변수가 생성 및 갱신 될 때이고, 보통은 덮어쓰기 되어지나, 30분 간격으로 새 백업 파일을 만들게 됩니다.
    # 백업한 데이터를 다시 불러올 수 있으며, 다음과 같이 실행합니다.

# %%

B = Shvar()
B = Shvar.readshvartext('A', imp=True)  # 반드시 imp=True를 넣어줘야 함
    # imp=False를 하게 되면, B에 아무것도 assign되지 않으며, 그저 print만 됨.
print('백업된 변수')
A.printfull()
print('백업을 불러온 변수')
B.printfull()

# %%

# 4. 피팅
    # 이 라이브러리는 linear_rel 함수를 통해 자동으로 linear regression을 해준다.
    # 주의 할 점은, uncertainty를 집어넣으면 자동으로 Weight로써 고려하게 된다.
    # linear_rel 함수에 X데이터, Y데이터로 넣을 수 있는 형식은 다음과 같다.
        # setufdatalist로 데이터를 넣은 타입
        # simplescalarlist로 데이터를 넣은 타입
        # 일반적인 리스트는 input으로 받지 못하므로, Shvar class object에 집어넣은 후에 사용해야 한다.

# %%

C = Shvar()
C.simplescalarlist([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

D = Shvar()
D.simpleuflist([Mass_list[i] + ufloat(np.sin(i), abs(np.cos(i))) for i in range(len(Mass_list))])

E = Shvar()
E.linear_rel(C, D)  # 현재 버전에서 linear_rel(C, D+1) 같은 식으로 사용할 수 없다.

E.printfull()

# %%

# 5. plot
    # 앞서 linear_rel를 이용해 선언된 object를 이용하면 바로 plot을 그릴 수 있다.

# %%

superplt.plot_comp(E, Title='test', Label=['X', 'Y'], datagraphname='testgraph', datacolor='blue')

# %%
    
    # plot_comp를 통해 생성된 plot과 그에 사용된 데이터에 대한 백업파일은 함수의 작동과 동시에 생성되며, 위치는 exp_plot.py가 저장된 폴더의 'plots'이다. plot은 이미지로, 그에 사용된 데이터는 txt로 저장된다.
    # plot_comp는 plt.figure부터 plt.show까지 한번에 이루어지기 때문에, 수정이 어렵다는 단점이 있다.
    # 수정을 거치고 싶을 경우, 특히 여러개를 한번에 그리고 싶은 경우 다음과 같이 사용하면 된다.

# %%

F = Shvar()
F.linear_rel(A, B)

plt.figure()
superplt.plot(F, datagraphname='hi')
superplt.plot(E, datacolor='blue', fitcolor='red', datagraphname='hello')
plt.title("test title")
plt.xlabel('x')
plt.ylabel('y')
plt.grid()
plt.legend()
plt.show()

# %%

# 6. 변수간의 계산
    # Shvar class로 생서된 object는 .tp라는 class variable을 갖게 된다.
        # .tp에는 일종의 '타입명'이 저장된다.
    # .tp에는 다음이 들어갈 수 있다.
        # 1. 'ufdata' : setufdata 함수로 생성된 Shvar class object의 .tp값이다.
        # 2. 'ufdatalist' : setufdatalist 함수로 생성된 Shvar class object의 .tp값이다.
        # 3. 'uf' : simpleuf 함수로 생성된 Shvar class object의 .tp값이다.
        # 4. 'uflist' : simpleuflist 함수로 생성된 Shvar class object의 .tp값이다.
        # 5. 'scalar' : simplescalar 함수로 생성된 Shvar class object의 .tp값이다.
        # 6. 'scalarlist' : simplescalarlist 함수로 생성된 Shvar class object의 .tp값이다.
        # 7. 'double group' : linear_rel 함수로 생성된 Shvar class object의 .tp값이다.
        # 8. None : object가 텅 비어있으면 가질 수 있는 .tp값이다.
    # Shvar class object는 기초적인 계산에 대한 계산을 지원하며, 연산이 가능한 .tp 조합은 다음과 같다.
        # 더하기 (+), 빼기 (-), 곱하기(*), 나누기(*)
            # ufdata + ufdata, ufdatalist, uf, uflist, scalar, scalarlist, 숫자
            # ufdatalist + ufdata, uf, scslar, 숫자
            # uf + ufdata, ufdatalist, uf, uflist, scalar, scalarlist, 숫자
            # uflist + ufdata, uf, scslar, 숫자
            # scalar + ufdata, ufdatalist, uf, uflist, scalar, scalarlist, 숫자
            # scalarlist + ufdata, uf, scslar, 숫자
            # double group은 연산이 불가능하다.
        # 위에서 언급한 숫자에는 ufloat도 들어간다. 자세한 이야기는 라이브러리 uncertainties를 참고.

# %%

uf = Shvar()
uf.simpleuf(10, 0.2)
ufdata = Shvar()
ufdata.setufdata(range(10))
uflist = Shvar()
uflist.simpleuflist([ufloat(i, 0.2 * i) for i in range(10)])
ufdatalist = Shvar()
ufdatalist.setufdatalist(Measurelist)
scalar = Shvar()
scalar.simplescalar(3.14)
scalarlist = Shvar()
scalarlist.simplescalarlist(range(10))
ufloatobject = ufloat(10, 0.2)
number = 10
realnumber = 10.4

result = uf + ufdata
print(result.uf)
result = uf + uflist
print(result.uf)
result = uf + ufdatalist
print(result.uf)

# %%

# 7. class variable 상세 내용
    # 다음은 Shvar class object가 가지는 class variable의 리스트와 그 내용이다.
        # self.tp : Shvar object의 타입명이 저장된다.
        # self.origin : ufdata와 ufdatalist 타입만 이 값이 저장되며, 변수 생성당시에 넣었던 데이터 원본이 저장된다.
        # self.eachlength : ufdatalist 타입만 이 값이 저장되며, 변수 생성당시에 넣어던 리스트의 원소들(얘도 리스트)의 길이가 리스트 형식으로 저장된다.
        # self.tbe : ufdata와 ufdatalist 타입만 이 값이 저장되며, rectangle distribution에 의해 생성된 type_b uncertainty값이 저장된다. 예시) 자의 눈금에 의한 uncertainty
        # self.mean : uf, uflist, ufdata, ufdatalist 타입만 이 값이 저장되며, uf, ufdata는 평균값, uflist, ufdatalist는 평균의 리스트가 저장된다.
        # self.vrc : ufdata, ufdatalist 타입만 이 값이 저장되며, 분산 또는 분산의 리스트가 들어간다.
        # self.stdv : ufdata, ufdatalist 타입만 이 값이 저장되며, 표준편차 또는 표준편차의 리스트가 들어간다.
        # self.SE : uf, uflist, ufdata, ufdatalist 타입만 이 값이 저장되며, 표준오차 또는 표준오차의 리스트가 들어간다.
        # self.uf : uf, uflist, ufdata, ufdatalist 타입만 이 값이 저장되며, ufloat(평균, 표준오차) 또는 그 리스트가 저장된다.
        # self.iftval : ufdata, ufdatalist 타입만 이 값이 저장되며, 실제값이 있는지 없는지 boolean의 형태로 저장된다.
        # self.tval : ufdata, ufdatalist 타입만 이 값이 저장되며, 실제값이 있는 경우에 한하여 그 실제값을 저장한다.
        # self.length : ufdata, ufdatalist, uflist, scalarlist 타입만 이 값이 저장되며, 리스트의 길이가 저장된다.
        # self.dsc : write_des 함수를 통해 적은 description이 여기에 들어간다.
        # self.scalar : scalar 타입만 이 값이 저장되며, scalar 값이 저장된다.
        # self.scalarlist : scalarlist 타입만 이 값이 저장되며, scalarlist 값이 저장된다.
        # self.intercept : double group 타입만 이 값이 저장되며, 피팅으로 나온 y절편 값을 저장한다.
        # self.slope : double group 타입만 이 값이 저장되며, 피팅으로 나온 기울기 값을 저장한다.
        # self.R2 : double group 타입만 이 값이 저장되며, 피팅으로 나온 R^2 값을 저장한다.
        # self.names : double group 타입만 이 값이 저장되며, X, Y 데이터의 varname을 리스트로 저장한다.
        # self.grouptp : double group 타입만 이 값이 저장되며, X, Y 데이터의 tp를 리스트로 저장한다.
        # self.XYdata : double group 타입만 이 값이 저장되며, X, Y 데이터의 값을 리스트로 저장한다.
        # self.varname : 모든 타입에 대해서 저장되며, 변수명이 저장된다.
