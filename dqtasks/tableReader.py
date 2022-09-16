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
import os
import re
from urllib.request import Request, urlopen
import ssl

from argcomplete.completers import ChoicesCompleter
from extramodules.choicesCompleterList import ChoicesCompleterList


class TableReader(object):
    
    """
    Class for Interface -> tableReader.cxx Task -> Configurable, Process Functions

    Args:
        object (parser_args() object): tableReader.cxx Interface
    """
    
    def __init__(self, parserTableReader = argparse.ArgumentParser(add_help = False)):
        super(TableReader, self).__init__()
        self.parserTableReader = parserTableReader
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        analysisSelections = {
            "eventSelection": "Run event selection on DQ skimmed events",
            "muonSelection": "Run muon selection on DQ skimmed muons",
            "trackSelection": "Run barrel track selection on DQ skimmed tracks",
            "eventMixing": "Run mixing on skimmed tracks based muon and track selections",
            "eventMixingVn": "Run vn mixing on skimmed tracks based muon and track selections",
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
        
        allAnalysisCuts = []
        allMixing = []
        
        ################################
        # Download DQ Libs From Github #
        ################################
        
        # It works on for only master branch
        
        # header for github download
        headers = {
            "User-Agent":
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
            }
        
        URL_CUTS_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/CutsLibrary.h?raw=true"
        URL_MCSIGNALS_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/MCSignalLibrary.h?raw=true"
        URL_MIXING_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/MixingLibrary.h?raw=true"
        
        # Github Links for CutsLibrary and MCSignalsLibrary from PWG-DQ --> download from github
        # This condition solves performance issues
        if not (os.path.isfile("tempCutsLibrary.h") or os.path.isfile("tempMCSignalsLibrary.h") or os.path.isfile("tempMixingLibrary.h")):
            print("[INFO] Some Libs are Missing. They will download.")
            
            # Dummy SSL Adder
            context = ssl._create_unverified_context() # prevent ssl problems
            
            # HTTP Request
            requestCutsLibrary = Request(URL_CUTS_LIBRARY, headers = headers)
            requestMCSignalsLibrary = Request(URL_MCSIGNALS_LIBRARY, headers = headers)
            requestMixingLibrary = Request(URL_MIXING_LIBRARY, headers = headers)
            
            # Get Files With Http Requests
            htmlCutsLibrary = urlopen(requestCutsLibrary, context = context).read()
            htmlMCSignalsLibrary = urlopen(requestMCSignalsLibrary, context = context).read()
            htmlMixingLibrary = urlopen(requestMixingLibrary, context = context).read()
            
            # Save Disk to temp DQ libs
            with open("tempCutsLibrary.h", "wb") as f:
                f.write(htmlCutsLibrary)
            with open("tempMCSignalsLibrary.h", "wb") as f:
                f.write(htmlMCSignalsLibrary)
            with open("tempMixingLibrary.h", "wb") as f:
                f.write(htmlMixingLibrary)
        
        # Read Cuts, Signals, Mixing vars from downloaded files
        with open("tempMixingLibrary.h") as f:
            for line in f:
                stringIfSearch = [x for x in f if "if" in x]
                for i in stringIfSearch:
                    getMixing = re.findall('"([^"]*)"', i)
                    allMixing = allMixing + getMixing
        
        with open("tempCutsLibrary.h") as f:
            for line in f:
                stringIfSearch = [x for x in f if "if" in x]
                for i in stringIfSearch:
                    getAnalysisCuts = re.findall('"([^"]*)"', i)
                    allAnalysisCuts = allAnalysisCuts + getAnalysisCuts
        
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
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserTableReader.parse_args()
