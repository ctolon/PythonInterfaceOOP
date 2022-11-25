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


# TODO It should check first local path then it should try download
class DQLibGetter(object):
    
    """
    Class for Downloading DQ Libraries Github and It gets analysis selections 
    like analysis cuts, MC signals and event mixing variables

    Args:
        object (object): self
    """
    
    def __init__(self, allAnalysisCuts = [], allMCSignals = [], allSels = [], allMixing = [], allEventHistos = [], allTrackHistos = [], allMCTruthHistos = [], allPairHistos = [], allDileptonHistos = []) -> None:
        
        # Define Analysis Cuts, MC Signals and Histograms
        self.allAnalysisCuts = list(allAnalysisCuts)
        self.allMCSignals = list(allMCSignals)
        self.allSels = list(allSels)
        self.allMixing = list(allMixing)
        self.allEventHistos = list(allEventHistos)
        self.allTrackHistos = list(allTrackHistos)
        self.allMCTruthHistos = list(allMCTruthHistos)
        self.allPairHistos = list(allPairHistos)
        self.allDileptonHistos = list(allDileptonHistos)

        # For filter selections
        allPairCuts = [] # only pair cuts
        nAddedallAnalysisCutsList = [] # e.g. muonQualityCuts:2
        nAddedPairCutsList = [] # e.g paircutMass:3
        selsWithOneColon = [] # track/muon cut:paircut:n
        oneColon = ":" # Namespace reference
        doubleColon = "::" # Namespace reference
        
        # Flags for DQ Lib Getter
        kEvents = True
        kTracks = True
        kMCtruths = True
        kPairs = True
        kDileptons = True
        
        # Lists for saving Histograms
        eventHistos = []
        trackHistos = []
        mctruthHistos = []
        pairHistos = []
        dileptonHistos = []
        
        headers = {
            "User-Agent":
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
            }
        
        URL_CUTS_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/CutsLibrary.h?raw=true"
        URL_MCSIGNALS_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/MCSignalLibrary.h?raw=true"
        URL_MIXING_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/MixingLibrary.h?raw=true"
        URL_HISTOGRAMS_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/HistogramsLibrary.h?raw=true"
        
        # Github Links for CutsLibrary and MCSignalsLibrary from PWG-DQ --> download from github
        # This condition solves performance issues
        if (os.path.isfile("tempCutsLibrary.h") and os.path.isfile("tempMCSignalsLibrary.h") and os.path.isfile("tempMixingLibrary.h") and os.path.isfile("tempHistogramsLibrary.h")) is False:
            print("[INFO] Some Libs are Missing. They will download.")
            
            # Dummy SSL Adder
            context = ssl._create_unverified_context() # prevent ssl problems
            # request = urllib.request.urlopen(URL_CUTS_LIBRARY, context=context)
            
            # HTTP Request
            requestCutsLibrary = Request(URL_CUTS_LIBRARY, headers = headers)
            requestMCSignalsLibrary = Request(URL_MCSIGNALS_LIBRARY, headers = headers)
            requestMixingLibrary = Request(URL_MIXING_LIBRARY, headers = headers)
            requestHistogramsLibrary = Request(URL_HISTOGRAMS_LIBRARY, headers = headers)
            
            # Get Files With Http Requests
            htmlCutsLibrary = urlopen(requestCutsLibrary, context = context).read()
            htmlMCSignalsLibrary = urlopen(requestMCSignalsLibrary, context = context).read()
            htmlMixingLibrary = urlopen(requestMixingLibrary, context = context).read()
            htmlHistogramsLibrary = urlopen(requestHistogramsLibrary, context = context).read()
            
            # Save Disk to temp DQ libs
            with open("tempCutsLibrary.h", "wb") as f:
                f.write(htmlCutsLibrary)
            f.close()
            with open("tempMCSignalsLibrary.h", "wb") as f:
                f.write(htmlMCSignalsLibrary)
            f.close()
            with open("tempMixingLibrary.h", "wb") as f:
                f.write(htmlMixingLibrary)
            f.close()
            with open("tempHistogramsLibrary.h", "wb") as f:
                f.write(htmlHistogramsLibrary)
            f.close()
            print("[INFO] Libs downloaded succesfully.")
        # Read Cuts, Signals, Mixing vars from downloaded files
        with open("tempMCSignalsLibrary.h") as f:
            stringIfSearch = [x for x in f if "if" in x]
            for i in stringIfSearch:
                getSignals = re.findall('"([^"]*)"', i)
                self.allMCSignals = self.allMCSignals + getSignals
        f.close() 
        
        with open("tempMixingLibrary.h") as f:
            stringIfSearch = [x for x in f if "if" in x]
            for i in stringIfSearch:
                getMixing = re.findall('"([^"]*)"', i)
                self.allMixing = self.allMixing + getMixing
        f.close() 
             
        # TODO create dep tree and improve better performance        
        with open("tempHistogramsLibrary.h") as f:
            for line in f:
                if "if" in line:
                    #print(line, len(line) - len(line.lstrip()))
                    if "track" not in line and kEvents is True: # get event histos
                        line = re.findall('"([^"]*)"', line)
                        eventHistos += line
                    elif "mctruth" not in line and kTracks is True: # get track histos
                        line = re.findall('"([^"]*)"', line)
                        kEvents = False
                        trackHistos += line
                    elif "pair" not in line and kMCtruths is True: # get mctruth histos # TODO test it
                        line = re.findall('"([^"]*)"', line)
                        kTracks = False
                        mctruthHistos += line
                    elif "dilepton" not in line and kPairs is True:  # get sep histos
                        line = re.findall('"([^"]*)"', line)
                        kMCtruths = False
                        pairHistos += line
                    else: # get dilepton histos
                        line = re.findall('"([^"]*)"', line)
                        kPairs = False
                        dileptonHistos += line
        f.close()       
        self.allEventHistos = eventHistos
        self.allTrackHistos = self.allTrackHistos + trackHistos
        self.allMCTruthHistos = self.allMCTruthHistos + mctruthHistos
        self.allPairHistos = self.allPairHistos + pairHistos
        self.allDileptonHistos = self.allDileptonHistos + dileptonHistos
        with open("tempCutsLibrary.h") as f:
            stringIfSearch = [x for x in f if "if" in x] # get lines only includes if string
            for i in stringIfSearch:
                getCuts = re.findall('"([^"]*)"', i) # get in double quotes string value with regex exp.
                getPairCuts = [y for y in getCuts if "pair" in y] # get pair cuts
                if getPairCuts: # if pair cut list is not empty
                    allPairCuts = (allPairCuts + getPairCuts) # Get Only pair cuts from CutsLibrary.h
                    namespacedPairCuts = [x + oneColon for x in allPairCuts] # paircut:
                self.allAnalysisCuts = (self.allAnalysisCuts + getCuts) # Get all Cuts from CutsLibrary.h
                nameSpacedallAnalysisCuts = [x + oneColon for x in self.allAnalysisCuts] # cut:
                nameSpacedallAnalysisCutsTwoDots = [x + doubleColon for x in self.allAnalysisCuts] # cut::
        
        # in Filter PP Task, sels options for barrel and muon uses namespaces e.g. "<track-cut>:[<pair-cut>]:<n> and <track-cut>::<n> For Manage this issue:
        for k in range(1, 10):
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
        f.close() 
        self.allSels = selsWithOneColon + nAddedallAnalysisCutsList
