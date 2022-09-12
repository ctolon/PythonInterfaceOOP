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


import argparse

from extramodules.choicesCompleterList import ChoicesCompleterList

class DebugOptions(object):
    """
    Class for Interface -> Debug Options 

    Args:
        object (parser_args() object): Debug Interface
    """
    
    
    def __init__(self, parserDebugOptions=argparse.ArgumentParser(add_help=False)):
        super(DebugOptions, self).__init__()
        self.parserDebugOptions = parserDebugOptions

    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """

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
        groupDebugOptions = self.parserDebugOptions.add_argument_group(title="Additional Debug Options")
        groupDebugOptions.add_argument("--debug", help="execute with debug options", action="store", type=str.upper, default="INFO", choices=debugLevelSelectionsList).completer = ChoicesCompleterList(debugLevelSelectionsList)
        groupDebugOptions.add_argument("--logFile", help="Enable logger for both file and CLI", action="store_true")
        groupDebug= self.parserDebugOptions.add_argument_group(title="Choice List for debug Parameters")

        for key,value in debugLevelSelections.items():
            groupDebug.add_argument(key, help=value, action="none")
            
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserDebugOptions.parse_args()