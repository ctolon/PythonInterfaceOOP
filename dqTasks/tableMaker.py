#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*- 
#############################################################################
##  © Copyright CERN 2018. All rights not expressly granted are reserved.  ##
##                   Author: ionut.cristian.arsene@cern.ch                 ##
##               Interface:  cevat.batuhan.tolon@cern.ch                   ## 
## This program is free software: you can redistribute it and/or modify it ##
##  under the terms of the GNU General Public License as published by the  ##
## Free Software Foundation, either version 3 of the License, or (at your  ##
## option) any later version. This program is distributed in the hope that ##
##  it will be useful, but WITHOUT ANY WARRANTY; without even the implied  ##
##     warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    ##
##           See the GNU General Public License for more details.          ##
##    You should have received a copy of the GNU General Public License    ##
##   along with this program. if not, see <https://www.gnu.org/licenses/>. ##
#############################################################################

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMaker.cxx

import argparse
import os
import re
import urllib.request
from urllib.request import Request, urlopen
import ssl

from argcomplete.completers import ChoicesCompleter
from extraModules.choicesCompleterList import ChoicesCompleterList

# Special configurations for filterPP are combined to avoid conflicts in the tableMaker interface

class TableMaker(object):
    """
    Class for Interface -> tableMaker.cxx Task -> Configurable, Process Functions. 
    Also this class includes some filterPP and dqFlow task arguments to avoid conflicts
    
    Args:
        object (parser_args() object): tableMaker.cxx Interface
    """
    
    def __init__(self, parserTableMaker=argparse.ArgumentParser(add_help=False)):
        super(TableMaker, self).__init__()
        self.parserTableMaker = parserTableMaker

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
            "OnlyBCs": "Analyze the BCs to store sampled lumi"
        }
        tableMakerProcessSelectionsList = []
        for k, v in tableMakerProcessSelections.items():
            tableMakerProcessSelectionsList.append(k)
        
        allAnalysisCuts = []  # all analysis cuts
        allPairCuts = []  # only pair cuts
        nAddedallAnalysisCutsList = []  # e.g. muonQualityCuts:2
        nAddedPairCutsList = []  # e.g paircutMass:3
        selsWithOneColon = []  # track/muon cut:paircut:n
        allSels = []  # track/muon cut::n
        oneColon = ":"  # Namespace reference
        doubleColon = "::"  # Namespace reference

        ################################
        # Download DQ Libs From Github #
        ################################

        # It works on for only master branch

        # header for github download
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
        }

        URL_CUTS_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/CutsLibrary.h?raw=true"
        URL_MCSIGNALS_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/MCSignalLibrary.h?raw=true"
        URL_MIXING_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/MixingLibrary.h?raw=true"

        
        # Github Links for CutsLibrary and MCSignalsLibrary from PWG-DQ --> download from github
        # This condition solves performance issues    
        if not (os.path.isfile("tempCutsLibrary.h") or os.path.isfile("tempMCSignalsLibrary.h") or os.path.isfile("tempMixingLibrary.h")):
            print("[INFO] Some Libs are Missing. They will download.")
            
            # Dummy SSL Adder
            context = ssl._create_unverified_context()  # prevent ssl problems
            request = urllib.request.urlopen(URL_CUTS_LIBRARY, context=context)
            
            # HTTP Request
            requestCutsLibrary = Request(URL_CUTS_LIBRARY, headers=headers)
            requestMCSignalsLibrary = Request(URL_MCSIGNALS_LIBRARY, headers=headers)
            requestMixingLibrary  = Request(URL_MIXING_LIBRARY , headers=headers)
            
            # Get Files With Http Requests
            htmlCutsLibrary = urlopen(requestCutsLibrary, context=context).read()
            htmlMCSignalsLibrary = urlopen(requestMCSignalsLibrary, context=context).read()
            htmlMixingLibrary = urlopen(requestMixingLibrary, context=context).read()
            
            # Save Disk to temp DQ libs  
            with open("tempCutsLibrary.h", "wb") as f:
                f.write(htmlCutsLibrary)
            with open("tempMCSignalsLibrary.h", "wb") as f:
                f.write(htmlMCSignalsLibrary)
            with open("tempMixingLibrary.h", "wb") as f:
                f.write(htmlMixingLibrary)

        # Read Cuts, Signals, Mixing vars from downloaded files                    
        with open("tempCutsLibrary.h") as f:
            for line in f:
                stringIfSearch = [x for x in f if 'if' in x]  # get lines only includes if string
                for i in stringIfSearch:
                    getAnalysisCuts = re.findall('"([^"]*)"', i)  # get in double quotes string value with regex exp.
                    getPairCuts = [y for y in getAnalysisCuts         # get pair cuts
                                if "pair" in y] 
                    if getPairCuts: # if pair cut list is not empty
                        allPairCuts = allPairCuts + getPairCuts # Get Only pair cuts from CutsLibrary.h
                        namespacedPairCuts = [x + oneColon for x in allPairCuts] # paircut:
                    allAnalysisCuts = allAnalysisCuts + getAnalysisCuts # Get all Cuts from CutsLibrary.h
                    nameSpacedallAnalysisCuts = [x + oneColon for x in allAnalysisCuts] # cut:
                    nameSpacedallAnalysisCutsTwoDots = [x + doubleColon for x in allAnalysisCuts]  # cut::

        # in Filter PP Task, sels options for barrel and muon uses namespaces e.g. "<track-cut>:[<pair-cut>]:<n> and <track-cut>::<n> For Manage this issue:
        for k in range (1,10):
            nAddedallAnalysisCuts = [x + str(k) for x in nameSpacedallAnalysisCutsTwoDots]
            nAddedallAnalysisCutsList = nAddedallAnalysisCutsList + nAddedallAnalysisCuts
            nAddedPairCuts = [x + str(k) for x in namespacedPairCuts]
            nAddedPairCutsList = nAddedPairCutsList + nAddedPairCuts
            
        # Style 1 <track-cut>:[<pair-cut>]:<n>:
        for i in nAddedPairCutsList:
            Style1 = [x + i for x in nameSpacedallAnalysisCuts]
            selsWithOneColon = selsWithOneColon + Style1
            
        # Style 2 <track-cut>:<n> --> nAddedallAnalysisCutsList

        # Merge All possible styles for Sels (cfgBarrelSels and cfgMuonSels) in FilterPP Task
        allSels = selsWithOneColon + nAddedallAnalysisCutsList
        booleanSelections = ["true", "false"]
    
        # Interface
        
        # table-maker configurables
        groupTableMakerConfigs = self.parserTableMaker.add_argument_group(title="Data processor options: table-maker-m-c")
        groupTableMakerConfigs.add_argument("--cfgEventCuts", help="Space separated list of event cuts", nargs="*", action="store", type=str, metavar="CFGEVENTCUTS", choices=allAnalysisCuts).completer = ChoicesCompleterList(allAnalysisCuts)
        groupTableMakerConfigs.add_argument("--cfgBarrelTrackCuts", help=" Space separated list of barrel track cuts", nargs="*", action="store", type=str, metavar="CFGBARRELTRACKCUTS", choices=allAnalysisCuts).completer = ChoicesCompleterList(allAnalysisCuts)
        groupTableMakerConfigs.add_argument("--cfgMuonCuts", help="Space separated list of muon cuts in table-maker", action="store", nargs="*", type=str, metavar="CFGMUONCUTS", choices=allAnalysisCuts).completer = ChoicesCompleterList(allAnalysisCuts)
        groupTableMakerConfigs.add_argument("--cfgBarrelLowPt", help="Low pt cut for tracks in the barrel", action="store", type=str)
        groupTableMakerConfigs.add_argument("--cfgMuonLowPt", help="Low pt cut for muons", action="store", type=str)
        groupTableMakerConfigs.add_argument("--cfgNoQA", help="If true, no QA histograms", action="store", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)
        groupTableMakerConfigs.add_argument("--cfgDetailedQA", help="If true, include more QA histograms (BeforeCuts classes and more)", action="store", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)
        #groupTableMakerConfigs.add_argument("--cfgIsRun2", help="Run selection true or false", action="store", choices=["true","false"], type=str) # no need
        groupTableMakerConfigs.add_argument("--cfgMinTpcSignal", help="Minimum TPC signal", action="store", type=str)
        groupTableMakerConfigs.add_argument("--cfgMaxTpcSignal", help="Maximum TPC signal", action="store", type=str)

        groupProcessTableMaker = self.parserTableMaker.add_argument_group(title="Data processor options: table-maker-m-c")
        groupProcessTableMaker.add_argument("--process",help="Process Selection options for tableMaker/tableMakerMC Data Processing and Skimming", action="store", type=str, nargs="*", metavar="PROCESS", choices=tableMakerProcessSelectionsList).completer = ChoicesCompleterList(tableMakerProcessSelectionsList)
        for key,value in tableMakerProcessSelections.items():
            groupProcessTableMaker.add_argument(key, help=value, action="none")
            
        # d-q-track barrel-task
        groupDQTrackBarrelTask = self.parserTableMaker.add_argument_group(title="Data processor options: d-q-track barrel-task")
        groupDQTrackBarrelTask.add_argument("--isBarrelSelectionTiny", help="Run barrel track selection instead of normal(process func. for barrel selection must be true)", action="store", default="false", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)

        # d-q muons-selection
        groupDQMuonsSelection = self.parserTableMaker.add_argument_group(title="Data processor options: d-q muons-selection")
        groupDQMuonsSelection.add_argument("--cfgMuonsCuts", help="Space separated list of ADDITIONAL muon track cuts", action="store", nargs="*", type=str, metavar="CFGMUONSCUT", choices=allAnalysisCuts).completer = ChoicesCompleterList(allAnalysisCuts)

        # d-q-filter-p-p-task
        groupDQFilterPP = self.parserTableMaker.add_argument_group(title="Data processor options: d-q-filter-p-p-task")
        groupDQFilterPP.add_argument("--cfgBarrelSels", help="Configure Barrel Selection <track-cut>:[<pair-cut>]:<n>,[<track-cut>:[<pair-cut>]:<n>],... | example jpsiO2MCdebugCuts2::1 ", action="store", type=str,nargs="*", metavar="CFGBARRELSELS", choices=allSels).completer = ChoicesCompleterList(allSels)
        groupDQFilterPP.add_argument("--cfgMuonSels", help="Configure Muon Selection <muon-cut>:[<pair-cut>]:<n> example muonQualityCuts:pairNoCut:1", action="store", type=str,nargs="*", metavar="CFGMUONSELS", choices=allSels).completer = ChoicesCompleterList(allSels)
        groupDQFilterPP.add_argument("--isFilterPPTiny", help="Run filter tiny task instead of normal (processFilterPP must be true) ", action="store", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)

        # analysis-qvector
        groupAnalysisQvector = self.parserTableMaker.add_argument_group(title="Data processor options: analysis-qvector")
        groupAnalysisQvector.add_argument("--cfgCutPtMin", help="Minimal pT for tracks", action="store", type=str, metavar="CFGCUTPTMIN")
        groupAnalysisQvector.add_argument("--cfgCutPtMax", help="Maximal pT for tracks", action="store", type=str, metavar="CFGCUTPTMAX")
        groupAnalysisQvector.add_argument("--cfgCutEta", help="Eta range for tracks", action="store", type=str, metavar="CFGCUTETA")
        groupAnalysisQvector.add_argument("--cfgEtaLimit", help="Eta gap separation, only if using subEvents", action="store", type=str, metavar="CFGETALIMIT")
        groupAnalysisQvector.add_argument("--cfgNPow", help="Power of weights for Q vector", action="store", type=str, metavar="CFGNPOW")
        groupAnalysisQvector.add_argument("--cfgEfficiency", help="CCDB path to efficiency object", action="store", type=str)
        groupAnalysisQvector.add_argument("--cfgAcceptance", help="CCDB path to acceptance object", action="store", type=str)
        
        #all d-q tasks and selections
        groupQASelections = self.parserTableMaker.add_argument_group(title="Data processor options: d-q-barrel-track-selection-task, d-q-muons-selection, d-q-event-selection-task, d-q-filter-p-p-task, analysis-qvector")
        groupQASelections.add_argument("--cfgWithQA", help="If true, fill QA histograms", action="store", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)
            
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserTableMaker.parse_args()
