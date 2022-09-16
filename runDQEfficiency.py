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
from extramodules.stringOperations import listToString, stringToList, multiConfigurableSet
from extramodules.dqExceptions import (CfgInvalidFormatError, ForgettedArgsError, NotInAlienvError,)

from dqtasks.dqEfficiency import DQEfficiency

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

readerPath = "configs/readerConfiguration_reducedEventMC.json"
writerPath = "configs/writerConfiguration_dileptonMC.json"

booleanSelections = ["true", "false"]

isAnalysisEventSelected = True
isAnalysisTrackSelected = True
isAnalysisMuonSelected = True
isAnalysisSameEventPairingSelected = True

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


class RunDQEfficiency(object):
    
    """
    This class is for managing the workflow by using the interface arguments from
    all other Common dependencies and the dqEfficiency Task's own arguments in a combined structure.

    Args:
      object (parser_args() object): runDQEfficiency.py workflow
    """
    
    def __init__(
            self, parserRunDQEfficiency = argparse.ArgumentParser(
                formatter_class = argparse.ArgumentDefaultsHelpFormatter,
                description = "Example Usage: ./runDQEfficiency.py <yourConfig.json> --arg value "
                ), dqEfficiency = DQEfficiency(), debugOptions = DebugOptions(),
        ):
        super(RunDQEfficiency, self).__init__()
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
        groupCoreSelections = self.parserRunDQEfficiency.add_argument_group(title = "Core configurations that must be configured")
        groupCoreSelections.add_argument("cfgFileName", metavar = "Config.json", default = "config.json", help = "config JSON file name",)
        
        # aod
        groupDPLReader = self.parserRunDQEfficiency.add_argument_group(title = "Data processor options: internal-dpl-aod-reader")
        groupDPLReader.add_argument("--aod", help = "Add your AOD File with path", action = "store", type = str)
        groupDPLReader.add_argument(
            "--reader",
            help = "Reader config JSON with path. For Standart Analysis use as default, for dilepton analysis change to dilepton JSON config file",
            action = "store", default = readerPath, type = str,
            )
        groupDPLReader.add_argument(
            "--writer", help = "Argument for producing dileptonAOD.root. Set false for disable", action = "store", default = writerPath,
            type = str,
            )
        
        # automation params
        groupAutomations = self.parserRunDQEfficiency.add_argument_group(title = "Automation Parameters")
        groupAutomations.add_argument(
            "--onlySelect", help = "If false JSON Overrider Interface If true JSON Additional Interface", action = "store",
            default = "true", type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        groupAutomations.add_argument(
            "--autoDummy", help = "Dummy automize parameter (don't configure it, true is highly recomended for automation)",
            action = "store", default = "true", type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        
        # helper lister commands
        # groupAdditionalHelperCommands = self.parserRunDQEfficiency.add_argument_group(title="Additional Helper Command Options")
        # groupAdditionalHelperCommands.add_argument("--cutLister", help="List all of the analysis cuts from CutsLibrary.h", action="store_true")
        # groupAdditionalHelperCommands.add_argument("--MCSignalsLister", help="List all of the MCSignals from MCSignalLibrary.h", action="store_true")
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        
        argcomplete.autocomplete(self.parserRunDQEfficiency, always_complete_options = False)
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


# init args manually
initArgs = RunDQEfficiency()
initArgs.mergeArgs()
initArgs.parseArgs()

args = initArgs.parseArgs()
configuredCommands = vars(args) # for get args

# Debug Settings
if args.debug and (not args.logFile):
    DEBUG_SELECTION = args.debug
    numeric_level = getattr(logging, DEBUG_SELECTION.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % DEBUG_SELECTION)
    logging.basicConfig(format = "[%(levelname)s] %(message)s", level = DEBUG_SELECTION)

if args.logFile and args.debug:
    log = logging.getLogger("")
    level = logging.getLevelName(args.debug)
    log.setLevel(level)
    format = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s")
    
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)
    
    loggerFile = "tableReader.log"
    if os.path.isfile(loggerFile):
        os.remove(loggerFile)
    
    fh = handlers.RotatingFileHandler(loggerFile, maxBytes = (1048576 * 5), backupCount = 7, mode = "w")
    fh.setFormatter(format)
    log.addHandler(fh)

# Transcation management for forgettining assign a value to parameters
forgetParams = []
for key, value in configuredCommands.items():
    if value is not None:
        if (isinstance(value, str) or isinstance(value, list)) and len(value) == 0:
            forgetParams.append(key)
try:
    if len(forgetParams) > 0:
        raise ForgettedArgsError(forgetParams)
except ForgettedArgsError as e:
    logging.exception(e)
    sys.exit()

# Get Some cfg values provided from --param
for keyCfg, valueCfg in configuredCommands.items():
    if valueCfg is not None: # Skipped None types, because can"t iterate in None type
        if keyCfg == "analysis":
            if isinstance(valueCfg, str):
                valueCfg = stringToList(valueCfg)
            analysisCfg = valueCfg
        if keyCfg == "process":
            if isinstance(valueCfg, str):
                valueCfg = stringToList(valueCfg)
            processCfg = valueCfg
# Make some checks on provided arguments
# if len(sys.argv) < 2:
# logging.error("Invalid syntax! The command line should look like this:")
# logging.info(" ./runDQEfficiency.py <yourConfig.json> --param value ...")
# sys.exit()

# Load the configuration file provided as the first parameter
cfgControl = sys.argv[1] == args.cfgFileName
isConfigJson = sys.argv[1].endswith(".json")
config = {}

try:
    if cfgControl:
        if not isConfigJson:
            raise CfgInvalidFormatError(sys.argv[1])
        else:
            logging.info("%s is valid json config file", args.cfgFileName)

except CfgInvalidFormatError as e:
    logging.exception(e)
    sys.exit()

with open(sys.argv[1]) as configFile:
    config = json.load(configFile)
"""
try:
    if cfgControl:
        with open(args.cfgFileName) as configFile:
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
"""

taskNameInCommandLine = "o2-analysis-dq-efficiency"

# Check alienv
try:
    if O2PHYSICS_ROOT is None:
        raise NotInAlienvError
    else:
        logging.info("You are in %s alienv", O2PHYSICS_ROOT)
except NotInAlienvError as e:
    logging.exception(e)
    sys.exit()

#############################
# Start Interface Processes #
#############################

logging.info("Only Select Configured as %s", args.onlySelect)
if args.onlySelect == "true":
    logging.info("INTERFACE MODE : JSON Overrider")
if args.onlySelect == "false":
    logging.info("INTERFACE MODE : JSON Additional")

for key, value in config.items():
    if type(value) == type(config):
        for value, value2 in value.items():
            
            # aod
            if value == "aod-file" and args.aod:
                config[key][value] = args.aod
                logging.debug(" - [%s] %s : %s", key, value, args.aod)
            # reader
            if value == "aod-reader-json" and args.reader:
                config[key][value] = args.reader
                logging.debug(" - [%s] %s : %s", key, value, args.reader)
            
            # analysis-skimmed-selections
            if value == "processSkimmed" and args.analysis:
                
                if key == "analysis-event-selection":
                    if "eventSelection" in analysisCfg:
                        config[key][value] = "true"
                        logging.debug(" - [%s] %s : true", key, value)
                        isAnalysisEventSelected = True
                    if "eventSelection" not in analysisCfg:
                        logging.warning(
                            "YOU MUST ALWAYS CONFIGURE eventSelection value in --analysis parameter!! It is Missing and this issue will fixed by CLI"
                            )
                        config[key][value] = "true"
                        logging.debug(" - [%s] %s : true", key, value)
                
                if key == "analysis-track-selection":
                    if "trackSelection" in analysisCfg:
                        config[key][value] = "true"
                        logging.debug(" - [%s] %s : true", key, value)
                        isAnalysisTrackSelected = True
                    if "trackSelection" not in analysisCfg and args.onlySelect == "true":
                        config[key][value] = "false"
                        logging.debug(" - [%s] %s : false", key, value)
                
                if key == "analysis-muon-selection":
                    if "muonSelection" in analysisCfg:
                        config[key][value] = "true"
                        logging.debug(" - [%s] %s : true", key, value)
                        isAnalysisMuonSelected = True
                    if "muonSelection" not in analysisCfg and args.onlySelect == "true":
                        config[key][value] = "false"
                        logging.debug(" - [%s] %s : false", key, value)
                
                if "sameEventPairing" in analysisCfg:
                    isAnalysisSameEventPairingSelected = True
                if "sameEventPairing" not in analysisCfg:
                    isAnalysisSameEventPairingSelected = False
            
            if value == "processDimuonMuonSkimmed" and args.analysis:
                
                if key == "analysis-dilepton-track":
                    if "dileptonTrackDimuonMuonSelection" in analysisCfg:
                        config[key][value] = "true"
                        logging.debug(" - [%s] %s : true", key, value)
                    if ("dileptonTrackDimuonMuonSelection" not in analysisCfg and args.onlySelect == "true"):
                        config[key][value] = "false"
                        logging.debug(" - [%s] %s : false", key, value)
            
            if value == "processDielectronKaonSkimmed" and args.analysis:
                
                if key == "analysis-dilepton-track":
                    if "dileptonTrackDielectronKaonSelection" in analysisCfg:
                        config[key][value] = "true"
                        logging.debug(" - [%s] %s : true", key, value)
                    if ("dileptonTrackDielectronKaonSelection" not in analysisCfg and args.onlySelect == "true"):
                        config[key][value] = "false"
                        logging.debug(" - [%s] %s : false", key, value)
            
            # QA selections
            if value == "cfgQA" and args.cfgQA:
                config[key][value] = args.cfgQA
                logging.debug(" - [%s] %s : %s", key, value, args.cfgQA)
            
            # analysis-event-selection
            if value == "cfgEventCuts" and args.cfgEventCuts:
                multiConfigurableSet(config, key, value, args.cfgEventCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgEventCuts)
            
            # analysis-track-selection
            if value == "cfgTrackCuts" and args.cfgTrackCuts:
                multiConfigurableSet(config, key, value, args.cfgTrackCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgTrackCuts)
            if value == "cfgTrackMCSignals" and args.cfgTrackMCSignals:
                multiConfigurableSet(config, key, value, args.cfgTrackMCSignals, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgTrackMCSignals)
            
            # analysis-muon-selection
            if value == "cfgMuonCuts" and args.cfgMuonCuts:
                multiConfigurableSet(config, key, value, args.cfgMuonCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgMuonCuts)
            if value == "cfgMuonMCSignals" and args.cfgMuonMCSignals:
                multiConfigurableSet(config, key, value, args.cfgMuonMCSignals, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgMuonMCSignals)
            
            # analysis-same-event-pairing
            if key == "analysis-same-event-pairing" and args.process:
                
                if not isAnalysisSameEventPairingSelected:
                    logging.warning("You forget to add sameEventPairing option to analysis for Workflow. It Automatically added by CLI.")
                    isAnalysisSameEventPairingSelected = True
                
                if "JpsiToEE" in processCfg and value == "processJpsiToEESkimmed":
                    if isAnalysisTrackSelected:
                        config[key]["processJpsiToEESkimmed"] = "true"
                        logging.debug(" - [%s] %s : true", key, value)
                    if not isAnalysisTrackSelected:
                        logging.error("trackSelection not found in analysis for processJpsiToEESkimmed -> analysis-same-event-pairing")
                        sys.exit()
                if ("JpsiToEE" not in processCfg and value == "processJpsiToEESkimmed" and args.onlySelect == "true"):
                    config[key]["processJpsiToEESkimmed"] = "false"
                    logging.debug(" - [%s] %s : false", key, value)
                
                if "JpsiToMuMu" in processCfg and value == "processJpsiToMuMuSkimmed":
                    if isAnalysisMuonSelected:
                        config[key]["processJpsiToMuMuSkimmed"] = "true"
                        logging.debug(" - [%s] %s : true", key, value)
                    if not isAnalysisMuonSelected:
                        logging.error("muonSelection not found in analysis for processJpsiToMuMuSkimmed -> analysis-same-event-pairing")
                        sys.exit()
                if ("JpsiToMuMu" not in processCfg and value == "processJpsiToMuMuSkimmed" and args.onlySelect == "true"):
                    config[key]["processJpsiToMuMuSkimmed"] = "false"
                    logging.debug(" - [%s] %s : false", key, value)
                
                if ("JpsiToMuMuVertexing" in processCfg and value == "processJpsiToMuMuVertexingSkimmed"):
                    if isAnalysisMuonSelected:
                        config[key]["processJpsiToMuMuVertexingSkimmed"] = "true"
                        logging.debug(" - [%s] %s : true", key, value)
                    if not isAnalysisMuonSelected:
                        logging.error(
                            "muonSelection not found in analysis for processJpsiToMuMuVertexingSkimmed -> analysis-same-event-pairing"
                            )
                        sys.exit()
                if ("JpsiToMuMuVertexing" not in processCfg and value == "processJpsiToMuMuVertexingSkimmed" and args.onlySelect == "true"):
                    config[key]["processJpsiToMuMuVertexingSkimmed"] = "false"
                    logging.debug(" - [%s] %s : false", key, value)
            
            # If no process function is provided, all SEP process functions are pulled false (for JSON Overrider mode)
            if (
                key == "analysis-same-event-pairing" and args.process is None and not isAnalysisSameEventPairingSelected and
                args.onlySelect == "true"
                ):
                config[key]["processJpsiToEESkimmed"] = "false"
                config[key]["processJpsiToMuMuSkimmed"] = "false"
                config[key]["processJpsiToMuMuVertexingSkimmed"] = "false"
            
            # analysis-same-event-pairing
            if key == "analysis-same-event-pairing":
                if value == "cfgBarrelMCRecSignals" and args.cfgBarrelMCRecSignals:
                    multiConfigurableSet(config, key, value, args.cfgBarrelMCRecSignals, args.onlySelect)
                    logging.debug(" - [%s] %s : %s", key, value, args.cfgBarrelMCRecSignals)
                
                if value == "cfgBarrelMCGenSignals" and args.cfgBarrelMCGenSignals:
                    multiConfigurableSet(config, key, value, args.cfgBarrelMCGenSignals, args.onlySelect)
                    logging.debug(" - [%s] %s : %s", key, value, args.cfgBarrelMCGenSignals)
                
                if value == "cfgFlatTables" and args.cfgFlatTables:
                    config[key][value] = args.cfgFlatTables
                    logging.debug(" - [%s] %s : %s", key, value, args.cfgFlatTables)
            
            # analysis-dilepton-track
            if key == "analysis-dilepton-track":
                if value == "cfgBarrelMCRecSignals" and args.cfgBarrelDileptonMCRecSignals:
                    multiConfigurableSet(config, key, value, args.cfgBarrelDileptonMCRecSignals, args.onlySelect)
                    config[key][value] = args.cfgBarrelDileptonMCRecSignals
                    logging.debug(" - [%s] %s : %s", key, value, args.cfgBarrelDileptonMCRecSignals)
                
                if value == "cfgBarrelMCGenSignals" and args.cfgBarrelDileptonMCGenSignals:
                    multiConfigurableSet(config, key, value, args.cfgBarrelDileptonMCGenSignals, args.onlySelect)
                    logging.debug(" - [%s] %s : %s", key, value, args.cfgBarrelDileptonMCGenSignals)
                if value == "cfgLeptonCuts" and args.cfgLeptonCuts:
                    multiConfigurableSet(config, key, value, args.cfgLeptonCuts, args.onlySelect)
                    logging.debug(" - [%s] %s : %s", key, value, args.cfgLeptonCuts)
                
                if value == "cfgFillCandidateTable" and args.cfgFillCandidateTable:
                    config[key][value] = args.cfgFillCandidateTable
                    logging.debug(" - [%s] %s : %s", key, value, args.cfgFillCandidateTable)
            
            # Dummy automizer
            if args.autoDummy:
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
if args.aod is not None:
    argProvidedAod = args.aod
    textAodList = argProvidedAod.startswith("@")
    endsWithRoot = argProvidedAod.endswith(".root")
    endsWithTxt = argProvidedAod.endswith("txt") or argProvidedAod.endswith("text")
    if textAodList and endsWithTxt:
        argProvidedAod = argProvidedAod.replace("@", "")
        logging.info("You provided AO2D list as text file : %s", argProvidedAod)
        try:
            open(argProvidedAod, "r")
            logging.info("%s has valid File Format and Path, File Found", argProvidedAod)
        
        except FileNotFoundError:
            logging.exception("%s AO2D file text list not found in path!!!", argProvidedAod)
            sys.exit()
    
    elif endsWithRoot:
        logging.info("You provided single AO2D root file : %s", argProvidedAod)
        try:
            open(argProvidedAod, "r")
            logging.info("%s has valid File Format and Path, File Found", argProvidedAod)
        
        except FileNotFoundError:
            logging.exception("%s AO2D single root file not found in path!!!", argProvidedAod)
            sys.exit()
    else:
        try:
            open(argProvidedAod, "r")
            logging.info("%s has valid File Format and Path, File Found", argProvidedAod)
        
        except FileNotFoundError:
            logging.exception("%s Wrong formatted File, check your file extension!", argProvidedAod)
            sys.exit()

if args.reader is not None:
    if not os.path.isfile(args.reader):
        logging.error("%s File not found in path!!!", args.reader)
        sys.exit()
elif not os.path.isfile((config["internal-dpl-aod-reader"]["aod-reader-json"])):
    logging.error(" %s File not found in path!!!", config["internal-dpl-aod-reader"]["aod-reader-json"])
    sys.exit()

###########################
# End Interface Processes #
###########################

# Write the updated configuration file into a temporary file
updatedConfigFileName = "tempConfigDQEfficiency.json"

with open(updatedConfigFileName, "w") as outputFile:
    json.dump(config, outputFile, indent = 2)

commandToRun = (taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " -b" + " --aod-writer-json " + args.writer)
if args.writer == "false":
    commandToRun = (taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " -b")

print("====================================================================================================================")
logging.info("Command to run:")
logging.info(commandToRun)
print("====================================================================================================================")

# Listing Added Commands
logging.info("Args provided configurations List")
print("====================================================================================================================")
for key, value in configuredCommands.items():
    if value is not None:
        if isinstance(value, list):
            listToString(value)
        logging.info("--%s : %s ", key, value)

os.system(commandToRun)

# Pycache remove after running in O2
# getParrentDir = sys.path[-1]

# trying to insert to false directory
try:
    parentPath = os.getcwd()
    if os.path.exists(parentPath) and os.path.isfile(parentPath + "/pycacheRemover.py"):
        logging.info("Inserting inside for pycache remove: %s", os.getcwd())
        pycacheRemover = PycacheRemover()
        pycacheRemover.__init__()
        logging.info("pycaches removed succesfully")
    
    elif not os.path.exists(parentPath):
        logging.error("OS Path is not valid for pycacheRemover. Fatal Error.")
        sys.exit()
    elif not os.path.isfile(parentPath + "/pycacheRemover.py"):
        raise FileNotFoundError

# Caching the exception
except FileNotFoundError:
    logging.exception("Something wrong with specified\
          directory. Exception- %s", sys.exc_info(),)
    sys.exit()
