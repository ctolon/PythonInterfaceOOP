#!/usr/bin/env python3
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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqFlow.cxx

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

from commondeps.eventSelection import EventSelectionTask
from commondeps.multiplicityTable import MultiplicityTable
from commondeps.pidTOFBase import TofEventTime
from commondeps.pidTOFBeta import TofPidBeta
from commondeps.pidTPCTOFFull import TpcTofPidFull
from commondeps.trackPropagation import TrackPropagation

from dqtasks.filterPP import DQFilterPPTask

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

clist = []  # control list for type control
threeSelectedList = []

booleanSelections = ["true", "false"]

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

#################
# Init Workflow #
#################

class RunFilterPP(object):
    """
    This class is for managing the workflow by using the interface arguments from
    all other Common dependencies and the filterPP Task's own arguments in a combined structure.
    
    Args:
      object (parser_args() object): runFilterPP.py workflow
    """

    def __init__(self, 
                parserRunFilterPP=argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                description="Arguments to pass"), 
                filterPP=DQFilterPPTask(),
                eventSelection=EventSelectionTask(), 
                multiplicityTable=MultiplicityTable(),
                tofEventTime=TofEventTime(),
                tofPidBeta=TofPidBeta(),
                tpcTofPidFull=TpcTofPidFull(),
                trackPropagation=TrackPropagation(),
                debugOptions=DebugOptions()
                ):
        super(RunFilterPP, self).__init__()
        self.parserRunFilterPP = parserRunFilterPP
        self.filterPP = filterPP
        self.eventSelection = eventSelection
        self.multiplicityTable = multiplicityTable
        self.tofEventTime = tofEventTime
        self.tofPidBeta = tofPidBeta
        self.tpcTofPidFull = tpcTofPidFull
        self.trackPropagation = trackPropagation
        self.debugOptions = debugOptions
        self.parserRunFilterPP.register("action", "none", NoAction)
        self.parserRunFilterPP.register("action", "store_choice", ChoicesAction)
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Core Part
        groupCoreSelections = self.parserRunFilterPP.add_argument_group(title="Core configurations that must be configured")
        groupCoreSelections.add_argument("cfgFileName", metavar="Config.json", default="config.json", help="config JSON file name")
        groupTaskAdders = self.parserRunFilterPP.add_argument_group(title="Additional Task Adding Options")
        groupTaskAdders.add_argument("--add_mc_conv", help="Add the converter from mcparticle to mcparticle+001 (Adds your workflow o2-analysis-mc-converter task)", action="store_true")
        groupTaskAdders.add_argument("--add_fdd_conv", help="Add the fdd converter (Adds your workflow o2-analysis-fdd-converter task)", action="store_true")
        groupTaskAdders.add_argument("--add_track_prop", help="Add track propagation to the innermost layer (TPC or ITS) (Adds your workflow o2-analysis-track-propagation task)", action="store_true")
                        
        # aod
        groupDPLReader = self.parserRunFilterPP.add_argument_group(title="Data processor options: internal-dpl-aod-reader")
        groupDPLReader.add_argument("--aod", help="Add your AOD File with path", action="store", type=str)

        # automation params
        groupAutomations = self.parserRunFilterPP.add_argument_group(title="Automation Parameters")
        groupAutomations.add_argument("--onlySelect", help="If false JSON Overrider Interface If true JSON Additional Interface", action="store", default="true", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)
        groupAutomations.add_argument("--autoDummy", help="Dummy automize parameter (don't configure it, true is highly recomended for automation)", action="store", default="true", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)
        
        # helper lister commands
        #groupAdditionalHelperCommands = self.parserRunFilterPP.add_argument_group(title="Additional Helper Command Options")
        #groupAdditionalHelperCommands.add_argument("--cutLister", help="List all of the analysis cuts from CutsLibrary.h", action="store_true")
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
 
        argcomplete.autocomplete(self.parserRunFilterPP, always_complete_options=False)  
        return self.parserRunFilterPP.parse_args()

    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """
        
        self.eventSelection.parserEventSelectionTask = self.parserRunFilterPP
        self.eventSelection.addArguments()
                
        self.multiplicityTable.parserMultiplicityTable = self.parserRunFilterPP
        self.multiplicityTable.addArguments()
        
        self.tofEventTime.parserTofEventTime = self.parserRunFilterPP
        self.tofEventTime.addArguments()
        
        self.tofPidBeta.parserTofPidBeta = self.parserRunFilterPP
        self.tofPidBeta.addArguments()
        
        self.tpcTofPidFull.parserTpcTofPidFull = self.parserRunFilterPP
        self.tpcTofPidFull.addArguments()
        
        self.trackPropagation.parserTrackPropagation = self.parserRunFilterPP
        self.trackPropagation.addArguments()
                
        self.debugOptions.parserDebugOptions = self.parserRunFilterPP
        self.debugOptions.addArguments()
        
        self.filterPP.parserDQFilterPPTask = self.parserRunFilterPP
        self.filterPP.addArguments()
                
        self.addArguments()
        
    # This function not work should be integrated instead of mergeArgs
    """  
    def mergeMultiArgs(self, *objects):
        parser = self.parserRunFilterPP
        for object in objects:
            object.parser = parser
            object.addArguments()
        self.addArguments()
    """

# init args manually     
initArgs = RunFilterPP()
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
    logging.error("Your forget assign a value to for this parameters: %s", forgetParams)
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
    
    loggerFile = "filterPP.log"
    if os.path.isfile(loggerFile):
        os.remove(loggerFile)
    
    fh = handlers.RotatingFileHandler(loggerFile, maxBytes=(1048576*5), backupCount=7, mode="w")
    fh.setFormatter(format)
    log.addHandler(fh)

###################
# HELPER MESSAGES #
###################

"""
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
"""

######################
# PREFIX ADDING PART #
###################### 

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
    "o2-analysis-multiplicity-table",
    "o2-analysis-trackselection",
    "o2-analysis-trackextension",
    "o2-analysis-pid-tof-base",
    "o2-analysis-pid-tof",
    "o2-analysis-pid-tof-full",
    "o2-analysis-pid-tof-beta",
    "o2-analysis-pid-tpc-full"
]

# Make some checks on provided arguments
if len(sys.argv) < 2:
  logging.error("Invalid syntax! The command line should look like this:")
  logging.info("  ./runFilterPP.py <yourConfig.json> --param value ...")
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
        logging.info("  ./runFilterPP.py<yourConfig.json> <-runData|-runMC> --param value ...")
        sys.exit()
        
except FileNotFoundError:
    isConfigJson = sys.argv[1].endswith(".json")
    if not isConfigJson:
            logging.error("Invalid syntax! After the script you must define your json configuration file!!! The command line should look like this:")
            logging.info(" ./runFilterPP.py <yourConfig.json> --param value ...")
            sys.exit()
    logging.error("Your JSON Config File found in path!!!")
    sys.exit()

taskNameInConfig = "d-q-filter-p-p-task"
taskNameInCommandLine = "o2-analysis-dq-filter-pp"

if not taskNameInConfig in config:
  logging.error("%s Task to be run not found in the configuration file!", taskNameInConfig)
  sys.exit()
  
# Check alienv
if O2PHYSICS_ROOT == None:
   logging.error("You must load O2Physics with alienv")
   sys.exit()
  
#############################
# Start Interface Processes #
#############################

logging.info("Only Select Configured as %s", extrargs.onlySelect)
if extrargs.onlySelect == "true":
    logging.info("INTERFACE MODE : JSON Overrider")
if extrargs.onlySelect == "false":
    logging.info("INTERFACE MODE : JSON Additional")

for key, value in config.items():
    if type(value) == type(config):
        for value, value2 in value.items():
                       
            # aod
            if value =="aod-file" and extrargs.aod:
                config[key][value] = extrargs.aod
                logging.debug(" - [%s] %s : %s",key,value,extrargs.aod)
                
            # DQ Selections for muons and barrel tracks
            if value =="processSelection" and extrargs.process:
                for keyCfg,valueCfg in configuredCommands.items():
                    if(valueCfg != None): # Cleaning None types, because can"t iterate in None type
                        if keyCfg == "process": #  Only Select key for analysis
                                      
                            if key == "d-q-barrel-track-selection":                    
                                if "barrelTrackSelection" in valueCfg:
                                    config[key][value] = "true"
                                    logging.debug(" - [%s] %s : true",key,value)
                                if "barrelTrackSelection" not in valueCfg and extrargs.onlySelect == "true":
                                    config[key][value] = "false"
                                    logging.debug(" - [%s] %s : false",key,value)
                                                      
                            if key == "d-q-muons-selection":
                                if "muonSelection" in valueCfg:
                                    config[key][value] = "true"
                                    logging.debug(" - [%s] %s : true",key,value)
                                if "muonSelection" not in valueCfg and extrargs.onlySelect == "true":
                                    config[key][value] = "false"
                                    logging.debug(" - [%s] %s : false",key,value)
                                                                                               
            # DQ Selections event    
            if value =="processEventSelection" and extrargs.process:
                for keyCfg,valueCfg in configuredCommands.items():
                    if(valueCfg != None): # Cleaning None types, because can"t iterate in None type
                        if keyCfg == "process": #  Only Select key for analysis
                            
                            if key == "d-q-event-selection-task":
                                if "eventSelection" in valueCfg:
                                    config[key][value] = "true"
                                    logging.debug(" - [%s] %s : true",key,value)
                                if "eventSelection" not in valueCfg:
                                    logging.warning("YOU MUST ALWAYS CONFIGURE eventSelection value in --process parameter!! It is Missing and this issue will fixed by CLI")
                                    config[key][value] = "true" 
                                    logging.debug(" - [%s] %s : true",key,value)
                                    
            # DQ Tiny Selection for barrel track
            if value =="processSelectionTiny" and extrargs.process:
                for keyCfg,valueCfg in configuredCommands.items():
                    if(valueCfg != None): # Cleaning None types, because can"t iterate in None type
                        if keyCfg == "process": #  Only Select key for analysis
                                      
                            if key == "d-q-barrel-track-selection":                    
                                if "barrelTrackSelectionTiny" in valueCfg:
                                    config[key][value] = "true"
                                    logging.debug(" - [%s] %s : true",key,value)
                                if "barrelTrackSelectionTiny" not in valueCfg and extrargs.onlySelect == "true":
                                    config[key][value] = "false"
                                    logging.debug(" - [%s] %s : false",key,value)
            
            # DQ Tiny Selection for filterPP
            if value =="processFilterPPTiny" and extrargs.process:
                for keyCfg,valueCfg in configuredCommands.items():
                    if(valueCfg != None): # Cleaning None types, because can"t iterate in None type
                        if keyCfg == "process": #  Only Select key for analysis
                                      
                            if key == "d-q-filter-p-p-task":                    
                                if "filterPPSelectionTiny" in valueCfg:
                                    config[key][value] = "true"
                                    config[key]["processFilterPP"] = "false"
                                    logging.debug(" - [%s] %s : true",key,value)
                                    logging.debug(" - [%s] processFilterPP : false",key)
                                if "filterPPSelectionTiny" not in valueCfg and extrargs.onlySelect == "true":
                                    config[key][value] = "false"
                                    config[key]["processFilterPP"] = "true"
                                    logging.debug(" - [%s] %s : false",key,value)
                                    logging.debug(" - [%s] processFilterPP : true",key)
                                                                                                          
            # Filter PP Selections        
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
                
            # DQ Cuts    
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
            if value =="cfgMuonsCuts" and extrargs.cfgMuonsCuts:
                if type(extrargs.cfgMuonsCuts) == type(clist):
                    extrargs.cfgMuonsCuts = listToString(extrargs.cfgMuonsCuts)
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgMuonsCuts = actualConfig + "," + extrargs.cfgMuonsCuts                  
                config[key][value] = extrargs.cfgMuonsCuts
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgMuonsCuts) 
            
            # QA Options  
            if value == "cfgWithQA" and extrargs.cfgWithQA:
                config[key][value] = extrargs.cfgWithQA
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgWithQA)  
                  
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
            
            # event-selection
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
                                                    
                                                  
            if value == "processDummy" and extrargs.autoDummy:            
                if config["d-q-barrel-track-selection"]["processSelection"] == "true":
                    config["d-q-barrel-track-selection"]["processDummy"] = "false"
                if config["d-q-barrel-track-selection"]["processSelection"] == "false":
                    config["d-q-barrel-track-selection"]["processDummy"] = "true"
                    
                if config["d-q-muons-selection"]["processSelection"] == "true":
                    config["d-q-muons-selection"]["processDummy"] = "false"
                if config["d-q-muons-selection"]["processSelection"] == "false":
                    config["d-q-muons-selection"]["processDummy"] = "true"
                    
                if config["d-q-event-selection-task"]["processEventSelection"] == "true":
                    config["d-q-event-selection-task"]["processDummy"] = "false"
                if config["d-q-event-selection-task"]["processEventSelection"] == "false":
                    config["d-q-event-selection-task"]["processDummy"] = "true"
                    
                if config["d-q-filter-p-p-task"]["processFilterPP"] =="true":
                    config["d-q-filter-p-p-task"]["processDummy"] = "false"
                if config["d-q-filter-p-p-task"]["processFilterPP"] == "false":
                    config["d-q-filter-p-p-task"]["processDummy"] = "true"
                

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
#if config["bc-selection-task"]["processRun3"] == "true":
    #commonDeps.remove("o2-analysis-trackextension")     
    #logging.info("o2-analysis-trackextension is not valid dep for run 3, It will deleted from your workflow.")
        
###########################
# End Interface Processes #
###########################

# Write the updated configuration file into a temporary file
updatedConfigFileName = "tempConfigFilterPP.json"

with open(updatedConfigFileName,"w") as outputFile:
  json.dump(config, outputFile ,indent=2)

# Check which dependencies need to be run
depsToRun = {}
for dep in commonDeps:
  depsToRun[dep] = 1
      
commandToRun = taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " --severity error --shm-segment-size 12000000000 -b"
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
#getParrentDir = sys.path[-1]

# trying to insert to false directory
try:
    #os.chdir(getParrentDir)
    logging.info("Inserting inside for pycache remove: %s", os.getcwd())

# Caching the exception   
except:
    logging.error("Something wrong with specified\
          directory. Exception- %s", sys.exc_info())

pycacheRemover = PycacheRemover()
pycacheRemover.__init__()

logging.info("pycaches removed succesfully")