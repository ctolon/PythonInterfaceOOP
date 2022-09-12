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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMaker.cxx

import json
import sys
import logging
import logging.config
from logging import handlers
import os
import argparse

from extramodules.actionHandler import NoAction
from extramodules.actionHandler import ChoicesAction
from extramodules.debugOptions import DebugOptions
from extramodules.stringOperations import listToString, stringToList

from commondeps.centralityTable import CentralityTable
from commondeps.eventSelection import EventSelectionTask
from commondeps.multiplicityTable import MultiplicityTable
from commondeps.pidTOFBase import TofEventTime
from commondeps.pidTOFBeta import TofPidBeta
from commondeps.pidTPCTOFFull import TpcTofPidFull
from commondeps.trackPropagation import TrackPropagation

from dqtasks.tableMaker import TableMaker
from dqtasks.v0selector import V0selector

from pycacheRemover import PycacheRemover

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
        
###################################
# Interface Predefined Selections #
###################################
   
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

ft0Parameters = ["processFT0", "processNoFT0", "processOnlyFT0", "processRun2"]

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

booleanSelections = ["true", "false"]

# Centrality Filter for pp systems in tableMaker
isNoDeleteNeedForCent = True
isProcessFuncLeftAfterCentDelete = True

threeSelectedList = []
clist = []  # control list for type control

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
    
#################
# Init Workflow #
#################

class RunTableMaker(object):
    """
    This class is for managing the workflow by using the interface arguments from
    all other Common dependencies and the tableMaker Task's own arguments in a combined structure.
    
    Args:
      object (parser_args() object): runTableMaker.py workflow
    """

    def __init__(self, 
                parserRunTableMaker=argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                description="Arguments to pass"), 
                eventSelection=EventSelectionTask(), 
                centralityTable=CentralityTable(),
                multiplicityTable=MultiplicityTable(),
                tofEventTime=TofEventTime(),
                tofPidBeta =TofPidBeta(),
                tpcTofPidFull=TpcTofPidFull(),
                trackPropagation=TrackPropagation(),
                v0selector = V0selector(),
                tableMaker=TableMaker(),
                debugOptions=DebugOptions()
                ):
        super(RunTableMaker, self).__init__()
        self.parserRunTableMaker = parserRunTableMaker
        self.eventSelection = eventSelection
        self.centralityTable = centralityTable
        self.multiplicityTable = multiplicityTable
        self.tofEventTime = tofEventTime
        self.tofPidBeta = tofPidBeta
        self.tpcTofPidFull = tpcTofPidFull
        self.trackPropagation = trackPropagation
        self.v0selector = v0selector
        self.tableMaker = tableMaker
        self.debugOptions = debugOptions
        self.parserRunTableMaker.register("action", "none", NoAction)
        self.parserRunTableMaker.register("action", "store_choice", ChoicesAction)

    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Core Part
        groupCoreSelections = self.parserRunTableMaker.add_argument_group(title="Core configurations that must be configured")
        groupCoreSelections.add_argument("cfgFileName", metavar="Config.json", default="config.json", help="config JSON file name")
        groupCoreSelections.add_argument("-runData", help="Run over Data", action="store_true", default=True)
        groupTaskAdders = self.parserRunTableMaker.add_argument_group(title="Additional Task Adding Options")
        groupTaskAdders.add_argument("--add_mc_conv", help="Add the converter from mcparticle to mcparticle+001 (Adds your workflow o2-analysis-mc-converter task)", action="store_true")
        groupTaskAdders.add_argument("--add_fdd_conv", help="Add the fdd converter (Adds your workflow o2-analysis-fdd-converter task)", action="store_true")
        groupTaskAdders.add_argument("--add_track_prop", help="Add track propagation to the innermost layer (TPC or ITS) (Adds your workflow o2-analysis-track-propagation task)", action="store_true")
                        
        # aod
        groupDPLReader = self.parserRunTableMaker.add_argument_group(title="Data processor options: internal-dpl-aod-reader")
        groupDPLReader.add_argument("--aod", help="Add your AOD File with path", action="store", type=str)
        groupDPLReader.add_argument("--aod-memory-rate-limit", help="Rate limit AOD processing based on memory", action="store", type=str)

        # automation params
        groupAutomations = self.parserRunTableMaker.add_argument_group(title="Automation Parameters")
        groupAutomations.add_argument("--onlySelect", help="If false JSON Overrider Interface If true JSON Additional Interface", action="store", default="true", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)
        groupAutomations.add_argument("--autoDummy", help="Dummy automize parameter (don't configure it, true is highly recomended for automation)", action="store", default="true", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)
        
        # helper lister commands
        #groupAdditionalHelperCommands = self.parserRunTableMaker.add_argument_group(title="Additional Helper Command Options")
        #groupAdditionalHelperCommands.add_argument("--cutLister", help="List all of the analysis cuts from CutsLibrary.h", action="store_true")
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
 
        argcomplete.autocomplete(self.parserRunTableMaker, always_complete_options=False)  
        return self.parserRunTableMaker.parse_args()

    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """
        
        self.eventSelection.parserEventSelectionTask = self.parserRunTableMaker
        self.eventSelection.addArguments()
        
        self.centralityTable.parserCentralityTable = self.parserRunTableMaker
        self.centralityTable.addArguments()
        
        self.multiplicityTable.parserMultiplicityTable = self.parserRunTableMaker
        self.multiplicityTable.addArguments()
        
        self.tofEventTime.parserTofEventTime = self.parserRunTableMaker
        self.tofEventTime.addArguments()
        
        self.tofPidBeta.parserTofPidBeta = self.parserRunTableMaker
        self.tofPidBeta.addArguments()
        
        self.tpcTofPidFull.parserTpcTofPidFull = self.parserRunTableMaker
        self.tpcTofPidFull.addArguments()
        
        self.trackPropagation.parserTrackPropagation = self.parserRunTableMaker
        self.trackPropagation.addArguments()
        
        self.v0selector.parserV0selector = self.parserRunTableMaker
        self.v0selector.addArguments()
                
        self.tableMaker.parserTableMaker = self.parserRunTableMaker
        self.tableMaker.addArguments()
        
        self.debugOptions.parserDebugOptions = self.parserRunTableMaker
        self.debugOptions.addArguments()
        
        self.addArguments()
        
    # This function not work should be integrated instead of mergeArgs
    """  
    def mergeMultiArgs(self, *objects):
        parser = self.parserRunTableMaker
        for object in objects:
            object.parser = parser
            object.addArguments()
        self.addArguments()
    """
     
# init args manually   
initArgs = RunTableMaker()
initArgs.mergeArgs()
initArgs.parseArgs()

extrargs = initArgs.parseArgs()
configuredCommands = vars(extrargs) # for get extrargs

# Transcation management for forgettining assign a value to parameters
forgetParams = []
for key,value in configuredCommands.items():
    if(value != None):
        if (type(value) == type("string") or type(value) == type(clist)) and len(value) == 0:
            forgetParams.append(key)
if len(forgetParams) > 0: 
    print("[ERROR] Your forget assign a value to for this parameters: ", forgetParams)
    sys.exit()
    
# Debug Settings
if extrargs.debug and (not extrargs.logFile):
    DEBUG_SELECTION = extrargs.debug
    numeric_level = getattr(logging, DEBUG_SELECTION.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % DEBUG_SELECTION)
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=DEBUG_SELECTION)
    
if extrargs.logFile and extrargs.debug:
    log = logging.getLogger("")
    level = logging.getLevelName(extrargs.debug)
    log.setLevel(level)
    format = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)
    
    loggerFile = "tableMaker.log"
    if os.path.isfile(loggerFile):
        os.remove(loggerFile)
    
    fh = handlers.RotatingFileHandler(loggerFile, maxBytes=(1048576*5), backupCount=7, mode="w")
    fh.setFormatter(format)
    log.addHandler(fh)


###################
# HELPER MESSAGES #
###################

allAnalysisCuts = []
allMCSignals = []

"""
   
