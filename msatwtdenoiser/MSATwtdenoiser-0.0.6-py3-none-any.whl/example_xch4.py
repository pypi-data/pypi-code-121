import matplotlib.pyplot as plt
import numpy as np
from MSATwtdenoiser import MSATdenoise
import scipy.io
import matplotlib.cm as cm
from netCDF4 import Dataset
import glob

MSAT_f = glob.glob('/Users/asouri/Documents/Methane_SAT_OSSEs/Main/co2_proxy_noisy_globa*')
for f in MSAT_f:
    MSAT = scipy.io.loadmat(f)
    XCH4 = MSAT['xCH4']
    XCH4[XCH4>1] = np.nan
    XCH4 = XCH4*1e9 
    XCH4[np.where((XCH4>2100) | (XCH4<1600))] = np.nan

    # denoiser
    flag = np.isnan(XCH4)
    denoiser = MSATdenoise(XCH4,'db6',3)
    denoised_img = denoiser.denoised
    denoised = {}
    denoised["xCH4"] = denoised_img
    exit()
    scipy.io.savemat(str(f) + '_wt.mat',denoised)



#plotting
fig = plt.figure(figsize=(12, 3))
ax = fig.add_subplot(1, 2, 1)
ax.imshow(XCH4, interpolation="nearest", cmap=cm.jet,vmin=1700, vmax=1900)
ax = fig.add_subplot(1, 2, 2)
ax.imshow(denoised_img, interpolation="nearest", cmap=cm.jet,vmin=1700, vmax=1900)
fig.tight_layout()
plt.show()

