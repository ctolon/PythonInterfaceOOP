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

# Orginal Task For pidTPCFull.cxx: https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/PID/pidTPCFull.cxx
# Orginal Task For pidTOFFull.cxx: https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/PID/pidTOFFull.cxx

import argparse

from extraModules.choicesCompleterList import ChoicesCompleterList
from argcomplete.completers import ChoicesCompleter

class TpcTofPidFull(object):
    """
    Class for Interface -> pidTPCFull.cxx and pidTOFFull.cxx Task -> Configurable, Process Functions  

    Args:
        object (parser_args() object): pidTPCFull.cxx and pidTOFFull.cxx Interface
    """
    
    def __init__(self, parserTpcTofPidFull=argparse.ArgumentParser(add_help=False)):
        super(TpcTofPidFull, self).__init__()
        self.parserTpcTofPidFull = parserTpcTofPidFull

    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """

        # Predefined Selections
        pidSelections = {
            "el": "Produce PID information for the Electron mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
            "mu": "Produce PID information for the Muon mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
            "pi": "Produce PID information for the Pion mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
            "ka": "Produce PID information for the Kaon mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
            "pr": "Produce PID information for the Proton mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
            "de": "Produce PID information for the Deuterons mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
            "tr": "Produce PID information for the Triton mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
            "he": "Produce PID information for the Helium3 mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
            "al": "Produce PID information for the Alpha mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)"
        }
        pidSelectionsList = []
        for k, v in pidSelections.items():
            pidSelectionsList.append(k)
        
        booleanSelections = ["true", "false"]

        # Interface
        groupPID = self.parserTpcTofPidFull.add_argument_group(title="Data processor options: tpc-pid-full, tof-pid-full")
        groupPID.add_argument("--pid", help="Produce PID information for the <particle> mass hypothesis", action="store", nargs="*", type=str.lower, metavar="PID", choices=pidSelectionsList).completer = ChoicesCompleterList(pidSelectionsList)

        for key,value in pidSelections.items():
            groupPID.add_argument(key, help=value, action = "none")
             
        groupTofPid = self.parserTpcTofPidFull.add_argument_group(title="Data processor options: tof-pid, tof-pid-full")   
        groupTofPid.add_argument("--isWSlice", help="Process with track slices", action="store",type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)
            
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserTpcTofPidFull.parse_args()