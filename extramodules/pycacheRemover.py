#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-

# Copyright 2019-2020 CERN and copyright holders of ALICE O2.
# See https://alice-o2.web.cern.ch/copyright for details of the copyright holders.
# All rights not expressly granted are reserved.
#
# This software is distributed under the terms of the GNU General Public
# License v3 (GPL Version 3), copied verbatim in the file "COPYING".
#
# In applying this license CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

# This scripts provides remove pycache files recursively

import os
import logging
import sys


class PycacheRemover(object):
    
    """This class creates two python commands in order to remove pycache files recursively

    Args:
        object (str): Creates two python command for deleting pycache files
    """
    
    def __init__(self):
        
        super(PycacheRemover, self).__init__()
        
        commandOne = ("python3 -Bc " + '"' + "import pathlib;" + "[p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]" + '"')
        commandTwo = ("python3 -Bc" + '"' + "import pathlib;" + "[p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]" + '"')
        
        os.system(commandOne)
        os.system(commandTwo)


def runPycacheRemover():
    """This function run two python command and it provides recursively deletes pycache files

    Raises:
        BaseException: If not path exists in OS
    """
    
    pycacheRemover = PycacheRemover()
    
    try:
        parentPath = os.getcwd()
        if os.path.exists(parentPath):
            logging.info("Inserting inside for pycache remove: %s", os.getcwd())
            pycacheRemover.__init__()
            logging.info("pycaches removed succesfully")
        
        elif not os.path.exists(parentPath):
            raise BaseException
    
    # Caching the exception
    except BaseException:
        logging.exception("Something wrong with specified\
            directory. Exception- %s", sys.exc_info(),)
        sys.exit()
