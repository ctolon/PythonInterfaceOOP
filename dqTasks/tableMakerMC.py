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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMakerMC.cxx

import argparse
import os
import re
import urllib.request
from urllib.request import Request, urlopen
import ssl

from argcomplete.completers import ChoicesCompleter
from ExtraModules.ChoicesCompleterList import ChoicesCompleterList
class TableMakerMC(object):
    """
    Class for Interface -> tableMakerMC.cxx Task -> Configurable, Process Functions  

    Args:
        object (parser_args() object): tableMakerMC.cxx Interface
    """
    
    def __init__(self, parserTableMakerMC=argparse.ArgumentParser(add_help=False)):
        super(TableMakerMC, self).__init__()
        self.parserTableMakerMC = parserTableMakerMC

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
        "OnlyBCs": "Analyze the BCs to store sampled lumi"
        }
        tableMakerProcessSelectionsList = []
        for k, v in tableMakerProcessSelections.items():
            tableMakerProcessSelectionsList.append(k)
            
        booleanSelections = ["true", "false"]
        
        allAnalysisCuts = []  # all analysis cuts
        allMCSignals = []  # all MC Signals

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
        with open("tempMCSignalsLibrary.h") as f:
            for line in f:
                stringIfSearch = [x for x in f if "if" in x] 
                for i in stringIfSearch:
                    getSignals = re.findall('"([^"]*)"', i)
                    allMCSignals = allMCSignals + getSignals
            
        with open("tempCutsLibrary.h") as f:
            for line in f:
                stringIfSearch = [x for x in f if "if" in x] 
                for i in stringIfSearch:
                    getAnalysisCuts = re.findall('"([^"]*)"', i)
                    allAnalysisCuts = allAnalysisCuts + getAnalysisCuts
                    
    
        # Interface
        groupTableMakerConfigs = self.parserTableMakerMC.add_argument_group(title="Data processor options: table-maker-m-c")
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
        groupTableMakerConfigs.add_argument("--cfgMCsignals", help="Space separated list of MC signals", action="store", nargs="*", type=str, metavar="CFGMCSIGNALS", choices=allMCSignals).completer = ChoicesCompleterList(allMCSignals)

        groupProcessTableMaker = self.parserTableMakerMC.add_argument_group(title="Data processor options: table-maker-m-c")
        groupProcessTableMaker.add_argument("--process",help="Process Selection options for tableMaker/tableMakerMC Data Processing and Skimming", action="store", type=str, nargs="*", metavar="PROCESS", choices=tableMakerProcessSelectionsList).completer = ChoicesCompleterList(tableMakerProcessSelectionsList)
        for key,value in tableMakerProcessSelections.items():
            groupProcessTableMaker.add_argument(key, help=value, action="none")
            
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserTableMakerMC.parse_args()
