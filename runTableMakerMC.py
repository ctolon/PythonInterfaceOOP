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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMakerMC.cxx

import json
import sys
import logging
import logging.config
from logging import handlers
import os
import argparse

from ExtraModules.ActionHandler import NoAction
from ExtraModules.ActionHandler import ChoicesAction
from ExtraModules.DebugOptions import DebugOptions
from ExtraModules.StringOperations import listToString

from CommonDeps.eventSelection import EventSelectionTask
from CommonDeps.multiplicityTable import MultiplicityTable
from CommonDeps.pidTOFBase import tofEventTime
from CommonDeps.pidTOFbeta import tofPidbeta
from CommonDeps.pidTPCTOFFull import tpcTofPidFull
from CommonDeps.trackPropagation import TrackPropagation

from dqTasks.tableMakerMC import TableMakerMC

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

class runTableMaker(object):
    """
    This class is for managing the workflow by using the interface arguments from
    all other Common dependencies and the tableMakerMC Task's own arguments in a combined structure.
    
    Args:
      object (parser_args() object): runTableMakerMC.py workflow
    """

    def __init__(self, 
                parserRunTableMaker=argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                description="Arguments to pass"), 
                eventSelection=EventSelectionTask(), 
                multiplicityTable=MultiplicityTable(),
                tofEventTime=tofEventTime(),
                tofPidBeta =tofPidbeta(),
                tpcTofPidFull=tpcTofPidFull(),
                trackPropagation=TrackPropagation(),
                tableMakerMC=TableMakerMC(),
                debugOptions=DebugOptions()
                ):
        super(runTableMaker, self).__init__()
        self.parserRunTableMaker = parserRunTableMaker
        self.eventSelection = eventSelection
        self.multiplicityTable = multiplicityTable
        self.tofEventTime = tofEventTime
        self.tofPidBeta = tofPidBeta
        self.tpcTofPidFull = tpcTofPidFull
        self.trackPropagation = trackPropagation
        self.tableMakerMC = tableMakerMC
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
        groupCoreSelections.add_argument("-runMC", help="Run over MC", action="store_true", default=True)
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
        #groupAdditionalHelperCommands.add_argument("--MCSignalsLister", help="List all of the MCSignals from MCSignalLibrary.h", action="store_true")
    

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
        
        self.multiplicityTable.parserMultiplicityTable = self.parserRunTableMaker
        self.multiplicityTable.addArguments()
        
        self.tofEventTime.parsertofEventTime = self.parserRunTableMaker
        self.tofEventTime.addArguments()
        
        self.tofPidBeta.parsertofPidbeta = self.parserRunTableMaker
        self.tofPidBeta.addArguments()
        
        self.tpcTofPidFull.parsertpcTofPidFull = self.parserRunTableMaker
        self.tpcTofPidFull.addArguments()
        
        self.trackPropagation.parserTrackPropagation = self.parserRunTableMaker
        self.trackPropagation.addArguments()
        
        self.tableMakerMC.parserTableMakerMC = self.parserRunTableMaker
        self.tableMakerMC.addArguments()
        
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
initArgs = runTableMaker()
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
    
    loggerFile = "tableMakerMC.log"
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
  logging.info("  ./runTableMakerMC.py <yourConfig.json> <-runData|-runMC> --param value ...")
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
        logging.info("  ./runTableMakerMC.py <yourConfig.json> <-runData|-runMC> --param value ...")
        sys.exit()
        
except FileNotFoundError:
    isConfigJson = sys.argv[1].endswith(".json")
    if not isConfigJson:
            logging.error("Invalid syntax! After the script you must define your json configuration file!!! The command line should look like this:")
            logging.info("  ./runTableMakerMC.py <yourConfig.json> <-runData|-runMC> --param value ...")
            sys.exit()
    logging.error("Your JSON Config File found in path!!!")
    sys.exit()
    
runOverMC = True
if (extrargs.runMC):
    runOverMC = True
    logging.info("runOverMC : %s, Reduced Tables will be produced for MC",runOverMC)
    


taskNameInConfig = "table-maker-m-c"
taskNameInCommandLine = "o2-analysis-dq-table-maker-mc"
  
# Check tablemaker-m-c dependencies
if extrargs.runMC:
    try:
        if config["table-maker-m-c"]:
            logging.info("tablemaker-m-c is in your JSON Config File")
    except:
        logging.error("JSON config does not include table-maker-m-c, It's for Data. Misconfiguration JSON File!!!")
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
                    
                    # check extrargs is contain Cov for transcation management --> add track prop task      
                    covSearch = [s for s in extrargs.process if "Cov" in s]
                    
                    # check extrargs is contain Cent for transcation management Centrality Filter
                    centSearch = [s for s in extrargs.process if "Cent" in s]
                                          
                elif extrargs.onlySelect == "true":
                    if value == "processOnlyBCs":
                        config[key][value] = "true"
                        logging.debug(" - [%s] %s : true",key,value)                     
                    else:
                        value2 = "false"
                        config[key][value] = value2
                        logging.debug(" - [%s] %s : %s",key,value,value2)
                                                                                                                
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
            if value == "cfgMCsignals" and extrargs.cfgMCsignals:
                if type(extrargs.cfgMCsignals) == type(clist):
                    extrargs.cfgMCsignals = listToString(extrargs.cfgMCsignals)
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgMCsignals = actualConfig + "," + extrargs.cfgMCsignals                     
                config[key][value] = extrargs.cfgMCsignals
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgMCsignals)  
                
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

    if extrargs.runMC:
        for deletedParamTableMaker in config["table-maker-m-c"]:
            if "process" not in deletedParamTableMaker: 
                continue
            elif config["table-maker-m-c"].get(deletedParamTableMaker) == "true":
                isProcessFuncLeftAfterCentDelete = True
                leftProcessAfterDeleteCent.append(deletedParamTableMaker)

# logging Message for Centrality
if not isNoDeleteNeedForCent: 
    logging.info("After deleting the process functions related to the centrality table (for collision system pp), the remaining processes: %s",leftProcessAfterDeleteCent)
 
if not (isProcessFuncLeftAfterCentDelete and isNoDeleteNeedForCent):
    logging.error("After deleting the process functions related to the centrality table, there are no functions left to process, misconfigure for process!!!")    
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
updatedConfigFileName = "tempConfigTableMakerMC.json"
    
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