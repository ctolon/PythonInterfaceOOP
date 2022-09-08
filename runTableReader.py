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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/tableReader.cxx

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


from dqtasks.tableReader import TableReader

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

readerPath = "configs/readerConfiguration_reducedEvent.json"
writerPath = "configs/writerConfiguration_dileptons.json"

isAnalysisEventSelected = True
isAnalysisTrackSelected = True
isAnalysisMuonSelected = True
isAnalysisSameEventPairingSelected = True
isAnalysisDileptonHadronSelected = True

booleanSelections = ["true", "false"]

threeSelectedList = []
clist = []  # control list for type control

# List for Selected skimmed process functions for dummy automizer
skimmedListEventSelection = []
skimmedListTrackSelection = []
skimmedListMuonSelection = []
skimmedListEventMixing = []
skimmedListSEP = []
skimmedListDileptonHadron = []

# Get system variables in alienv.
O2DPG_ROOT = os.environ.get("O2DPG_ROOT")
QUALITYCONTROL_ROOT = os.environ.get("QUALITYCONTROL_ROOT")
O2_ROOT = os.environ.get("O2_ROOT")
O2PHYSICS_ROOT = os.environ.get("O2PHYSICS_ROOT")

#################
# Init Workflow #
#################

class RunTableReader(object):
    """
    This class is for managing the workflow by using the interface arguments from
    all other Common dependencies and the tableReader Task's own arguments in a combined structure.
    
    Args:
      object (parser_args() object): runTableReader.py workflow
    """
    
    def __init__(self, 
                parserRunTableReader=argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                description="Arguments to pass"), 
                tableReader=TableReader(),
                debugOptions=DebugOptions()
                ):
        super(RunTableReader, self).__init__()
        self.parserRunTableReader = parserRunTableReader
        self.tableReader = tableReader
        self.debugOptions = debugOptions
        self.parserRunTableReader.register("action", "none", NoAction)
        self.parserRunTableReader.register("action", "store_choice", ChoicesAction)
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Core Part
        groupCoreSelections = self.parserRunTableReader.add_argument_group(title="Core configurations that must be configured")
        groupCoreSelections.add_argument("cfgFileName", metavar="Config.json", default="config.json", help="config JSON file name")
                        
        # aod
        groupDPLReader = self.parserRunTableReader.add_argument_group(title="Data processor options: internal-dpl-aod-reader")
        groupDPLReader.add_argument("--aod", help="Add your AOD File with path", action="store", type=str)
        groupDPLReader.add_argument("--reader", help="Add your AOD Reader JSON with path", action="store", default=readerPath, type=str)
        groupDPLReader.add_argument("--writer", help="Add your AOD Writer JSON with path", action="store", default=writerPath, type=str)

        # automation params
        groupAutomations = self.parserRunTableReader.add_argument_group(title="Automation Parameters")
        groupAutomations.add_argument("--onlySelect", help="If false JSON Overrider Interface If true JSON Additional Interface", action="store", default="true", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)
        groupAutomations.add_argument("--autoDummy", help="Dummy automize parameter (don't configure it, true is highly recomended for automation)", action="store", default="true", type=str.lower, choices=booleanSelections).completer = ChoicesCompleter(booleanSelections)
        
        # helper lister commands
        #groupAdditionalHelperCommands = self.parserRunTableReader.add_argument_group(title="Additional Helper Command Options")
        #groupAdditionalHelperCommands.add_argument("--cutLister", help="List all of the analysis cuts from CutsLibrary.h", action="store_true")
        #groupAdditionalHelperCommands.add_argument("--mixingLister", help="List all of the event mixing selections from MixingLibrary.h", action="store_true")
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
 
        argcomplete.autocomplete(self.parserRunTableReader, always_complete_options=False)  
        return self.parserRunTableReader.parse_args()

    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """
        
        self.debugOptions.parserDebugOptions = self.parserRunTableReader
        self.debugOptions.addArguments()
        
        self.tableReader.parserTableReader = self.parserRunTableReader
        self.tableReader.addArguments()
                
        self.addArguments()
        
    # This function not work should be integrated instead of mergeArgs
    """  
    def mergeMultiArgs(self, *objects):
        parser = self.parserRuntableReader
        for object in objects:
            object.parser = parser
            object.addArguments()
        self.addArguments()
    """

# init args manually    
initArgs = RunTableReader()
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
    
# Get Some cfg values provided from --param
for keyCfg,valueCfg in configuredCommands.items():
    if(valueCfg != None): # Skipped None types, because can"t iterate in None type
        if keyCfg == "analysis":
            if type(valueCfg) == type("string"):
                valueCfg = stringToList(valueCfg)
            analysisCfg = valueCfg
        if keyCfg == "mixing":
            if type(valueCfg) == type("string"):
                valueCfg = stringToList(valueCfg)
            mixingCfg = valueCfg
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
    
    loggerFile = "tableReader.log"
    if os.path.isfile(loggerFile):
        os.remove(loggerFile)
    
    fh = handlers.RotatingFileHandler(loggerFile, maxBytes=(1048576*5), backupCount=7, mode="w")
    fh.setFormatter(format)
    log.addHandler(fh)


# Make some checks on provided arguments
if len(sys.argv) < 2:
  logging.error("Invalid syntax! The command line should look like this:")
  logging.info("  ./runTableReader.py <yourConfig.json> --param value ...")
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
        logging.info("  ./runTableReader.py <yourConfig.json> <-runData|-runMC> --param value ...")
        sys.exit()
        
except FileNotFoundError:
    isConfigJson = sys.argv[1].endswith(".json")
    if not isConfigJson:
            logging.error("Invalid syntax! After the script you must define your json configuration file!!! The command line should look like this:")
            logging.info(" ./runTableReader.py <yourConfig.json> --param value ...")
            sys.exit()
    logging.error("Your JSON Config File found in path!!!")
    sys.exit()


taskNameInCommandLine = "o2-analysis-dq-table-reader"

# Check alienv
if O2PHYSICS_ROOT == None:
   logging.error("You must load O2Physics with alienv")
   sys.exit()

###################
# HELPER MESSAGES #
###################
    
"""    
if extrargs.cutLister and extrargs.mixingLister:
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
        
    print("\n====================\nEvent Mixing Selections :")
    print("====================")
    counter = 0
    temp = ""
    threeSelectedList.clear()    
    for i in allMixing:
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
    
