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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMakerMC.cxx

import argparse

from argcomplete.completers import ChoicesCompleter
import argcomplete
from extramodules.choicesCompleterList import ChoicesCompleterList
from extramodules.helperOptions import HelperOptions
from extramodules.actionHandler import NoAction
from extramodules.actionHandler import ChoicesAction
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

from extramodules.dqLibGetter import DQLibGetter


class TableMakerMC(object):
    
    """
    Class for Interface -> tableMakerMC.cxx Task -> Configurable, Process Functions

    Args:
        object (parser_args() object): tableMakerMC.cxx Interface
    """
    
    def __init__(
        self, parserTableMakerMC = argparse.ArgumentParser(
            formatter_class = argparse.ArgumentDefaultsHelpFormatter,
            description = "Example Usage: ./runTableMakerMC.py <yourConfig.json> --arg value",
            ), eventSelection = EventSelectionTask(), centralityTable = CentralityTable(), multiplicityTable = MultiplicityTable(),
        tofEventTime = TofEventTime(), tofPidBeta = TofPidBeta(), tpcTofPidFull = TpcTofPidFull(), trackPropagation = TrackPropagation(),
        trackSelection = TrackSelectionTask(), helperOptions = HelperOptions(), o2Converters = O2Converters(), dplAodReader = DplAodReader()
        ):
        super(TableMakerMC, self).__init__()
        self.parserTableMakerMC = parserTableMakerMC
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
        self.parserTableMakerMC.register("action", "none", NoAction)
        self.parserTableMakerMC.register("action", "store_choice", ChoicesAction)
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        tableMakerProcessSelections = {
            "Full": "Build full DQ skimmed data model, w/o centrality",
            "FullWithCov": "Build full DQ skimmed data model, w/ track and fwdtrack covariance tables",
            "BarrelOnly": "Build barrel-only DQ skimmed data model, w/o centrality",
            "BarrelOnlyWithCov": "Build barrel-only DQ skimmed data model, w/ track cov matrix",
            "BarrelOnlyWithCent": "Build barrel-only DQ skimmed data model, w/ centrality",
            "MuonOnlyWithCov": "Build muon-only DQ skimmed data model, w/ muon cov matrix",
            "MuonOnlyWithCent": "Build muon-only DQ skimmed data model, w/ centrality",
            "OnlyBCs": "Analyze the BCs to store sampled lumi",
            }
        tableMakerProcessSelectionsList = []
        for k, v in tableMakerProcessSelections.items():
            tableMakerProcessSelectionsList.append(k)
        
        booleanSelections = ["true", "false"]
        
        # init for get DQ libraries
        allAnalysisCuts, allMCSignals, allSels, allMixing = DQLibGetter.getAnalysisSelections(self)
        
        # Interface
        groupTableMakerConfigs = self.parserTableMakerMC.add_argument_group(title = "Data processor options: table-maker-m-c")
        groupTableMakerConfigs.add_argument(
            "--cfgEventCuts", help = "Space separated list of event cuts", nargs = "*", action = "store", type = str,
            metavar = "CFGEVENTCUTS", choices = allAnalysisCuts,
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        groupTableMakerConfigs.add_argument(
            "--cfgBarrelTrackCuts", help = " Space separated list of barrel track cuts", nargs = "*", action = "store", type = str,
            metavar = "CFGBARRELTRACKCUTS", choices = allAnalysisCuts,
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        groupTableMakerConfigs.add_argument(
            "--cfgMuonCuts", help = "Space separated list of muon cuts in table-maker", action = "store", nargs = "*", type = str,
            metavar = "CFGMUONCUTS", choices = allAnalysisCuts,
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        groupTableMakerConfigs.add_argument("--cfgBarrelLowPt", help = "Low pt cut for tracks in the barrel", action = "store", type = str)
        groupTableMakerConfigs.add_argument("--cfgMuonLowPt", help = "Low pt cut for muons", action = "store", type = str)
        groupTableMakerConfigs.add_argument(
            "--cfgNoQA", help = "If true, no QA histograms", action = "store", type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        groupTableMakerConfigs.add_argument(
            "--cfgDetailedQA", help = "If true, include more QA histograms (BeforeCuts classes and more)", action = "store",
            type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        # groupTableMakerConfigs.add_argument("--cfgIsRun2", help="Run selection true or false", action="store", choices=["true","false"], type=str) # no need
        groupTableMakerConfigs.add_argument("--cfgMinTpcSignal", help = "Minimum TPC signal", action = "store", type = str)
        groupTableMakerConfigs.add_argument("--cfgMaxTpcSignal", help = "Maximum TPC signal", action = "store", type = str)
        groupTableMakerConfigs.add_argument(
            "--cfgMCsignals", help = "Space separated list of MC signals", action = "store", nargs = "*", type = str,
            metavar = "CFGMCSIGNALS", choices = allMCSignals,
            ).completer = ChoicesCompleterList(allMCSignals)
        
        groupProcessTableMaker = self.parserTableMakerMC.add_argument_group(title = "Data processor options: table-maker-m-c")
        groupProcessTableMaker.add_argument(
            "--process", help = "Process Selection options for tableMaker/tableMakerMC Data Processing and Skimming", action = "store",
            type = str, nargs = "*", metavar = "PROCESS", choices = tableMakerProcessSelectionsList,
            ).completer = ChoicesCompleterList(tableMakerProcessSelectionsList)
        for key, value in tableMakerProcessSelections.items():
            groupProcessTableMaker.add_argument(key, help = value, action = "none")
        
        # Core Part
        groupCoreSelections = self.parserTableMakerMC.add_argument_group(title = "Core configurations that must be configured")
        groupCoreSelections.add_argument("-runMC", help = "Run over MC", action = "store_true", default = True)
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        argcomplete.autocomplete(self.parserTableMakerMC, always_complete_options = False)
        return self.parserTableMakerMC.parse_args()
    
    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """
        
        self.eventSelection.parserEventSelectionTask = self.parserTableMakerMC
        self.eventSelection.addArguments()
        
        self.centralityTable.parserCentralityTable = self.parserTableMakerMC
        self.centralityTable.addArguments()
        
        self.multiplicityTable.parserMultiplicityTable = self.parserTableMakerMC
        self.multiplicityTable.addArguments()
        
        self.tofEventTime.parserTofEventTime = self.parserTableMakerMC
        self.tofEventTime.addArguments()
        
        self.tofPidBeta.parserTofPidBeta = self.parserTableMakerMC
        self.tofPidBeta.addArguments()
        
        self.tpcTofPidFull.parserTpcTofPidFull = self.parserTableMakerMC
        self.tpcTofPidFull.addArguments()
        
        self.trackPropagation.parserTrackPropagation = self.parserTableMakerMC
        self.trackPropagation.addArguments()
        
        self.trackSelection.parserTrackSelectionTask = self.parserTableMakerMC
        self.trackSelection.addArguments()
        
        self.helperOptions.parserHelperOptions = self.parserTableMakerMC
        self.helperOptions.addArguments()
        
        # self.o2Converters.parserO2Converters = self.parserTableMakerMC
        # self.o2Converters.addArguments()
        
        self.dplAodReader.parserDplAodReader = self.parserTableMakerMC
        self.dplAodReader.addArguments()
        
        self.addArguments()
