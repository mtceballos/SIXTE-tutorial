#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 18:06:49 2021

@author: dgiron
"""

from subprocess import check_call, STDOUT
import shutil, shlex

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

