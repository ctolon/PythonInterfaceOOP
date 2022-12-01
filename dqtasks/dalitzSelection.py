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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/DalitzSelection.cxx

import argparse
import os
import re
from urllib.request import Request, urlopen
import ssl
import argcomplete
from argcomplete.completers import ChoicesCompleter
from extramodules.choicesHandler import ChoicesCompleterList
from extramodules.choicesHandler import NoAction
from extramodules.choicesHandler import ChoicesAction
from extramodules.dqLibGetter import DQLibGetter
from extramodules.helperOptions import HelperOptions
from extramodules.converters import O2Converters
from commondeps.centralityTable import CentralityTable
from commondeps.eventSelection import EventSelectionTask
from commondeps.multiplicityTable import MultiplicityTable
from commondeps.pidTOFBase import TofEventTime
from commondeps.pidTOFBeta import TofPidBeta
from commondeps.pidTPCTOFFull import TpcTofPidFull
from commondeps.trackPropagation import TrackPropagation
from commondeps.trackselection import TrackSelectionTask
from commondeps.dplAodReader import DplAodReader


class DalitzPairing(object):
    
    """
    Class for Interface -> DalitzSelection.cxx.cxx Task -> Configurable, Process Functions

    Args:
        object (parser_args() object): DalitzSelection.cxx.cxx Interface
    """
    
    def __init__(
        self, parserDalitzPairing = argparse.ArgumentParser(
            formatter_class = argparse.ArgumentDefaultsHelpFormatter,
            description = "Example Usage: ./runDalitzSelection.py <yourConfig.json> --arg value "
            ), eventSelection = EventSelectionTask(), centralityTable = CentralityTable(), multiplicityTable = MultiplicityTable(),
        tofEventTime = TofEventTime(), tofPidBeta = TofPidBeta(), tpcTofPidFull = TpcTofPidFull(), trackPropagation = TrackPropagation(),
        trackSelection = TrackSelectionTask(), helperOptions = HelperOptions(), o2Converters = O2Converters(),
        dplAodReader = DplAodReader(), dqLibGetter = DQLibGetter()
        ):
        super(DalitzPairing, self).__init__()
        self.parserDalitzPairing = parserDalitzPairing
        self.eventSelection = eventSelection
        self.centralityTable = centralityTable
        self.multiplicityTable = multiplicityTable
        self.tofEventTime = tofEventTime
        self.tofPidBeta = tofPidBeta
        self.tpcTofPidFull = tpcTofPidFull
        self.trackPropagation = trackPropagation
        self.trackSelection = trackSelection
        self.helperOptions = helperOptions
        self.o2Converters = o2Converters
        self.dplAodReader = dplAodReader
        self.dqLibGetter = dqLibGetter
        self.parserDalitzPairing.register("action", "none", NoAction)
        self.parserDalitzPairing.register("action", "store_choice", ChoicesAction)
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        booleanSelections = ["true", "false"]
        
        # Get DQ Analysis Selections from O2-DQ Framework Header Files
        allAnalysisCuts = self.dqLibGetter.allAnalysisCuts
        allTrackHistos = self.dqLibGetter.allTrackHistos
        # allPairCuts = self.dqLibGetter.all
        
        # Interface
        groupDalitzPairing = self.parserDalitzPairing.add_argument_group(title = "Data processor options: dalitz-pairing")
        groupDalitzPairing.add_argument(
            "--cfgEventCuts", help = "Space separated list of event cuts", choices = allAnalysisCuts, nargs = "*", action = "store",
            type = str, metavar = "CFGEVENTCUT",
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        groupDalitzPairing.add_argument(
            "--cfgDalitzTrackCuts", help = "Space separated list of Dalitz track selection cuts", choices = allAnalysisCuts, nargs = "*",
            action = "store", type = str, metavar = "CFGDALITZTRACKCUTS",
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        groupDalitzPairing.add_argument(
            "--cfgDalitzPairCuts", help = "Space separated list of Dalitz pair selection cuts", action = "store", choices = allAnalysisCuts, nargs = "*",
            type = str, metavar = "CFGDALITZPAIRCUTS",
            ).completer = ChoicesCompleterList(allAnalysisCuts)
        groupDalitzPairing.add_argument(
            "--cfgAddTrackHistogram", help = "Comma separated list of track histograms", action = "store", nargs= "*", type = str, metavar="CFGADDTRACKHISTOGRAM", choices = allTrackHistos,
            ).completer = ChoicesCompleterList(allTrackHistos)
        groupDalitzPairing.add_argument(
            "--cfgQA", help = "If true, fill QA histograms", action = "store", type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        groupDalitzPairing.add_argument(
            "--cfgBarrelLowPIN", help = "Low pt cut for Dalitz tracks in the barrel", action = "store", type = str, metavar = "CFGBARRELLOWPIN",
            )
        groupDalitzPairing.add_argument(
            "--cfgEtaCut", help = "Eta cut for Dalitz tracks in the barrel", action = "store", type = str, metavar = "CFGETACUT",
            )
        groupDalitzPairing.add_argument(
            "--cfgTPCNSigElLow", help = "LOW TPCNsigEl cut for Dalitz tracks in the barrel", action = "store", type = str, metavar = "CFGTPCNSIGELLOW",
            )
        groupDalitzPairing.add_argument(
            "--cfgTPCNSigElHigh", help = "High TPCNsigEl cut for Dalitz tracks in the barrel", action = "store", type = str, metavar = "CFGTPCNSIGELHIGH",
            )
            
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        argcomplete.autocomplete(self.parserDalitzPairing, always_complete_options = False)
        return self.parserDalitzPairing.parse_args()
    
    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """
        
        self.helperOptions.parserHelperOptions = self.parserDalitzPairing
        self.helperOptions.addArguments()
        
        self.dplAodReader.parserDplAodReader = self.parserDalitzPairing
        self.dplAodReader.addArguments()
        
        self.eventSelection.parserEventSelectionTask = self.parserDalitzPairing
        self.eventSelection.addArguments()
        
        self.trackSelection.parserTrackSelectionTask = self.parserDalitzPairing
        self.trackSelection.addArguments()
        
        self.trackPropagation.parserTrackPropagation = self.parserDalitzPairing
        self.trackPropagation.addArguments()
        
        self.multiplicityTable.parserMultiplicityTable = self.parserDalitzPairing
        self.multiplicityTable.addArguments()
        
        self.centralityTable.parserCentralityTable = self.parserDalitzPairing
        self.centralityTable.addArguments()
        
        self.tpcTofPidFull.parserTpcTofPidFull = self.parserDalitzPairing
        self.tpcTofPidFull.addArguments()
        
        self.tofEventTime.parserTofEventTime = self.parserDalitzPairing
        self.tofEventTime.addArguments()
        
        self.tofPidBeta.parserTofPidBeta = self.parserDalitzPairing
        self.tofPidBeta.addArguments()
        
        self.o2Converters.parserO2Converters = self.parserDalitzPairing
        self.o2Converters.addArguments()
        
        self.addArguments()
