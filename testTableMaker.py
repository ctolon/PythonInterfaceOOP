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

# Orginal Task For tableMaker.cxx: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMaker.cxx
# Orginal Task For tableMakerMC.cxx: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMakerMC.cxx

import json
import sys
import logging
import logging.config
from logging.handlers import RotatingFileHandler
from logging import handlers
from ast import parse
import os
import argparse
from argparse import Namespace
import re
import urllib.request
from urllib.request import Request, urlopen
import ssl
from CommonDeps.centralityTable import extrargs2
#from CommonDeps.eventSelection import extrargs

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

import argparse

class B(object):

  def __init__(self, parserB=argparse.ArgumentParser()):
    super(B, self).__init__()
    self.parserB = parserB

  def addArguments(self):
    self.parserB.add_argument("-tb", "--test-b", help="Test B", type=str, metavar="")
    #Add more arguments specific to B

  def parseArgs(self):
    return self.parserB.parse_args()

class A(object):

  def __init__(self, parserA=argparse.ArgumentParser(), b=B()):
    super(A, self).__init__()
    self.parserA = parserA
    self.b = b

  def addArguments(self):
    self.parserA.add_argument("-ta", "--test-a", help="Test A", type=str, metavar="")
    #Add more arguments specific to A

  def parseArgs(self):
    return self.parserA.parse_args()

  def mergeArgs(self):
    self.b.parserB = self.parserA
    self.b.addArguments()
    self.addArguments() 

def merge_args_safe(args1: Namespace, args2: Namespace) -> Namespace:
    """
    Merges two namespaces but throws an error if there are keys that collide.

    ref: https://stackoverflow.com/questions/56136549/how-can-i-merge-two-argparse-namespaces-in-python-2-x
    :param args1:
    :param args2:
    :return:
    """
    # - the merged args
    # The vars() function returns the __dict__ attribute to values of the given object e.g {field:value}.
    args = Namespace(**vars(args1), **vars(args2))
    return args

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
   
