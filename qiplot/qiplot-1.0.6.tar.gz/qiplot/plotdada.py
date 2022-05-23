import os, sys, string, argparse, re
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtGui, QtCore
from glob import glob
from time import time
from matplotlib import cm
import matplotlib.pyplot as plt

pg.setConfigOption('leftButtonPan', False)


def _mouseMoved(evt):
    mousePoint = plt.vb.mapSceneToView(evt[0])
    label.setText("<span style='font-size: 14pt; color: white'> x=%-10.4f y=%-10.4f" %(mousePoint.x(), mousePoint.y()))


def _getcmcolors(length, cmapname):
    cmap_inds = np.linspace(0, 255, length).astype(np.uint8)
    try:
        cmapobj = getattr(cm, cmapname)
    except:
        print('Defaulting to cmap jet')
        cmapobj = getattr(cm, 'jet')
    return [tuple([int(255*j) for j in cmapobj(i)]) for i in cmap_inds]


def _streak(nums, show=True):
    """
    :type nums: List[int]
    :rtype: int
    example = [0, 2, 4, 7, 8, 9, 10, 20, 21, 22, 23, 24, 25, 26, 30, 33, 34, 35]
    _streak(example, show=True)
    """
    nums = list(dict.fromkeys(nums))
    best = [0,0,0] #ini, fin, len
    curr = [0,0,0]
    for index, value in enumerate(nums):
        if index + 1 >= len(nums):
            break
        curr[0] = nums[index]
        if nums[index + 1] != value + 1:
            curr[1] = nums[index]
            curr[2] = 0
        elif nums[index + 1] == value + 1:
            curr[2] += 1
            curr[1] = nums[index+1]
            curr[0] = nums[index-(curr[2]-1)]
            if curr[2] > best[2]:
                best[2] = curr[2]
                best[0] = curr[0]
                best[1] = curr[1]
        if show==True:
            print('current:',curr, 'best:',best)
    return best   #actual line indices. Add 1 to final index for *range* indices


def _lcheck(line):
    "Return 0:skip signal. Return 1:accept signal"
    li = line.strip()
    res = 0
    if li.replace('.','').replace(' ','').isdigit or li.replace('.','').replace(',','').isdigit:
        if re.search(',', li):
            sep = ','
        else:
            sep = None
        c = li.split(sep)
        if len(c) > 1:
            try:
                x, y = float(c[0]), float(c[1])
                res = 1
            except:
                return res
    return res


def filelinescheck(lines):
    "Input: list of lines from readlines()"
    accept = []
    for n, l in enumerate(lines):
        res = _lcheck(l)
        if res == 1:
            accept.append(n)
    longest = _streak(accept, show=False)
    return longest[0], longest[1]+1


def get_xye(argfiles, label, romin=0, romax=10000):
    argfiles = [glob('%s' %arg) for arg in argfiles  ]
    argfiles = sorted(set([j for i in argfiles for j in i]))
    names, data = [], []
    for ind, f in enumerate(argfiles):
        print('%-4d. %s' %(ind, f), end='')
        if os.path.isfile(f):
            with open(f, 'r') as fil:
                lines = fil.readlines()
            romin, romax = filelinescheck(lines); print(romin)
            try:
                x,y,e = np.loadtxt(f, unpack=True, usecols=(0,1,2), skiprows=romin, max_rows=romax)
            except IndexError:  #no third column
                x,y = np.loadtxt(f, unpack=True, usecols=(0,1), skiprows=romin, max_rows=romax)
                e = np.zeros(y.shape)
            except StopIteration: # empty file 1
                print('Not enough data'); sys.exit(0)
            except ValueError: # empty file 2
                print('Not enough data'); sys.exit(0)
            print(': %d points' %(len(x)))
            data.append([x,y,e])
            if '/' in f:
                sep = '/'
            elif '\\' in f:
                sep = '\\'
            else:
                sep = '\\'
            if label == 'index':
                names.append(f.split(sep)[-1].split('.')[0].split('_')[-1])
            elif label == 'prefix':
                names.append(f.split(sep)[-1].split('.')[0])
            elif label == 'dir':
                names.append('/'.join(os.path.abspath(f).split(sep)[-2:]).split('.')[0])
            elif label == 'full':
                names.append(os.path.abspath(f))
    return data, names


