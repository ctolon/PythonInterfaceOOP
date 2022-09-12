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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/filterPP.cxx

import argparse
import os
import re
import urllib.request
from urllib.request import Request, urlopen
import ssl

from argcomplete.completers import ChoicesCompleter
from extramodules.choicesCompleterList import ChoicesCompleterList

class DQFilterPPTask(object):
    """
    Class for Interface -> filterPP.cxx Task -> Configurable, Process Functions  

    Args:
        object (parser_args() object): filterPP.cxx Interface
    """
    
    def __init__(self, parserDQFilterPPTask=argparse.ArgumentParser(add_help=False)):
        super(DQFilterPPTask, self).__init__()
        self.parserDQFilterPPTask = parserDQFilterPPTask

    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        dqSelections = {
            "eventSelection": "Run DQ event selection",
            "barrelTrackSelection": "Run DQ barrel track selection",
            "muonSelection": "Run DQ muon selection",
            "barrelTrackSelectionTiny": "Run DQ barrel track selection tiny",
            "filterPPSelectionTiny": "Run filter task tiny"
        }
        dqSelectionsList = []
        for k, v in dqSelections.items():
            dqSelectionsList.append(k)

        booleanSelections = ["true", "false"]

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

        # Interface

        # DQ Task Selections
        groupProcessFilterPP= self.parserDQFilterPPTask.add_argument_group(title="Data processor options: d-q-filter-p-p-task, d-q-event-selection-task, d-q-barrel-track-selection, d-q-muons-selection ")
        groupProcessFilterPP.add_argument("--process",help="DQ Tasks process Selections options", action="store", type=str, nargs="*", metavar="PROCESS", choices=dqSelectionsList).completer = ChoicesCompleterList(dqSelectionsList)

        for key,value in dqSelections.items():
            groupProcessFilterPP.add_argument(key, help=value, action="none")

        # d-q-filter-p-p-task
        groupDQFilterPP = self.parserDQFilterPPTask.add_argument_group(title="Data processor options: d-q-filter-p-p-task")
        groupDQFilterPP.add_argument("--cfgBarrelSels", help="Configure Barrel Selection <track-cut>:[<pair-cut>]:<n>,[<track-cut>:[<pair-cut>]:<n>],... | example jpsiO2MCdebugCuts2::1 ", action="store", type=str,nargs="*", metavar="CFGBARRELSELS", choices=allSels).completer = ChoicesCompleterList(allSels)
        groupDQFilterPP.add_argument("--cfgMuonSels", help="Configure Muon Selection <muon-cut>:[<pair-cut>]:<n> example muonQualityCuts:pairNoCut:1", action="store", type=str,nargs="*", metavar="CFGMUONSELS", choices=allSels).completer = ChoicesCompleterList(allSels)

        ## d-q-event-selection-task
        groupDQEventSelection = self.parserDQFilterPPTask.add_argument_group(title="Data processor options: d-q-event-selection-task")
        groupDQEventSelection.add_argument("--cfgEventCuts", help="Space separated list of event cuts", nargs="*", action="store", type=str, metavar="CFGEVENTCUTS", choices=allAnalysisCuts).completer = ChoicesCompleterList(allAnalysisCuts)

        ## d-q-barrel-track-selection
        groupDQBarrelTrackSelection = self.parserDQFilterPPTask.add_argument_group(title="Data processor options: d-q-barrel-track-selection")
        groupDQBarrelTrackSelection.add_argument("--cfgBarrelTrackCuts", help="Space separated list of barrel track cuts", nargs="*", action="store", type=str, metavar="CFGBARRELTRACKCUTS", choices=allAnalysisCuts).completer = ChoicesCompleterList(allAnalysisCuts)

        ## d-q-muons-selection
        groupDQMuonsSelection = self.parserDQFilterPPTask.add_argument_group(title="Data processor options: d-q-muons-selection")
        groupDQMuonsSelection.add_argument("--cfgMuonsCuts", help="Space separated list of muon cuts in d-q muons selection", action="store", nargs="*", type=str, metavar="CFGMUONSCUT", choices=allAnalysisCuts).completer = ChoicesCompleterList(allAnalysisCuts)

        #all d-q tasks and selections
        groupQASelections = self.parserDQFilterPPTask.add_argument_group(title="Data processor options: d-q-barrel-track-selection-task, d-q-muons-selection, d-q-event-selection-task, d-q-filter-p-p-task")
        groupQASelections.add_argument("--cfgWithQA", help="If true, fill QA histograms", action="store", type=str.lower, choices=(booleanSelections)).completer = ChoicesCompleter(booleanSelections)
            
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserDQFilterPPTask.parse_args()