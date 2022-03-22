#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 18:06:49 2021

@author: dgiron
"""

import matplotlib.pyplot as plt
import numpy as np
from subprocess import check_call, STDOUT
import shutil, shlex

def run_comm(comm, msg=""):
    """
    Run a command in the shell

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
           

def draw_second_axis(fig, axs, sq_downleft, sq_upright, ln, mov_ra=0, mov_dec=0, lon_lines=15, num_lines=10, mov_x_text=(0, 0), mov_y_text=(0, 0), xlabel='RA', ylabel='Dec', 
                     num_axis=0, dist_txt=10, zero_between=False, display_format='.2f'):
    """
    Paints a second axis on the plot for the right ascension (x-axis) and the declination (y-axis). It is prepared to paint with the RA incresing either to the left
    or right (and the same for the Dec). It is also prepared to work with RA increasing from 0 to 360, so it works even if 360 is reached before the end of the 
    plot. The Dec is given in a -180º to 180º scale. The functions paints values equally separated, with the number of those given by the user. IMPORTANT: the function only works with 
    axis and fig objects which are given to the function as parameters after being created. Sintax of the type plt.plot, plt.xlabel ... is not allowed

    Parameters
    ----------
    fig: object 
        figure object. Usual sintax: fig, _axs = plt.subplots(1, 1)
    axs: object
        axis object where the secondary axis wants to be plotted. IF THE AXIS OBJECT ONLY HAVES ONE ELEMENT IT SHOULD BE GIVEN IN THE FOLLOWING WAY (inside a one element 
        list and with the parameter num_axis=0): axs = [_axs]. 
    sq_downleft : tuple or list
        vector containing the coordinates of the down left square of the plot in the form: (RA, Dec).
    sq_upright : tuple or list
        vector containing the coordinates of the up right square of the plot in the form: (RA, Dec).
    ln : int
        length of the x-axis (should be equal to the y-axis one) i.e. number of p\'ixels in one line'.
    mov_ra : float, optional
        moves the RA coordinates to the right (lower values, even negatives) or left (higher values). Values between [-10, 20] are probably needed, though any value out of the interval
        can be used. The default is 0.
    mov_dec : float, optional
        moves the Dec coordinates up (lower values, even negatives) or down (higher values). Values between [-5, 10] are probably needed, though any value out of the interval
        can be used. The default is 0.
    lon_lines : float, optional
        length of the transversal lines of the x-axis and y-axis (around 15 for regular plots). The default is 15.
    num_lines : int, optional
        number of equal intervals in which the axis is divided. The default is 10.
    mov_x_text : tuple or list, optional 
        allows to move the x-axis label in the case it is not visible cause of the axis. The form should be [x, y], being x movement along the x-axis and same for y.
        Lower values in the x and y coordinates move the label to the down left square. The default is (0, 0).
    mov_y_text : tuple or list, optional
        allows to move the y-axis label in the case it is not visible cause of the axis. The form should be [x, y], being x movement along the x-axis and same for y.
        Lower values in the x and y coordinates move the label to the down left square. The default is (0, 0).
    xlabel : str, optional
        string containing the label of the secondary x-axis. It is compatible with latex characters using the following form: r'$latex characters$ non-latex characters'. The default is 'RA'.
    ylabel : str, optional
        string containing the label of the secondary x-axis. It is compatible with latex characters using the following form: r'$latex characters$ non-latex characters'. The default is 'Dec'.
    num_axis : int, optional
        number of the axis element. Allows to select which subplot of the axs object is required to have a secondary axis. The default is 0.
    dist_txt : float, optional
        moves the numbers in both axis away from the plot (larger values) or closer (lower values). The default is 10.
    zero_between : bool, optional
        True if the RA passes through 0º before the end of the axis. False if not. The default is False.
    display_format: str, optional
        format of the values of the second axis. Double dots should not be given as they are also included in the function. The default is '.2f'.

    Returns
    -------
    None.

    """
    m = 1
    m2 = 1
    
    # If zero is between, the calculation of the step needs an adition of 360 to the lower value which can be either the left one or the right one (works with RA increasing or decreasing 
    # to the right). This is corrected via the m and m2 variables (whether the step is added or substracted from the initial value) 
    
    
    if zero_between:
        if (sq_downleft[0] > sq_upright[0]):
            aux = np.array([sq_upright[0] + 360, sq_upright[1]])
            a = np.abs((sq_downleft - aux) / ln)
    
        elif (sq_upright[0] > sq_downleft[0]):
            aux = np.array([sq_downleft[0] + 360, sq_downleft[1]])
            m = -1
            a = np.abs((aux - sq_upright) / ln)
    else:
        a = np.abs((sq_downleft - sq_upright) / ln)
        if sq_downleft[0] > sq_upright[0]:
            m = -1
            
    if sq_downleft[1] > sq_upright[1]:
            m2 = -1
    h = ln / num_lines
    
    for i in range(num_lines+1):
        aux = m * a[0] * h * i + sq_downleft[0] # Saves the new x-value to be plotted. Increases the same step every loop
        if aux >= 360:
            aux = aux - 360
        if aux < 0:
            aux = aux + 360
        axs[num_axis].plot([h * i, h * i], [ln - lon_lines, ln], 'k-', linewidth=4.0) # Plot the x-bars
        axs[num_axis].text(h * i - mov_ra, ln + dist_txt, f'{aux:{display_format}}') # Plot the values of the x-axis

        aux2 = m2 * i * a[1] * h + sq_downleft[1] # Saves the new x-value to be plotted. Increases the same step every loop
        
        axs[num_axis].plot([ln - lon_lines, ln], [h * i, h * i], 'k-', linewidth=4.0) # Plot the y-bars
        axs[num_axis].text(ln + dist_txt, h * i - mov_dec, f'{aux2:{display_format}}') # Plot the y-values
    
    # Plot both labels 
    axs[num_axis].text(ln / 2 + mov_x_text[0], ln + mov_x_text[1], xlabel) 
    axs[num_axis].text(ln + mov_y_text[0], ln / 2 + mov_y_text[1], ylabel)
    
    
