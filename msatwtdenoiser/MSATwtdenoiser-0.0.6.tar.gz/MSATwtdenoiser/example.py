import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
from MSATwtdenoiser import MSATdenoise
            
img = np.array(mpimg.imread('steve.jpg'))
img.astype(float)
img = np.mean(img,axis=2)
img = img+np.random.normal(0,100,[np.shape(img)[0],np.shape(img)[1]])

# denoiser

denoiser = MSATdenoise(img,'db4',5)
denoised_img = denoiser.denoised


#plotting
fig = plt.figure(figsize=(12, 3))
ax = fig.add_subplot(1, 2, 1)
ax.imshow(img, interpolation="nearest", cmap=plt.cm.gray)
ax = fig.add_subplot(1, 2, 2)
ax.imshow(denoised_img, interpolation="nearest", cmap=plt.cm.gray)
fig.tight_layout()
plt.show()