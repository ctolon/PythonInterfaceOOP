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


# TODO Carry Helper Commands here

"""
import argparse

from argcomplete.completers import ChoicesCompleter
from ExtraModules.ChoicesCompleterList import ChoicesCompleterList

class HelperCommands(object):
    
    def __init__(self, parserHelperCommands=argparse.ArgumentParser(add_help=False)):
        super(HelperCommands, self).__init__()
        self.parserHelperCommands = parserHelperCommands

    def addArguments(self):

        # Predefined Selections
        debugLevelSelections = {
            "NOTSET": "Set Debug Level to NOTSET",
            "DEBUG": "Set Debug Level to DEBUG",
            "INFO": "Set Debug Level to INFO",
            "WARNING": "Set Debug Level to WARNING",
            "ERROR": "Set Debug Level to ERROR",
            "CRITICAL": "Set Debug Level to CRITICAL"
        }
        debugLevelSelectionsList = []
        for k, v in debugLevelSelections.items():
            debugLevelSelectionsList.append(k)
    
        # Interface
        groupHelperCommands = self.parserHelperCommands.add_argument_group(title="Additional Debug Options")
        groupHelperCommands.add_argument("--debug", help="execute with debug options", action="store", type=str.upper, default="INFO", choices=debugLevelSelectionsList).completer = ChoicesCompleterList(debugLevelSelectionsList)
        groupHelperCommands.add_argument("--logFile", help="Enable logger for both file and CLI", action="store_true")
        groupDebug= self.parserHelperCommands.add_argument_group(title="Choice List for debug Parameters")

        for key,value in debugLevelSelections.items():
            groupDebug.add_argument(key, help=value, action="none")
            
    def parseArgs(self):
        return self.parserHelperCommands.parse_args()
        
"""