def get_zoom_coord(sq_dwl, sq_upr, ln, x, y, zero_between=False):
    """    
    Returns the coordinates (RA, Dec) of the down left square and the up right one
    of a zoomed area, delimited by pixel numbers given as parameters.
    Parameters
    ----------
    sq_dwl : tuple or list
        vector containing the coordinates of the down left square of the plot in the form: (RA, Dec).
    sq_upr : tuple or list
        vector containing the coordinates of the up right square of the plot in the form: (RA, Dec).
    ln: int
        number of pixels in one line in the original plot. IMPORTANT: Not to be confused with the zoomed plot length
    x : tuple or list
        contains the x-interval that wants to be zoomed. For example, [700, 900] for the pixels between 700 and 900 (in the x-axis).
    y : tuple or list
        contains the y-interval that wants to be zoomed. For example, [700, 900] for the pixels between 700 and 900 (in the y-axis).
    zero_between : bool, optional
        True if the RA passes through 0º before the end of the axis. False if not. The default is False.

    Returns
    -------
    sq1 : tuple
        coordinates of the down left square. Format: (x(RA), y(Dec)) .
    sq2 : tuple
        coordinates of the up right square. Format: (x(RA), y(Dec)) .

    """
    m = 1
    m2 = 1
    # If zero is between, the calculation of the step needs an adition of 360 to the lower value which can be either the left one or the right one (works with RA increasing or decreasing 
    # to the right). This is corrected via the m and m2 variables (whether the step is added or substracted from the initial value) 
    if zero_between:
        if (sq_upr[0] > sq_dwl[0]):
            m = -1
            aux = sq_dwl[0] + 360
            a = np.array([aux, sq_dwl[1]])
            step = (a - sq_upr)/ln
            
        elif (sq_upr[0] < sq_dwl[0]):
            aux = sq_upr[0] + 360
            a = np.array([aux, sq_upr[1]])
            step = (sq_dwl - a)/ln

    else:
        step = (sq_dwl - sq_upr)/ln
        if sq_dwl[0] > sq_upr[0]:
            m = -1  
    if sq_dwl[1] > sq_upr[1]:
        m2 = -1
    sq1 = np.array((m * step[0] * x[0] + sq_dwl[0], m2 * step[1] * y[1] + sq_upr[1]))
    sq2 = np.array((m * step[0] * x[1] + sq_dwl[0], m2 * step[1] * y[0] + sq_upr[1]))
    # If there is any value higher than 360 is corrected (or lower than zero)
    if sq1[0] > 360:
        sq1[0] = sq1[0] - 360
    if sq1[0] < 0:
        sq1[0] = sq1[0] + 360
    if sq2[0] < 0:
        sq2[0] = sq2[0] + 360
    if sq2[0] > 360:
        sq2[0] = sq2[0] - 360
    return sq1, sq2


        
def img_subplot(fig, axs, a, b, route='./'):
    """
    Saves only one subplot from a plt.subplots object

    Parameters
    ----------
    fig : object
        figure object.
    axs : object
        axis object.
    a : float
        increase the area (vertical) to let the label in (values like 1.1, 1.2...).
    b : float
        increase the area (horizontal) to let the label in (values like 1.1, 1.2...).
    route : sre, optional
        route to the directory where the image is going to be saved. The default is './'.

    Returns
    -------
    None.

    """
    extent = axs.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(route, bbox_inches=extent.expanded(a, b), dpi=720)
    