tableMakerProcessSelections = {
    "Full": "Build full DQ skimmed data model, w/o centrality",
    "FullTiny": "Build full DQ skimmed data model tiny",
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

tablemakerProcessAllParameters = [
    "processFull",
    "processFullTiny",
    "processFullWithCov",
    "processFullWithCent",
    "processBarrelOnlyWithV0Bits",
    "processBarrelOnlyWithEventFilter",
    "processBarrelOnlyWithQvector",
    "processBarrelOnlyWithCent",
    "processBarrelOnlyWithCov",
    "processBarrelOnly",
    "processMuonOnlyWithCent",
    "processMuonOnlyWithCov",
    "processMuonOnly",
    "processMuonOnlyWithFilter",
    "processMuonOnlyWithQvector",
    "processOnlyBCs"
]

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

v0SelectorParameters = [
    "d_bz",
    "v0cospa",
    "dcav0dau",
    "v0RMin",
    "v0Rmax",
    "dcamin",
    "dcamax",
    "mincrossedrows",
    "maxchi2tpc"
]

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

# Centrality Filter for pp systems in tableMaker
isNoDeleteNeedForCent = True
isProcessFuncLeftAfterCentDelete = True

# For MC/Data Process func Filtering in tableMaker
isValidProcessFunc = True

threeSelectedList = []

clist = []  # control list for type control
allValuesCfg = []  # counter for provided args
allAnalysisCuts = []  # all analysis cuts
allMCSignals = []  # all MC Signals
allPairCuts = []  # only pair cuts
nAddedallAnalysisCutsList = []  # e.g. muonQualityCuts:2
nAddedPairCutsList = []  # e.g paircutMass:3
selsWithOneColon = []  # track/muon cut:paircut:n
allSels = []  # track/muon cut::n
oneColon = ":"  # Namespace reference
doubleColon = "::"  # Namespace reference

# List for Transcation management for FilterPP
muonCutList = []  # List --> transcation management for filterPP
barrelTrackCutList = []  # List --> transcation management for filterPP
barrelSelsList = []
muonSelsList = []
barrelSelsListAfterSplit = []
muonSelsListAfterSplit = []

O2DPG_ROOT = os.environ.get("O2DPG_ROOT")
QUALITYCONTROL_ROOT = os.environ.get("QUALITYCONTROL_ROOT")
O2_ROOT = os.environ.get("O2_ROOT")
O2PHYSICS_ROOT = os.environ.get("O2PHYSICS_ROOT")

# Predefined values for DQ Logger messages
isDQBarrelSelected = False
isDQBarrelTinySelected = False
isDQMuonSelected = False
isDQEventSelected = True
isDQFullSelected = False
isFilterPPSelected = False
isFilterPPTinySelected = False
isQVectorSelected = False

# Predefined Search Lists
fullSearch = []
barrelSearch = []
muonSearch = []
#bcsSearch = []      
covSearch = []
centSearch = []
filterSearch = []   
qVectorSearch = [] 

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
        stringIfSearch = [x for x in f if 'if' in x] 
        for i in stringIfSearch:
            getSignals = re.findall('"([^"]*)"', i)
            allMCSignals = allMCSignals + getSignals
            
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

    
###################
# Main Parameters #
###################

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Arguments to pass")
parser.register("action", "none", NoAction)
parser.register("action", "store_choice", ChoicesAction)
groupCoreSelections = parser.add_argument_group(title="Core configurations that must be configured")
groupCoreSelections.add_argument("-runData", help="Run over data", action="store_true")
groupCoreSelections.add_argument("-runMC", help="Run over MC", action="store_true")
parser.add_argument("--run", help="Run Number Selection (2 or 3)", action="store", type=str, choices=("2","3")).completer = ChoicesCompleter(["2","3"])
#parser.add_argument("analysisString", metavar="text", help="my analysis string", required=False) # optional interface
groupTaskAdders = parser.add_argument_group(title="Additional Task Adding Options")
groupTaskAdders.add_argument("--add_mc_conv", help="Add the converter from mcparticle to mcparticle+001 (Adds your workflow o2-analysis-mc-converter task)", action="store_true")
groupTaskAdders.add_argument("--add_fdd_conv", help="Add the fdd converter (Adds your workflow o2-analysis-fdd-converter task)", action="store_true")
groupTaskAdders.add_argument("--add_track_prop", help="Add track propagation to the innermost layer (TPC or ITS) (Adds your workflow o2-analysis-track-propagation task)", action="store_true")

########################
# Interface Parameters #
########################

# aod
groupDPLReader = parser.add_argument_group(title="Data processor options: internal-dpl-aod-reader")
groupDPLReader.add_argument("--aod", help="Add your AOD File with path", action="store", type=str)
groupDPLReader.add_argument("--aod-memory-rate-limit", help="Rate limit AOD processing based on memory", action="store", type=str)

# automation params
groupAutomations = parser.add_argument_group(title="Automation Parameters")
groupAutomations.add_argument("--onlySelect", help="If false JSON Overrider Interface If true JSON Additional Interface", action="store", default="true", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)
groupAutomations.add_argument("--autoDummy", help="Dummy automize parameter (don't configure it, true is highly recomended for automation)", action="store", default="true", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)

# table-maker
groupTableMakerConfigs = parser.add_argument_group(title="Data processor options: table-maker/table-maker-m-c")
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

# table-maker process
groupProcessTableMaker = parser.add_argument_group(title="Data processor options: table-maker/table-maker-m-c")
groupProcessTableMaker.add_argument("--process",help="Process Selection options for tableMaker/tableMakerMC Data Processing and Skimming", action="store", type=str, nargs="*", metavar="PROCESS", choices=tableMakerProcessSelectionsList).completer = ChoicesCompleterList(tableMakerProcessSelectionsList)
for key,value in tableMakerProcessSelections.items():
    groupProcessTableMaker.add_argument(key, help=value, action="none")


groupAnalysisQvector = parser.add_argument_group(title="Data processor options: analysis-qvector")
groupAnalysisQvector.add_argument("--cfgCutPtMin", help="Minimal pT for tracks", action="store", type=str, metavar="CFGCUTPTMIN")
groupAnalysisQvector.add_argument("--cfgCutPtMax", help="Maximal pT for tracks", action="store", type=str, metavar="CFGCUTPTMAX")
groupAnalysisQvector.add_argument("--cfgCutEta", help="Eta range for tracks", action="store", type=str, metavar="CFGCUTETA")
groupAnalysisQvector.add_argument("--cfgEtaLimit", help="Eta gap separation, only if using subEvents", action="store", type=str, metavar="CFGETALIMIT")
groupAnalysisQvector.add_argument("--cfgNPow", help="Power of weights for Q vector", action="store", type=str, metavar="CFGNPOW")
groupAnalysisQvector.add_argument("--cfgEfficiency", help="CCDB path to efficiency object", action="store", type=str)
groupAnalysisQvector.add_argument("--cfgAcceptance", help="CCDB path to acceptance object", action="store", type=str)


#all d-q tasks and selections
groupQASelections = parser.add_argument_group(title="Data processor options: d-q-barrel-track-selection-task, d-q-muons-selection, d-q-event-selection-task, d-q-filter-p-p-task, analysis-qvector")
groupQASelections.add_argument("--cfgWithQA", help="If true, fill QA histograms", action="store", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)

# v0-selector
groupV0Selector = parser.add_argument_group(title="Data processor options: v0-selector")
groupV0Selector.add_argument("--d_bz", help="bz field", action="store", type=str)
groupV0Selector.add_argument("--v0cospa", help="v0cospa", action="store", type=str)
groupV0Selector.add_argument("--dcav0dau", help="DCA V0 Daughters", action="store", type=str)
groupV0Selector.add_argument("--v0Rmin", help="v0Rmin", action="store", type=str)
groupV0Selector.add_argument("--v0Rmax", help="v0Rmax", action="store", type=str)
groupV0Selector.add_argument("--dcamin", help="dcamin", action="store", type=str)
groupV0Selector.add_argument("--dcamax", help="dcamax", action="store", type=str)
groupV0Selector.add_argument("--mincrossedrows", help="Min crossed rows", action="store", type=str)
groupV0Selector.add_argument("--maxchi2tpc", help="max chi2/NclsTPC", action="store", type=str)

# pid
groupPID = parser.add_argument_group(title="Data processor options: tof-pid, tpc-pid-full, tof-pid-full")
groupPID.add_argument("--pid", help="Produce PID information for the <particle> mass hypothesis", action="store", nargs="*", type=str.lower, metavar="PID", choices=pidSelectionsList).completer = ChoicesCompleterList(pidSelectionsList)

for key,value in pidSelections.items():
    groupPID.add_argument(key, help=value, action = "none")

# helper lister commands
groupAdditionalHelperCommands = parser.add_argument_group(title="Additional Helper Command Options")
groupAdditionalHelperCommands.add_argument("--cutLister", help="List all of the analysis cuts from CutsLibrary.h", action="store_true")
groupAdditionalHelperCommands.add_argument("--MCSignalsLister", help="List all of the MCSignals from MCSignalLibrary.h", action="store_true")

# debug options
groupAdditionalHelperCommands.add_argument("--debug", help="execute with debug options", action="store", type=str.upper, default="INFO", choices=debugLevelSelectionsList).completer = ChoicesCompleterList(debugLevelSelectionsList)
groupAdditionalHelperCommands.add_argument("--logFile", help="Enable logger for both file and CLI", action="store_true")
groupDebug= parser.add_argument_group(title="Choice List for debug Parameters")

for key,value in debugLevelSelections.items():
    groupDebug.add_argument(key, help=value, action="none")

argcomplete.autocomplete(parser, always_complete_options=False)



extrargs = parser.parse_args(namespace=extrargs2)




a = A()
a.addArguments()
print(vars(a.parseArgs()))

aCombined = A()
aCombined.mergeArgs()
print(vars(aCombined.parseArgs()))








#dict_baz = vars(extrargs)

#dict_baz.update(vars(extrargs2))

#options_baz = Namespace(**dict_baz)

#print(options_baz)

#options_baz = Namespace(**vars(extrargs2), **vars(extrargs))

#options_baz = parser.parse_args()

#extrargs = merge_args_safe(args1=extrargs, args2=extrargs2)

#print(extrargs)




#options_baz = parser.parse_args()



#configuredCommands = vars(extrargs) # for get extrargs
