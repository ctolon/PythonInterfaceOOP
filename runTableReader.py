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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/tableReader.cxx

import json
import sys
import logging
import logging.config
import os
from extramodules.configGetter import configGetter
from extramodules.debugSettings import debugSettings

from extramodules.monitoring import dispArgs
from extramodules.dqTranscations import aodFileChecker, forgettedArgsChecker, jsonTypeChecker, mainTaskChecker
from extramodules.configSetter import multiConfigurableSet, processDummySet
from extramodules.pycacheRemover import runPycacheRemover

from dqtasks.tableReader import TableReader

###################################
# Interface Predefined Selections #
###################################

isAnalysisEventSelected = True
isAnalysisTrackSelected = True
isAnalysisMuonSelected = True
isAnalysisSameEventPairingSelected = True
isAnalysisDileptonHadronSelected = True

booleanSelections = ["true", "false"]

#################
# Init Workflow #
#################

# init args manually
initArgs = TableReader()
initArgs.mergeArgs()
initArgs.parseArgs()

args = initArgs.parseArgs()
allArgs = vars(args) # for get args

# Debug settings
debugSettings(args.debug, args.logFile, fileName = "tableReader.log")

# Transcation management
forgettedArgsChecker(allArgs)

# Get Some cfg values provided from --param
analysisCfg = configGetter(allArgs, "analysis")
mixingCfg = configGetter(allArgs, "mixing")
processCfg = configGetter(allArgs, "process")

# Load the configuration file provided as the first parameter
config = {}
with open(args.cfgFileName) as configFile:
    config = json.load(configFile)

jsonTypeChecker(args.cfgFileName)

taskNameInCommandLine = "o2-analysis-dq-table-reader"
taskNameInConfig = "analysis-event-selection"

mainTaskChecker(config, taskNameInConfig)

#############################
# Start Interface Processes #
#############################

logging.info("Only Select Configured as %s", args.onlySelect)
if args.onlySelect == "true":
    logging.info("INTERFACE MODE : JSON Overrider")
if args.onlySelect == "false":
    logging.info("INTERFACE MODE : JSON Additional")

