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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqFlow.cxx

import argparse
import os
import re
from urllib.request import Request, urlopen
import ssl
import argcomplete
from argcomplete.completers import ChoicesCompleter
from extramodules.choicesHandler import ChoicesCompleterList
from extramodules.choicesHandler import NoAction
from extramodules.choicesHandler import ChoicesAction
from extramodules.dqLibGetter import DQLibGetter
from extramodules.helperOptions import HelperOptions
from extramodules.converters import O2Converters
from commondeps.centralityTable import CentralityTable
from commondeps.eventSelection import EventSelectionTask
from commondeps.multiplicityTable import MultiplicityTable
from commondeps.pidTOFBase import TofEventTime
from commondeps.pidTOFBeta import TofPidBeta
from commondeps.pidTPCTOFFull import TpcTofPidFull
from commondeps.trackPropagation import TrackPropagation
from commondeps.trackselection import TrackSelectionTask
from commondeps.dplAodReader import DplAodReader


class AnalysisQvector(object):
    
    """
    Class for Interface -> dqFlow.cxx Task -> Configurable, Process Functions

    Args:
        object (parser_args() object): dqFlow.cxx Interface
    """
    
    def __init__(
        self, parserAnalysisQvector = argparse.ArgumentParser(
            formatter_class = argparse.ArgumentDefaultsHelpFormatter,
            description = "Example Usage: ./runDQFlow.py <yourConfig.json> --arg value "
            ), eventSelection = EventSelectionTask(), centralityTable = CentralityTable(), multiplicityTable = MultiplicityTable(),
        tofEventTime = TofEventTime(), tofPidBeta = TofPidBeta(), tpcTofPidFull = TpcTofPidFull(), trackPropagation = TrackPropagation(),
        trackSelection = TrackSelectionTask(), helperOptions = HelperOptions(), o2Converters = O2Converters(), dplAodReader = DplAodReader()
        ):
        super(AnalysisQvector, self).__init__()
        self.parserAnalysisQvector = parserAnalysisQvector
        self.eventSelection = eventSelection
        self.centralityTable = centralityTable
        self.multiplicityTable = multiplicityTable
        self.tofEventTime = tofEventTime
        self.tofPidBeta = tofPidBeta
        self.tpcTofPidFull = tpcTofPidFull
        self.trackPropagation = trackPropagation
        self.trackSelection = trackSelection
        self.helperOptions = helperOptions
        self.o2Converters = o2Converters
        self.dplAodReader = dplAodReader
        self.parserAnalysisQvector.register("action", "none", NoAction)
        self.parserAnalysisQvector.register("action", "store_choice", ChoicesAction)
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        booleanSelections = ["true", "false"]
        
        # init for get DQ libraries
        allAnalysisCuts, allMCSignals, allSels, allMixing = DQLibGetter.getAnalysisSelections(self)
        
        # Interface
        groupAnalysisQvector = self.parserAnalysisQvector.add_argument_group(title = "Data processor options: analysis-qvector")
        groupAnalysisQvector.add_argument(
            "--cfgBarrelTrackCuts", help = "Space separated list of barrel track cuts", choices = allAnalysisCuts, nargs = "*",
            action = "store", type = str, metavar = "CFGBARRELTRACKCUTS",
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        groupAnalysisQvector.add_argument(
            "--cfgMuonCuts", help = "Space separated list of muon cuts", action = "store", choices = allAnalysisCuts, nargs = "*",
            type = str, metavar = "CFGMUONCUTS",
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        groupAnalysisQvector.add_argument(
            "--cfgEventCuts", help = "Space separated list of event cuts", choices = allAnalysisCuts, nargs = "*", action = "store",
            type = str, metavar = "CFGEVENTCUT",
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        groupAnalysisQvector.add_argument(
            "--cfgWithQA", help = "If true, fill QA histograms", action = "store", type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        groupAnalysisQvector.add_argument(
            "--cfgCutPtMin", help = "Minimal pT for tracks", action = "store", type = str, metavar = "CFGCUTPTMIN",
            )
        groupAnalysisQvector.add_argument(
            "--cfgCutPtMax", help = "Maximal pT for tracks", action = "store", type = str, metavar = "CFGCUTPTMAX",
            )
        groupAnalysisQvector.add_argument(
            "--cfgCutEta", help = "Eta range for tracks", action = "store", type = str, metavar = "CFGCUTETA",
            )
        groupAnalysisQvector.add_argument(
            "--cfgEtaLimit", help = "Eta gap separation, only if using subEvents", action = "store", type = str, metavar = "CFGETALIMIT",
            )
        groupAnalysisQvector.add_argument(
            "--cfgNPow", help = "Power of weights for Q vector", action = "store", type = str, metavar = "CFGNPOW",
            )
        groupAnalysisQvector.add_argument("--cfgEfficiency", help = "CCDB path to efficiency object", action = "store", type = str)
        groupAnalysisQvector.add_argument("--cfgAcceptance", help = "CCDB path to acceptance object", action = "store", type = str)
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        argcomplete.autocomplete(self.parserAnalysisQvector, always_complete_options = False)
        return self.parserAnalysisQvector.parse_args()
    
    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """
        
        self.helperOptions.parserHelperOptions = self.parserAnalysisQvector
        self.helperOptions.addArguments()
        
        self.dplAodReader.parserDplAodReader = self.parserAnalysisQvector
        self.dplAodReader.addArguments()
        
        self.eventSelection.parserEventSelectionTask = self.parserAnalysisQvector
        self.eventSelection.addArguments()
        
        self.trackSelection.parserTrackSelectionTask = self.parserAnalysisQvector
        self.trackSelection.addArguments()
        
        self.trackPropagation.parserTrackPropagation = self.parserAnalysisQvector
        self.trackPropagation.addArguments()
        
        self.multiplicityTable.parserMultiplicityTable = self.parserAnalysisQvector
        self.multiplicityTable.addArguments()
        
        self.centralityTable.parserCentralityTable = self.parserAnalysisQvector
        self.centralityTable.addArguments()
        
        self.tpcTofPidFull.parserTpcTofPidFull = self.parserAnalysisQvector
        self.tpcTofPidFull.addArguments()
        
        self.tofEventTime.parserTofEventTime = self.parserAnalysisQvector
        self.tofEventTime.addArguments()
        
        self.tofPidBeta.parserTofPidBeta = self.parserAnalysisQvector
        self.tofPidBeta.addArguments()
        
        self.o2Converters.parserO2Converters = self.parserAnalysisQvector
        self.o2Converters.addArguments()
        
        self.addArguments()
