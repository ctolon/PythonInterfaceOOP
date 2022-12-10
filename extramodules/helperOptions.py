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
from argcomplete.completers import ChoicesCompleter
from extramodules.choicesHandler import ChoicesCompleterList


class HelperOptions(object):
    
    """
    Class for Interface -> Helper Options

    Args:
        object (parser_args() object): Helper Options Interface
    """
    
    def __init__(self, parserHelperOptions = argparse.ArgumentParser(add_help = False)):
        super(HelperOptions, self).__init__()
        self.parserHelperOptions = parserHelperOptions
    
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
            "CRITICAL": "Set Debug Level to CRITICAL",
            }
        debugLevelSelectionsList = []
        for k, v in debugLevelSelections.items():
            debugLevelSelectionsList.append(k)
        
        booleanSelections = ["true", "false"]
        
        # Interface
        groupDebugOptions = self.parserHelperOptions.add_argument_group(title = "Additional Debug Options")
        groupDebugOptions.add_argument("--debug", help = "execute with debug options", action = "store", type = str.upper, metavar = "DEBUG", default = "INFO", choices = debugLevelSelectionsList,).completer = ChoicesCompleterList(debugLevelSelectionsList)
        groupDebugOptions.add_argument("--logFile", help = "Enable logger for both file and CLI", action = "store_true")
        groupDebug = self.parserHelperOptions.add_argument_group(title = "Choice List for debug Parameters")
        
        for key, value in debugLevelSelections.items():
            groupDebug.add_argument(key, help = value, action = "none")
        
        groupAutomations = self.parserHelperOptions.add_argument_group(title = "Interface Mode Selection Parameters")
        groupAutomations.add_argument("--onlySelect", help = "If false JSON Overrider Interface If true JSON Additional Interface", action = "store", default = "true", type = str.lower, choices = booleanSelections,).completer = ChoicesCompleter(booleanSelections)
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserHelperOptions.parse_args()
