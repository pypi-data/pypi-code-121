{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "a8a6742b",
   "metadata": {},
   "outputs": [],
   "source": [
    "import matplotlib.pyplot as plt\n",
    "import numpy as np"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "88a8f874",
   "metadata": {},
   "outputs": [],
   "source": [
    "np.random.seed(10)\n",
    "data = np.random.normal(1, 20, 200)\n",
    "fig = plt.figure(figsize =(10, 10))\n",
    "plt.boxplot(data)\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "1581c066",
   "metadata": {
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "np.random.seed(10)\n",
    " \n",
    "data_1 = np.random.normal(100, 10, 200)\n",
    "data_2 = np.random.normal(90, 20, 200)\n",
    "data_3 = np.random.normal(80, 30, 200)\n",
    "data_4 = np.random.normal(70, 40, 200)\n",
    "data = [data_1, data_2, data_3, data_4]\n",
    " \n",
    "fig = plt.figure(figsize =(10, 10))\n",
    "\n",
    "ax = fig.add_axes([0, 0, 1, 1])\n",
    "\n",
    "bp = ax.boxplot(data)\n",
    "\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "96afeea7",
   "metadata": {},
   "outputs": [],
   "source": [
    "fig = plt.figure(figsize =(10, 10))\n",
    "\n",
    "ax = fig.add_axes([0, 0, 1, 1])\n",
    "\n",
    "bp = ax.boxplot(data,notch=True)\n",
    "\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "e96ab00e",
   "metadata": {},
   "outputs": [],
   "source": [
    "fig = plt.figure(figsize =(10, 10))\n",
    "\n",
    "ax = fig.add_axes([0, 0, 1, 1])\n",
    "\n",
    "bp = ax.boxplot(data,vert=0)\n",
    "\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "0a7eee89",
   "metadata": {},
   "outputs": [],
   "source": [
    "fig = plt.figure(figsize =(10, 10))\n",
    "\n",
    "ax = fig.add_axes([0, 0, 1, 1])\n",
    "\n",
    "bp = ax.boxplot(data)\n",
    "\n",
    "plt.title(\"Box PLot\")\n",
    "plt.xlabel(\"test\")\n",
    "plt.ylabel(\"speed\")\n",
    "\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "3d224290",
   "metadata": {},
   "outputs": [],
   "source": [
    "fig = plt.figure(figsize =(10, 10))\n",
    "\n",
    "ax = fig.add_axes([0, 0, 1, 1])\n",
    "\n",
    "bp = ax.boxplot(data)\n",
    "\n",
    "plt.title(\"Box PLot\")\n",
    "plt.xlabel(\"test\")\n",
    "plt.ylabel(\"speed\")\n",
    "\n",
    "plt.show()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "c5ec91db",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "daed8633",
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "40727fb4",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
