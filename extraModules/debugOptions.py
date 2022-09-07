#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*- 
#############################################################################
##  © Copyright CERN 2018. All rights not expressly granted are reserved.  ##
##                   Author: ionut.cristian.arsene@cern.ch                 ##
##               Interface:  cevat.batuhan.tolon@cern.ch                   ## 
## This program is free software: you can redistribute it and/or modify it ##
##  under the terms of the GNU General Public License as published by the  ##
## Free Software Foundation, either version 3 of the License, or (at your  ##
## option) any later version. This program is distributed in the hope that ##
##  it will be useful, but WITHOUT ANY WARRANTY; without even the implied  ##
##     warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    ##
##           See the GNU General Public License for more details.          ##
##    You should have received a copy of the GNU General Public License    ##
##   along with this program. if not, see <https://www.gnu.org/licenses/>. ##
#############################################################################

import argparse

from argcomplete.completers import ChoicesCompleter
from extraModules.choicesCompleterList import ChoicesCompleterList

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