if extrargs.mixingLister:
    counter = 0
    temp = ""
    print("Event Mixing Selections :")
    print("====================")  
    for i in allMixing:
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
                
            # analysis-event-selection, analysis-track-selection, analysis-muon-selection, analysis-same-event-pairing
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
                if key == "analysis-dilepton-hadron":
                    if "dileptonHadron" in analysisCfg:
                        config[key][value] = "true"
                        isAnalysisDileptonHadronSelected = True
                        logging.debug(" - [%s] %s : true",key,value)
                    if "dileptonHadron" not in analysisCfg and extrargs.onlySelect == "true":
                        config[key][value] = "false"
                        logging.debug(" - [%s] %s : false",key,value)
                                                            
                if "sameEventPairing" in analysisCfg:
                    isAnalysisSameEventPairingSelected = True
                if "sameEventPairing" not in analysisCfg:
                    isAnalysisSameEventPairingSelected = False
                                    
            # Analysis-event-mixing with automation
            if extrargs.mixing == None:
                if value == "processBarrelSkimmed" and extrargs.analysis:                        
          
                    if key == "analysis-event-mixing":                             
                        if "trackSelection" in analysisCfg and "eventMixing" in analysisCfg:
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true",key,value)
                        if "eventMixing" not in analysisCfg and extrargs.onlySelect == "true":
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false",key,value)
                        if "eventMixing" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error("For Configuring eventMixing, You have to specify either trackSelection or muonSelection in --analysis parameter!")
                            sys.exit()
                                                                            
                if value == "processMuonSkimmed" and extrargs.analysis:                        

                    if key == "analysis-event-mixing":                                       
                        if "muonSelection" in analysisCfg and "eventMixing" in analysisCfg:
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true",key,value)
                        if "eventMixing" not in analysisCfg and extrargs.onlySelect == "true":
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false",key,value)
                        if "eventMixing" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error("For Configuring eventMixing, You have to specify either trackSelection or muonSelection in --analysis parameter!")
                            sys.exit()
                                                                            
                if value == "processBarrelMuonSkimmed" and extrargs.analysis:                        

                    if key == "analysis-event-mixing":                                                             
                        if "trackSelection" in analysisCfg and "muonSelection" in analysisCfg and "eventMixing" in analysisCfg:
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true",key,value)
                        if "eventMixing" not in analysisCfg and extrargs.onlySelect == "true":
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false",key,value)
                        if "eventMixing" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error("For Configuring eventMixing, You have to specify either trackSelection or muonSelection in --analysis parameter!")
                            sys.exit()
                                        
                if value == "processBarrelVnSkimmed" and extrargs.analysis:                        

                    if key == "analysis-event-mixing":                             
                        if "trackSelection" in analysisCfg and "eventMixingVn" in analysisCfg:
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true",key,value)
                        if "eventMixingVn" not in analysisCfg and extrargs.onlySelect == "true":
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false",key,value)
                        if "eventMixingVn" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error("For Configuring eventMixingVn, You have to specify either trackSelection or muonSelection in --analysis parameter!")
                            sys.exit()
                                                                            
                if value == "processMuonVnSkimmed" and extrargs.analysis:                        
       
                    if key == "analysis-event-mixing":                                        
                        if "muonSelection" in analysisCfg and "eventMixingVn" in analysisCfg:
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true",key,value)
                        if "eventMixingVn" not in analysisCfg and extrargs.onlySelect == "true":
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false",key,value)
                        if "eventMixingVn" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error("For Configuring eventMixingVn, You have to specify either trackSelection or muonSelection in --analysis parameter!")
                            sys.exit()
                                        
            # Analysis-event-mixing selection manually
            if extrargs.mixing != None:
                if value == "processBarrelSkimmed" and extrargs.analysis:                        

                    if key == "analysis-event-mixing":                             
                        if "trackSelection" in analysisCfg and "eventMixing" in analysisCfg and "Barrel" in mixingCfg:
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true",key,value)
                        if "trackSelection" in analysisCfg and "Barrel" not in mixingCfg and extrargs.onlySelect == "true":
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false",key,value)
                        if "eventMixing" not in analysisCfg and "Barrel" in mixingCfg:
                            logging.error("When configuring analysis-event-mixing for Barrel, you must configure eventMixing within the --analysis parameter!")
                            sys.exit()
                        if "Barrel" in mixingCfg and "trackSelection" not in analysisCfg:
                            logging.error("When configuring analysis-event-mixing for Barrel, you must configure trackSelection within the --analysis parameter!")
                            sys.exit()
                        if "eventMixing" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error("For Configuring eventMixing, You have to specify either trackSelection or muonSelection in --analysis parameter!")
                            sys.exit()
                                                                            
                if value == "processMuonSkimmed" and extrargs.analysis:                        
          
                    if key == "analysis-event-mixing":                                       
                        if "muonSelection" in analysisCfg and "eventMixing" in analysisCfg and "Muon" in mixingCfg:
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true",key,value)
                        if "muonSelection" in analysisCfg and "Muon" not in mixingCfg and extrargs.onlySelect == "true":
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false",key,value)
                        if "eventMixing" not in analysisCfg and "Muon" in mixingCfg:
                            logging.error("When configuring analysis-event-mixing for Muon, you must configure eventMixing within the --analysis parameter!")
                            sys.exit()
                        if "Muon" in mixingCfg and "muonSelection" not in analysisCfg:
                            logging.error("When configuring analysis-event-mixing for Muon, you must configure muonSelection within the --analysis parameter!")
                            sys.exit()
                        if "eventMixing" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error("For Configuring eventMixing, You have to specify either trackSelection or muonSelection in --analysis parameter!")
                            sys.exit()
                                                                            
                if value == "processBarrelMuonSkimmed" and extrargs.analysis:                        

                    if key == "analysis-event-mixing":                                                             
                        if "trackSelection" in analysisCfg and "muonSelection" in analysisCfg and "eventMixing" in analysisCfg and "BarrelMuon" in mixingCfg:
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true",key,value)
                        if "trackSelection" in analysisCfg and "muonSelection" in analysisCfg and "BarrelMuon" not in mixingCfg and extrargs.onlySelect == "true":
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false",key,value)
                        if "eventMixing" not in analysisCfg and "BarrelMuon" in mixingCfg:
                            logging.error("When configuring analysis-event-mixing for BarrelMuon, you must configure eventMixing within the --analysis parameter!")
                            sys.exit()
                        if "BarrelMuon" in mixingCfg and ("muonSelection" not in analysisCfg or "trackSelection" not in analysisCfg):
                            logging.error("When configuring analysis-event-mixing for BarrelMuon, you must configure both of muonSelection and trackSelection within the --analysis parameter!")
                            sys.exit()                                                                            
                        if "eventMixing" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error("For Configuring eventMixing, You have to specify either trackSelection or muonSelection in --analysis parameter!")
                            sys.exit()
                                        
                if value == "processBarrelVnSkimmed" and extrargs.analysis:                        

                    if key == "analysis-event-mixing":                             
                        if "trackSelection" in analysisCfg and "eventMixingVn" in analysisCfg and "BarrelVn" in mixingCfg:
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true",key,value)
                        if "trackSelection" in analysisCfg and "BarrelVn" not in mixingCfg and extrargs.onlySelect == "true":
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false",key,value)
                        if "eventMixingVn" not in analysisCfg and "BarrelVn" in mixingCfg:
                            logging.error("When configuring analysis-event-mixing for BarrelVn, you must configure eventMixingVn within the --analysis parameter!")
                            sys.exit()
                        if "BarrelVn" in mixingCfg and "trackSelection" not in analysisCfg:
                            logging.error("When configuring analysis-event-mixing for BarrelVn, you must configure trackSelection within the --analysis parameter!")
                            sys.exit()
                        if "eventMixingVn" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error("For Configuring eventMixingVn, You have to specify either trackSelection or muonSelection in --analysis parameter!")
                            sys.exit()
                                                                            
                if value == "processMuonVnSkimmed" and extrargs.analysis:                        

                    if key == "analysis-event-mixing":                                        
                        if "muonSelection" in analysisCfg and "eventMixingVn" in analysisCfg and "MuonVn" in mixingCfg:
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true",key,value)
                        if "muonSelection" in analysisCfg and "MuonVn" not in mixingCfg and extrargs.onlySelect == "true":
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false",key,value)
                        if "eventMixingVn" not in analysisCfg and "MuonVn" in mixingCfg:
                            logging.error("When configuring analysis-event-mixing for MuonVn, you must configure eventMixingVn within the --analysis parameter!")
                            sys.exit()
                        if "MuonVn" in mixingCfg and "muonSelection" not in analysisCfg:
                            logging.error("When configuring analysis-event-mixing for MuonVn, you must configure muonSelection within the --analysis parameter!")
                            sys.exit()
                        if "eventMixingVn" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error("For Configuring eventMixingVn, You have to specify either trackSelection or muonSelection in --analysis parameter!")
                            sys.exit()
                 
            # QA selections  
            if value =="cfgQA" and extrargs.cfgQA:
                config[key][value] = extrargs.cfgQA
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgQA)
                                              
            # analysis-event-selection
            if value == "cfgMixingVars" and extrargs.cfgMixingVars:
                if type(extrargs.cfgMixingVars) == type(clist):
                    extrargs.cfgMixingVars = listToString(extrargs.cfgMixingVars)
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgMixingVars = actualConfig + "," + extrargs.cfgMixingVars   
                config[key][value] = extrargs.cfgMixingVars
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgMixingVars)
            if value == "cfgEventCuts" and extrargs.cfgEventCuts:
                if type(extrargs.cfgEventCuts) == type(clist):
                    extrargs.cfgEventCuts = listToString(extrargs.cfgEventCuts)
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgEventCuts = actualConfig + "," + extrargs.cfgEventCuts   
                config[key][value] = extrargs.cfgEventCuts
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgEventCuts)

            # analysis-track-selection
            if value =="cfgTrackCuts" and extrargs.cfgTrackCuts:
                if type(extrargs.cfgTrackCuts) == type(clist):
                    extrargs.cfgTrackCuts = listToString(extrargs.cfgTrackCuts)
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgTrackCuts = actualConfig + "," + extrargs.cfgTrackCuts   
                config[key][value] = extrargs.cfgTrackCuts
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgTrackCuts)
                
            # analysis-muon-selection
            if value =="cfgMuonCuts" and extrargs.cfgMuonCuts:
                if type(extrargs.cfgMuonCuts) == type(clist):
                    extrargs.cfgMuonCuts = listToString(extrargs.cfgMuonCuts)
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgMuonCuts = actualConfig + "," + extrargs.cfgMuonCuts
                config[key][value] = extrargs.cfgMuonCuts
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgMuonCuts)
                
            # analysis-dilepton-hadron
            if value =="cfgLeptonCuts" and extrargs.cfgLeptonCuts:
                if type(extrargs.cfgLeptonCuts) == type(clist):
                    extrargs.cfgLeptonCuts = listToString(extrargs.cfgLeptonCuts)
                if extrargs.onlySelect == "false":
                    actualConfig = config[key][value]
                    extrargs.cfgLeptonCuts = actualConfig + "," + extrargs.cfgLeptonCuts 
                config[key][value] = extrargs.cfgLeptonCuts
                logging.debug(" - [%s] %s : %s",key,value,extrargs.cfgLeptonCuts)
            
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
                    
                if "VnJpsiToEE" in processCfg and value == "processVnJpsiToEESkimmed":
                    if isAnalysisTrackSelected:
                        config[key]["processVnJpsiToEESkimmed"] = "true"
                        logging.debug(" - [%s] %s : true",key,value)
                    if not isAnalysisTrackSelected:
                        logging.error("trackSelection not found in analysis for processVnJpsiToEESkimmed -> analysis-same-event-pairing")
                        sys.exit()
                if "VnJpsiToEE" not in processCfg and value == "processVnJpsiToEESkimmed" and extrargs.onlySelect == "true":
                        config[key]["processVnJpsiToEESkimmed"] = "false"
                        logging.debug(" - [%s] %s : false",key,value)
                        
                if "VnJpsiToMuMu" in processCfg and value == "processVnJpsiToMuMuSkimmed":
                    if isAnalysisMuonSelected:
                        config[key]["processVnJpsiToMuMuSkimmed"] = "true"
                        logging.debug(" - [%s] %s : true",key,value)
                    if not isAnalysisMuonSelected:
                        logging.error("muonSelection not found in analysis for processVnJpsiToMuMuSkimmed -> analysis-same-event-pairing")
                        sys.exit()                                   
                if "VnJpsiToMuMu" not in processCfg and value == "processVnJpsiToMuMuSkimmed" and extrargs.onlySelect == "true":
                    config[key]["processVnJpsiToMuMuSkimmed"] = "false"
                    logging.debug(" - [%s] %s : false",key,value)
                    
                if "ElectronMuon" in processCfg and value == "processElectronMuonSkimmed":
                    if isAnalysisTrackSelected and isAnalysisMuonSelected:
                        config[key]["processElectronMuonSkimmed"] = "true"
                        logging.debug(" - [%s] %s : true",key,value)
                    else:
                        logging.error("trackSelection and muonSelection not found in analysis for processElectronMuonSkimmed -> analysis-same-event-pairing")
                        sys.exit()
                if "ElectronMuon" not in processCfg and value == "processElectronMuonSkimmed" and extrargs.onlySelect == "true":
                    config[key]["processElectronMuonSkimmed"] = "false"
                    logging.debug(" - [%s] %s : false",key,value)
                    
                if "All" in processCfg and value == "processAllSkimmed":
                    if isAnalysisEventSelected and isAnalysisMuonSelected and isAnalysisTrackSelected:
                        config[key]["processAllSkimmed"] = "true"
                        logging.debug(" - [%s] %s : true",key,value)
                    else:
                        logging.debug("eventSelection, trackSelection and muonSelection not found in analysis for processAllSkimmed -> analysis-same-event-pairing")
                        sys.exit()
                if "All" not in processCfg and value == "processAllSkimmed" and extrargs.onlySelect == "true":
                    config[key]["processAllSkimmed"] = "false"
                    logging.debug(" - [%s] %s : false",key,value)
   
            # If no process function is provided, all SEP process functions are pulled false (for JSON Overrider mode)                 
            if key == "analysis-same-event-pairing" and extrargs.process == None and isAnalysisSameEventPairingSelected == False and extrargs.onlySelect == "true":
                config[key]["processJpsiToEESkimmed"] = "false"
                config[key]["processJpsiToMuMuSkimmed"] = "false"
                config[key]["processJpsiToMuMuVertexingSkimmed"] = "false"
                config[key]["processVnJpsiToEESkimmed"] = "false"
                config[key]["processVnJpsiToMuMuSkimmed"] = "false"
                config[key]["processElectronMuonSkimmed"] = "false"
                config[key]["processAllSkimmed"] = "false"
                     
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
                        
                if key == "analysis-event-mixing":
                    if value.endswith("Skimmed"):
                        if config[key][value] == "true":
                            skimmedListEventMixing.append("true")
                        if config[key][value] == "false":
                            skimmedListEventMixing.append("false")                         
                    if "true" in skimmedListEventMixing:
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
                        
                if key == "analysis-dilepton-hadron":
                    if value.endswith("Skimmed"):
                        if config[key][value] == "true":
                            skimmedListDileptonHadron.append("true")
                        if config[key][value] == "false":
                            skimmedListDileptonHadron.append("false")            
                    if "true" in skimmedListDileptonHadron:
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
updatedConfigFileName = "tempConfigTableReader.json"

with open(updatedConfigFileName,"w") as outputFile:
  json.dump(config, outputFile ,indent=2)
      
#commandToRun = taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " -b"
commandToRun = taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " --aod-writer-json " + extrargs.writer + " -b"

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