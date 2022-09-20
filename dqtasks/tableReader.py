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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/tableReader.cxx

import argparse

import argcomplete
from argcomplete.completers import ChoicesCompleter
from commondeps.dplAodReader import DplAodReader
from extramodules.dqLibGetter import DQLibGetter
from extramodules.choicesCompleterList import ChoicesCompleterList
from extramodules.helperOptions import HelperOptions

from extramodules.actionHandler import NoAction
from extramodules.actionHandler import ChoicesAction
from extramodules.helperOptions import HelperOptions


class TableReader(object):
    
    """
    Class for Interface -> tableReader.cxx Task -> Configurable, Process Functions

    Args:
        object (parser_args() object): tableReader.cxx Interface
    """
    
    def __init__(
        self, parserTableReader = argparse.ArgumentParser(
            formatter_class = argparse.ArgumentDefaultsHelpFormatter,
            description = "Example Usage: ./runTableReader.py <yourConfig.json> --arg value",
            ), helperOptions = HelperOptions(), dplAodReader = DplAodReader()
        ):
        super(TableReader, self).__init__()
        self.parserTableReader = parserTableReader
        self.helperOptions = helperOptions
        self.dplAodReader = dplAodReader
        self.parserTableReader.register("action", "none", NoAction)
        self.parserTableReader.register("action", "store_choice", ChoicesAction)
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        readerPath = "configs/readerConfiguration_reducedEvent.json"
        writerPath = "configs/writerConfiguration_dileptons.json"
        
        # Predefined Selections
        analysisSelections = {
            "eventSelection": "Run event selection on DQ skimmed events",
            "muonSelection": "Run muon selection on DQ skimmed muons",
            "trackSelection": "Run barrel track selection on DQ skimmed tracks",
            "eventMixing": "Run mixing on skimmed tracks based muon and track selections",
            "sameEventPairing": "Run same event pairing selection on DQ skimmed data",
            "dileptonHadron": "Run dilepton-hadron pairing, using skimmed data",
            }
        analysisSelectionsList = []
        for k, v in analysisSelections.items():
            analysisSelectionsList.append(k)
        
        sameEventPairingProcessSelections = {
            "JpsiToEE": "Run electron-electron pairing, with skimmed tracks",
            "JpsiToMuMu": "Run muon-muon pairing, with skimmed muons",
            "JpsiToMuMuVertexing": "Run muon-muon pairing and vertexing, with skimmed muons",
            "VnJpsiToEE": "Run barrel-barrel vn mixing on skimmed tracks",
            "VnJpsiToMuMu": "Run muon-muon vn mixing on skimmed tracks",
            "ElectronMuon": "Run electron-muon pairing, with skimmed tracks/muons",
            "All": "Run all types of pairing, with skimmed tracks/muons",
            }
        sameEventPairingProcessSelectionsList = []
        for k, v in sameEventPairingProcessSelections.items():
            sameEventPairingProcessSelectionsList.append(k)
        
        booleanSelections = ["true", "false"]
        
        mixingSelections = {
            "Barrel": "Run barrel-barrel mixing on skimmed tracks",
            "Muon": "Run muon-muon mixing on skimmed muons",
            "BarrelMuon": "Run barrel-muon mixing on skimmed tracks/muons",
            "BarrelVn": "Run barrel-barrel vn mixing on skimmed tracks",
            "MuonVn": "Run muon-muon vn mixing on skimmed tracks",
            }
        mixingSelectionsList = []
        for k, v in mixingSelections.items():
            mixingSelectionsList.append(k)
        
        # init for get DQ libraries
        allAnalysisCuts, allMCSignals, allSels, allMixing = DQLibGetter.getAnalysisSelections(self)
        
        # Interface
        
        # analysis task selections
        groupAnalysisSelections = self.parserTableReader.add_argument_group(
            title = "Data processor options: analysis-event-selection, analysis-muon-selection, analysis-track-selection, analysis-event-mixing, analysis-dilepton-hadron"
            )
        groupAnalysisSelections.add_argument(
            "--analysis", help = "Skimmed process selections for Data Analysis", action = "store", nargs = "*", type = str,
            metavar = "ANALYSIS", choices = analysisSelectionsList,
            ).completer = ChoicesCompleterList(analysisSelectionsList)
        
        for key, value in analysisSelections.items():
            groupAnalysisSelections.add_argument(key, help = value, action = "none")
        
        # same event pairing process function selection
        groupProcessSEPSelections = self.parserTableReader.add_argument_group(title = "Data processor options: analysis-same-event-pairing")
        groupProcessSEPSelections.add_argument(
            "--process", help = "Skimmed process selections for analysis-same-event-pairing task", action = "store", nargs = "*",
            type = str, metavar = "PROCESS", choices = sameEventPairingProcessSelectionsList,
            ).completer = ChoicesCompleterList(sameEventPairingProcessSelectionsList)
        groupProcess = self.parserTableReader.add_argument_group(
            title = "Choice List for analysis-same-event-pairing task Process options (when a value added to parameter, processSkimmed value is converted from false to true)"
            )
        
        for key, value in sameEventPairingProcessSelections.items():
            groupProcess.add_argument(key, help = value, action = "none")
        
        # analysis-event-mixing
        groupAnalysisEventMixing = self.parserTableReader.add_argument_group(title = "Data processor options: analysis-event-mixing")
        groupAnalysisEventMixing.add_argument(
            "--mixing", help = "Skimmed process selections for Event Mixing manually", nargs = "*", action = "store", type = str,
            choices = mixingSelectionsList,
            ).completer = ChoicesCompleterList(mixingSelectionsList)
        
        # cfg for QA
        groupQASelections = self.parserTableReader.add_argument_group(
            title = "Data processor options: analysis-event-selection, analysis-muon-selection, analysis-track-selection, analysis-event-mixing"
            )
        groupQASelections.add_argument(
            "--cfgQA", help = "If true, fill QA histograms", action = "store", type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        
        # analysis-event-selection
        groupAnalysisEventSelection = self.parserTableReader.add_argument_group(title = "Data processor options: analysis-event-selection")
        groupAnalysisEventSelection.add_argument(
            "--cfgMixingVars", help = "Mixing configs separated by a space", nargs = "*", action = "store", type = str,
            metavar = "CFGMIXINGVARS", choices = allMixing,
            ).completer = ChoicesCompleterList(allMixing)
        groupAnalysisEventSelection.add_argument(
            "--cfgEventCuts", help = "Space separated list of event cuts", nargs = "*", action = "store", type = str,
            metavar = "CFGEVENTCUTS", choices = allAnalysisCuts,
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        
        # analysis-muon-selection
        groupAnalysisMuonSelection = self.parserTableReader.add_argument_group(title = "Data processor options: analysis-muon-selection")
        groupAnalysisMuonSelection.add_argument(
            "--cfgMuonCuts", help = "Space separated list of muon cuts", nargs = "*", action = "store", type = str, metavar = "CFGMUONCUTS",
            choices = allAnalysisCuts,
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        
        # analysis-track-selection
        groupAnalysisTrackSelection = self.parserTableReader.add_argument_group(title = "Data processor options: analysis-track-selection")
        groupAnalysisTrackSelection.add_argument(
            "--cfgTrackCuts", help = "Space separated list of barrel track cuts", nargs = "*", action = "store", type = str,
            metavar = "CFGTRACKCUTS", choices = allAnalysisCuts,
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        
        # analysis-dilepton-hadron
        groupAnalysisDileptonHadron = self.parserTableReader.add_argument_group(title = "Data processor options: analysis-dilepton-hadron")
        groupAnalysisDileptonHadron.add_argument(
            "--cfgLeptonCuts", help = "Space separated list of barrel track cuts", nargs = "*", action = "store", type = str,
            metavar = "CFGLEPTONCUTS", choices = allAnalysisCuts,
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        
        # Aod Writer - Reader configs
        groupDPLReader = self.parserTableReader.add_argument_group(
            title = "Data processor options: internal-dpl-aod-reader, internal-dpl-aod-writer"
            )
        groupDPLReader.add_argument(
            "--reader",
            help = "Reader config JSON with path. For Standart Analysis use as default, for dilepton analysis change to dilepton JSON config file",
            action = "store", default = readerPath, type = str
            )
        groupDPLReader.add_argument(
            "--writer", help = "Argument for producing dileptonAOD.root. Set false for disable", action = "store", default = writerPath,
            type = str
            )
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        argcomplete.autocomplete(self.parserTableReader, always_complete_options = False)
        return self.parserTableReader.parse_args()
    
    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """
        
        self.helperOptions.parserHelperOptions = self.parserTableReader
        self.helperOptions.addArguments()
        
        self.dplAodReader.parserDplAodReader = self.parserTableReader
        self.dplAodReader.addArguments()
        
        self.addArguments()
