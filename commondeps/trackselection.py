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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/trackselection.cxx

import argparse

from argcomplete.completers import ChoicesCompleter

class TrackSelectionTask(object):
    """
    Class for Interface -> trackselection.cxx.cxx Task -> Configurable, Process Functions  

    Args:
        object (parser_args() object): trackselection.cxx.cxx Interface
    """
    
    def __init__(self, parserTrackSelectionTask=argparse.ArgumentParser(add_help=False)):
        super(TrackSelectionTask, self).__init__()
        self.parserTrackSelectionTask = parserTrackSelectionTask

    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        itsMatchingSelections = ["0","1","2"]
    
        # Interface
        groupTrackSelectionTask = self.parserTrackSelectionTask.add_argument_group(title="Data processor options: track-selection")
        groupTrackSelectionTask.add_argument("--itsMatching", help="condition for ITS matching (0: Run2 SPD kAny, 1: Run3ITSibAny, 2: Run3ITSallAny, 3: Run3ITSall7Layers)", action="store", type=str, choices=(itsMatchingSelections)).completer = ChoicesCompleter(itsMatchingSelections)

            
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserTrackSelectionTask.parse_args()
