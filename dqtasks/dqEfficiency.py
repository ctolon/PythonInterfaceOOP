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

# Orginal Task For dqEfficiency.cxx: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqEfficiency.cxx

import argparse
import os
import re
from urllib.request import Request, urlopen
import ssl
import argcomplete
from argcomplete.completers import ChoicesCompleter
from commondeps.dplAodReader import DplAodReader
from extramodules.choicesHandler import ChoicesCompleterList
from extramodules.choicesHandler import NoAction
from extramodules.choicesHandler import ChoicesAction
from extramodules.dqLibGetter import DQLibGetter
from extramodules.helperOptions import HelperOptions


class DQEfficiency(object):
    
    """
    Class for Interface -> dqEfficiency.cxx Task -> Configurable, Process Functions

    Args:
        object (parser_args object): dqEfficiency.cxx Interface
    """
    
    def __init__(
        self, parserDQEfficiency = argparse.ArgumentParser(
            formatter_class = argparse.ArgumentDefaultsHelpFormatter,
            description = "Example Usage: ./runDQEfficiency.py <yourConfig.json> --arg value "
            ), helperOptions = HelperOptions(), dplAodReader = DplAodReader(), dqLibGetter = DQLibGetter()
        ):
        super(DQEfficiency, self).__init__()
        self.parserDQEfficiency = parserDQEfficiency
        self.dplAodReader = dplAodReader
        self.helperOptions = helperOptions
        self.dqLibGetter = dqLibGetter
        self.parserDQEfficiency.register("action", "none", NoAction)
        self.parserDQEfficiency.register("action", "store_choice", ChoicesAction)
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        
        readerPath = "configs/readerConfiguration_reducedEventMC.json"
        writerPath = "configs/writerConfiguration_dileptonMC.json"
        
        analysisSelections = {
            "eventSelection": "Run event selection on DQ skimmed events",
            "muonSelection": "Run muon selection on DQ skimmed muons",
            "trackSelection": "Run barrel track selection on DQ skimmed tracks",
            "sameEventPairing": "Run same event pairing selection on DQ skimmed data",
            "dileptonTrackDimuonMuonSelection": "Run dimuon-muon pairing, using skimmed data",
            "dileptonTrackDielectronKaonSelection": "Run dielectron-kaon pairing, using skimmed data",
            }
        analysisSelectionsList = []
        for k, v in analysisSelections.items():
            analysisSelectionsList.append(k)
        
        sameEventPairingProcessSelections = {
            "DecayToEE": "Run electron-electron pairing, with skimmed tracks",
            "DecayToEEVertexing": "Run barrel barrel pairing on DQ skimmed tracks including vertexing",
            "DecayToMuMu": "Run muon-muon pairing, with skimmed muons",
            "DecayToMuMuVertexing": "Run muon-muon pairing and vertexing, with skimmed muons",
            }
        sameEventPairingProcessSelectionsList = []
        for k, v in sameEventPairingProcessSelections.items():
            sameEventPairingProcessSelectionsList.append(k)
        
        booleanSelections = ["true", "false"]
        
        # Get DQ Analysis Selections from O2-DQ Framework Header Files
        allAnalysisCuts = self.dqLibGetter.allAnalysisCuts
        allMCSignals = self.dqLibGetter.allMCSignals
        
        # Interface
        
        # analysis task selections
        groupAnalysisSelections = self.parserDQEfficiency.add_argument_group(
            title = "Data processor options: analysis-event-selection, analysis-muon-selection, analysis-track-selection, analysis-dilepton-track"
            )
        groupAnalysisSelections.add_argument(
            "--analysis", help = "Skimmed process selections for MC Analysis", action = "store", nargs = "*", type = str,
            metavar = "ANALYSIS", choices = analysisSelectionsList,
            ).completer = ChoicesCompleterList(analysisSelectionsList)
        
        for key, value in analysisSelections.items():
            groupAnalysisSelections.add_argument(key, help = value, action = "none")
        
        # same event pairing process function selection
        groupProcessSEPSelections = self.parserDQEfficiency.add_argument_group(
            title = "Data processor options: analysis-same-event-pairing"
            )
        groupProcessSEPSelections.add_argument(
            "--cfgBarrelMCRecSignals", help = "Space separated list of MC signals (reconstructed)", nargs = "*", action = "store",
            type = str, metavar = "CFGBARRELMCRECSIGNALS", choices = allMCSignals,
            ).completer = ChoicesCompleterList(allMCSignals)
        groupProcessSEPSelections.add_argument(
            "--cfgBarrelMCGenSignals", help = "Space separated list of MC signals (generated)", nargs = "*", action = "store", type = str,
            metavar = "CFGBARRELMCGENSIGNALS", choices = allMCSignals,
            ).completer = ChoicesCompleterList(allMCSignals)
        groupProcessSEPSelections.add_argument(
            "--cfgFlatTables", help = "Produce a single flat tables with all relevant information of the pairs and single tracks",
            action = "store", type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        groupProcessSEPSelections.add_argument(
            "--process", help = "analysis-same-event-pairing: PROCESS_SWITCH options", action = "store", nargs = "*", type = str,
            metavar = "PROCESS", choices = sameEventPairingProcessSelectionsList,
            ).completer = ChoicesCompleterList(sameEventPairingProcessSelectionsList)
        groupProcess = self.parserDQEfficiency.add_argument_group(
            title = "Choice List for analysis-same-event-pairing PROCESS_SWITCH options"
            )
        
        for key, value in sameEventPairingProcessSelections.items():
            groupProcess.add_argument(key, help = value, action = "none")
        
        # cfg for QA
        groupQASelections = self.parserDQEfficiency.add_argument_group(
            title = "Data processor options: analysis-event-selection, analysis-muon-selection, analysis-track-selection, analysis-event-mixing, analysis-dilepton-hadron"
            )
        groupQASelections.add_argument(
            "--cfgQA", help = "If true, fill QA histograms", action = "store", type = str.lower, choices = (booleanSelections),
            ).completer = ChoicesCompleter(booleanSelections)
        
        # analysis-event-selection
        groupAnalysisEventSelection = self.parserDQEfficiency.add_argument_group(title = "Data processor options: analysis-event-selection")
        groupAnalysisEventSelection.add_argument(
            "--cfgEventCuts", help = "Space separated list of event cuts", nargs = "*", action = "store", type = str,
            metavar = "CFGEVENTCUTS", choices = allAnalysisCuts,
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        
        # analysis-track-selection
        groupAnalysisTrackSelection = self.parserDQEfficiency.add_argument_group(title = "Data processor options: analysis-track-selection")
        groupAnalysisTrackSelection.add_argument(
            "--cfgTrackCuts", help = "Space separated list of barrel track cuts", nargs = "*", action = "store", type = str,
            metavar = "CFGTRACKCUTS", choices = allAnalysisCuts,
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        groupAnalysisTrackSelection.add_argument(
            "--cfgTrackMCSignals", help = "Space separated list of MC signals", nargs = "*", action = "store", type = str,
            metavar = "CFGTRACKMCSIGNALS", choices = allMCSignals,
            ).completer = ChoicesCompleterList(allMCSignals)
        
        # analysis-muon-selection
        groupAnalysisMuonSelection = self.parserDQEfficiency.add_argument_group(title = "Data processor options: analysis-muon-selection")
        groupAnalysisMuonSelection.add_argument(
            "--cfgMuonCuts", help = "Space separated list of muon cuts", nargs = "*", action = "store", type = str, metavar = "CFGMUONCUTS",
            choices = allAnalysisCuts,
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        groupAnalysisMuonSelection.add_argument(
            "--cfgMuonMCSignals", help = "Space separated list of MC signals", nargs = "*", action = "store", type = str,
            metavar = "CFGMUONMCSIGNALS", choices = allMCSignals,
            ).completer = ChoicesCompleterList(allMCSignals)
        
        # analysis-dilepton-track
        groupAnalysisDileptonTrack = self.parserDQEfficiency.add_argument_group(title = "Data processor options: analysis-dilepton-track")
        groupAnalysisDileptonTrack.add_argument(
            "--cfgLeptonCuts", help = "Space separated list of barrel track cuts", nargs = "*", action = "store", type = str,
            metavar = "CFGLEPTONCUTS", choices = allAnalysisCuts,
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        groupAnalysisDileptonTrack.add_argument(
            "--cfgFillCandidateTable", help = "Produce a single flat tables with all relevant information dilepton-track candidates",
            action = "store", type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        groupAnalysisDileptonTrack.add_argument(
            "--cfgBarrelDileptonMCRecSignals", help = "Space separated list of MC signals (reconstructed)", nargs = "*", action = "store",
            type = str, metavar = "CFGBARRELDILEPTONMCRECSIGNALS", choices = allMCSignals,
            ).completer = ChoicesCompleterList(allMCSignals)
        groupAnalysisDileptonTrack.add_argument(
            "--cfgBarrelDileptonMCGenSignals", help = "Space separated list of MC signals (generated)", nargs = "*", action = "store",
            type = str, metavar = "CFGBARRELDILEPTONMCRECSIGNALS", choices = allMCSignals,
            ).completer = ChoicesCompleterList(allMCSignals)
        
        # Aod Writer - Reader configs
        groupDPLReader = self.parserDQEfficiency.add_argument_group(
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
        
        argcomplete.autocomplete(self.parserDQEfficiency, always_complete_options = False)
        return self.parserDQEfficiency.parse_args()
    
    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """
        
        self.helperOptions.parserHelperOptions = self.parserDQEfficiency
        self.helperOptions.addArguments()
        
        self.dplAodReader.parserDplAodReader = self.parserDQEfficiency
        self.dplAodReader.addArguments()
        
        self.addArguments()