if extrargs.cutLister and extrargs.MCSignalsLister:
    counter = 0
    print("Analysis Cut Options :")
    print("====================")
    temp = ""  
    for i in allAnalysisCuts:
        if len(temp) == 0:
            temp = temp + i
        else:
            temp = temp + "," + i
        counter = counter + 1
        if counter == 3:
            temp = stringToList(temp)
            threeSelectedList.append(temp)
            temp = ""
            counter = 0
    for list_ in threeSelectedList:
        print("{:<40s} {:<40s} {:<40s}".format(*list_)) 
        
    counter = 0
    print("MC Signals :")
    print("====================")
    temp = ""
    threeSelectedList.clear()  
    for i in allMCSignals:
        if len(temp) == 0:
            temp = temp + i
        else:
            temp = temp + "," + i
        counter = counter + 1
        if counter == 3:
            temp = stringToList(temp)
            threeSelectedList.append(temp)
            temp = ""
            counter = 0
    for list_ in threeSelectedList:
        print("{:<40s} {:<40s} {:<40s}".format(*list_))  
    sys.exit()
    
if extrargs.cutLister:
    counter = 0
    print("Analysis Cut Options :")
    print("====================")
    temp = ""  
    for i in allAnalysisCuts:
        if len(temp) == 0:
            temp = temp + i
        else:
            temp = temp + "," + i
        counter = counter + 1
        if counter == 3:
            temp = stringToList(temp)
            threeSelectedList.append(temp)
            temp = ""
            counter = 0
    for list_ in threeSelectedList:
        print("{:<40s} {:<40s} {:<40s}".format(*list_))      
    sys.exit()
    
if extrargs.MCSignalsLister:
    counter = 0
    print("MC Signals :")
    print("====================")
    temp = ""  
    for i in allMCSignals:
        if len(temp) == 0:
            temp = temp + i
        else:
            temp = temp + "," + i
        counter = counter + 1
        if counter == 3:
            temp = stringToList(temp)
            threeSelectedList.append(temp)
            temp = ""
            counter = 0
    for list_ in threeSelectedList:
        print("{:<40s} {:<40s} {:<40s}".format(*list_))     
    sys.exit()
    