for key, value in config.items():
    if isinstance(value, dict):
        for value, value2 in value.items():
            
            # aod
            if value == "aod-file" and args.aod:
                config[key][value] = args.aod
                logging.debug(" - [%s] %s : %s", key, value, args.aod)
            # reader
            if value == "aod-reader-json" and args.reader:
                config[key][value] = args.reader
                logging.debug(" - [%s] %s : %s", key, value, args.reader)
            
            # analysis-event-selection, analysis-track-selection, analysis-muon-selection, analysis-same-event-pairing
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
                if key == "analysis-dilepton-hadron":
                    if "dileptonHadron" in analysisCfg:
                        config[key][value] = "true"
                        isAnalysisDileptonHadronSelected = True
                        logging.debug(" - [%s] %s : true", key, value)
                    if "dileptonHadron" not in analysisCfg and args.onlySelect == "true":
                        config[key][value] = "false"
                        logging.debug(" - [%s] %s : false", key, value)
                
                if "sameEventPairing" in analysisCfg:
                    isAnalysisSameEventPairingSelected = True
                if "sameEventPairing" not in analysisCfg:
                    isAnalysisSameEventPairingSelected = False
            
            # Analysis-event-mixing with automation
            if args.mixing is None:
                if value == "processBarrelSkimmed" and args.analysis:
                    
                    if key == "analysis-event-mixing":
                        if "trackSelection" in analysisCfg and "eventMixing" in analysisCfg:
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true", key, value)
                        if "eventMixing" not in analysisCfg and args.onlySelect == "true":
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false", key, value)
                        if "eventMixing" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error(
                                "For Configuring eventMixing, You have to specify either trackSelection or muonSelection in --analysis parameter!"
                                )
                            sys.exit()
                
                if value == "processMuonSkimmed" and args.analysis:
                    
                    if key == "analysis-event-mixing":
                        if "muonSelection" in analysisCfg and "eventMixing" in analysisCfg:
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true", key, value)
                        if "eventMixing" not in analysisCfg and args.onlySelect == "true":
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false", key, value)
                        if "eventMixing" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error(
                                "For Configuring eventMixing, You have to specify either trackSelection or muonSelection in --analysis parameter!"
                                )
                            sys.exit()
                
                if value == "processBarrelMuonSkimmed" and args.analysis:
                    
                    if key == "analysis-event-mixing":
                        if ("trackSelection" in analysisCfg and "muonSelection" in analysisCfg and "eventMixing" in analysisCfg):
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true", key, value)
                        if "eventMixing" not in analysisCfg and args.onlySelect == "true":
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false", key, value)
                        if "eventMixing" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error(
                                "For Configuring eventMixing, You have to specify either trackSelection or muonSelection in --analysis parameter!"
                                )
                            sys.exit()
                
                if value == "processBarrelVnSkimmed" and args.analysis:
                    
                    if key == "analysis-event-mixing":
                        if "trackSelection" in analysisCfg and "eventMixingVn" in analysisCfg:
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true", key, value)
                        if "eventMixingVn" not in analysisCfg and args.onlySelect == "true":
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false", key, value)
                        if "eventMixingVn" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error(
                                "For Configuring eventMixingVn, You have to specify either trackSelection or muonSelection in --analysis parameter!"
                                )
                            sys.exit()
                
                if value == "processMuonVnSkimmed" and args.analysis:
                    
                    if key == "analysis-event-mixing":
                        if "muonSelection" in analysisCfg and "eventMixingVn" in analysisCfg:
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true", key, value)
                        if "eventMixingVn" not in analysisCfg and args.onlySelect == "true":
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false", key, value)
                        if "eventMixingVn" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error(
                                "For Configuring eventMixingVn, You have to specify either trackSelection or muonSelection in --analysis parameter!"
                                )
                            sys.exit()
            
            # Analysis-event-mixing selection manually
            if args.mixing is not None:
                if value == "processBarrelSkimmed" and args.analysis:
                    
                    if key == "analysis-event-mixing":
                        if ("trackSelection" in analysisCfg and "eventMixing" in analysisCfg and "Barrel" in mixingCfg):
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true", key, value)
                        if ("trackSelection" in analysisCfg and "Barrel" not in mixingCfg and args.onlySelect == "true"):
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false", key, value)
                        if "eventMixing" not in analysisCfg and "Barrel" in mixingCfg:
                            logging.error(
                                "When configuring analysis-event-mixing for Barrel, you must configure eventMixing within the --analysis parameter!"
                                )
                            sys.exit()
                        if "Barrel" in mixingCfg and "trackSelection" not in analysisCfg:
                            logging.error(
                                "When configuring analysis-event-mixing for Barrel, you must configure trackSelection within the --analysis parameter!"
                                )
                            sys.exit()
                        if "eventMixing" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error(
                                "For Configuring eventMixing, You have to specify either trackSelection or muonSelection in --analysis parameter!"
                                )
                            sys.exit()
                
                if value == "processMuonSkimmed" and args.analysis:
                    
                    if key == "analysis-event-mixing":
                        if ("muonSelection" in analysisCfg and "eventMixing" in analysisCfg and "Muon" in mixingCfg):
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true", key, value)
                        if ("muonSelection" in analysisCfg and "Muon" not in mixingCfg and args.onlySelect == "true"):
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false", key, value)
                        if "eventMixing" not in analysisCfg and "Muon" in mixingCfg:
                            logging.error(
                                "When configuring analysis-event-mixing for Muon, you must configure eventMixing within the --analysis parameter!"
                                )
                            sys.exit()
                        if "Muon" in mixingCfg and "muonSelection" not in analysisCfg:
                            logging.error(
                                "When configuring analysis-event-mixing for Muon, you must configure muonSelection within the --analysis parameter!"
                                )
                            sys.exit()
                        if "eventMixing" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error(
                                "For Configuring eventMixing, You have to specify either trackSelection or muonSelection in --analysis parameter!"
                                )
                            sys.exit()
                
                if value == "processBarrelMuonSkimmed" and args.analysis:
                    
                    if key == "analysis-event-mixing":
                        if (
                            "trackSelection" in analysisCfg and "muonSelection" in analysisCfg and "eventMixing" in analysisCfg and
                            "BarrelMuon" in mixingCfg
                            ):
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true", key, value)
                        if (
                            "trackSelection" in analysisCfg and "muonSelection" in analysisCfg and "BarrelMuon" not in mixingCfg and
                            args.onlySelect == "true"
                            ):
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false", key, value)
                        if "eventMixing" not in analysisCfg and "BarrelMuon" in mixingCfg:
                            logging.error(
                                "When configuring analysis-event-mixing for BarrelMuon, you must configure eventMixing within the --analysis parameter!"
                                )
                            sys.exit()
                        if "BarrelMuon" in mixingCfg and ("muonSelection" not in analysisCfg or "trackSelection" not in analysisCfg):
                            logging.error(
                                "When configuring analysis-event-mixing for BarrelMuon, you must configure both of muonSelection and trackSelection within the --analysis parameter!"
                                )
                            sys.exit()
                        if "eventMixing" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error(
                                "For Configuring eventMixing, You have to specify either trackSelection or muonSelection in --analysis parameter!"
                                )
                            sys.exit()
                
                if value == "processBarrelVnSkimmed" and args.analysis:
                    
                    if key == "analysis-event-mixing":
                        if ("trackSelection" in analysisCfg and "eventMixingVn" in analysisCfg and "BarrelVn" in mixingCfg):
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true", key, value)
                        if ("trackSelection" in analysisCfg and "BarrelVn" not in mixingCfg and args.onlySelect == "true"):
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false", key, value)
                        if "eventMixingVn" not in analysisCfg and "BarrelVn" in mixingCfg:
                            logging.error(
                                "When configuring analysis-event-mixing for BarrelVn, you must configure eventMixingVn within the --analysis parameter!"
                                )
                            sys.exit()
                        if "BarrelVn" in mixingCfg and "trackSelection" not in analysisCfg:
                            logging.error(
                                "When configuring analysis-event-mixing for BarrelVn, you must configure trackSelection within the --analysis parameter!"
                                )
                            sys.exit()
                        if "eventMixingVn" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error(
                                "For Configuring eventMixingVn, You have to specify either trackSelection or muonSelection in --analysis parameter!"
                                )
                            sys.exit()
                
                if value == "processMuonVnSkimmed" and args.analysis:
                    
                    if key == "analysis-event-mixing":
                        if ("muonSelection" in analysisCfg and "eventMixingVn" in analysisCfg and "MuonVn" in mixingCfg):
                            config[key][value] = "true"
                            logging.debug(" - [%s] %s : true", key, value)
                        if ("muonSelection" in analysisCfg and "MuonVn" not in mixingCfg and args.onlySelect == "true"):
                            config[key][value] = "false"
                            logging.debug(" - [%s] %s : false", key, value)
                        if "eventMixingVn" not in analysisCfg and "MuonVn" in mixingCfg:
                            logging.error(
                                "When configuring analysis-event-mixing for MuonVn, you must configure eventMixingVn within the --analysis parameter!"
                                )
                            sys.exit()
                        if "MuonVn" in mixingCfg and "muonSelection" not in analysisCfg:
                            logging.error(
                                "When configuring analysis-event-mixing for MuonVn, you must configure muonSelection within the --analysis parameter!"
                                )
                            sys.exit()
                        if "eventMixingVn" in analysisCfg and ("trackSelection" not in analysisCfg and "muonSelection" not in analysisCfg):
                            logging.error(
                                "For Configuring eventMixingVn, You have to specify either trackSelection or muonSelection in --analysis parameter!"
                                )
                            sys.exit()
            
            # QA selections
            if value == "cfgQA" and args.cfgQA:
                config[key][value] = args.cfgQA
                logging.debug(" - [%s] %s : %s", key, value, args.cfgQA)
            
            # analysis-event-selection
            if value == "cfgMixingVars" and args.cfgMixingVars:
                multiConfigurableSet(config, key, value, args.cfgMixingVars, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgMixingVars)
            if value == "cfgEventCuts" and args.cfgEventCuts:
                multiConfigurableSet(config, key, value, args.cfgEventCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgEventCuts)
            
            # analysis-track-selection
            if value == "cfgTrackCuts" and args.cfgTrackCuts:
                multiConfigurableSet(config, key, value, args.cfgTrackCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgTrackCuts)
            
            # analysis-muon-selection
            if value == "cfgMuonCuts" and args.cfgMuonCuts:
                multiConfigurableSet(config, key, value, args.cfgMuonCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgMuonCuts)
            
            # analysis-dilepton-hadron
            if value == "cfgLeptonCuts" and args.cfgLeptonCuts:
                multiConfigurableSet(config, key, value, args.cfgLeptonCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgLeptonCuts)
            
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
                
                if "VnJpsiToEE" in processCfg and value == "processVnJpsiToEESkimmed":
                    if isAnalysisTrackSelected:
                        config[key]["processVnJpsiToEESkimmed"] = "true"
                        logging.debug(" - [%s] %s : true", key, value)
                    if not isAnalysisTrackSelected:
                        logging.error("trackSelection not found in analysis for processVnJpsiToEESkimmed -> analysis-same-event-pairing")
                        sys.exit()
                if ("VnJpsiToEE" not in processCfg and value == "processVnJpsiToEESkimmed" and args.onlySelect == "true"):
                    config[key]["processVnJpsiToEESkimmed"] = "false"
                    logging.debug(" - [%s] %s : false", key, value)
                
                if "VnJpsiToMuMu" in processCfg and value == "processVnJpsiToMuMuSkimmed":
                    if isAnalysisMuonSelected:
                        config[key]["processVnJpsiToMuMuSkimmed"] = "true"
                        logging.debug(" - [%s] %s : true", key, value)
                    if not isAnalysisMuonSelected:
                        logging.error("muonSelection not found in analysis for processVnJpsiToMuMuSkimmed -> analysis-same-event-pairing")
                        sys.exit()
                if ("VnJpsiToMuMu" not in processCfg and value == "processVnJpsiToMuMuSkimmed" and args.onlySelect == "true"):
                    config[key]["processVnJpsiToMuMuSkimmed"] = "false"
                    logging.debug(" - [%s] %s : false", key, value)
                
                if "ElectronMuon" in processCfg and value == "processElectronMuonSkimmed":
                    if isAnalysisTrackSelected and isAnalysisMuonSelected:
                        config[key]["processElectronMuonSkimmed"] = "true"
                        logging.debug(" - [%s] %s : true", key, value)
                    else:
                        logging.error(
                            "trackSelection and muonSelection not found in analysis for processElectronMuonSkimmed -> analysis-same-event-pairing"
                            )
                        sys.exit()
                if ("ElectronMuon" not in processCfg and value == "processElectronMuonSkimmed" and args.onlySelect == "true"):
                    config[key]["processElectronMuonSkimmed"] = "false"
                    logging.debug(" - [%s] %s : false", key, value)
                
                if "All" in processCfg and value == "processAllSkimmed":
                    if (isAnalysisEventSelected and isAnalysisMuonSelected and isAnalysisTrackSelected):
                        config[key]["processAllSkimmed"] = "true"
                        logging.debug(" - [%s] %s : true", key, value)
                    else:
                        logging.debug(
                            "eventSelection, trackSelection and muonSelection not found in analysis for processAllSkimmed -> analysis-same-event-pairing"
                            )
                        sys.exit()
                if ("All" not in processCfg and value == "processAllSkimmed" and args.onlySelect == "true"):
                    config[key]["processAllSkimmed"] = "false"
                    logging.debug(" - [%s] %s : false", key, value)
            
            # If no process function is provided, all SEP process functions are pulled false (for JSON Overrider mode)
            if (
                key == "analysis-same-event-pairing" and args.process is None and not isAnalysisSameEventPairingSelected and
                args.onlySelect == "true"
                ):
                config[key]["processJpsiToEESkimmed"] = "false"
                config[key]["processJpsiToMuMuSkimmed"] = "false"
                config[key]["processJpsiToMuMuVertexingSkimmed"] = "false"
                config[key]["processVnJpsiToEESkimmed"] = "false"
                config[key]["processVnJpsiToMuMuSkimmed"] = "false"
                config[key]["processElectronMuonSkimmed"] = "false"
                config[key]["processAllSkimmed"] = "false"

processDummySet(config) # dummy automizer
aodFileChecker(args.aod)

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
updatedConfigFileName = "tempConfigTableReader.json"

with open(updatedConfigFileName, "w") as outputFile:
    json.dump(config, outputFile, indent = 2)

# commandToRun = taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " -b"
commandToRun = (taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " --aod-writer-json " + args.writer + " -b")

if args.writer == "false":
    commandToRun = (taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " -b")

print("====================================================================================================================")
logging.info("Command to run:")
logging.info(commandToRun)
print("====================================================================================================================")

# Listing Added Commands
dispArgs(allArgs)

os.system(commandToRun)

runPycacheRemover()
