import numpy as np
import matplotlib.pyplot as plt
import matplotlib
# matplotlib.rcParams['text.usetex'] = False
    # 원래 spyder면 레이텍을 불러와야 하지만, 코랩에서는 불러올 수 없는데다가,
    # 없어도 그냥 쓸 수 있다.

import uncertainties
from uncertainties import ufloat
from uncertainties.umath import *

import os  # path 수정용
import platform  # windows 확인용

import copy  # 복사용

from .exp import *
from .linfit import *


UF = "<class 'uncertainties.core.Variable'>"
UFAS = "<class 'uncertainties.core.AffineScalarFunc'>"
UFlist = [UF, UFAS]


# 자동으로 좋은 plot을 짜주는 함수를 짜고 싶다.
# animation도 목표로 넣도록 하자.
    # 진짜?


class superplt():
    def write_superplt(relation, Directory, textTitle, Time=None):
        # input : relation 의 입력 검사
        if isinstance(relation, Shvar) is False:
            raise TypeError("Input 'relation' should be a Shvar class object.")

        if relation.tp != 'double group':
            raise TypeError("Input 'relation' should have .tp value as 'double group'.")

        # input : Directory 의 입력 검사
        if isinstance(Directory, str) is False:
            raise TypeError("Input 'Directory' should be a string.")

        if os.path.isdir(Directory) is False:
            raise FileNotFoundError("The Directory does not exist.")

        TEXT = []

        # 작성 시간
        renewTime = Time.replace('-', ':')
        TEXT.append("Drew Time : " + renewTime)

        # 작성 변수
        TEXT.append("names : " + str(relation.names))
        TEXT.append("grouptp : " + str(relation.grouptp))
        TEXT.append("XYdata : " + str(relation.XYdata))

        # 피팅 결과
        if relation.slope is not None:
            TEXT.append("slope : {:.16}".format(relation.slope))
            TEXT.append("intercept : {:.16}".format(relation.intercept))
            TEXT.append("Coefficient of Determination : " + str(relation.R2))

        f = open(Directory + textTitle + '.txt', 'w')
        for x in TEXT:
            f.write(x + '\n')
        f.close()


    def plot(relation, fitxnum=1001, Capsize=3, datagraphname=None, FMT='-o',
             MS=5, fitcolor=(0.1, 0.1, 0.1, 0.9), datacolor='black'):


        """
        A method creating two plot rapidly. (not showed)

        Parameter
            relation      : The 'double group' type Shvar object to draw a plot.
            fitxnum       : The number of x-axes data used to draw a fitting graph.
            Capsize       : The wides of errorbar. default=3
            datagraphname : The name of datagraph
            FMT           : The properties of plot line and marker. Refer to matplotlib.pyplot.plot
            MS            : The markersize. default=5
            fitcolor      : The color of fitting graph.
            datacolor     : The color of data graph.
        """


        # 입력 검사.
            # 입력은 반드시 Shvar 클래스의 'double group' type이여야 한다.
        if isinstance(relation, Shvar):
            if relation.tp == 'double group':
                pass
            else:
                raise TypeError("The input 'relation' should be a Shvar class and have 'double group' type.")
        else:
            raise TypeError("The input 'relation' should be a Shvar class.")

        # X, Y가 각각 uf인 경우/아닌 경우에 맞춰 에러바를 그린다.
        if relation.grouptp[0] in ['uflist', 'ufdatalist']:
            Xn = [x.n for x in relation.XYdata[0]]
            Xs = [x.s for x in relation.XYdata[0]]
            XERR = Xs
        else:
            Xn = copy(relation.XYdata[0])
            XERR = None
        if relation.grouptp[1] in ['uflist', 'ufdatalist']:
            Yn = [y.n for y in relation.XYdata[1]]
            Ys = [y.s for y in relation.XYdata[1]]
            YERR = Ys
        else:
            Yn = copy(relation.XYdata[1])
            YERR = None

        plt.errorbar(Xn, Yn, xerr=XERR, yerr=YERR, capsize=Capsize,
                     label=datagraphname, fmt=FMT, ms=MS, color=datacolor)

        if relation.slope is not None:
            def fitting_func(x):  # 피팅 결과를 보여줄 함수
                y = relation.slope.n * x + relation.intercept.n
                return y

            # 피팅의 결과는 데이터보다 앞뒤로 좀더 보여준다. (10%)
            minx = min(Xn)
            maxx = max(Xn)
            firstx = -0.1 * (maxx - minx) + minx
            endx = 0.1 * (maxx - minx) + maxx
            fitX = np.linspace(firstx, endx, fitxnum)
            fitY = [fitting_func(x) for x in fitX]
            plt.plot(fitX, fitY, label='linear regression', color=fitcolor)


    def plot_comp(relation, fitxnum=1001, Title=None, pos_leg='right',
                  Label=['normal', 'normal'], Capsize=3, FMT='-o', MS=5,
                  datagraphname=None, canvascolor='white', backcolor='white',
                  text=True, fitcolor=(0.1, 0.1, 0.1, 0.9), datacolor='black'):


        """
        A method making a plot rapidly.

        Parameter
            relation      : The 'double group' type Shvar object to draw a plot.
            fitxnum       : The number of x-axes data used to draw a fitting graph.
            Title         : Title of plot. String type. default=None
            pos_leg       : Position of legend. 'right' or 'left'. The up/downward position of legend is decided by the sign of slope.
            Label         : The name of xlabel and ylabel. [string, string].
            Capsize       : The wides of errorbar. default=3
            FMT           : The properties of plot line and marker. Refer to matplotlib.pyplot.plot
            MS            : The markersize. default=5
            datagraphname : The name of datagraph. If this is None, Legend does not created.
            canvascolor   : The color of canvas.
            backcolor     : The color of background of plot area.
            text          : Whether the text is used. bullen type. default=True
            fitcolor      : The color of fitting graph.
            datacolor     : The color of data graph.

        This method make the following files.
            plot_date_time.png
            plotinfo_date_time.txt
        """


        # 입력 검사.
            # 입력은 반드시 Shvar 클래스의 'double group' type이여야 한다.
        if isinstance(relation, Shvar):
            if relation.tp == 'double group':
                pass
            else:
                raise TypeError("The input 'relation' should be a Shvar class and have 'double group' type.")
        else:
            raise TypeError("The input 'relation' should be a Shvar class.")

            # pos_leg 는 'right'거나 'left'여야 한다.
        if pos_leg != 'right' and pos_leg != 'left':
            raise ValueError("'pos_leg' should be 'right' or 'left'.")

        # X, Y가 각각 uf인 경우/아닌 경우에 맞춰 에러바를 그린다.
        if relation.grouptp[0] in ['uflist', 'ufdatalist']:
            Xn = [x.n for x in relation.XYdata[0]]
            Xs = [x.s for x in relation.XYdata[0]]
            XERR = Xs
        else:
            Xn = copy(relation.XYdata[0])
            XERR = None
        if relation.grouptp[1] in ['uflist', 'ufdatalist']:
            Yn = [y.n for y in relation.XYdata[1]]
            Ys = [y.s for y in relation.XYdata[1]]
            YERR = Ys
        else:
            Yn = copy(relation.XYdata[1])
            YERR = None

        fig = plt.figure()  # 캔버스 생성
        fig.set_facecolor(canvascolor)  # 캔버스 색상 설정
        ax = fig.add_subplot()  # 프레임(그림 뼈대) 생성
        ax.set_facecolor(backcolor)  # 그래프 영역 배경 색상 설정

        # 에러바 그래프 생성
        ax.errorbar(Xn, Yn, xerr=XERR, yerr=YERR, capsize=Capsize,
                    label=datagraphname, fmt=FMT, ms=MS, color=datacolor)

        # relation object에 피팅값이 있는 경우
        if relation.slope is not None:
            def fitting_func(x):  # 피팅 결과를 보여줄 함수
                y = relation.slope.n * x + relation.intercept.n
                return y

            # 피팅의 결과는 데이터보다 앞뒤로 좀더 보여준다. (10%)
            minx = min(Xn)
            maxx = max(Xn)
            firstx = -0.1 * (maxx - minx) + minx
            endx = 0.1 * (maxx - minx) + maxx
            fitX = np.linspace(firstx, endx, fitxnum)
            fitY = [fitting_func(x) for x in fitX]
            ax.plot(fitX, fitY, label='linear regression', color=fitcolor)

            # 피팅 결과은 식으로도 보여주게 되는데, 텍스트로 보여준다.
                # 텍스트의 위치는 데이터의 90%, 80%, 70% 위치 또는
                # 10%, 20%, 30% 위치에서 보여주게 된다.
            minY = min(fitY)
            maxY = max(fitY)
            posx = minx + 0.65 * (maxx - minx)  # 텍스트가 오른쪽 방면에 쓰여질 때의 x좌표이다.
            if text is True:
                if relation.slope.n >= 0:  # 기울기가 양수일 때
                    if pos_leg == 'right':  # 범례가 오른쪽일 때
                        firstposy = minY + 0.9 * (maxY - minY)
                        secondposy = minY + 0.83 * (maxY - minY)
                        thirdposy = minY + 0.76 * (maxY - minY)
                        fourthposy = minY + 0.69 * (maxY - minY)
                        ax.text(minx, firstposy, r'$y=ax+b$', fontsize=10)
                        ax.text(minx, secondposy, 'a={:.2uP}'.format(relation.slope), fontsize=10)
                        ax.text(minx, thirdposy, 'b={:.2uP}'.format(relation.intercept), fontsize=10)
                        ax.text(minx, fourthposy, '$R^2$={:.3f}'.format(relation.R2), fontsize=10)
                    else:  # 범례가 왼쪽일 때
                        firstposy = minY + 0.31 * (maxY - minY)
                        secondposy = minY + 0.24 * (maxY - minY)
                        thirdposy = minY + 0.17 * (maxY - minY)
                        fourthposy = minY + 0.1 * (maxY - minY)
                        ax.text(posx, firstposy, r'$y=ax+b$', fontsize=10)
                        ax.text(posx, secondposy, 'a={:.2uP}'.format(relation.slope), fontsize=10)
                        ax.text(posx, thirdposy, 'b={:.2uP}'.format(relation.intercept), fontsize=10)
                        ax.text(minx, fourthposy, '$R^2$={:.3f}'.format(relation.R2), fontsize=10)
                else:  # 기울기가 음수일 때
                    if pos_leg == 'right':  # 범례가 오른쪽일 때
                        firstposy = minY + 0.31 * (maxY - minY)
                        secondposy = minY + 0.24 * (maxY - minY)
                        thirdposy = minY + 0.17 * (maxY - minY)
                        fourthposy = minY + 0.1 * (maxY - minY)
                        ax.text(minx, firstposy, r'$y=ax+b$', fontsize=10)
                        ax.text(minx, secondposy, 'a={:.2uP}'.format(relation.slope), fontsize=10)
                        ax.text(minx, thirdposy, 'b={:.2uP}'.format(relation.intercept), fontsize=10)
                        ax.text(minx, fourthposy, '$R^2$={:.3f}'.format(relation.R2), fontsize=10)
                    else:  # 범례가 왼쪽일 때
                        firstposy = minY + 0.9 * (maxY - minY)
                        secondposy = minY + 0.83 * (maxY - minY)
                        thirdposy = minY + 0.76 * (maxY - minY)
                        fourthposy = minY + 0.69 * (maxY - minY)
                        ax.text(posx, firstposy, r'$y=ax+b$', fontsize=10)
                        ax.text(posx, secondposy, 'a={:.2uP}'.format(relation.slope), fontsize=10)
                        ax.text(posx, thirdposy, 'b={:.2uP}'.format(relation.intercept), fontsize=10)
                        ax.text(minx, fourthposy, '$R^2$={:.3f}'.format(relation.R2), fontsize=10)

        # Xlabel 작성
        if Label[0] == 'normal':
            ax.set_xlabel(relation.names[0])
        else:
            ax.set_xlabel(Label[0])

        # Ylabel 작성
        if Label[1] == 'normal':
            ax.set_ylabel(relation.names[1])
        else:
            ax.set_ylabel(Label[1])

        # 제목 작성
        ax.set_title(Title)

        # 그리드 작성
        ax.grid()

        # 범례 작성
        if datagraphname is not None:
            handles, labels = ax.get_legend_handles_labels()  # 범례 처리되는 요소와 해당 라벨
            dict_labels_handles = dict(zip(labels, handles))  # 라벨을 키로 요소를 밸류로 하는 딕셔너리 생성
            labels = [datagraphname, 'linear regression']  # 원하는 순서 라벨
            handles = [dict_labels_handles[j] for j in labels]  # 라벨 순서에 맞게 요소 재배치
            if pos_leg == 'right':
                if relation.slope.n > 0:
                    ax.legend(handles, labels, loc='lower right')
                else:
                    ax.legend(handles, labels, loc='upper right')
            else:
                if relation.slope.n > 0:
                    ax.legend(handles, labels, loc='upper left')
                else:
                    ax.legend(handles, labels, loc='lower left')

        # fig.show()

        # 백업 파일 기본 디렉토리
        if platform.system() == 'Windows':
            BaseDirectory = __file__.replace('exp_plot.py', 'plots\\')
            if os.path.isdir(BaseDirectory.replace('plots\\', 'plots')) is False:
                os.mkdir(BaseDirectory.replace('plots\\', 'plots'))
        else:
            BaseDirectory = __file__.replace('exp_plot.py', 'plots/')
            if os.path.isdir(BaseDirectory.replace('plots/', 'plots')) is False:
                os.mkdir(BaseDirectory.replace('plots/', 'plots'))

        timelist = Shvar.change_time_to_text()  # 현재시간을 텍스트 형식으로 불러온다.
        time_for_Title = timelist[0] + '_' + timelist[1]  # 제목으로 바꾼다.
        Title = 'plot_' + time_for_Title  # 플롯 제목
        textTitle = 'plotinfo_' + time_for_Title  # 플롯 인포메이션 제목
        plt.savefig(BaseDirectory + Title + '.png')  # 플롯 저장
        superplt.write_superplt(relation, BaseDirectory, textTitle, Time=time_for_Title)