"""
    
######################
# PREFIX ADDING PART #
###################### 

# add prefix for extrargs.process for table-maker/table-maker-m-c and d-q-filter-p-p
if extrargs.process != None:
    prefix_process = "process"
    extrargs.process = [prefix_process + sub for sub in extrargs.process]

# add prefix for extrargs.pid for pid selection
if extrargs.pid != None:
    prefix_pid = "pid-"
    extrargs.pid = [prefix_pid + sub for sub in extrargs.pid]
    
# add prefix for extrargs.est for centrality-table
if extrargs.est != None:
    prefix_est = "est"
    extrargs.est = [prefix_est + sub for sub in extrargs.est]

# add prefix for extrargs.FT0 for tof-event-time
if extrargs.FT0 != None:
    prefix_process = "process"
    extrargs.FT0 = prefix_process + extrargs.FT0
    
######################################################################################

commonDeps = [
    "o2-analysis-timestamp",
    "o2-analysis-event-selection",
    "o2-analysis-multiplicity-table"
]
barrelDeps = [
    "o2-analysis-trackselection",
    "o2-analysis-trackextension",
    "o2-analysis-pid-tof-base",
    "o2-analysis-pid-tof",
    "o2-analysis-pid-tof-full",
    "o2-analysis-pid-tof-beta",
    "o2-analysis-pid-tpc-full"
]
specificDeps = {
  "processFull": [],
  "processFullTiny": [],
  "processFullWithCov": [],
  "processFullWithCent": ["o2-analysis-centrality-table"],
  "processBarrelOnly": [],
  "processBarrelOnlyWithCov": [],
  "processBarrelOnlyWithV0Bits": ["o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
  "processBarrelOnlyWithEventFilter": ["o2-analysis-dq-filter-pp"],
  "processBarrelOnlyWithQvector": ["o2-analysis-centrality-table", "o2-analysis-dq-flow"],
  "processBarrelOnlyWithCent": ["o2-analysis-centrality-table"],
  "processMuonOnly": [],
  "processMuonOnlyWithCov": [],
  "processMuonOnlyWithCent": ["o2-analysis-centrality-table"],
  "processMuonOnlyWithQvector": ["o2-analysis-centrality-table", "o2-analysis-dq-flow"],
  "processMuonOnlyWithFilter": ["o2-analysis-dq-filter-pp"]
  #"processFullWithCentWithV0Bits": ["o2-analysis-centrality-table","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
  #"processFullWithEventFilterWithV0Bits": ["o2-analysis-dq-filter-pp","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
} 

# Definition of all the tables we may write
tables = {
  "ReducedEvents": {"table": "AOD/REDUCEDEVENT/0", "treename": "ReducedEvents"},
  "ReducedEventsExtended": {"table": "AOD/REEXTENDED/0", "treename": "ReducedEventsExtended"},
  "ReducedEventsVtxCov": {"table": "AOD/REVTXCOV/0", "treename": "ReducedEventsVtxCov"},
  "ReducedEventsQvector": {"table": "AOD/REQVECTOR/0", "treename": "ReducedEventsQvector"},
  "ReducedMCEventLabels": {"table": "AOD/REMCCOLLBL/0", "treename": "ReducedMCEventLabels"},
  "ReducedMCEvents": {"table": "AOD/REMC/0", "treename": "ReducedMCEvents"},
  "ReducedTracks": {"table": "AOD/REDUCEDTRACK/0", "treename": "ReducedTracks"},
  "ReducedTracksBarrel": {"table": "AOD/RTBARREL/0", "treename": "ReducedTracksBarrel"},
  "ReducedTracksBarrelCov": {"table": "AOD/RTBARRELCOV/0", "treename": "ReducedTracksBarrelCov"},
  "ReducedTracksBarrelPID": {"table": "AOD/RTBARRELPID/0", "treename": "ReducedTracksBarrelPID"},
  "ReducedTracksBarrelLabels": {"table": "AOD/RTBARRELLABELS/0", "treename": "ReducedTracksBarrelLabels"},
  "ReducedMCTracks": {"table": "AOD/RTMC/0", "treename": "ReducedMCTracks"},
  "ReducedMuons": {"table": "AOD/RTMUON/0", "treename": "ReducedMuons"},
  "ReducedMuonsExtra" : {"table": "AOD/RTMUONEXTRA/0", "treename": "ReducedMuonsExtra"},
  "ReducedMuonsCov": {"table": "AOD/RTMUONCOV/0", "treename": "ReducedMuonsCov"},
  "ReducedMuonsLabels": {"table": "AOD/RTMUONSLABELS/0", "treename": "ReducedMuonsLabels"}
}
# Tables to be written, per process function
commonTables = ["ReducedEvents", "ReducedEventsExtended", "ReducedEventsVtxCov"]
barrelCommonTables = ["ReducedTracks","ReducedTracksBarrel","ReducedTracksBarrelPID"]
muonCommonTables = ["ReducedMuons", "ReducedMuonsExtra"]
specificTables = {
  "processFull": [],
  "processFullTiny": [],
  "processFullWithCov": ["ReducedTracksBarrelCov", "ReducedMuonsCov"],
  "processFullWithCent": [],
  "processBarrelOnly": [],
  "processBarrelOnlyWithCov": ["ReducedTracksBarrelCov"],
  "processBarrelOnlyWithV0Bits": [],
  "processBarrelOnlyWithQvector": ["ReducedEventsQvector"],
  "processBarrelOnlyWithEventFilter": [],
  "processBarrelOnlyWithCent": [],
  "processMuonOnly": [],
  "processMuonOnlyWithCov": ["ReducedMuonsCov"],
  "processMuonOnlyWithCent": [],
  "processMuonOnlyWithQvector": ["ReducedEventsQvector"],
  "processMuonOnlyWithFilter": []
}

# Make some checks on provided arguments
if len(sys.argv) < 2:
  logging.error("Invalid syntax! The command line should look like this:")
  logging.info("  ./runTableMaker.py <yourConfig.json> <-runData|-runMC> --param value ...")
  sys.exit()

# Load the configuration file provided as the first parameter
cfgControl = sys.argv[1] == extrargs.cfgFileName 
config = {}
try:
    if cfgControl:
        with open(extrargs.cfgFileName) as configFile:           
            config = json.load(configFile)
    else:
        logging.error("Invalid syntax! After the script you must define your json configuration file!!! The command line should look like this:")
        logging.info("  ./runTableMaker.py <yourConfig.json> <-runData|-runMC> --param value ...")
        sys.exit()
        
except FileNotFoundError:
    isConfigJson = sys.argv[1].endswith(".json")
    if not isConfigJson:
            logging.error("Invalid syntax! After the script you must define your json configuration file!!! The command line should look like this:")
            logging.info("  ./runTableMaker.py <yourConfig.json> <-runData|-runMC> --param value ...")
            sys.exit()
    logging.error("Your JSON Config File found in path!!!")
    sys.exit()

runOverMC = False
if (extrargs.runData):
    runOverMC = False
    logging.info("runOverMC : %s, Reduced Tables will be produced for Data",runOverMC)
    
taskNameInConfig = "table-maker"
taskNameInCommandLine = "o2-analysis-dq-table-maker"
  
# Check tablemaker dependencies
if extrargs.runData:
    try:
        if config[taskNameInConfig]:
            logging.info("%s is in your JSON Config File", taskNameInConfig)
    except:
        logging.error("JSON config does not include %s, It's for Data. Misconfiguration JSON File!!!", taskNameInConfig)
        sys.exit()
        
# Check alienv
if O2PHYSICS_ROOT == None:
   logging.error("You must load O2Physics with alienv")
   #sys.exit()

#############################
# Start Interface Processes #
#############################

logging.info("Only Select Configured as %s", extrargs.onlySelect)
if extrargs.onlySelect == "true":
    logging.info("INTERFACE MODE : JSON Overrider")
if extrargs.onlySelect == "false":
    logging.info("INTERFACE MODE : JSON Additional")

# For adding a process function from TableMaker and all process should be added only once so set type used
tableMakerProcessSearch= set ()

for key, value in config.items():
    if type(value) == type(config):
        for value, value2 in value.items():
                       
            # aod
            if value =="aod-file" and extrargs.aod:
                config[key][value] = extrargs.aod
                logging.debug(" - [%s] %s : %s",key,value,extrargs.aod)
                
            # table-maker/table-maker-m-c process selections
            if (value in tablemakerProcessAllParameters) and extrargs.process:
                if value in extrargs.process:
                    
                    # processOnlyBCs have to always be true
                    if "processOnlyBCs" not in extrargs.process:
                        extrargs.process.append("processOnlyBCs")
                        logging.warning("You forget to add OnlyBCs value in --process parameter! It will automaticaly added.")
                    value2 = "true"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s",key,value,value2)
                                           
                    # For find all process parameters for TableMaker/TableMakerMC in Orginal JSON
                    for s in config[key].keys():
                        if s in tablemakerProcessAllParameters:
                            tableMakerProcessSearch.add(s)
                    # check extraargs is contain Full Barrel Muon or Bcs
                    fullSearch = [s for s in extrargs.process if "Full" in s]
                    barrelSearch = [s for s in extrargs.process if "Barrel" in s]
                    muonSearch = [s for s in extrargs.process if "Muon" in s]
                    #bcsSearch = [s for s in extrargs.process if "BCs" in s]
                    
                    # check extrargs is contain Cov for transcation management --> add track prop task      
                    covSearch = [s for s in extrargs.process if "Cov" in s]
                    
                    # check extrargs is contain Cent for transcation management Centrality Filter
                    centSearch = [s for s in extrargs.process if "Cent" in s]
                    
                    # check extrargs is contain Filter for automatize Filter PP task
                    filterSearch = [s for s in extrargs.process if "Filter" in s]   
                    
                    # check extrargs is contain Qvector for automatize dqFlow task
                    qVectorSearch = [s for s in extrargs.process if "Qvector" in s] 
                                                         
                    # Automatization for Activate or Disable d-q barrel, muon and event tasks regarding to process func. in tablemaker
                    if len(fullSearch) > 0 and extrargs.runData:
                        config["d-q-barrel-track-selection-task"]["processSelection"] = "true"
                        isDQFullSelected = True
                        #logging.debug(" - [d-q-barrel-track-selection-task] processSelection : true")
                        
                        if extrargs.isBarrelSelectionTiny == "false":
                            config["d-q-barrel-track-selection-task"]["processSelection"] = "true"
                            config["d-q-barrel-track-selection-task"]["processSelectionTiny"] = extrargs.isBarrelSelectionTiny
                            #logging.debug(" - [d-q-barrel-track-selection-task] processSelection : true")
                            #logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : false")
                        if extrargs.isBarrelSelectionTiny == "true":
                            config["d-q-barrel-track-selection-task"]["processSelection"] = "false"
                            config["d-q-barrel-track-selection-task"]["processSelectionTiny"] = extrargs.isBarrelSelectionTiny
                            isDQBarrelTinySelected = True
                            #logging.debug(" - [d-q-barrel-track-selection-task] processSelection : false")
                            #logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : true")

                        config["d-q-muons-selection"]["processSelection"] = "true"
                        isDQMuonSelected  = True
                        #logging.debug(" - [d-q-muons-selection] processSelection : true")
                                   
                    if len(barrelSearch) > 0 and extrargs.runData:
                        if extrargs.isBarrelSelectionTiny == "false":
                            config["d-q-barrel-track-selection-task"]["processSelection"] = "true"
                            config["d-q-barrel-track-selection-task"]["processSelectionTiny"] = extrargs.isBarrelSelectionTiny
                            isDQBarrelSelected = True
                            isDQBarrelTinySelected = False
                            #logging.debug(" - [d-q-barrel-track-selection-task] processSelection : true")
                            #logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : false")
                        if extrargs.isBarrelSelectionTiny == "true":
                            config["d-q-barrel-track-selection-task"]["processSelection"] = "false"
                            config["d-q-barrel-track-selection-task"]["processSelectionTiny"] = extrargs.isBarrelSelectionTiny
                            isDQBarrelSelected = False
                            isDQBarrelTinySelected = True
                            #logging.debug(" - [d-q-barrel-track-selection-task] processSelection : false")
                            #logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : true")
   
                    if len(barrelSearch) == 0 and len(fullSearch) == 0 and extrargs.runData and extrargs.onlySelect == "true":
                        config["d-q-barrel-track-selection-task"]["processSelection"] = "false"
                        config["d-q-barrel-track-selection-task"]["processSelectionTiny"] = "false"
                        #logging.debug(" - [d-q-barrel-track-selection-task] processSelection : false")
                        #logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : false")
                                         
                    if len(muonSearch) > 0 and extrargs.runData:
                        config["d-q-muons-selection"]["processSelection"] = "true"
                        #logging.debug(" - [d-q-muons-selection] processSelection : true")
                        isDQMuonSelected  = True
                    if len(muonSearch) == 0 and len(fullSearch) == 0 and extrargs.runData and extrargs.onlySelect == "true":
                        config["d-q-muons-selection"]["processSelection"] = "false"
                        #logging.debug(" - [d-q-muons-selection] processSelection : false")
                            
                    # processEventSelection have to always be true        
                    if extrargs.runData:
                        config["d-q-event-selection-task"]["processEventSelection"] = "true"
                        isDQEventSelected = True
                        #logging.debug(" - [d-q-event-selection-task] processEventSelection : true")
            
                    # Automatization for Activate or Disable d-q filter-p-p
                    if len(filterSearch) > 0 and extrargs.runData:
                        config["d-q-filter-p-p-task"]["processFilterPP"] ="true"
                        config["d-q-filter-p-p-task"]["processFilterPPTiny"] ="false"
                        isFilterPPSelected = True
                        isFilterPPTinySelected = False                     
                        #logging.debug(" - [d-q-filter-p-p-task-task] processFilterPP : true")
                        #logging.debug(" - [d-q-filter-p-p-task-task] processFilterPPTiny : false")
                        if extrargs.isFilterPPTiny == "true":
                            config["d-q-filter-p-p-task"]["processFilterPP"] = "false"
                            config["d-q-filter-p-p-task"]["processFilterPPTiny"] = "true"
                            isFilterPPSelected = False
                            isFilterPPTinySelected = True  
                            #logging.debug(" - [d-q-filter-p-p-task-task] processFilterPP : false")
                            #logging.debug(" - [d-q-filter-p-p-task-task] processFilterPPTiny : true")
                                 
                    if len(filterSearch) == 0 and extrargs.runData and extrargs.onlySelect == "true":
                        config["d-q-filter-p-p-task"]["processFilterPP"] = "false"
                        config["d-q-filter-p-p-task"]["processFilterPPTiny"] = "false"
                        isFilterPPSelected = False
                        isFilterPPTinySelected = False 
                        #logging.debug(" - [d-q-filter-p-p-task-task] processFilterPP : false")
                        #logging.debug(" - [d-q-filter-p-p-task-task] processFilterPPTiny : true")
                        
                    # Automatization for Activate or Disable analysis-qvector
                    if len(qVectorSearch) > 0 and extrargs.runData:
                        config["analysis-qvector"]["processBarrelQvector"] ="true"
                        isQVectorSelected = True

                    if len(qVectorSearch) == 0 and extrargs.runData and extrargs.onlySelect == "true":
                        config["analysis-qvector"]["processBarrelQvector"] ="false"
                        isQVectorSelected = False
                                                                        
                elif extrargs.onlySelect == "true":
                    if value == "processOnlyBCs":
                        config[key][value] = "true"
                        logging.debug(" - [%s] %s : true",key,value)                     
                    else:
                        value2 = "false"
                        config[key][value] = value2
                        logging.debug(" - [%s] %s : %s",key,value,value2)
                                                     
            # filterPP Selections        
            if value == "cfgBarrelSels" and extrargs.cfgBarrelSels:
                if type(extrargs.cfgBarrelSels) == type(clist):
                    extrargs.cfgBarrelSels = listToString(extrargs.cfgBarrelSels) 
                config[key][value] = extrargs.cfgBarrelSels
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgBarrelSels)
            if value == "cfgMuonSels" and extrargs.cfgMuonSels:
                if type(extrargs.cfgMuonSels) == type(clist):
                    extrargs.cfgMuonSels = listToString(extrargs.cfgMuonSels) 
                config[key][value] = extrargs.cfgMuonSels
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgMuonSels)
                                                           
            # PID Selections
            if  (value in pidParameters) and extrargs.pid and key != "tof-pid":
                if value in extrargs.pid:
                    value2 = "1"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s",key,value,value2)  
                elif extrargs.onlySelect == "true":
                    value2 = "-1"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s",key,value,value2)
                    
            # analysis-qvector selections    
            if value =="cfgCutPtMin" and extrargs.cfgCutPtMin:
                config[key][value] = extrargs.cfgCutPtMin
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgCutPtMin)
            if value =="cfgCutPtMax" and extrargs.cfgCutPtMax:
                config[key][value] = extrargs.cfgCutPtMax
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgCutPtMax)
            if value =="cfgCutEta" and extrargs.cfgCutEta:
                config[key][value] = extrargs.cfgCutEta
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgCutEta)
            if value =="cfgEtaLimit" and extrargs.cfgEtaLimit:
                config[key][value] = extrargs.cfgEtaLimit
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgEtaLimit)
            if value =="cfgNPow" and extrargs.cfgNPow:
                config[key][value] = extrargs.cfgNPow
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgNPow)
            if value =="cfgEfficiency" and extrargs.cfgEfficiency:
                config[key][value] = extrargs.cfgEfficiency
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgEfficiency)
            if value =="cfgAcceptance" and extrargs.cfgAcceptance:
                config[key][value] = extrargs.cfgAcceptance
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgAcceptance)  
                    
            # v0-selector
            if value =="d_bz_input" and extrargs.d_bz_input:
                config[key][value] = extrargs.d_bz_input
                logging.debug(" - [%s] %s : %s",key,value,extrargs.d_bz_input)  
            if value == "v0cospa" and extrargs.v0cospa:
                config[key][value] = extrargs.v0cospa
                logging.debug(" - [%s] %s : %s",key,value,extrargs.v0cospa)  
            if value == "dcav0dau" and extrargs.dcav0dau:
                config[key][value] = extrargs.dcav0dau
                logging.debug(" - [%s] %s : %s",key,value,extrargs.dcav0dau)                  
            if value =="v0Rmin" and extrargs.v0Rmin:
                config[key][value] = extrargs.v0Rmin
                logging.debug(" - [%s] %s : %s",key,value,extrargs.v0Rmin)                  
            if value == "v0Rmax" and extrargs.v0Rmax:
                config[key][value] = extrargs.v0Rmax
                logging.debug(" - [%s] %s : %s",key,value,extrargs.v0Rmax)                  
            if value == "dcamin" and extrargs.dcamin:
                config[key][value] = extrargs.dcamin
                logging.debug(" - [%s] %s : %s",key,value,extrargs.dcamin)                  
            if value == "dcamax" and extrargs.dcamax:
                config[key][value] = extrargs.dcamax
                logging.debug(" - [%s] %s : %s",key,value,extrargs.dcamax)                  
            if value =="mincrossedrows" and extrargs.mincrossedrows:
                config[key][value] = extrargs.mincrossedrows
                logging.debug(" - [%s] %s : %s",key,value,extrargs.mincrossedrows)                  
            if value == "maxchi2tpc" and extrargs.maxchi2tpc:
                config[key][value] = extrargs.maxchi2tpc
                logging.debug(" - [%s] %s : %s",key,value,extrargs.maxchi2tpc)                  
                
            # centrality-table
            if (value in centralityTableParameters) and extrargs.est:
                if value in extrargs.est:
                    value2 = "1"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s",key,value,value2)   
                elif extrargs.onlySelect == "true":
                    value2 = "-1"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s",key,value,value2)  
                    
            # table-maker/table-maker-m-c cfg selections
            if value == "cfgEventCuts" and extrargs.cfgEventCuts:
                if type(extrargs.cfgEventCuts) == type(clist):
                    extrargs.cfgEventCuts = listToString(extrargs.cfgEventCuts)
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgEventCuts = actualConfig + "," + extrargs.cfgEventCuts 
                config[key][value] = extrargs.cfgEventCuts
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgEventCuts)  
            if value == "cfgBarrelTrackCuts" and extrargs.cfgBarrelTrackCuts:
                if type(extrargs.cfgBarrelTrackCuts) == type(clist):
                    extrargs.cfgBarrelTrackCuts = listToString(extrargs.cfgBarrelTrackCuts)
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgBarrelTrackCuts = actualConfig + "," + extrargs.cfgBarrelTrackCuts 
                config[key][value] = extrargs.cfgBarrelTrackCuts
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgBarrelTrackCuts)  
            if value =="cfgMuonCuts" and extrargs.cfgMuonCuts:
                if type(extrargs.cfgMuonCuts) == type(clist):
                    extrargs.cfgMuonCuts = listToString(extrargs.cfgMuonCuts)  
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgMuonCuts = actualConfig + "," + extrargs.cfgMuonCuts               
                config[key][value] = extrargs.cfgMuonCuts
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgMuonCuts)  
            if value == "cfgBarrelLowPt" and extrargs.cfgBarrelLowPt:
                config[key][value] = extrargs.cfgBarrelLowPt
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgBarrelLowPt)  
            if value == "cfgMuonLowPt" and extrargs.cfgMuonLowPt:
                config[key][value] = extrargs.cfgMuonLowPt
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgMuonLowPt)  
            if value =="cfgNoQA" and extrargs.cfgNoQA:
                config[key][value] = extrargs.cfgNoQA
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgNoQA)  
            if value == "cfgDetailedQA" and extrargs.cfgDetailedQA:
                config[key][value] = extrargs.cfgDetailedQA
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgDetailedQA)  
            #if value == "cfgIsRun2" and extrargs.run == "2":
                #config[key][value] = "true"
                #logging.debug(" - %s %s : true",key,value)  
            if value =="cfgMinTpcSignal" and extrargs.cfgMinTpcSignal:
                config[key][value] = extrargs.cfgMinTpcSignal
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgMinTpcSignal)  
            if value == "cfgMaxTpcSignal" and extrargs.cfgMaxTpcSignal:
                config[key][value] = extrargs.cfgMaxTpcSignal
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgMaxTpcSignal)  
                 
            #d-q-muons-selection
            if value =="cfgMuonsCuts" and extrargs.cfgMuonsCuts:
                if type(extrargs.cfgMuonsCuts) == type(clist):
                    extrargs.cfgMuonsCuts = listToString(extrargs.cfgMuonsCuts)
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgMuonsCuts = actualConfig + "," + extrargs.cfgMuonsCuts                  
                config[key][value] = extrargs.cfgMuonsCuts
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgMuonsCuts) 

            # event-selection-task
            if value == "syst" and extrargs.syst:
                config[key][value] = extrargs.syst
                logging.debug(" - [%s] %s : %s",key,value,extrargs.syst)  
            if value =="muonSelection" and extrargs.muonSelection:
                config[key][value] = extrargs.muonSelection
                logging.debug(" - [%s] %s : %s",key,value,extrargs.muonSelection)  
            if value == "customDeltaBC" and extrargs.customDeltaBC:
                config[key][value] = extrargs.customDeltaBC
                logging.debug(" - [%s] %s : %s",key,value,extrargs.customDeltaBC)  
             
            # multiplicity-table
            if value == "doVertexZeq" and extrargs.isVertexZeq:
                if extrargs.isVertexZeq == "true":
                    config[key][value] = "1"
                    config[key]["doDummyZeq"] = "0"
                    logging.debug(" - %s %s : 1",key,value)
                    logging.debug(" - [%s] doDummyZeq : 0",key)  
                if extrargs.isVertexZeq == "false":
                    config[key][value] = "0"
                    config[key]["doDummyZeq"] = "1"
                    logging.debug(" - %s %s : 0",key,value) 
                    logging.debug(" - [%s] doDummyZeq : 1",key)
                    
            # tof-pid, tof-pid-full
            if value == "processWSlice" and extrargs.isWSlice:
                if extrargs.isWSlice == "true":
                    config[key][value] = "true"
                    config[key]["processWoSlice"] = "false"
                    logging.debug(" - %s %s : true",key,value)
                    logging.debug(" - [%s] processWoSlice : false",key)  
                if extrargs.isWSlice == "false":
                    config[key][value] = "false"
                    config[key]["processWoSlice"] = "true"
                    logging.debug(" - %s %s : false",key,value) 
                    logging.debug(" - [%s] processWoSlice : true",key)
                                         
            # tof-pid-beta
            if value == "tof-expreso" and extrargs.tof_expreso:
                config[key][value] = extrargs.tof_expreso
                logging.debug(" - [%s] %s : %s",key,value,extrargs.tof_expreso)
                
            # tof-event-time
            if  (value in ft0Parameters) and extrargs.FT0 and key == "tof-event-time":
                if value  == extrargs.FT0:
                    value2 = "true"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s",key,value,value2)  
                elif value != extrargs.FT0:
                    value2 = "false"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s",key,value,value2)  
                                             
            # all d-q tasks and selections
            if (value == "cfgWithQA" or value == "cfgQA") and extrargs.cfgWithQA:
                config[key][value] = extrargs.cfgWithQA
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgWithQA)  
                                  
            # track-propagation
            if extrargs.isCovariance:
                if (value =="processStandard" or value == "processCovariance") and extrargs.isCovariance == "false" :
                    config[key]["processStandard"] = "true"
                    config[key]["processCovariance"] = "false"
                    logging.debug(" - [%s] processStandart : true",key)
                    logging.debug(" - [%s] processCovariance : false",key) 
                if (value =="processStandard" or value == "processCovariance") and extrargs.isCovariance == "true" :
                    config[key]["processStandard"] = "false"
                    config[key]["processCovariance"] = "true"
                    logging.debug(" - [%s] processStandart : false",key)
                    logging.debug(" - [%s] processCovariance : true",key) 
                                    
            # dummy automizer
            if value == "processDummy" and extrargs.autoDummy and extrargs.runData:
                
                if config["d-q-barrel-track-selection-task"]["processSelection"] == "true" or config["d-q-barrel-track-selection-task"]["processSelectionTiny"] == "true":
                    config["d-q-barrel-track-selection-task"]["processDummy"] = "false"
                    #logging.debug("d-q-barrel-track-selection-task:processDummy:false") 
                if config["d-q-barrel-track-selection-task"]["processSelection"] == "false" and config["d-q-barrel-track-selection-task"]["processSelectionTiny"]  == "false":
                    config["d-q-barrel-track-selection-task"]["processDummy"] = "true"
                    #logging.debug("d-q-barrel-track-selection-task:processDummy:true") 
                    
                if config["d-q-muons-selection"]["processSelection"] == "true":
                    config["d-q-muons-selection"]["processDummy"] = "false"
                    #logging.debug("d-q-muons-selection:processDummy:false") 
                if config["d-q-muons-selection"]["processSelection"] == "false":
                    config["d-q-muons-selection"]["processDummy"] = "true"
                    #logging.debug("d-q-muons-selection:processDummy:true") 
                    
                if config["d-q-event-selection-task"]["processEventSelection"] == "true":
                    config["d-q-event-selection-task"]["processDummy"] = "false"
                    #logging.debug("d-q-event-selection-task:processDummy:false") 
                if config["d-q-event-selection-task"]["processEventSelection"] == "false":
                    config["d-q-event-selection-task"]["processDummy"] = "true"
                    #logging.debug("d-q-event-selection-task:processDummy:true") 
                    
                if config["d-q-filter-p-p-task"]["processFilterPP"] =="true" or config["d-q-filter-p-p-task"]["processFilterPPTiny"] == "true":
                    config["d-q-filter-p-p-task"]["processDummy"] = "false"
                    #logging.debug("d-q-filter-p-p-task:processDummy:false")
                if config["d-q-filter-p-p-task"]["processFilterPP"] == "false" and config["d-q-filter-p-p-task"]["processFilterPPTiny"] == "false" :
                    config["d-q-filter-p-p-task"]["processDummy"] = "true"
                    #logging.debug("d-q-filter-p-p-task:processDummy:true")
                    
                if config["analysis-qvector"]["processBarrelQvector"] == "true":
                    config["analysis-qvector"]["processDummy"] = "false" 
                if config["analysis-qvector"]["processBarrelQvector"] == "false":
                    config["analysis-qvector"]["processDummy"] = "true"             
                    
# LOGGER MESSAGES FOR DQ SELECTIONS

if extrargs.runData and extrargs.process:

    if isDQFullSelected:
        logging.debug(" - [d-q-event-selection-task] processEventSelection : true")
        
        if isDQBarrelSelected:
            logging.debug(" - [d-q-barrel-track-selection-task] processSelection : true")
            logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : false")
        if isDQBarrelTinySelected:
            logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : true")
            logging.debug(" - [d-q-barrel-track-selection-task] processSelection : false")
            
        logging.debug(" - [d-q-muons-selection] processSelection : true")

    if isDQEventSelected and (not isDQFullSelected):
        logging.debug(" - [d-q-event-selection-task] processEventSelection : true") 
    if (not isDQEventSelected) and (not isDQFullSelected):
        logging.debug(" - [d-q-event-selection-task] processEventSelection : false")                        
    if isDQBarrelSelected and (not isDQFullSelected):           
        logging.debug(" - [d-q-barrel-track-selection-task] processSelection : true")
    if (not isDQBarrelSelected) and (not isDQFullSelected):           
        logging.debug(" - [d-q-barrel-track-selection-task] processSelection : false")                 
    if isDQBarrelTinySelected and (not isDQFullSelected):
        logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : true")
    if (not isDQBarrelTinySelected) and (not isDQFullSelected):
        logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : false")                    
    if isDQMuonSelected and (not isDQFullSelected):
        logging.debug(" - [d-q-muons-selection] processSelection : true")
    if (not isDQMuonSelected) and (not isDQFullSelected):
        logging.debug(" - [d-q-muons-selection] processSelection : false")         
    if isFilterPPSelected:
        logging.debug(" - [d-q-filter-p-p-task-task] processFilterPP : true")
    if not isFilterPPSelected:
        logging.debug(" - [d-q-filter-p-p-task-task] processFilterPP : false")                  
    if isFilterPPTinySelected:
        logging.debug(" - [d-q-filter-p-p-task-task] processFilterPPTiny : true")
    if not isFilterPPTinySelected:
        logging.debug(" - [d-q-filter-p-p-task-task] processFilterPPTiny : false")
    if isQVectorSelected:
        logging.debug(" - [analysis-qvector] processBarrelQvector : true") 
    if not isQVectorSelected:
        logging.debug(" - [analysis-qvector] processBarrelQvector : false") 
                                                  
# Centrality table delete for pp processes
if extrargs.process and len(centSearch) != 0 and (extrargs.syst == "pp" or (extrargs.syst == None and config["event-selection-task"]["syst"] == "pp")):
    # delete centrality-table configurations for data. If it"s MC don't delete from JSON
    # Firstly try for Data then if not data it gives warning message for MC
    isNoDeleteNeedForCent = False
    try:
        logging.warning("JSON file does not include configs for centrality-table task, It's for DATA. Centrality will removed because you select pp collision system.")
        #del(config["centrality-table"])
    except:
        if extrargs.runMC:
            logging.warning("JSON file does not include configs for centrality-table task, It's for MC. Centrality will removed because you select pp collision system.")
    # check for is TableMaker includes task related to Centrality?
    try:
        processCentralityMatch = [s for s in extrargs.process if "Cent" in s]
        if len(processCentralityMatch) > 0:
            logging.warning("Collision System pp can't be include related task about Centrality. They Will be removed in automation. Check your JSON configuration file for Tablemaker process function!!!")
            for paramValueTableMaker in processCentralityMatch:
                # Centrality process should be false
                if extrargs.runMC:
                    try:       
                        config["table-maker-m-c"][paramValueTableMaker] = "false"
                    except:
                        logging.error("JSON config does not include table-maker-m-c, It's for Data. Misconfiguration JSON File!!!")
                        sys.exit()
                if extrargs.runData:
                    try:       
                        config["table-maker"][paramValueTableMaker] = "false"
                    except:
                        logging.error("JSON config does not include table-maker, It's for MC. Misconfiguration JSON File!!!")
                        sys.exit()
    except:
        logging.warning("No process function provided so no need delete related to centrality-table dependency")
         
    # After deleting centrality we need to check if we have process function
    isProcessFuncLeftAfterCentDelete = True
    leftProcessAfterDeleteCent =[] 
    if extrargs.runData:
        for deletedParamTableMaker in config["table-maker"]:
            if "process" not in deletedParamTableMaker: 
                continue
            elif config["table-maker"].get(deletedParamTableMaker) == "true":
                isProcessFuncLeftAfterCentDelete = True
                leftProcessAfterDeleteCent.append(deletedParamTableMaker)

# logging Message for Centrality
if not isNoDeleteNeedForCent: 
    logging.info("After deleting the process functions related to the centrality table (for collision system pp), the remaining processes: %s",leftProcessAfterDeleteCent)
 
if not (isProcessFuncLeftAfterCentDelete and isNoDeleteNeedForCent):
    logging.error("After deleting the process functions related to the centrality table, there are no functions left to process, misconfigure for process!!!")    
    sys.exit()    
    

# ================================================================    
# Transcation Management for barrelsels and muonsels in filterPP 
# ================================================================

for key,value in configuredCommands.items():
    if(value != None):
        if key == "cfgMuonsCuts":
            muonCutList.append(value)
        if key == "cfgBarrelTrackCuts":
            barrelTrackCutList.append(value)
        if key == "cfgBarrelSels":
            barrelSelsList.append(value)
        if key == "cfgMuonSels":
            muonSelsList.append(value)

##############################
# For MuonSels From FilterPP #
##############################
if extrargs.cfgMuonSels:
    
    # transcation management
    if extrargs.cfgMuonsCuts == None:
        logging.error("For configure to cfgMuonSels (For DQ Filter PP Task), you must also configure cfgMuonsCuts!!!")
        sys.exit()
        
    # Convert List Muon Cuts                     
    for muonCut in muonCutList:
        muonCut = stringToList(muonCut)

    # seperate string values to list with comma
    for muonSels in muonSelsList:
        muonSels = muonSels.split(",")    

    # remove string values after :
    for i in muonSels:
        i = i[ 0 : i.index(":")]
        muonSelsListAfterSplit.append(i)

    # Remove duplicated values with set convertion
    muonSelsListAfterSplit = set(muonSelsListAfterSplit)
    muonSelsListAfterSplit = list(muonSelsListAfterSplit)

    for i in muonSelsListAfterSplit:
        if i in muonCut:
            continue
        else:
            print("====================================================================================================================")
            logging.error("--cfgMuonSels <value>: %s not in --cfgMuonsCuts %s ",i, muonCut)
            logging.info("For fixing this issue, you should have the same number of cuts (and in the same order) provided to the cfgMuonsCuts from dq-selection as those provided to the cfgMuonSels in the DQFilterPPTask.") 
            logging.info("For example, if cfgMuonCuts is muonLowPt,muonHighPt, then the cfgMuonSels has to be something like: muonLowPt::1,muonHighPt::1,muonLowPt:pairNoCut:1")  
            sys.exit()
                            
    for i in muonCut:    
        if i in muonSelsListAfterSplit:
            continue
        else:
            print("====================================================================================================================")
            logging.error("--cfgMuonsCut <value>: %s not in --cfgMuonSels %s ",i,muonSelsListAfterSplit)
            logging.info("[INFO] For fixing this issue, you should have the same number of cuts (and in the same order) provided to the cfgMuonsCuts from dq-selection as those provided to the cfgMuonSels in the DQFilterPPTask.") 
            logging.info("For example, if cfgMuonCuts is muonLowPt,muonHighPt,muonLowPt then the cfgMuonSels has to be something like: muonLowPt::1,muonHighPt::1,muonLowPt:pairNoCut:1")  
            sys.exit()
            
################################
# For BarrelSels from FilterPP # 
################################
if extrargs.cfgBarrelSels:
    
    # transcation management
    if extrargs.cfgBarrelTrackCuts == None:
        logging.error("For configure to cfgBarrelSels (For DQ Filter PP Task), you must also configure cfgBarrelTrackCuts!!!")
        sys.exit()
         
    # Convert List Barrel Track Cuts                     
    for barrelTrackCut in barrelTrackCutList:
        barrelTrackCut = stringToList(barrelTrackCut)

    # seperate string values to list with comma
    for barrelSels in barrelSelsList:
        barrelSels = barrelSels.split(",")   

    # remove string values after :
    for i in barrelSels:
        i = i[ 0 : i.index(":")]
        barrelSelsListAfterSplit.append(i)

    # Remove duplicated values with set convertion
    barrelSelsListAfterSplit = set(barrelSelsListAfterSplit)
    barrelSelsListAfterSplit = list(barrelSelsListAfterSplit)

    for i in barrelSelsListAfterSplit:
        if i in barrelTrackCut:
            continue
        else:
            print("====================================================================================================================")
            logging.error("--cfgBarrelTrackCuts <value>: %s not in --cfgBarrelSels %s",i,barrelTrackCut)
            logging.info("For fixing this issue, you should have the same number of cuts (and in the same order) provided to the cfgBarrelTrackCuts from dq-selection as those provided to the cfgBarrelSels in the DQFilterPPTask.")  
            logging.info("For example, if cfgBarrelTrackCuts is jpsiO2MCdebugCuts,jpsiO2MCdebugCuts2,jpsiO2MCdebugCuts then the cfgBarrelSels has to be something like: jpsiO2MCdebugCuts::1,jpsiO2MCdebugCuts2::1,jpsiO2MCdebugCuts:pairNoCut:1") 
            sys.exit()
                            
    for i in barrelTrackCut:    
        if i in barrelSelsListAfterSplit:
            continue
        else:
            print("====================================================================================================================")
            logging.error("--cfgBarrelTrackCuts <value>: %s not in --cfgBarrelSels %s",i,barrelSelsListAfterSplit)
            logging.info("For fixing this issue, you should have the same number of cuts (and in the same order) provided to the cfgBarrelTrackCuts from dq-selection as those provided to the cfgBarrelSels in the DQFilterPPTask.") 
            logging.info("For example, if cfgBarrelTrackCuts is jpsiO2MCdebugCuts,jpsiO2MCdebugCuts2,jpsiO2MCdebugCuts then the cfgBarrelSels has to be something like: jpsiO2MCdebugCuts::1,jpsiO2MCdebugCuts2::1,jpsiO2MCdebugCuts:pairNoCut:1")      
            sys.exit()
            

            
# AOD File Checker 
if extrargs.aod != None:
    argProvidedAod =  extrargs.aod
    textAodList = argProvidedAod.startswith("@")
    endsWithRoot = argProvidedAod.endswith(".root")
    endsWithTxt = argProvidedAod.endswith("txt") or argProvidedAod.endswith("text") 
    if textAodList and endsWithTxt:
        argProvidedAod = argProvidedAod.replace("@","")
        logging.info("You provided AO2D list as text file : %s",argProvidedAod)
        if not os.path.isfile(argProvidedAod):
            logging.error("%s File not found in path!!!", argProvidedAod)
            sys.exit()
        else:
            logging.info("%s has valid File Format and Path, File Found", argProvidedAod)
         
    elif endsWithRoot:
        logging.info("You provided single AO2D as root file  : %s",argProvidedAod)
        if not os.path.isfile(argProvidedAod):
            logging.error("%s File not found in path!!!", argProvidedAod)
            sys.exit()
        else:
            logging.info("%s has valid File Format and Path, File Found", argProvidedAod)                
    else:
        logging.error("%s Wrong formatted File, check your file!!!", argProvidedAod)
        sys.exit()    
        
 
        
#####################
# Deps Transcations #
#####################

# In extended tracks, o2-analysis-trackextension is not a valid dep for run 3
# More Information : https://aliceo2group.github.io/analysis-framework/docs/helperTasks/trackselection.html?highlight=some%20of%20the%20track%20parameters
"""
Some of the track parameters used in the track selection require additional calculation effort and are then stored in a table called TracksExtended 
which is produced by either the o2-analysis-trackextension task (Run 2) or o2-analysis-track-propagation (Run 3). 
The quantities contained in this table can also be directly used in the analysis.
"""
if config["bc-selection-task"]["processRun3"] == "true":
    barrelDeps.remove("o2-analysis-trackextension")
    logging.info("o2-analysis-trackextension is not valid dep for run 3, It will deleted from your workflow.")

                 
###########################
# End Interface Processes #
###########################

# Write the updated configuration file into a temporary file
updatedConfigFileName = "tempConfigTableMaker.json"
    
with open(updatedConfigFileName,"w") as outputFile:
  json.dump(config, outputFile ,indent=2)

# Check which dependencies need to be run  
depsToRun = {}
for dep in commonDeps:
  depsToRun[dep] = 1

for processFunc in specificDeps.keys():
  if not processFunc in config[taskNameInConfig].keys():
    continue        
  if config[taskNameInConfig][processFunc] == "true":      
    if "processFull" in processFunc or "processBarrel" in processFunc:
      for dep in barrelDeps:
        depsToRun[dep] = 1
    for dep in specificDeps[processFunc]:
      depsToRun[dep] = 1

# Check which tables are required in the output
tablesToProduce = {}
for table in commonTables:
  tablesToProduce[table] = 1

if runOverMC:
  tablesToProduce["ReducedMCEvents"] = 1
  tablesToProduce["ReducedMCEventLabels"] = 1
  
for processFunc in specificDeps.keys():
  if not processFunc in config[taskNameInConfig].keys():
    continue          
  if config[taskNameInConfig][processFunc] == "true":
    logging.info("processFunc ========")
    logging.info("%s", processFunc)
    if "processFull" in processFunc or "processBarrel" in processFunc:
      logging.info("common barrel tables==========")      
      for table in barrelCommonTables:
        logging.info("%s", table)      
        tablesToProduce[table] = 1
      if runOverMC:
        tablesToProduce["ReducedTracksBarrelLabels"] = 1
    if "processFull" in processFunc or "processMuon" in processFunc:
      logging.info("common muon tables==========")      
      for table in muonCommonTables:
        logging.info("%s", table)
        tablesToProduce[table] = 1
      if runOverMC:
        tablesToProduce["ReducedMuonsLabels"] = 1  
    if runOverMC:
      tablesToProduce["ReducedMCTracks"] = 1
    logging.info("specific tables==========")      
    for table in specificTables[processFunc]:
      logging.info("%s", table)      
      tablesToProduce[table] = 1

# Generate the aod-writer output descriptor json file
writerConfig = {}
writerConfig["OutputDirector"] = {
  "debugmode": True,
  "resfile": "reducedAod",
  "resfilemode": "RECREATE",
  "ntfmerge": 1,
  "OutputDescriptors": []
}

# Generate the aod-reader output descriptor json file
readerConfig = {}
readerConfig["InputDirector"] = {
    "debugmode": True,
    "InputDescriptors": []
}

iTable = 0
for table in tablesToProduce.keys():
  writerConfig["OutputDirector"]["OutputDescriptors"].insert(iTable, tables[table])
  readerConfig["InputDirector"]["InputDescriptors"].insert(iTable, tables[table])
  iTable += 1
  
writerConfigFileName = "aodWriterTempConfig.json"
with open(writerConfigFileName,"w") as writerConfigFile:
  json.dump(writerConfig, writerConfigFile, indent=2)
  
  
readerConfigFileName = "aodReaderTempConfig.json"
with open(readerConfigFileName,"w") as readerConfigFile:
  json.dump(readerConfig, readerConfigFile, indent=2)
  
logging.info("aodWriterTempConfig==========")  
print(writerConfig)
#sys.exit()
logging.info("aodReaderTempConfig==========")  
print(readerConfig)
      
commandToRun = taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " --severity error --shm-segment-size 12000000000 --aod-writer-json " + writerConfigFileName + " -b"
if extrargs.aod_memory_rate_limit:
    commandToRun = taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " --severity error --shm-segment-size 12000000000 --aod-memory-rate-limit " + extrargs.aod_memory_rate_limit + " --aod-writer-json " + writerConfigFileName + " -b"
    
for dep in depsToRun.keys():
  commandToRun += " | " + dep + " --configuration json://" + updatedConfigFileName + " -b"
  logging.debug("%s added your workflow",dep)

if extrargs.add_mc_conv:
    logging.debug("o2-analysis-mc-converter added your workflow")
    commandToRun += " | o2-analysis-mc-converter --configuration json://" + updatedConfigFileName + " -b"

if extrargs.add_fdd_conv:
    commandToRun += " | o2-analysis-fdd-converter --configuration json://" + updatedConfigFileName + " -b"
    logging.debug("o2-analysis-fdd-converter added your workflow")

if extrargs.add_track_prop:
    commandToRun += " | o2-analysis-track-propagation --configuration json://" + updatedConfigFileName + " -b"
    logging.debug("o2-analysis-track-propagation added your workflow")

print("====================================================================================================================")
logging.info("Command to run:")
logging.info(commandToRun)
print("====================================================================================================================")
logging.info("Tables to produce:")
logging.info(tablesToProduce.keys())
print("====================================================================================================================")
#sys.exit()

# Listing Added Commands
logging.info("Args provided configurations List")
print("====================================================================================================================")
for key,value in configuredCommands.items():
    if(value != None):
        if type(value) == type(clist):
            listToString(value)
        logging.info("--%s : %s ",key,value)

os.system(commandToRun)

# Pycache remove after running in O2
getParrentDir = sys.path[-1]

# trying to insert to false directory
try:
    os.chdir(getParrentDir)
    logging.info("Inserting inside for pycache remove: %s", os.getcwd())

# Caching the exception   
except:
    logging.error("Something wrong with specified\
          directory. Exception- %s", sys.exc_info())

pycacheRemover = PycacheRemover()
pycacheRemover.__init__()

logging.info("pycaches removed succesfully")