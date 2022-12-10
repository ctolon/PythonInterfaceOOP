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

# \Author: ionut.cristian.arsene@cern.ch
# \Interface:  cevat.batuhan.tolon@cern.ch

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/filterPP.cxx

import argparse
import os
import re
from urllib.request import Request, urlopen
import ssl
from argcomplete.completers import ChoicesCompleter
import argcomplete
from extramodules.choicesHandler import ChoicesCompleterList
from extramodules.choicesHandler import NoAction
from extramodules.choicesHandler import ChoicesAction
from extramodules.helperOptions import HelperOptions
from extramodules.converters import O2Converters
from commondeps.eventSelection import EventSelectionTask
from commondeps.multiplicityTable import MultiplicityTable
from commondeps.pidTOFBase import TofEventTime
from commondeps.pidTOFBeta import TofPidBeta
from commondeps.pidTPCTOFFull import TpcTofPidFull
from commondeps.trackPropagation import TrackPropagation
from commondeps.trackselection import TrackSelectionTask
from commondeps.dplAodReader import DplAodReader
from extramodules.dqLibGetter import DQLibGetter


class DQFilterPPTask(object):
    
    """
    Class for Interface -> filterPP.cxx Task -> Configurable, Process Functions

    Args:
        object (parser_args() object): filterPP.cxx Interface
    """
    
    def __init__(
        self, parserDQFilterPPTask = argparse.ArgumentParser(formatter_class = argparse.ArgumentDefaultsHelpFormatter, description = "Example Usage: ./runFilterPP.py <yourConfig.json> --arg value",
                                                            ), eventSelection = EventSelectionTask(), multiplicityTable = MultiplicityTable(), tofEventTime = TofEventTime(), tofPidBeta = TofPidBeta(), tpcTofPidFull = TpcTofPidFull(), trackPropagation = TrackPropagation(), trackSelection = TrackSelectionTask(), helperOptions = HelperOptions(),
        o2Converters = O2Converters(), dplAodReader = DplAodReader(), dqLibGetter = DQLibGetter()
        ):
        super(DQFilterPPTask, self).__init__()
        self.parserDQFilterPPTask = parserDQFilterPPTask
        self.eventSelection = eventSelection
        self.multiplicityTable = multiplicityTable
        self.tofEventTime = tofEventTime
        self.tofPidBeta = tofPidBeta
        self.tpcTofPidFull = tpcTofPidFull
        self.trackPropagation = trackPropagation
        self.trackSelection = trackSelection
        self.helperOptions = helperOptions
        self.o2Converters = o2Converters
        self.dplAodReader = dplAodReader
        self.dqLibGetter = dqLibGetter
        self.parserDQFilterPPTask.register("action", "none", NoAction)
        self.parserDQFilterPPTask.register("action", "store_choice", ChoicesAction)
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        dqSelections = {
            "eventSelection": "Run DQ event selection",
            "barrelTrackSelection": "Run DQ barrel track selection",
            "muonSelection": "Run DQ muon selection",
            "barrelTrackSelectionTiny": "Run DQ barrel track selection tiny",
            "filterPPSelection": "Run filter task",
            "filterPPSelectionTiny": "Run filter task tiny"
            }
        dqSelectionsList = []
        for k, v in dqSelections.items():
            dqSelectionsList.append(k)
        
        booleanSelections = ["true", "false"]
        
        # Get DQ Analysis Selections from O2-DQ Framework Header Files
        allAnalysisCuts = self.dqLibGetter.allAnalysisCuts
        allSels = self.dqLibGetter.allSels
        
        # Interface
        
        # DQ Task Selections
        groupProcessFilterPP = self.parserDQFilterPPTask.add_argument_group(title = "Data processor options: d-q-filter-p-p-task, d-q-event-selection-task, d-q-barrel-track-selection, d-q-muons-selection ")
        groupProcessFilterPP.add_argument("--process", help = "DQ Tasks process Selections options", action = "store", type = str, nargs = "*", metavar = "PROCESS", choices = dqSelectionsList,).completer = ChoicesCompleterList(dqSelectionsList)
        
        for key, value in dqSelections.items():
            groupProcessFilterPP.add_argument(key, help = value, action = "none")
        
        # d-q-filter-p-p-task
        groupDQFilterPP = self.parserDQFilterPPTask.add_argument_group(title = "Data processor options: d-q-filter-p-p-task")
        groupDQFilterPP.add_argument("--cfgBarrelSels", help = "Configure Barrel Selection <track-cut>:[<pair-cut>]:<n>,[<track-cut>:[<pair-cut>]:<n>],... | example jpsiO2MCdebugCuts2::1 ", action = "store", type = str, nargs = "*", metavar = "CFGBARRELSELS", choices = allSels,).completer = ChoicesCompleterList(allSels)
        groupDQFilterPP.add_argument("--cfgMuonSels", help = "Configure Muon Selection <muon-cut>:[<pair-cut>]:<n> example muonQualityCuts:pairNoCut:1", action = "store", type = str, nargs = "*", metavar = "CFGMUONSELS", choices = allSels,).completer = ChoicesCompleterList(allSels)
        
        # d-q-event-selection-task
        groupDQEventSelection = self.parserDQFilterPPTask.add_argument_group(title = "Data processor options: d-q-event-selection-task")
        groupDQEventSelection.add_argument("--cfgEventCuts", help = "Space separated list of event cuts", nargs = "*", action = "store", type = str, metavar = "CFGEVENTCUTS", choices = allAnalysisCuts,).completer = ChoicesCompleterList(allAnalysisCuts)
        
        # d-q-barrel-track-selection
        groupDQBarrelTrackSelection = self.parserDQFilterPPTask.add_argument_group(title = "Data processor options: d-q-barrel-track-selection")
        groupDQBarrelTrackSelection.add_argument("--cfgBarrelTrackCuts", help = "Space separated list of barrel track cuts", nargs = "*", action = "store", type = str, metavar = "CFGBARRELTRACKCUTS", choices = allAnalysisCuts,).completer = ChoicesCompleterList(allAnalysisCuts)
        
        # d-q-muons-selection
        groupDQMuonsSelection = self.parserDQFilterPPTask.add_argument_group(title = "Data processor options: d-q-muons-selection")
        groupDQMuonsSelection.add_argument("--cfgMuonsCuts", help = "Space separated list of muon cuts in d-q muons selection", action = "store", nargs = "*", type = str, metavar = "CFGMUONSCUT", choices = allAnalysisCuts,).completer = ChoicesCompleterList(allAnalysisCuts)
        
        # all d-q tasks and selections
        groupQASelections = self.parserDQFilterPPTask.add_argument_group(title = "Data processor options: d-q-barrel-track-selection-task, d-q-muons-selection, d-q-event-selection-task, d-q-filter-p-p-task")
        groupQASelections.add_argument("--cfgWithQA", help = "If true, fill QA histograms", action = "store", type = str.lower, choices = (booleanSelections),).completer = ChoicesCompleter(booleanSelections)
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        argcomplete.autocomplete(self.parserDQFilterPPTask, always_complete_options = False)
        return self.parserDQFilterPPTask.parse_args()
    
    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """
        
        self.helperOptions.parserHelperOptions = self.parserDQFilterPPTask
        self.helperOptions.addArguments()
        
        self.dplAodReader.parserDplAodReader = self.parserDQFilterPPTask
        self.dplAodReader.addArguments()
        
        self.eventSelection.parserEventSelectionTask = self.parserDQFilterPPTask
        self.eventSelection.addArguments()
        
        self.trackSelection.parserTrackSelectionTask = self.parserDQFilterPPTask
        self.trackSelection.addArguments()
        
        self.trackPropagation.parserTrackPropagation = self.parserDQFilterPPTask
        self.trackPropagation.addArguments()
        
        self.multiplicityTable.parserMultiplicityTable = self.parserDQFilterPPTask
        self.multiplicityTable.addArguments()
        
        self.tpcTofPidFull.parserTpcTofPidFull = self.parserDQFilterPPTask
        self.tpcTofPidFull.addArguments()
        
        self.tofEventTime.parserTofEventTime = self.parserDQFilterPPTask
        self.tofEventTime.addArguments()
        
        self.tofPidBeta.parserTofPidBeta = self.parserDQFilterPPTask
        self.tofPidBeta.addArguments()
        
        self.o2Converters.parserO2Converters = self.parserDQFilterPPTask
        self.o2Converters.addArguments()
        
        self.addArguments()
