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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqEfficiency.cxx

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

from dqtasks.dqEfficiency import DQEfficiency

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

readerPath = "configs/readerConfiguration_reducedEventMC.json"
writerPath = "configs/writerConfiguration_dileptonMC.json"

booleanSelections = ["true", "false"]

isAnalysisEventSelected = True
isAnalysisTrackSelected = True
isAnalysisMuonSelected = True
isAnalysisSameEventPairingSelected = True

clist = []  # control list for type control

O2DPG_ROOT = os.environ.get("O2DPG_ROOT")
QUALITYCONTROL_ROOT = os.environ.get("QUALITYCONTROL_ROOT")
O2_ROOT = os.environ.get("O2_ROOT")
O2PHYSICS_ROOT = os.environ.get("O2PHYSICS_ROOT")

threeSelectedList = []

# List for Selected skimmed process functions for dummy automizer
skimmedListEventSelection = []
skimmedListTrackSelection = []
skimmedListMuonSelection = []
skimmedListSEP = []
skimmedListDileptonTrack = []

#################
# Init Workflow #
#################

class RunDQEffciency(object):
    """
    This class is for managing the workflow by using the interface arguments from
    all other Common dependencies and the dqEfficiency Task's own arguments in a combined structure.
    
    Args:
      object (parser_args() object): runDQEfficiency.py workflow
    """

    def __init__(self, 
                parserRunDQEfficiency=argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                description="Arguments to pass"), 
                dqEfficiency=DQEfficiency(),
                debugOptions=DebugOptions()
                ):
        super(RunDQEffciency, self).__init__()
        self.parserRunDQEfficiency = parserRunDQEfficiency
        self.dqEfficiency = dqEfficiency
        self.debugOptions = debugOptions
        self.parserRunDQEfficiency.register("action", "none", NoAction)
        self.parserRunDQEfficiency.register("action", "store_choice", ChoicesAction)
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Core Part
        groupCoreSelections = self.parserRunDQEfficiency.add_argument_group(title="Core configurations that must be configured")
        groupCoreSelections.add_argument("cfgFileName", metavar="Config.json", default="config.json", help="config JSON file name")
                        
        # aod
        groupDPLReader = self.parserRunDQEfficiency.add_argument_group(title="Data processor options: internal-dpl-aod-reader")
        groupDPLReader.add_argument("--aod", help="Add your AOD File with path", action="store", type=str)
        groupDPLReader.add_argument("--reader", help="Add your AOD Reader JSON with path", action="store", default=readerPath, type=str)
        groupDPLReader.add_argument("--writer", help="Add your AOD Writer JSON with path", action="store", default=writerPath, type=str)

        # automation params
        groupAutomations = self.parserRunDQEfficiency.add_argument_group(title="Automation Parameters")
        groupAutomations.add_argument("--onlySelect", help="If false JSON Overrider Interface If true JSON Additional Interface", action="store", default="true", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)
        groupAutomations.add_argument("--autoDummy", help="Dummy automize parameter (don't configure it, true is highly recomended for automation)", action="store", default="true", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)
        
        # helper lister commands
        #groupAdditionalHelperCommands = self.parserRunDQEfficiency.add_argument_group(title="Additional Helper Command Options")
        #groupAdditionalHelperCommands.add_argument("--cutLister", help="List all of the analysis cuts from CutsLibrary.h", action="store_true")
        #groupAdditionalHelperCommands.add_argument("--MCSignalsLister", help="List all of the MCSignals from MCSignalLibrary.h", action="store_true")
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
 
        argcomplete.autocomplete(self.parserRunDQEfficiency, always_complete_options=False)  
        return self.parserRunDQEfficiency.parse_args()

    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """
        
        self.debugOptions.parserDebugOptions = self.parserRunDQEfficiency
        self.debugOptions.addArguments()
        
        self.dqEfficiency.parserDQEfficiency = self.parserRunDQEfficiency
        self.dqEfficiency.addArguments()
                
        self.addArguments()
        
    # This function not work should be integrated instead of mergeArgs
    """  
    def mergeMultiArgs(self, *objects):
        parser = self.parserRunDQEfficiency
        for object in objects:
            object.parser = parser
            object.addArguments()
        self.addArguments()
    """

# init args manually    
initArgs = RunDQEffciency()
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
    logging.error("Your forget assign a value to for this parameters: ", forgetParams)
    sys.exit()
    
# Get Some cfg values provided from --param
for keyCfg,valueCfg in configuredCommands.items():
    if(valueCfg != None): # Skipped None types, because can"t iterate in None type
        if keyCfg == "analysis":
            if type(valueCfg) == type("string"):
                valueCfg = stringToList(valueCfg)
            analysisCfg = valueCfg
        if keyCfg == "process":
            if type(valueCfg) == type("string"):
                valueCfg = stringToList(valueCfg)
            processCfg = valueCfg

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
    
    loggerFile = "dqEfficiency.log"
    if os.path.isfile(loggerFile):
        os.remove(loggerFile)
    
    fh = handlers.RotatingFileHandler(loggerFile, maxBytes=(1048576*5), backupCount=7, mode="w")
    fh.setFormatter(format)
    log.addHandler(fh)
    
# Make some checks on provided arguments
if len(sys.argv) < 2:
  logging.error("Invalid syntax! The command line should look like this:")
  logging.info(" ./runDQEfficiency.py <yourConfig.json> --param value ...")
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
        logging.info("  ./runDQEfficiency.py <yourConfig.json> <-runData|-runMC> --param value ...")
        sys.exit()
        
except FileNotFoundError:
    isConfigJson = sys.argv[1].endswith(".json")
    if not isConfigJson:
            logging.error("Invalid syntax! After the script you must define your json configuration file!!! The command line should look like this:")
            logging.info(" ./runDQEfficiency.py <yourConfig.json> --param value ...")
            sys.exit()
    logging.error("Your JSON Config File found in path!!!")
    sys.exit()

taskNameInCommandLine = "o2-analysis-dq-efficiency"

# Check alienv
if O2PHYSICS_ROOT == None:
   logging.error("You must load O2Physics with alienv")
   sys.exit()

###################
# HELPER MESSAGES #
###################

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

            #aod
            if value =="aod-file" and extrargs.aod:
                config[key][value] = extrargs.aod
                logging.debug(" - [%s] %s : %s",key,value,extrargs.aod)
            # reader    
            if value =="aod-reader-json" and extrargs.reader:
                config[key][value] = extrargs.reader
                logging.debug(" - [%s] %s : %s",key,value,extrargs.reader)
                
            # analysis-skimmed-selections
            if value =="processSkimmed" and extrargs.analysis:
                            
                if key == "analysis-event-selection":
                    if "eventSelection" in analysisCfg:
                        config[key][value] = "true"
                        logging.debug(" - [%s] %s : true",key,value)
                        isAnalysisEventSelected = True
                    if "eventSelection" not in analysisCfg:
                        logging.warning("YOU MUST ALWAYS CONFIGURE eventSelection value in --analysis parameter!! It is Missing and this issue will fixed by CLI")
                        config[key][value] = "true" 
                        logging.debug(" - [%s] %s : true",key,value)
                        
                if key == "analysis-track-selection":                  
                    if "trackSelection" in analysisCfg:
                        config[key][value] = "true"
                        logging.debug(" - [%s] %s : true",key,value)
                        isAnalysisTrackSelected = True
                    if "trackSelection" not in analysisCfg and extrargs.onlySelect == "true":
                        config[key][value] = "false"
                        logging.debug(" - [%s] %s : false",key,value)
                                            
                if key == "analysis-muon-selection":
                    if "muonSelection" in analysisCfg:
                        config[key][value] = "true"
                        logging.debug(" - [%s] %s : true",key,value)
                        isAnalysisMuonSelected = True
                    if "muonSelection" not in analysisCfg and extrargs.onlySelect == "true":
                        config[key][value] = "false"
                        logging.debug(" - [%s] %s : false",key,value)   
                                                
                if "sameEventPairing" in analysisCfg:
                    isAnalysisSameEventPairingSelected = True
                if "sameEventPairing" not in analysisCfg:
                    isAnalysisSameEventPairingSelected = False
                                    
            if value =="processDimuonMuonSkimmed" and extrargs.analysis:

                if key == "analysis-dilepton-track":
                    if "dileptonTrackDimuonMuonSelection" in analysisCfg:
                        config[key][value] = "true"
                        logging.debug(" - [%s] %s : true",key,value)
                    if "dileptonTrackDimuonMuonSelection" not in analysisCfg and extrargs.onlySelect == "true":
                        config[key][value] = "false" 
                        logging.debug(" - [%s] %s : false",key,value)
                                    
            if value =="processDielectronKaonSkimmed" and extrargs.analysis:
                            
                if key == "analysis-dilepton-track":
                    if "dileptonTrackDielectronKaonSelection" in analysisCfg:
                        config[key][value] = "true"
                        logging.debug(" - [%s] %s : true",key,value)
                    if "dileptonTrackDielectronKaonSelection" not in analysisCfg and extrargs.onlySelect == "true":
                        config[key][value] = "false" 
                        logging.debug(" - [%s] %s : false",key,value)
                                                                           
            # QA selections  
            if value =="cfgQA" and extrargs.cfgQA:
                config[key][value] = extrargs.cfgQA
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgQA)
                              
            # analysis-event-selection
            if value == "cfgEventCuts" and extrargs.cfgEventCuts:
                if type(extrargs.cfgEventCuts) == type(clist):
                    extrargs.cfgEventCuts = listToString(extrargs.cfgEventCuts)
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgEventCuts = actualConfig + "," + extrargs.cfgEventCuts 
                config[key][value] = extrargs.cfgEventCuts
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgEventCuts)

            # analysis-track-selection
            if value == "cfgTrackCuts" and extrargs.cfgTrackCuts:
                if type(extrargs.cfgTrackCuts) == type(clist):
                    extrargs.cfgTrackCuts = listToString(extrargs.cfgTrackCuts) 
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgTrackCuts = actualConfig + "," + extrargs.cfgTrackCuts 
                config[key][value] = extrargs.cfgTrackCuts
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgTrackCuts)
            if value == "cfgTrackMCSignals" and extrargs.cfgTrackMCSignals:
                if type(extrargs.cfgTrackMCSignals) == type(clist):
                    extrargs.cfgTrackMCSignals = listToString(extrargs.cfgTrackMCSignals)
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgTrackMCSignals = actualConfig + "," + extrargs.cfgTrackMCSignals 
                config[key][value] = extrargs.cfgTrackMCSignals
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgTrackMCSignals)
                
            # analysis-muon-selection
            if value == "cfgMuonCuts" and extrargs.cfgMuonCuts:
                if type(extrargs.cfgMuonCuts) == type(clist):
                    extrargs.cfgMuonCuts = listToString(extrargs.cfgMuonCuts)  
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgMuonCuts = actualConfig + "," + extrargs.cfgMuonCuts               
                config[key][value] = extrargs.cfgMuonCuts
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgMuonCuts) 
            if value == "cfgMuonMCSignals" and extrargs.cfgMuonMCSignals:
                if type(extrargs.cfgMuonMCSignals) == type(clist):
                    extrargs.cfgMuonMCSignals = listToString(extrargs.cfgMuonMCSignals) 
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgMuonMCSignals = actualConfig + "," + extrargs.cfgMuonMCSignals 
                config[key][value] = extrargs.cfgMuonMCSignals
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgMuonMCSignals)
                
            # analysis-same-event-pairing
            if key == "analysis-same-event-pairing" and extrargs.process:

                if not isAnalysisSameEventPairingSelected:
                    logging.warning("You forget to add sameEventPairing option to analysis for Workflow. It Automatically added by CLI.")
                    isAnalysisSameEventPairingSelected = True
        
                if "JpsiToEE" in processCfg and value == "processJpsiToEESkimmed":
                    if isAnalysisTrackSelected:
                        config[key]["processJpsiToEESkimmed"] = "true"
                        logging.debug(" - [%s] %s : true",key,value)
                    if not isAnalysisTrackSelected:
                        logging.error("trackSelection not found in analysis for processJpsiToEESkimmed -> analysis-same-event-pairing")
                        sys.exit()
                if "JpsiToEE" not in processCfg and value == "processJpsiToEESkimmed" and extrargs.onlySelect == "true":
                        config[key]["processJpsiToEESkimmed"] = "false"
                        logging.debug(" - [%s] %s : false",key,value)
                        
                if "JpsiToMuMu" in processCfg and value == "processJpsiToMuMuSkimmed":
                    if isAnalysisMuonSelected:
                        config[key]["processJpsiToMuMuSkimmed"] = "true"
                        logging.debug(" - [%s] %s : true",key,value)
                    if not isAnalysisMuonSelected:
                        logging.error("muonSelection not found in analysis for processJpsiToMuMuSkimmed -> analysis-same-event-pairing")
                        sys.exit()
                if "JpsiToMuMu" not in processCfg and value == "processJpsiToMuMuSkimmed" and extrargs.onlySelect == "true":
                    config[key]["processJpsiToMuMuSkimmed"] = "false"
                    logging.debug(" - [%s] %s : false",key,value)

                if "JpsiToMuMuVertexing" in processCfg and value == "processJpsiToMuMuVertexingSkimmed":
                    if isAnalysisMuonSelected:
                        config[key]["processJpsiToMuMuVertexingSkimmed"] = "true"
                        logging.debug(" - [%s] %s : true",key,value)
                    if not isAnalysisMuonSelected:
                        logging.error("muonSelection not found in analysis for processJpsiToMuMuVertexingSkimmed -> analysis-same-event-pairing")
                        sys.exit()
                if "JpsiToMuMuVertexing" not in processCfg and value == "processJpsiToMuMuVertexingSkimmed" and extrargs.onlySelect == "true":
                    config[key]["processJpsiToMuMuVertexingSkimmed"] = "false"
                    logging.debug(" - [%s] %s : false",key,value)
                    
            # If no process function is provided, all SEP process functions are pulled false (for JSON Overrider mode)                               
            if key == "analysis-same-event-pairing" and extrargs.process == None and isAnalysisSameEventPairingSelected == False and extrargs.onlySelect == "true":
                config[key]["processJpsiToEESkimmed"] = "false"
                config[key]["processJpsiToMuMuSkimmed"] = "false"
                config[key]["processJpsiToMuMuVertexingSkimmed"] = "false"
            
            # analysis-same-event-pairing
            if key == "analysis-same-event-pairing":
                if value == "cfgBarrelMCRecSignals" and extrargs.cfgBarrelMCRecSignals:
                    if type(extrargs.cfgBarrelMCRecSignals) == type(clist):
                        extrargs.cfgBarrelMCRecSignals = listToString(extrargs.cfgBarrelMCRecSignals) 
                    if extrargs.onlySelect == "false":
                        actualConfig = config[key][value]
                        extrargs.cfgBarrelMCRecSignals = actualConfig + "," + extrargs.cfgBarrelMCRecSignals 
                    config[key][value] = extrargs.cfgBarrelMCRecSignals
                    logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgBarrelMCRecSignals)
                           
                if value == "cfgBarrelMCGenSignals" and extrargs.cfgBarrelMCGenSignals:
                    if type(extrargs.cfgBarrelMCGenSignals) == type(clist):
                        extrargs.cfgBarrelMCGenSignals = listToString(extrargs.cfgBarrelMCGenSignals)
                    if extrargs.onlySelect == "false":
                        actualConfig = config[key][value]
                        extrargs.cfgBarrelMCGenSignals = actualConfig + "," + extrargs.cfgBarrelMCGenSignals  
                    config[key][value] = extrargs.cfgBarrelMCGenSignals
                    logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgBarrelMCGenSignals)
                    
                if value == "cfgFlatTables" and extrargs.cfgFlatTables:
                    config[key][value] = extrargs.cfgFlatTables
                    logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgFlatTables)
                
            # analysis-dilepton-track
            if key == "analysis-dilepton-track":
                if value == "cfgBarrelMCRecSignals" and extrargs.cfgBarrelDileptonMCRecSignals:
                    if type(extrargs.cfgBarrelDileptonMCRecSignals) == type(clist):
                        extrargs.cfgBarrelDileptonMCRecSignals = listToString(extrargs.cfgBarrelDileptonMCRecSignals)
                    if extrargs.onlySelect == "false":
                        actualConfig = config[key][value]
                        extrargs.cfgBarrelDileptonMCRecSignals = actualConfig + "," + extrargs.cfgBarrelDileptonMCRecSignals   
                    config[key][value] = extrargs.cfgBarrelDileptonMCRecSignals
                    logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgBarrelDileptonMCRecSignals)
                    
                if value == "cfgBarrelMCGenSignals" and extrargs.cfgBarrelDileptonMCGenSignals:
                    if type(extrargs.cfgBarrelDileptonMCGenSignals) == type(clist):
                        extrargs.cfgBarrelDileptonMCGenSignals = listToString(extrargs.cfgBarrelDileptonMCGenSignals)
                    if extrargs.onlySelect == "false":
                        actualConfig = config[key][value]
                        extrargs.cfgBarrelDileptonMCGenSignals = actualConfig + "," + extrargs.cfgBarrelDileptonMCGenSignals   
                    config[key][value] = extrargs.cfgBarrelDileptonMCRecSignals
                    logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgBarrelDileptonMCGenSignals)            
                if value == "cfgLeptonCuts" and extrargs.cfgLeptonCuts:
                    if type(extrargs.cfgLeptonCuts) == type(clist):
                        extrargs.cfgLeptonCuts = listToString(extrargs.cfgLeptonCuts)
                    if extrargs.onlySelect == "false":
                        actualConfig = config[key][value]
                        extrargs.cfgLeptonCuts = actualConfig + "," + extrargs.cfgLeptonCuts 
                    config[key][value] = extrargs.cfgLeptonCuts
                    logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgLeptonCuts)
                    
                if value == "cfgFillCandidateTable" and extrargs.cfgFillCandidateTable:
                    config[key][value] = extrargs.cfgFillCandidateTable
                    logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgFillCandidateTable)
                    
            # Dummy automizer
            if extrargs.autoDummy:
                """ 
                value.endswith("Skimmed") --> get all skimmed process functions without dummy
                if "true" in skimmedListEventSelection ... else ... --> # if no skimmed process true, processDummy true else processDummy false
                """
                                 
                if key == "analysis-event-selection": 
                    if value.endswith("Skimmed"):
                        if config[key][value] == "true":
                            skimmedListEventSelection.append("true")
                        if config[key][value] == "false":
                            skimmedListEventSelection.append("false")               
                    if "true" in skimmedListEventSelection:
                        config[key]["processDummy"] = "false"
                    else:
                        config[key]["processDummy"] = "true" 
                        
                if key == "analysis-muon-selection":
                    if value.endswith("Skimmed"):
                        if config[key][value] == "true":
                            skimmedListMuonSelection.append("true")
                        if config[key][value] == "false":
                            skimmedListMuonSelection.append("false")     
                    if "true" in skimmedListMuonSelection:
                        config[key]["processDummy"] = "false"
                    else:
                        config[key]["processDummy"] = "true"
                        
                if key == "analysis-track-selection":
                    if value.endswith("Skimmed"):
                        if config[key][value] == "true":
                            skimmedListTrackSelection.append("true")
                        if config[key][value] == "false":
                            skimmedListTrackSelection.append("false")        
                    if "true" in skimmedListTrackSelection:
                        config[key]["processDummy"] = "false"
                    else:
                        config[key]["processDummy"] = "true"
                                                
                if key == "analysis-same-event-pairing":
                    if value.endswith("Skimmed"):
                        if config[key][value] == "true":
                            skimmedListSEP.append("true")
                        if config[key][value] == "false":
                            skimmedListSEP.append("false")           
                    if "true" in skimmedListSEP:
                        config[key]["processDummy"] = "false"
                    else:
                        config[key]["processDummy"] = "true" 
                        
                if key == "analysis-dilepton-track":
                    if value.endswith("Skimmed"):
                        if config[key][value] == "true":
                            skimmedListDileptonTrack.append("true")
                        if config[key][value] == "false":
                            skimmedListDileptonTrack.append("false")            
                    if "true" in skimmedListDileptonTrack:
                        config[key]["processDummy"] = "false"
                    else:
                        config[key]["processDummy"] = "true"

# AOD File and Reader-Writer Checker                    
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
        
if extrargs.reader != None:
    if not os.path.isfile(extrargs.reader):
        logging.error("%s File not found in path!!!",extrargs.reader)
        sys.exit()
elif not os.path.isfile((config["internal-dpl-aod-reader"]["aod-reader-json"])):
        print("[ERROR]",config["internal-dpl-aod-reader"]["aod-reader-json"],"File not found in path!!!")
        sys.exit()
                         
###########################
# End Interface Processes #
###########################   

# Write the updated configuration file into a temporary file
updatedConfigFileName = "tempConfigDQEfficiency.json"
    
with open(updatedConfigFileName,"w") as outputFile:
  json.dump(config, outputFile ,indent=2)

commandToRun = taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " -b" + " --aod-writer-json " + extrargs.writer
if extrargs.writer == "false":
    commandToRun = taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " -b"

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