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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGEM/Dilepton/Tasks/emEfficiencyEE.cxx

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


class EMEfficiencyNoSkimmed(object):
    
    """
    Class for Interface -> emEfficiencyEE.cxx Task -> Configurable, Process Functions

    Args:
        object (parser_args() object): emEfficiencyEE.cxx Interface
    """
    
    def __init__(
        self, parserEMEfficiencyNoSkimmed = argparse.ArgumentParser(formatter_class = argparse.ArgumentDefaultsHelpFormatter, description = "Example Usage: ./runEMEfficiencyNoSkimmed.py <yourConfig.json> --arg value",
                                                                    ), eventSelection = EventSelectionTask(), multiplicityTable = MultiplicityTable(), tofEventTime = TofEventTime(), tofPidBeta = TofPidBeta(), tpcTofPidFull = TpcTofPidFull(), trackPropagation = TrackPropagation(), trackSelection = TrackSelectionTask(),
        helperOptions = HelperOptions(), o2Converters = O2Converters(), dplAodReader = DplAodReader(), dqLibGetter = DQLibGetter()
        ):
        super(EMEfficiencyNoSkimmed, self).__init__()
        self.parserEMEfficiencyNoSkimmed = parserEMEfficiencyNoSkimmed
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
        self.parserEMEfficiencyNoSkimmed.register("action", "none", NoAction)
        self.parserEMEfficiencyNoSkimmed.register("action", "store_choice", ChoicesAction)
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        dqSelections = {
            "eventSelection": "Run event selection on DQ skimmed events",
            "eventQA": "Run event QA on DQ skimmed events",
            "trackSelection": "Run barrel track selection on DQ skimmed tracks"
            }
        dqSelectionsList = []
        for k, v in dqSelections.items():
            dqSelectionsList.append(k)
        
        booleanSelections = ["true", "false"]
        
        # Get DQ Analysis Selections from O2-DQ Framework Header Files
        allAnalysisCuts = self.dqLibGetter.allAnalysisCuts
        allMCSignals = self.dqLibGetter.allMCSignals
        
        # Interface
        
        # analysis task selections
        groupAnalysisSelections = self.parserEMEfficiencyNoSkimmed.add_argument_group(title = "Data processor options: analysis-event-selection, analysis-track-selection")
        groupAnalysisSelections.add_argument("--analysis", help = "Noskimmed process selections for MC Analysis", action = "store", nargs = "*", type = str, metavar = "ANALYSIS", choices = dqSelectionsList,).completer = ChoicesCompleterList(dqSelectionsList)
        
        for key, value in dqSelections.items():
            groupAnalysisSelections.add_argument(key, help = value, action = "none")
        
        # cfg for QA
        groupQASelections = self.parserEMEfficiencyNoSkimmed.add_argument_group(title = "Data processor options: analysis-event-selection, analysis-track-selection")
        groupQASelections.add_argument("--cfgQA", help = "If true, fill QA histograms", action = "store", type = str.lower, choices = (booleanSelections),).completer = ChoicesCompleter(booleanSelections)
        
        # analysis-event-selection
        groupAnalysisEventSelection = self.parserEMEfficiencyNoSkimmed.add_argument_group(title = "Data processor options: analysis-event-selection")
        groupAnalysisEventSelection.add_argument("--cfgEventCuts", help = "Space separated list of event cuts", nargs = "*", action = "store", type = str, metavar = "CFGEVENTCUTS", choices = allAnalysisCuts,).completer = ChoicesCompleterList(allAnalysisCuts)
        
        # analysis-track-selection
        groupAnalysisTrackSelection = self.parserEMEfficiencyNoSkimmed.add_argument_group(title = "Data processor options: analysis-track-selection")
        groupAnalysisTrackSelection.add_argument("--cfgTrackCuts", help = "Space separated list of barrel track cuts", nargs = "*", action = "store", type = str, metavar = "CFGTRACKCUTS", choices = allAnalysisCuts,).completer = ChoicesCompleterList(allAnalysisCuts)
        groupAnalysisTrackSelection.add_argument("--cfgTrackMCSignals", help = "Space separated list of MC signals", nargs = "*", action = "store", type = str, metavar = "CFGTRACKMCSIGNALS", choices = allMCSignals,).completer = ChoicesCompleterList(allMCSignals)
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        argcomplete.autocomplete(self.parserEMEfficiencyNoSkimmed, always_complete_options = False)
        return self.parserEMEfficiencyNoSkimmed.parse_args()
    
    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """
        
        self.helperOptions.parserHelperOptions = self.parserEMEfficiencyNoSkimmed
        self.helperOptions.addArguments()
        
        self.dplAodReader.parserDplAodReader = self.parserEMEfficiencyNoSkimmed
        self.dplAodReader.addArguments()
        
        self.eventSelection.parserEventSelectionTask = self.parserEMEfficiencyNoSkimmed
        self.eventSelection.addArguments()
        
        self.trackSelection.parserTrackSelectionTask = self.parserEMEfficiencyNoSkimmed
        self.trackSelection.addArguments()
        
        self.trackPropagation.parserTrackPropagation = self.parserEMEfficiencyNoSkimmed
        self.trackPropagation.addArguments()
        
        self.multiplicityTable.parserMultiplicityTable = self.parserEMEfficiencyNoSkimmed
        self.multiplicityTable.addArguments()
        
        self.tpcTofPidFull.parserTpcTofPidFull = self.parserEMEfficiencyNoSkimmed
        self.tpcTofPidFull.addArguments()
        
        self.tofEventTime.parserTofEventTime = self.parserEMEfficiencyNoSkimmed
        self.tofEventTime.addArguments()
        
        self.tofPidBeta.parserTofPidBeta = self.parserEMEfficiencyNoSkimmed
        self.tofPidBeta.addArguments()
        
        self.o2Converters.parserO2Converters = self.parserEMEfficiencyNoSkimmed
        self.o2Converters.addArguments()
        
        self.addArguments()
