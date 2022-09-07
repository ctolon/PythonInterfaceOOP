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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/eventSelection.cxx

import argparse

from argcomplete.completers import ChoicesCompleter
class EventSelectionTask(object):
    """
    Class for Interface -> eventSelection.cxx Task -> Configurable, Process Functions  

    Args:
        object (parser_args() object): eventSelection.cxx Interface
    """

    def __init__(self, parserEventSelectionTask=argparse.ArgumentParser(add_help=False)):
        super(EventSelectionTask, self).__init__()
        self.parserEventSelectionTask = parserEventSelectionTask

    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
      
        # Predefined Selections  
        collisionSystemSelections = ["PbPb", "pp", "pPb", "Pbp", "XeXe"]
        eventMuonSelections = ["0", "1", "2"]
        
        # Interface
        groupEventSelection = self.parserEventSelectionTask.add_argument_group(title="Data processor options: event-selection-task")
        groupEventSelection.add_argument("--syst", help="Collision System Selection ex. pp", action="store", type=str, choices=(collisionSystemSelections)).completer = ChoicesCompleter(collisionSystemSelections)
        groupEventSelection.add_argument("--muonSelection", help="0 - barrel, 1 - muon selection with pileup cuts, 2 - muon selection without pileup cuts", action="store", type=str, choices=(eventMuonSelections)).completer = ChoicesCompleter(eventMuonSelections)
        groupEventSelection.add_argument("--customDeltaBC", help="custom BC delta for FIT-collision matching", action="store", type=str)
        
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserEventSelectionTask.parse_args()