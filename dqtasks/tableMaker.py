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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMaker.cxx

import argparse
from extramodules.choicesHandler import NoAction
from extramodules.choicesHandler import ChoicesAction
from extramodules.helperOptions import HelperOptions
from extramodules.converters import O2Converters
import argcomplete
from argcomplete.completers import ChoicesCompleter
from extramodules.choicesHandler import ChoicesCompleterList
from commondeps.centralityTable import CentralityTable
from commondeps.eventSelection import EventSelectionTask
from commondeps.multiplicityTable import MultiplicityTable
from commondeps.pidTOFBase import TofEventTime
from commondeps.pidTOFBeta import TofPidBeta
from commondeps.pidTPCTOFFull import TpcTofPidFull
from commondeps.trackPropagation import TrackPropagation
from commondeps.trackselection import TrackSelectionTask
from commondeps.dplAodReader import DplAodReader
from dqtasks.v0selector import V0selector
from extramodules.dqLibGetter import DQLibGetter

# Special configurations for filterPP are combined to avoid conflicts in the tableMaker interface


class TableMaker(object):
    
    """
    Class for Interface -> tableMaker.cxx Task -> Configurable, Process Functions.
    Also this class includes some filterPP and dqFlow task arguments to avoid conflicts

    Args:
        object (parser_args() object): tableMaker.cxx Interface
    """
    
    def __init__(
        self, parserTableMaker = argparse.ArgumentParser(
            formatter_class = argparse.ArgumentDefaultsHelpFormatter,
            description = "Example Usage: ./runTableMaker.py <yourConfig.json> --arg value "
            ), eventSelection = EventSelectionTask(), centralityTable = CentralityTable(), multiplicityTable = MultiplicityTable(),
        tofEventTime = TofEventTime(), tofPidBeta = TofPidBeta(), tpcTofPidFull = TpcTofPidFull(), trackPropagation = TrackPropagation(),
        trackSelection = TrackSelectionTask(), v0selector = V0selector(), helperOptions = HelperOptions(), o2Converters = O2Converters(),
        dplAodReader = DplAodReader(), dqLibGetter = DQLibGetter()
        ):
        super(TableMaker, self).__init__()
        self.parserTableMaker = parserTableMaker
        self.eventSelection = eventSelection
        self.centralityTable = centralityTable
        self.multiplicityTable = multiplicityTable
        self.tofEventTime = tofEventTime
        self.tofPidBeta = tofPidBeta
        self.tpcTofPidFull = tpcTofPidFull
        self.trackPropagation = trackPropagation
        self.trackSelection = trackSelection
        self.v0selector = v0selector
        self.helperOptions = helperOptions
        self.o2Converters = o2Converters
        self.dplAodReader = dplAodReader
        self.dqLibGetter = dqLibGetter
        self.parserTableMaker.register("action", "none", NoAction)
        self.parserTableMaker.register("action", "store_choice", ChoicesAction)
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        tableMakerProcessSelections = {
            "Full": "Build full DQ skimmed data model, w/o centrality",
            "FullWithCov": "Build full DQ skimmed data model, w/ track and fwdtrack covariance tables",
            "FullWithCent": "Build full DQ skimmed data model, w/ centrality",
            "BarrelOnly": "Build barrel-only DQ skimmed data model, w/o centrality",
            "BarrelOnlyWithCov": "Build barrel-only DQ skimmed data model, w/ track cov matrix",
            "BarrelOnlyWithV0Bits": "Build full DQ skimmed data model, w/o centrality, w/ V0Bits",
            "BarrelOnlyWithEventFilter": "Build full DQ skimmed data model, w/o centrality, w/ event filter",
            "BarrelOnlyWithQvector": "Build full DQ skimmed data model, w/ centrality, w/ q vector",
            "BarrelOnlyWithCent": "Build barrel-only DQ skimmed data model, w/ centrality",
            "MuonOnly": "Build muon-only DQ skimmed data model",
            "MuonOnlyWithCov": "Build muon-only DQ skimmed data model, w/ muon cov matrix",
            "MuonOnlyWithCent": "Build muon-only DQ skimmed data model, w/ centrality",
            "MuonOnlyWithFilter": "Build muon-only DQ skimmed data model, w/ event filter",
            "MuonOnlyWithQvector": "Build muon-only DQ skimmed data model, w/ q vector",
            "OnlyBCs": "Analyze the BCs to store sampled lumi",
            }
        tableMakerProcessSelectionsList = []
        for k, v in tableMakerProcessSelections.items():
            tableMakerProcessSelectionsList.append(k)
        
        booleanSelections = ["true", "false"]
        
        # Get DQ Analysis Selections from O2-DQ Framework Header Files
        allAnalysisCuts = self.dqLibGetter.allAnalysisCuts
        allSels = self.dqLibGetter.allSels
        allHistos = self.dqLibGetter.allHistos
        
        # Interface
        
        # analysis-qvector
        groupAnalysisQvector = self.parserTableMaker.add_argument_group(title = "Data processor options: analysis-qvector")
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
        
        # all d-q tasks and selections
        groupQASelections = self.parserTableMaker.add_argument_group(
            title = "Data processor options: d-q-event-selection-task, d-q-barrel-track-selection-task, d-q-muons-selection, d-q-filter-p-p-task, analysis-qvector"
            )
        groupQASelections.add_argument(
            "--cfgWithQA", help = "If true, fill QA histograms", action = "store", type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        
        # d-q-track barrel-task
        groupDQTrackBarrelTask = self.parserTableMaker.add_argument_group(title = "Data processor options: d-q-barrel-track-selection-task")
        groupDQTrackBarrelTask.add_argument(
            "--isBarrelSelectionTiny",
            help = "Run barrel track selection instead of normal(process func. for barrel selection must be true)", action = "store",
            type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        
        # d-q muons-selection
        groupDQMuonsSelection = self.parserTableMaker.add_argument_group(title = "Data processor options: d-q muons-selection")
        groupDQMuonsSelection.add_argument(
            "--cfgMuonsCuts", help = "Space separated list of ADDITIONAL muon track cuts", action = "store", nargs = "*", type = str,
            metavar = "CFGMUONSCUT", choices = allAnalysisCuts,
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        
        # d-q-filter-p-p-task
        groupDQFilterPP = self.parserTableMaker.add_argument_group(title = "Data processor options: d-q-filter-p-p-task")
        groupDQFilterPP.add_argument(
            "--cfgBarrelSels",
            help = "Configure Barrel Selection <track-cut>:[<pair-cut>]:<n>,[<track-cut>:[<pair-cut>]:<n>],... | example jpsiO2MCdebugCuts2::1 ",
            action = "store", type = str, nargs = "*", metavar = "CFGBARRELSELS", choices = allSels,
            ).completer = ChoicesCompleterList(allSels)
        groupDQFilterPP.add_argument(
            "--cfgMuonSels", help = "Configure Muon Selection <muon-cut>:[<pair-cut>]:<n> example muonQualityCuts:pairNoCut:1",
            action = "store", type = str, nargs = "*", metavar = "CFGMUONSELS", choices = allSels,
            ).completer = ChoicesCompleterList(allSels)
        groupDQFilterPP.add_argument(
            "--isFilterPPTiny", help = "Run filter tiny task instead of normal (processFilterPP must be true) ", action = "store",
            type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        
        # table-maker configurables
        groupTableMakerConfigs = self.parserTableMaker.add_argument_group(title = "Data processor options: table-maker")
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
        groupTableMakerConfigs.add_argument(
            "--cfgAddEventHistogram", help = "Comma separated list of event histograms", action = "store", type = str, metavar="CFGADDEVENTHISTOGRAM", choices = allHistos,
            ).completer = ChoicesCompleterList(allHistos)
        groupTableMakerConfigs.add_argument(
            "--cfgAddTrackHistogram", help = "Comma separated list of track histograms", action = "store", type = str, metavar="CFGADDTRACKHISTOGRAM", choices = allHistos,
            ).completer = ChoicesCompleterList(allHistos)
        groupTableMakerConfigs.add_argument(
            "--cfgAddMuonHistogram", help = "Comma separated list of muon histograms", action = "store", type = str, metavar="CFGADDMUONHISTOGRAM", choices = allHistos,
            ).completer = ChoicesCompleterList(allHistos)
        groupTableMakerConfigs.add_argument("--cfgBarrelLowPt", help = "Low pt cut for tracks in the barrel", action = "store", type = str)
        groupTableMakerConfigs.add_argument("--cfgMuonLowPt", help = "Low pt cut for muons", action = "store", type = str)
        groupTableMakerConfigs.add_argument(
            "--cfgQA", help = "If true, fill QA histograms", action = "store", type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        groupTableMakerConfigs.add_argument(
            "--cfgDetailedQA", help = "If true, include more QA histograms (BeforeCuts classes and more)", action = "store",
            type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        # groupTableMakerConfigs.add_argument("--cfgIsRun2", help="Run selection true or false", action="store", choices=["true","false"], type=str) # no need
        groupTableMakerConfigs.add_argument(
            "--cfgIsAmbiguous", help = "Whether we enable QA plots for ambiguous tracks", action = "store", choices = booleanSelections,
            type = str.lower
            ).completer = ChoicesCompleter(booleanSelections)
        groupTableMakerConfigs.add_argument("--cfgMinTpcSignal", help = "Minimum TPC signal", action = "store", type = str)
        groupTableMakerConfigs.add_argument("--cfgMaxTpcSignal", help = "Maximum TPC signal", action = "store", type = str)
        groupTableMakerConfigs.add_argument(
            "--process", help = "table-maker: PROCESS_SWITCH options", action = "store", type = str, nargs = "*", metavar = "PROCESS",
            choices = tableMakerProcessSelectionsList,
            ).completer = ChoicesCompleterList(tableMakerProcessSelectionsList)
        groupProcess = self.parserTableMaker.add_argument_group(title = "Choice List for table-maker PROCESS_SWITCH options")
        for key, value in tableMakerProcessSelections.items():
            groupProcess.add_argument(key, help = value, action = "none")
        
        # core part
        groupCoreSelections = self.parserTableMaker.add_argument_group(title = "Core configurations that must be configured")
        groupCoreSelections.add_argument("-runData", help = "Run over Data", action = "store_true", default = True)
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        
        argcomplete.autocomplete(self.parserTableMaker, always_complete_options = False)
        return self.parserTableMaker.parse_args()
    
    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """
        
        self.helperOptions.parserHelperOptions = self.parserTableMaker
        self.helperOptions.addArguments()
        
        self.dplAodReader.parserDplAodReader = self.parserTableMaker
        self.dplAodReader.addArguments()
        
        self.eventSelection.parserEventSelectionTask = self.parserTableMaker
        self.eventSelection.addArguments()
        
        self.trackSelection.parserTrackSelectionTask = self.parserTableMaker
        self.trackSelection.addArguments()
        
        self.trackPropagation.parserTrackPropagation = self.parserTableMaker
        self.trackPropagation.addArguments()
        
        self.multiplicityTable.parserMultiplicityTable = self.parserTableMaker
        self.multiplicityTable.addArguments()
        
        self.centralityTable.parserCentralityTable = self.parserTableMaker
        self.centralityTable.addArguments()
        
        self.v0selector.parserV0selector = self.parserTableMaker
        self.v0selector.addArguments()
        
        self.tpcTofPidFull.parserTpcTofPidFull = self.parserTableMaker
        self.tpcTofPidFull.addArguments()
        
        self.tofEventTime.parserTofEventTime = self.parserTableMaker
        self.tofEventTime.addArguments()
        
        self.tofPidBeta.parserTofPidBeta = self.parserTableMaker
        self.tofPidBeta.addArguments()
        
        self.o2Converters.parserO2Converters = self.parserTableMaker
        self.o2Converters.addArguments()
        
        self.addArguments()
    
    # This function not work should be integrated instead of mergeArgs
    
    """
    def mergeMultiArgs(self, *objects):
        parser = self.parserTableMaker
        for object in objects:
            object.parser = parser
            object.addArguments()
        self.addArguments()
    """
