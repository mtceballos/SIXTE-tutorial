#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 18:06:49 2021

@author: dgiron
"""

from subprocess import check_call, STDOUT
import shutil, shlex
import numpy as np
from astropy.io import fits
from astropy.wcs import WCS
import matplotlib.pyplot as plt
import matplotlib.colors as colors


def run_comm(comm, msg=""):
    """
    Help function to run a command in the shell

    Parameters
    ----------
    comm : str
        string containing the command to be executed.
    
    msg : str
        message to be displayed below the executed cell.

    """
    print(msg)
    print(comm)
    try:
        args = shlex.split(comm)
        check_call(args, stderr=STDOUT)
    except Exception as mess:
        print(mess)
        raise

def showximage(imgfile):
    image_data = fits.getdata(imgfile, ext=0)
    hdu = fits.open(imgfile)[0]
    wcs = WCS(hdu.header)

    fig = plt.figure(figsize=(14,8))
    cmap = plt.cm.Blues_r

    #plot image
    ax = fig.add_subplot(1, 1, 1, projection=wcs)
    im = ax.imshow(image_data, cmap=cmap, norm=colors.LogNorm(vmin=np.median(image_data)*0.1, vmax=np.max(image_data), clip=True), origin="lower")
    ax.set_xlabel("RA")
    ax.set_ylabel("Dec")
    fig.colorbar(im,ax=ax, pad=0.1)
    plt.tight_layout()
    return fig,ax