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

import logging
from logging import handlers
import sys
import os


def debugSettings(argDebug: bool, argLogFile: bool, fileName: str):
    """Debug settings for CLI

    Args:
        argDebug (bool): Debug Level
        argLogFile (bool): CLI argument as logFile
        fileName (str): Output name of log file

    Raises:
        ValueError: If selected invalid log level
    """
    
    if argDebug and (not argLogFile):
        DEBUG_SELECTION = argDebug
        numeric_level = getattr(logging, DEBUG_SELECTION.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError("Invalid log level: %s" % DEBUG_SELECTION)
        logging.basicConfig(format = "[%(levelname)s] %(message)s", level = DEBUG_SELECTION)
    
    if argLogFile and argDebug:
        log = logging.getLogger("")
        level = logging.getLevelName(argDebug)
        log.setLevel(level)
        format = logging.Formatter("[%(levelname)s] %(message)s")
        
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(format)
        log.addHandler(ch)
        
        loggerFile = "tableReader.log"
        if os.path.isfile(loggerFile):
            os.remove(loggerFile)
        
        fh = handlers.RotatingFileHandler(loggerFile, maxBytes = (1048576 * 5), backupCount = 7, mode = "w")
        fh.setFormatter(format)
        log.addHandler(fh)
