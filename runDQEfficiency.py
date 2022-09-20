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
import os
from extramodules.configGetter import configGetter
from extramodules.debugSettings import debugSettings

from extramodules.monitoring import dispArgs
from extramodules.dqTranscations import aodFileChecker, forgettedArgsChecker, jsonTypeChecker, mainTaskChecker
from extramodules.configSetter import multiConfigurableSet, processDummySet
from extramodules.pycacheRemover import runPycacheRemover

from dqtasks.dqEfficiency import DQEfficiency

###################################
# Interface Predefined Selections #
###################################

booleanSelections = ["true", "false"]

isAnalysisEventSelected = True
isAnalysisTrackSelected = True
isAnalysisMuonSelected = True
isAnalysisSameEventPairingSelected = True

# init args manually
initArgs = DQEfficiency()
initArgs.mergeArgs()
initArgs.parseArgs()

args = initArgs.parseArgs()
allArgs = vars(args) # for get args

# Debug Settings
debugSettings(args.debug, args.logFile, fileName = "dqEfficiency.log")

# Transcation management
forgettedArgsChecker(allArgs)

# Get Some cfg values provided from --param
analysisCfg = configGetter(allArgs, "analysis")
processCfg = configGetter(allArgs, "process")

# Load the configuration file provided as the first parameter
config = {}
with open(args.cfgFileName) as configFile:
    config = json.load(configFile)

jsonTypeChecker(args.cfgFileName)

taskNameInCommandLine = "o2-analysis-dq-efficiency"
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
dispArgs(allArgs)

os.system(commandToRun)

runPycacheRemover()
