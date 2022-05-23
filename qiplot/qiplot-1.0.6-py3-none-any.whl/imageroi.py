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
    # parser.add_argument('--cmap', type=str, default='rainbow', nargs='?', help='One of the available matplotlib cmaps')
    args = parser.parse_args()

    # read input files
    fdata, names = get_xye(args.datafiles[::args.every], args.label, args.rmin, args.rmax)
    t1 = time(); print('getting data', np.round(t1-t0, 3), 's')

    # flip images by default (did not test the other choice)
    pg.setConfigOptions(imageAxisOrder='row-major')

    # create window
    app = pg.mkQApp()
    win = pg.GraphicsLayoutWidget(title=args.title, size=(750,400))

    # create 2d plot box
    p1 = win.addPlot(row=0, col=0, name='p1', title='')
    img = pg.ImageItem()
    p1.addItem(img)

    # try to apply colormap directly
    pos = np.array([0., 1., 0.5, 0.25, 0.75])
    color = np.array([[0,255,255,255], [255,255,0,255], [0,0,0,255], (0, 0, 255, 255), (255, 0, 0, 255)], dtype=np.ubyte)
    # color = pg.colormap.get('magma')
    cmap = pg.ColorMap(pos, color)
    # lut = cmap.getLookupTable(0.0, 1.0, 100)
    # img.setLookupTable(lut)

    # fill image with data
    data = np.empty((len(fdata), len(fdata[0][0])))
    # edata = np.empty((len(fdata), len(fdata[0][0])))
    for ii in range(len(fdata)):
        data[ii,:] = fdata[ii][1]
        # edata[ii,:] = fdata[ii][2]
    if args.diff != None and type(args.diff) == int:
        if args.diff != -99:
            data -= data[args.diff,:]
            # edata -= edata[args.diff,:]
        elif args.diff == -99:
            data -= np.mean(data, axis=0),
            # edata -= np.mean(edata, axis=0)
    xdata = fdata[0][0]
    img.setImage(data, autoLevels=True)#, lut=lut)

    # scale from npoints to actual x-axis
    xmin, xmax = min(xdata),max(xdata)
    datarange = QtCore.QRectF(xmin, 0, xmax, data.shape[0])
    img.setRect(datarange)

    # img.setLevels([0,256])


    # Custom ROI for selecting an image region
    # default settings: x position around the most intense feature; x and y size 1/20 of the range;
    #                   move/resize limited to data range; no snap resize
    hsize = np.ceil(abs(xmax-xmin)/20)
    vsize = np.ceil(data.shape[0]/20)
    roi = pg.ROI(pos=[ xdata[np.argmax(np.mean(data, axis=0))]-hsize/2, 0], size=[hsize,vsize],
                 maxBounds=datarange, snapSize=max(1, int(hsize/4)), translateSnap=True)
    roi.addScaleHandle([0.5, 1], [0.5, 0.])
    roi.addScaleHandle([0.5, 0], [0.5, 1.])
    roi.addScaleHandle([1, 0.5], [0., 0.5])
    roi.addScaleHandle([0, 0.5], [1., 0.5])
    roi.addScaleHandle([0, 0], [1, 1])
    roi.addScaleHandle([0, 1], [1, 0])
    roi.addScaleHandle([1, 0], [0, 1])
    roi.addScaleHandle([1, 1], [0, 0])
    p1.addItem(roi)
    roi.setZValue(10)  # make sure ROI is drawn above image

    # Isocurve drawing
    iso = pg.IsocurveItem(level=0.8, pen='g')
    iso.setParentItem(img)
    iso.setZValue(5)

    # Contrast/color control
    hist = pg.HistogramLUTItem(image=img, orientation='vertical')
    hist.gradient.setColorMap(cmap)  #this is the bloody crucial command
    win.addItem(hist)

    # Draggable line for setting isocurve level
    isoLine = pg.InfiniteLine(angle=0, movable=True, pen='g')
    hist.vb.addItem(isoLine)
    hist.vb.setMouseEnabled(y=False) # makes user interaction a little easier
    isoLine.setValue(0)
    isoLine.setZValue(1000) # bring iso line above contrast controls

    # Another plot area for displaying ROI data
    p2 = win.addPlot(row=1, col=0, colspan=2)
    p2.showGrid(x=True, y=True, alpha=0.5)

    # build isocurves from smoothed data
    iso.setData(pg.gaussianFilter(data, (2, 2)))

    # zoom to fit imageo
    p1.autoRange()

    # Callbacks for handling user interaction
    def updatePlot():
        global img, roi, data, p2
        selected = roi.getArrayRegion(data, img)
        x0 = roi.getState()['pos'][0]
        x1 = roi.getState()['size'][0]+x0
        newx = np.linspace(x0, x1, selected.shape[1])
        # newx = fdata[0][0][np.argmin(abs(fdata[0][0]-x0)):1+np.argmin(abs(fdata[0][0]-x1))]
#        p2.plot(newx, selected.mean(axis=0), clear=True)
        p2.plot(newx, np.nanmean(selected, axis=0), clear=True)
        p2.setRange(xRange=(x0,x1))

    roi.sigRegionChanged.connect(updatePlot)
    updatePlot()

    def updateIsocurve():
        global isoLine, iso
        iso.setLevel(isoLine.value())

    isoLine.sigDragged.connect(updateIsocurve)

    def imageHoverEvent(event):
        """Show the position, pixel, and value under the mouse cursor.
        """
        if event.isExit():
            p1.setTitle("")
            return
        pos = event.pos()
        i, j = pos.y(), pos.x()
        i = int(np.clip(i, 0, data.shape[0] - 1))
        j = int(np.clip(j, 0, data.shape[1] - 1))
        val = data[i, j]
        ppos = img.mapToParent(pos)
        x, y = ppos.x(), ppos.y()
        p1.setTitle("pos: (%0.3f, %0.3f)  pixel: (%d, %d)  value: %g" % (x, y, j, i, val))

    # Monkey-patch the image to use our custom hover function.
    # This is generally discouraged (you should subclass ImageItem instead),
    # but it works for a very simple use like this.
    img.hoverEvent = imageHoverEvent

    screensize = app.primaryScreen().size()
    win.resize(int(screensize.width()/2), int(screensize.height()/2))
    # win.showMaximized()
    win.show()


    t2 = time(); print('graphics and plotting', np.round(t2-t1, 3), 's')


    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        pg.mkQApp().instance().exec_()


if __name__ == '__main__':
    main()
