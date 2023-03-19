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

import os
import re
from urllib.request import Request, urlopen
import ssl
import pathlib

from .utils import getIfStartedInDoubleQuotes, writeFile


class DQLibGetter(object):
    
    """
    Class for Downloading DQ Libraries Github and It gets analysis selections
    like analysis cuts, MC signals and event mixing variables
    Args:
        object (object): self
    """
    
    def __init__(self, allAnalysisCuts = [], allOnlyPairCuts = [], allMCSignals = [], allSels = [], allMixing = [], allLHCPeriods = [], allHistos = [], allEventHistos = [], allTrackHistos = [], allMCTruthHistos = [], allPairHistos = [], allDileptonHistos = []) -> None:
        
        # Define Analysis Cuts, MC Signals and Histograms
        self.allAnalysisCuts = list(allAnalysisCuts)
        self.allOnlyPairCuts = list(allOnlyPairCuts)
        self.allMCSignals = list(allMCSignals)
        self.allSels = list(allSels)
        self.allMixing = list(allMixing)
        self.allLHCPeriods = list(allLHCPeriods)
        self.allHistos = list(allHistos)
        self.allEventHistos = list(allEventHistos)
        self.allTrackHistos = list(allTrackHistos)
        self.allMCTruthHistos = list(allMCTruthHistos)
        self.allPairHistos = list(allPairHistos)
        self.allDileptonHistos = list(allDileptonHistos)
        
        # For filter selections
        allPairCuts = [] # only pair cuts
        selsWithDoubleColon = [] # e.g. muonQualityCuts::2
        pairCutsWithSingleColon = [] # e.g paircutMass:3
        selsWithSingleColon = [] # track/muon cut:paircut:n
        singleColon = ":" # Namespace reference
        doubleColon = "::" # Namespace reference
        
        # Flags for DQ Lib Getter
        kEvents = True
        kTracks = True
        kMCtruths = True
        kPairs = True
        # kDileptons = True
        
        # Lists for saving Histograms
        eventHistos = []
        trackHistos = []
        mctruthHistos = []
        pairHistos = []
        dileptonHistos = []
        allHistograms = []
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
            }
        
        URL_CUTS_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/CutsLibrary.cxx?raw=true"
        URL_MCSIGNALS_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/MCSignalLibrary.cxx?raw=true"
        URL_MIXING_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/MixingLibrary.cxx?raw=true"
        URL_HISTOGRAMS_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/HistogramsLibrary.cxx?raw=true"
        URL_VAR_MANAGER = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/VarManager.cxx?raw=true"
        
        # Create templibs directory if not exist
        if not os.path.isdir("templibs"):
            path = pathlib.Path(__file__).parent.parent.resolve()
            pathWithFile = os.path.join(path, "templibs")
            try:
                os.mkdir(pathWithFile)
            except OSError as error:
                raise OSError(error)
        
        # Github Links for CutsLibrary and MCSignalsLibrary from PWG-DQ --> download from github
        # This condition solves performance issues
        if (os.path.isfile("templibs/tempCutsLibrary.cxx") and os.path.isfile("templibs/tempMCSignalsLibrary.cxx") and os.path.isfile("templibs/tempMixingLibrary.cxx") and os.path.isfile("templibs/tempHistogramsLibrary.cxx") and os.path.isfile("templibs/tempVarManager.cxx")) is False:
            print("[INFO] Some Libs are Missing. They will download.")
            
            # Dummy SSL Adder
            context = ssl._create_unverified_context() # prevent ssl problems
            # request = urllib.request.urlopen(URL_CUTS_LIBRARY, context=context)
            
            # HTTP Request
            requestCutsLibrary = Request(URL_CUTS_LIBRARY, headers = headers)
            requestMCSignalsLibrary = Request(URL_MCSIGNALS_LIBRARY, headers = headers)
            requestMixingLibrary = Request(URL_MIXING_LIBRARY, headers = headers)
            requestHistogramsLibrary = Request(URL_HISTOGRAMS_LIBRARY, headers = headers)
            requestVarManager = Request(URL_VAR_MANAGER, headers = headers)
            
            # Get Files With Http Requests
            htmlCutsLibrary = urlopen(requestCutsLibrary, context = context).read()
            htmlMCSignalsLibrary = urlopen(requestMCSignalsLibrary, context = context).read()
            htmlMixingLibrary = urlopen(requestMixingLibrary, context = context).read()
            htmlHistogramsLibrary = urlopen(requestHistogramsLibrary, context = context).read()
            htmlVarManager= urlopen(requestVarManager, context = context).read()
            
            # Save Disk to temp DQ libs
            writeFile("templibs/tempCutsLibrary.cxx", htmlCutsLibrary)
            writeFile("templibs/tempMCSignalsLibrary.cxx", htmlMCSignalsLibrary)
            writeFile("templibs/tempMixingLibrary.cxx", htmlMixingLibrary)
            writeFile("templibs/tempHistogramsLibrary.cxx", htmlHistogramsLibrary)
            writeFile("templibs/tempVarManager.cxx", htmlVarManager)
            print("[INFO] Libs downloaded succesfully.")
        
        # Get MC Signals and Mixing vars from DQ Framework header files
        self.allMCSignals = getIfStartedInDoubleQuotes("templibs/tempMCSignalsLibrary.cxx")
        self.allMixing = getIfStartedInDoubleQuotes("templibs/tempMixingLibrary.cxx")
        
        # Get LHC Periods from DQ Framework VarManager cxx file
        with open("templibs/tempVarManager.cxx") as f:
            stringIfSearch = [x for x in f if "if" and "period.Contains" in x]
            for i in stringIfSearch:
                self.allLHCPeriods.extend(re.findall('"([^"]*)"', i))
            
        # Get All histograms with flags
        with open("templibs/tempHistogramsLibrary.cxx") as f:
            for line in f:
                if "if" in line:
                    if "track" not in line and kEvents is True: # get event histos
                        line = re.findall('"([^"]*)"', line)
                        eventHistos += line
                        allHistograms += line
                    elif "mctruth" not in line and kTracks is True: # get track histos
                        line = re.findall('"([^"]*)"', line)
                        kEvents = False
                        trackHistos += line
                        allHistograms += line
                    elif "mctruth" in line and kMCtruths is True: # get mctruth histos
                        line = re.findall('"([^"]*)"', line)
                        kTracks = False
                        mctruthHistos += line
                        allHistograms += line
                    elif "dilepton" not in line and kPairs is True: # get sep histos
                        line = re.findall('"([^"]*)"', line)
                        kMCtruths = False
                        pairHistos += line
                        allHistograms += line
                    else: # get dilepton histos
                        line = re.findall('"([^"]*)"', line)
                        kPairs = False
                        dileptonHistos += line
                        allHistograms += line
        f.close()
        
        # Save histograms to class arguments
        self.allHistos = allHistograms
        self.allEventHistos += eventHistos
        self.allTrackHistos += trackHistos
        self.allMCTruthHistos += mctruthHistos
        self.allPairHistos += pairHistos
        self.allDileptonHistos += dileptonHistos
        
        self.allAnalysisCuts = getIfStartedInDoubleQuotes("templibs/tempCutsLibrary.cxx")
        getPairCuts = [y for y in self.allAnalysisCuts if "pair" in y]
        if getPairCuts: # if pair cut list is not empty
            allPairCuts += getPairCuts # Get Only pair cuts from CutsLibrary.cxx
            namespacedPairCuts = [x + singleColon for x in allPairCuts] # paircut:
            self.allOnlyPairCuts += allPairCuts # Get all Pair Cuts from CutsLibrary.cxx
        
        # NOTE : Now we have brute-force solution for format specifiers (for dalitz cuts)
        # TODO We need more simple and flexible solution for this isue
        getCleanDalitzCuts = []
        getDalitzCutsWithFormatSpecifiers = [x for x in self.allAnalysisCuts if "%d" in x]
        getDalitzCutsWithFormatSpecifiers = list(map(lambda x: x.replace('%d', ''), getDalitzCutsWithFormatSpecifiers)) # delete format specifiers with list comp.
        #print(getDalitzCutsWithFormatSpecifiers)
        
        # add one to eight suffix due to for loop in O2-DQ Framework
        for i in getDalitzCutsWithFormatSpecifiers:
            for j in range(1, 9):
                i = i + str(j) # add suffix integers
                getCleanDalitzCuts.append(i)
                i = i[:-1] # remove last character after suffix
        
        # after getting clean dalitz cuts, we need remove has format specifier dalitz cuts from allAnalysisCuts and add clean dalitz cuts
        self.allAnalysisCuts = [x for x in self.allAnalysisCuts if "%d" not in x] # clean the has format specifier dalitz cuts
        self.allAnalysisCuts += getCleanDalitzCuts # add clean dalitz cuts
        
        # in Filter PP Task, sels options for barrel and muon uses colons e.g. "<track-cut>:[<pair-cut>]:<n> and <track-cut>::<n> For Manage this issue:
        allAnalysisCutsSingleColon = [x + singleColon for x in self.allAnalysisCuts] # cut:
        allAnalysisCutsDoubleColon = [x + doubleColon for x in self.allAnalysisCuts] # cut::
        
        for k in range(1, 10):
            # Style 1 <track-cut>::<n> --> selsWithDoubleColon
            dubletStyle = [x + str(k) for x in allAnalysisCutsDoubleColon] # cut::n
            selsWithDoubleColon += dubletStyle
            nAddedPairCuts = [x + str(k) for x in namespacedPairCuts]
            pairCutsWithSingleColon += nAddedPairCuts
        
        # Style 2 <track-cut>:[<pair-cut>]:<n> --> selsWithSingleColon:
        for i in pairCutsWithSingleColon:
            tripletStyle = [x + i for x in allAnalysisCutsSingleColon]
            selsWithSingleColon += tripletStyle
        
        # Merge All possible styles for Sels (cfgBarrelSels and cfgMuonSels) in FilterPP Task
        f.close()
        self.allSels = selsWithSingleColon + selsWithDoubleColon
