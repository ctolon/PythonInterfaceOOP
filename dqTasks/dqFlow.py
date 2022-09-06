#!/usr/bin/env python3
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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqFlow.cxx

import json
import sys
import logging
import logging.config
from logging.handlers import RotatingFileHandler
from logging import handlers
from ast import parse
import os
import argparse
import re
import urllib.request
from urllib.request import Request, urlopen
import ssl

"""
argcomplete - Bash tab completion for argparse
Documentation https://kislyuk.github.io/argcomplete/
Instalation Steps
pip install argcomplete
sudo activate-global-python-argcomplete
Only Works On Local not in O2
Activate libraries in below and activate #argcomplete.autocomplete(parser) line
"""
import argcomplete  
from argcomplete.completers import ChoicesCompleter

def listToString(s):
    """
    ListToString provides converts lists to strings with commas.
    This function is written to save as string type instead of list


    Args:
        s (list): Input as List

    Returns:
        string: Comma seperated string
    """
    if len(s) > 1:
        # initialize an empty string
        str1 = ","

        # return string
        return str1.join(s)
    else:
        str1 = " "

        return str1.join(s)


def stringToList(string):
    """
    stringToList provides converts strings to list with commas.
    This function is written to save as list type instead of string

    Args:
        string (string): Input as String

    Returns:
        list: Comma separated list
    """
    li = list(string.split(","))
    return li


