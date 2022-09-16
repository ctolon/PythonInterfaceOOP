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

from argcomplete.completers import ChoicesCompleter
from extramodules.choicesCompleterList import ChoicesCompleterList


class AnalysisQvector(object):
    
    """
    Class for Interface -> dqFlow.cxx Task -> Configurable, Process Functions

    Args:
        object (parser_args() object): dqFlow.cxx Interface
    """
    
    def __init__(self, parserAnalysisQvector = argparse.ArgumentParser(add_help = False)):
        super(AnalysisQvector, self).__init__()
        self.parserAnalysisQvector = parserAnalysisQvector
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        booleanSelections = ["true", "false"]
        allAnalysisCuts = [] # all analysis cuts
        
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
            # request = urllib.request.urlopen(URL_CUTS_LIBRARY, context=context)
            
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
        with open("tempCutsLibrary.h") as f:
            for line in f:
                stringIfSearch = [x for x in f if "if" in x]
                for i in stringIfSearch:
                    getAnalysisCuts = re.findall('"([^"]*)"', i)
                    allAnalysisCuts = allAnalysisCuts + getAnalysisCuts
        
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
        
        return self.parserAnalysisQvector.parse_args()
