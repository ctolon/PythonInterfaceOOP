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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/PID/pidTOFBase.cxx

import argparse

from argcomplete.completers import ChoicesCompleter

class TofEventTime(object):
    """
    Class for Interface -> pidTOFBase.cxx.cxx Task -> Configurable, Process Functions  

    Args:
        object (parser_args() object): pidTOFBase.cxx.cxx Interface
    """
    
    def __init__(self, parserTofEventTime=argparse.ArgumentParser(add_help=False)):
        super(TofEventTime, self).__init__()
        self.parserTofEventTime = parserTofEventTime

    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        ft0Selections = ["FT0", "NoFT0", "OnlyFT0", "Run2"]
    
        # Interface
        groupTofEventTime = self.parserTofEventTime.add_argument_group(title="Data processor options: tof-event-time")
        groupTofEventTime.add_argument("--FT0", help="FT0: Process with FT0, NoFT0: Process without FT0, OnlyFT0: Process only with FT0, Run2: Process with Run2 data", action="store", type=str, choices=ft0Selections).completer = ChoicesCompleter(ft0Selections)
            
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserTofEventTime.parse_args()