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


class DQLibGetter(object):
    
    """
    Class for Downloading DQ Libraries Github and It gets analysis selections 
    like analysis cuts, MC signals and event mixing variables

    Args:
        object (object): self
    """
    
    def __init__(self):
        super(DQLibGetter, self).__init__()
    
    def getAnalysisSelections(self):
        """This function allows to get all analysis selections from DQ libraries

        Returns:
            allAnalysisCuts, allMCSignals, allSels, allMixing: All analysis selections with order
        """
        
        allAnalysisCuts = [] # all analysis cuts
        allPairCuts = [] # only pair cuts
        nAddedallAnalysisCutsList = [] # e.g. muonQualityCuts:2
        nAddedPairCutsList = [] # e.g paircutMass:3
        selsWithOneColon = [] # track/muon cut:paircut:n
        allSels = [] # track/muon cut::n
        oneColon = ":" # Namespace reference
        doubleColon = "::" # Namespace reference
        allMCSignals = [] # Get MC Signals
        allMixing = [] # Get Event Mixing vars
        
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
        with open("tempMCSignalsLibrary.h") as f:
            for line in f:
                stringIfSearch = [x for x in f if "if" in x]
                for i in stringIfSearch:
                    getSignals = re.findall('"([^"]*)"', i)
                    allMCSignals = allMCSignals + getSignals
        
        with open("tempMixingLibrary.h") as f:
            for line in f:
                stringIfSearch = [x for x in f if "if" in x]
                for i in stringIfSearch:
                    getMixing = re.findall('"([^"]*)"', i)
                    allMixing = allMixing + getMixing
        
        with open("tempCutsLibrary.h") as f:
            for line in f:
                stringIfSearch = [x for x in f if "if" in x] # get lines only includes if string
                for i in stringIfSearch:
                    getCuts = re.findall('"([^"]*)"', i) # get in double quotes string value with regex exp.
                    getPairCuts = [y for y in getCuts if "pair" in y] # get pair cuts
                    if getPairCuts: # if pair cut list is not empty
                        allPairCuts = (allPairCuts + getPairCuts) # Get Only pair cuts from CutsLibrary.h
                        namespacedPairCuts = [x + oneColon for x in allPairCuts] # paircut:
                    allAnalysisCuts = (allAnalysisCuts + getCuts) # Get all Cuts from CutsLibrary.h
                    nameSpacedallAnalysisCuts = [x + oneColon for x in allAnalysisCuts] # cut:
                    nameSpacedallAnalysisCutsTwoDots = [x + doubleColon for x in allAnalysisCuts] # cut::
        
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
        allSels = selsWithOneColon + nAddedallAnalysisCutsList
        
        # TODO : should be flaged
        return allAnalysisCuts, allMCSignals, allSels, allMixing