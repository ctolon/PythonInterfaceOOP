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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/v0selector.cxx

import argparse
from extramodules.choicesHandler import NoAction
from extramodules.choicesHandler import ChoicesAction
from extramodules.choicesHandler import ChoicesCompleterList
from extramodules.helperOptions import HelperOptions
from extramodules.converters import O2Converters
import argcomplete
from commondeps.centralityTable import CentralityTable
from commondeps.eventSelection import EventSelectionTask
from commondeps.multiplicityTable import MultiplicityTable
from commondeps.pidTOFBase import TofEventTime
from commondeps.pidTOFBeta import TofPidBeta
from commondeps.pidTPCTOFFull import TpcTofPidFull
from commondeps.trackPropagation import TrackPropagation
from commondeps.trackselection import TrackSelectionTask
from commondeps.dplAodReader import DplAodReader


class V0selector(object):
    
    """
    Class for Interface -> v0selector.cxx Task -> Configurable, Process Functions

    Args:
        object (parser_args() object): v0selector.cxx Interface
    """
    
    def __init__(
        self, parserV0selector = argparse.ArgumentParser(
            formatter_class = argparse.ArgumentDefaultsHelpFormatter,
            description = "Example Usage: ./runV0selector.py <yourConfig.json> --arg value"
            ), eventSelection = EventSelectionTask(), centralityTable = CentralityTable(), multiplicityTable = MultiplicityTable(),
        tofEventTime = TofEventTime(), tofPidBeta = TofPidBeta(), tpcTofPidFull = TpcTofPidFull(), trackPropagation = TrackPropagation(),
        trackSelection = TrackSelectionTask(), helperOptions = HelperOptions(), o2Converters = O2Converters(), dplAodReader = DplAodReader()
        ):
        super(V0selector, self).__init__()
        self.parserV0selector = parserV0selector
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
        self.parserV0selector.register("action", "none", NoAction)
        self.parserV0selector.register("action", "store_choice", ChoicesAction)
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        v0GammaQASelections = {
            "NM": "Run gamma->ee QA",
            }
        v0GammaQASelectionsList = []
        for k, v in v0GammaQASelections.items():
            v0GammaQASelectionsList.append(k)
            
        trackPIDQASelections = {
            "QA": "Run PID QA for barrel tracks",
            }
        trackPIDQASelectionsList = []
        for k, v in trackPIDQASelections.items():
            trackPIDQASelectionsList.append(k)
        
        # Interface
        
        #v0-selector
        groupV0Selector = self.parserV0selector.add_argument_group(title = "Data processor options: v0-selector")
        groupV0Selector.add_argument("--d_bz_input", help = "bz field in kG, -999 is automatic", action = "store", type = str)
        groupV0Selector.add_argument("--v0max_mee", help = "max mee for photon", action = "store", type = str)
        groupV0Selector.add_argument("--maxpsipair", help = "max psi_pair for photon", action = "store", type = str)
        groupV0Selector.add_argument("--v0cospa", help = "v0cospa", action = "store", type = str)
        groupV0Selector.add_argument("--dcav0dau", help = "DCA V0 Daughters", action = "store", type = str)
        groupV0Selector.add_argument("--v0Rmin", help = "v0Rmin", action = "store", type = str)
        groupV0Selector.add_argument("--v0Rmax", help = "v0Rmax", action = "store", type = str)
        groupV0Selector.add_argument("--dcamin", help = "dcamin", action = "store", type = str)
        groupV0Selector.add_argument("--dcamax", help = "dcamax", action = "store", type = str)
        groupV0Selector.add_argument("--mincrossedrows", help = "Min crossed rows", action = "store", type = str)
        groupV0Selector.add_argument("--maxchi2tpc", help = "max chi2/NclsTPC", action = "store", type = str)
        
        #track-pid-qa
        groupTrackPIDQA = self.parserV0selector.add_argument_group(title = "Data processor options: track-pid-qa")
        groupTrackPIDQA.add_argument(
            "--QA", help = "track-pid-qa: PROCESS_SWITCH options", action = "store", type = str, nargs="*", metavar = "QA",
            choices = trackPIDQASelectionsList,
            ).completer = ChoicesCompleterList(trackPIDQASelectionsList)
        groupProcessTrackPIDQA = self.parserV0selector.add_argument_group(title = "Choice List for track-pid-qa PROCESS_SWITCH options")
        for key, value in trackPIDQASelections.items():
            groupProcessTrackPIDQA.add_argument(key, help = value, action = "none")
        
        #v0-gamma-qa
        groupV0GammaQA = self.parserV0selector.add_argument_group(title = "Data processor options: v0-gamma-qa")
        groupV0GammaQA.add_argument(
            "--NM", help = "v0-gamma-qa: PROCESS_SWITCH options", action = "store", type = str, nargs = "*", metavar = "NM",
            choices = v0GammaQASelectionsList,
            ).completer = ChoicesCompleterList(v0GammaQASelectionsList)
        groupProcessV0GammaQA = self.parserV0selector.add_argument_group(title = "Choice List for v0-gamma-qa PROCESS_SWITCH options")
        for key, value in v0GammaQASelections.items():
            groupProcessV0GammaQA.add_argument(key, help = value, action = "none")
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        
        argcomplete.autocomplete(self.parserV0selector, always_complete_options = False)
        return self.parserV0selector.parse_args()
    
    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """
        
        self.helperOptions.parserHelperOptions = self.parserV0selector
        self.helperOptions.addArguments()
        
        self.dplAodReader.parserDplAodReader = self.parserV0selector
        self.dplAodReader.addArguments()
        
        self.eventSelection.parserEventSelectionTask = self.parserV0selector
        self.eventSelection.addArguments()
        
        self.trackSelection.parserTrackSelectionTask = self.parserV0selector
        self.trackSelection.addArguments()
        
        self.trackPropagation.parserTrackPropagation = self.parserV0selector
        self.trackPropagation.addArguments()
        
        self.multiplicityTable.parserMultiplicityTable = self.parserV0selector
        self.multiplicityTable.addArguments()
        
        self.centralityTable.parserCentralityTable = self.parserV0selector
        self.centralityTable.addArguments()
        
        self.tpcTofPidFull.parserTpcTofPidFull = self.parserV0selector
        self.tpcTofPidFull.addArguments()
        
        self.tofEventTime.parserTofEventTime = self.parserV0selector
        self.tofEventTime.addArguments()
        
        self.tofPidBeta.parserTofPidBeta = self.parserV0selector
        self.tofPidBeta.addArguments()
        
        self.o2Converters.parserO2Converters = self.parserV0selector
        self.o2Converters.addArguments()
        
        self.addArguments()