def main():
    t0 = time()
    parser = argparse.ArgumentParser(description='At least better than plotdata')
    parser.add_argument('datafiles', nargs='+', type=str,
                        help='String(s) passed to glob to look for plottable files')
    parser.add_argument('-l','--label', choices=['index','prefix','dir','full'],
                        default='prefix', help='Cut legend label at: \
                        index (0002), prefix (Cr2O3_98keV_x1200_0002), dir (Cr2O3/Cr2O3_98keV_x1200_0002),\
                        full (/gz/data/id15/inhouse3/2018/ch5514/Cr2O3/Cr2O3_98keV_x1200_0002)')
    parser.add_argument('-t','--title', default=os.path.realpath('.').split('/')[-1], help='Window title')
    parser.add_argument('--every', default=1, type=int, help='Plot only every N-th input file')
    parser.add_argument('--rmin', default=0, type=int, help='Cut N lines at the beginning of each file')
    parser.add_argument('--rmax', default=10000, type=int, help='Cut after the first rmin+N lines of each file')
    parser.add_argument('--diff', default=None, type=int, const=0, nargs='?',
                        help='If True, plot the difference between each curve and the N-th input curve. \
                              Default (no value) = 0 (first curve). To subtract mean use --diff -99. \
                              Error is propagated over the two curves.')
    parser.add_argument('--cmap', type=str, default='rainbow', nargs='?', help='One of the available matplotlib cmaps')
    args = parser.parse_args()
    data, names = get_xye(args.datafiles[::args.every], args.label, args.rmin, args.rmax)
    t1 = time(); print('getting data', np.round(t1-t0, 3), 's')
#    app = QtGui.QApplication([])
    app = pg.mkQApp()
    win = pg.GraphicsWindow(title=args.title)
#    plt = pg.plot(title=args.title)
    label = pg.LabelItem(justify = "right")
    win.addItem(label)
    plt = win.addPlot(row=1, col=0, name='p1')
    plt.showGrid(True, True, 0.5)
    proxy = pg.SignalProxy(plt.scene().sigMouseMoved, rateLimit=60, slot=_mouseMoved)
    leg = plt.addLegend()
    leg.autoAnchor(pg.Point(plt.width()*0.95,plt.height()*0.0))
    t2 = time(); print('starting window', np.round(t2-t1, 3), 's')
    colors = _getcmcolors(len(data), args.cmap)
    for ii in range(len(data)):
        x,y,e = data[ii][0], data[ii][1], data[ii][2]
        if args.diff != None and type(args.diff) == int:
            if args.diff != -99:
                ysubtr, esubtr = data[args.diff][1], data[args.diff][2]
            elif args.diff == -99:
                ysubtr, esubtr = np.mean(np.array(data)[:,1], axis=0), np.mean(np.array(data)[:,2], axis=0)
            y = y-ysubtr
            if sum(e) != 0:
                e = np.sqrt(e**2 + esubtr**2)
#        li = plt.plot(x, y, pen=(ii,len(data)), name=names[ii])
        cpen = pg.mkPen(colors[ii], width=1.25)
        li = pg.PlotDataItem(x=x, y=y, pen=cpen, name=names[ii])
        plt.addItem(li)
        if sum(e) != 0:
            err = pg.ErrorBarItem(x=x, y=y, top=e/2, bottom=e/2, beam=0.5*np.mean(np.diff(x)), pen=cpen) #(ii,len(data)))
            plt.addItem(err)
    t3 = time(); print('plotting', np.round(t3-t2, 3), 's')
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
#        QtGui.QApplication.instance().exec_()
        pg.mkQApp().instance().exec_()

if __name__ == '__main__':
    main()