class NoAction(argparse.Action):
    """
    NoAction class adds dummy positional arguments to an argument,
    so sub helper messages can be created

    Args:
        argparse (Class): Input as args
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("default", argparse.SUPPRESS)
        kwargs.setdefault("nargs", 0)
        super(NoAction, self).__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        pass


class ChoicesAction(argparse._StoreAction):
    """
    ChoicesAction class is used to add extra choices
    to a parseargs choices list

    Args:
        argparse (Class): Input as args
    """

    def add_choice(self, choice, help=""):
        if self.choices is None:
            self.choices = []
        self.choices.append(choice)
        self.container.add_argument(choice, help=help, action="none")


class ChoicesCompleterList(object):
    """
    For the ChoicesCompleterList package argcomplete,
    the TAB key is the class written for autocomplete and validation when an argument can take multiple values.
    By default, the argcomplete package has the ChoicesCompleter Class,
    which can only validate arguments that take an one value and allows autocomplete with the TAB key.

    Args:
        object (list): parserargs choices object as a list
    """

    def __init__(self, choices):
        self.choices = list(choices)

    def __call__(self, **kwargs):
        return self.choices
        
###################################
# Interface Predefined Selections #
###################################

centralityTableSelections = {
    "Run2V0M": "Produces centrality percentiles using V0 multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "Run2SPDtks": "Produces Run2 centrality percentiles using SPD tracklets multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "Run2SPDcls": "Produces Run2 centrality percentiles using SPD clusters multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "Run2CL0": "Produces Run2 centrality percentiles using CL0 multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "Run2CL1": "Produces Run2 centrality percentiles using CL1 multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "FV0A": "Produces centrality percentiles using FV0A multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "FT0M": "Produces centrality percentiles using FT0 multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "FDDM": "Produces centrality percentiles using FDD multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "NTPV": "Produces centrality percentiles using number of tracks contributing to the PV. -1: auto, 0: don't, 1: yes. Default: auto (-1)"
}
centralityTableSelectionsList = []
for k, v in centralityTableSelections.items():
    centralityTableSelectionsList.append(k)

centralityTableParameters = [
    "estRun2V0M",
    "estRun2SPDtks",
    "estRun2SPDcls",
    "estRun2CL0",
    "estRun2CL1",
    "estFV0A",
    "estFT0M",
    "estFDDM",
    "estNTPV"
]
# TODO: Add genname parameter

ft0Selections = ["FT0", "NoFT0", "OnlyFT0", "Run2"]

ft0Parameters = ["processFT0", "processNoFT0", "processOnlyFT0", "processRun2"]

pidSelections = {
    "el": "Produce PID information for the Electron mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
    "mu": "Produce PID information for the Muon mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
    "pi": "Produce PID information for the Pion mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
    "ka": "Produce PID information for the Kaon mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
    "pr": "Produce PID information for the Proton mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
    "de": "Produce PID information for the Deuterons mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
    "tr": "Produce PID information for the Triton mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
    "he": "Produce PID information for the Helium3 mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)",
    "al": "Produce PID information for the Alpha mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1)"
}
pidSelectionsList = []
for k, v in pidSelections.items():
    pidSelectionsList.append(k)

pidParameters = [
    "pid-el",
    "pid-mu",
    "pid-pi",
    "pid-ka",
    "pid-pr",
    "pid-de",
    "pid-tr",
    "pid-he",
    "pid-al"
]

collisionSystemSelections = ["PbPb", "pp", "pPb", "Pbp", "XeXe"]

booleanSelections = ["true", "false"]

debugLevelSelections = {
    "NOTSET": "Set Debug Level to NOTSET",
    "DEBUG": "Set Debug Level to DEBUG",
    "INFO": "Set Debug Level to INFO",
    "WARNING": "Set Debug Level to WARNING",
    "ERROR": "Set Debug Level to ERROR",
    "CRITICAL": "Set Debug Level to CRITICAL"
}
debugLevelSelectionsList = []
for k, v in debugLevelSelections.items():
    debugLevelSelectionsList.append(k)

eventMuonSelections = ["0", "1", "2"]

clist = []  # control list for type control
allValuesCfg = []  # counter for provided args
allAnalysisCuts = []  # all analysis cuts

# Get system variables in alienv. In alienv we don't have cuts and signal library!!! We need discuss this thing
O2DPG_ROOT = os.environ.get("O2DPG_ROOT")
QUALITYCONTROL_ROOT = os.environ.get("QUALITYCONTROL_ROOT")
O2_ROOT = os.environ.get("O2_ROOT")
O2PHYSICS_ROOT = os.environ.get("O2PHYSICS_ROOT")

threeSelectedList = []

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
        stringIfSearch = [x for x in f if "if" in x] 
        for i in stringIfSearch:
            getAnalysisCuts = re.findall('"([^"]*)"', i)
            allAnalysisCuts = allAnalysisCuts + getAnalysisCuts


###################
# Main Parameters #
###################
    
parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Arguments to pass")
groupCoreSelections = parser.add_argument_group(title="Core configurations that must be configured")
groupCoreSelections.add_argument("cfgFileName", metavar="Config.json", default="config.json", help="config JSON file name")
parser.register("action", "none", NoAction)
parser.register("action", "store_choice", ChoicesAction)

# DQ Flow Task Selections
groupAnalysisQvector = parser.add_argument_group(title="Data processor options: analysis-qvector")
groupAnalysisQvector.add_argument("--cfgBarrelTrackCuts", help="Space separated list of barrel track cuts", choices=allAnalysisCuts,nargs="*", action="store", type=str, metavar="CFGBARRELTRACKCUTS").completer = ChoicesCompleterList(allAnalysisCuts)
groupAnalysisQvector.add_argument("--cfgMuonCuts", help="Space separated list of muon cuts", action="store", choices=allAnalysisCuts, nargs="*", type=str, metavar="CFGMUONCUTS").completer = ChoicesCompleterList(allAnalysisCuts)
groupAnalysisQvector.add_argument("--cfgEventCuts", help="Space separated list of event cuts", choices=allAnalysisCuts, nargs="*", action="store", type=str, metavar="CFGEVENTCUT").completer = ChoicesCompleterList(allAnalysisCuts)
groupAnalysisQvector.add_argument("--cfgWithQA", help="If true, fill QA histograms", action="store", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)
groupAnalysisQvector.add_argument("--cfgCutPtMin", help="Minimal pT for tracks", action="store", type=str, metavar="CFGCUTPTMIN")
groupAnalysisQvector.add_argument("--cfgCutPtMax", help="Maximal pT for tracks", action="store", type=str, metavar="CFGCUTPTMAX")
groupAnalysisQvector.add_argument("--cfgCutEta", help="Eta range for tracks", action="store", type=str, metavar="CFGCUTETA")
groupAnalysisQvector.add_argument("--cfgEtaLimit", help="Eta gap separation, only if using subEvents", action="store", type=str, metavar="CFGETALIMIT")
groupAnalysisQvector.add_argument("--cfgNPow", help="Power of weights for Q vector", action="store", type=str, metavar="CFGNPOW")

groupAnalysisQvector.add_argument("--cfgEfficiency", help="CCDB path to efficiency object", action="store", type=str)
groupAnalysisQvector.add_argument("--cfgAcceptance", help="CCDB path to acceptance object", action="store", type=str)

argcomplete.autocomplete(parser, always_complete_options=False)
extrargs = parser.parse_args()

configuredCommands = vars(extrargs) # for get extrargs

