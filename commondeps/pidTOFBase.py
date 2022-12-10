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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/PID/pidTOFBase.cxx

import argparse
from argcomplete.completers import ChoicesCompleter


class TofEventTime(object):
    
    """
    Class for Interface -> pidTOFBase.cxx.cxx Task -> Configurable, Process Functions

    Args:
        object (parser_args() object): pidTOFBase.cxx.cxx Interface
    """
    
    def __init__(self, parserTofEventTime = argparse.ArgumentParser(add_help = False)):
        super(TofEventTime, self).__init__()
        self.parserTofEventTime = parserTofEventTime
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        ft0Selections = {
            "FT0": "FT0: Process with FT0",
            "NoFT0": "Process without FT0",
            "OnlyFT0": "Process only with FT0",
            "Run2": "Process with Run2 data"
            }
        ft0SelectionsList = []
        for k, v in ft0Selections.items():
            ft0SelectionsList.append(k)
        
        # Interface
        groupTofEventTime = self.parserTofEventTime.add_argument_group(title = "Data processor options: tof-event-time")
        groupTofEventTime.add_argument("--minMomentum", help = "Minimum momentum to select track sample for TOF event time", action = "store", metavar = "MINMOMENTUM", type = str)
        groupTofEventTime.add_argument("--maxMomentum", help = "Maximum momentum to select track sample for TOF event time", action = "store", metavar = "MAXMOMENTUM", type = str)
        groupTofEventTime.add_argument("--FT0", help = "tof-event-time: PROCESS_SWITCH options", action = "store", metavar = "FT0", type = str, choices = ft0SelectionsList,).completer = ChoicesCompleter(ft0SelectionsList)
        groupProcess = self.parserTofEventTime.add_argument_group(title = "Choice List for tof-event-time PROCESS_SWITCH options")
        for key, value in ft0Selections.items():
            groupProcess.add_argument(key, help = value, action = "none")
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserTofEventTime.parse_args()
