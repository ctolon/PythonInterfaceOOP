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
import logging
import logging.config
import os
from extramodules.dqTranscations import MandatoryArgChecker, aodFileChecker, depsChecker, forgettedArgsChecker, jsonTypeChecker, mainTaskChecker, oneToMultiDepsChecker
from extramodules.configSetter import CONFIG_SET, NOT_CONFIGURED_SET_FALSE, PROCESS_SWITCH, SELECTION_SET, debugSettings, PROCESS_DUMMY, dispArgs, multiConfigurableSet, prefixSuffixSet
from extramodules.pycacheRemover import runPycacheRemover
from dqtasks.dqEfficiency import DQEfficiency

# Predefined selections for PROCESS_SWITCH function
sepParameters = ["processJpsiToEESkimmed", "processJpsiToMuMuSkimmed", "processJpsiToMuMuVertexingSkimmed"]
# yapf: disable
# All Dependencies
analysisSelectionDeps = {
    "trackSelection": {"analysis-track-selection": "processSkimmed"},
    "eventSelection": {"analysis-event-selection": "processSkimmed"},
    "muonSelection": {"analysis-muon-selection": "processSkimmed"},
    "dileptonTrackDimuonMuonSelection": {"analysis-dilepton-track": "processDimuonMuonSkimmed"},
    "dileptonTrackDielectronKaonSelection": {"analysis-dilepton-track": "processDielectronKaonSkimmed"}
    }
sepKey = "analysis-same-event-pairing"
sepDeps = {
    "processJpsiToEESkimmed": {"analysis-track-selection": "processSkimmed"},
    "processJpsiToMuMuSkimmed": {"analysis-muon-selection": "processSkimmed"},
    "processJpsiToMuMuVertexingSkimmed": {"analysis-muon-selection": "processSkimmed"}
    }
dileptonTrackKey = "analysis-dilepton-track"
dileptonTrackDeps = {
    "processDimuonMuonSkimmed": {"analysis-muon-selection": "processSkimmed"},
    "processDielectronKaonSkimmed": {"analysis-track-selection": "processSkimmed"}
    }
# yapf: enable
# init args manually
initArgs = DQEfficiency()
initArgs.mergeArgs()
initArgs.parseArgs()
args = initArgs.parseArgs()
allArgs = vars(args) # for get args

# Debug Settings
debugSettings(args.debug, args.logFile, fileName = "dqEfficiency.log")

# if cliMode true, Overrider mode else additional mode
cliMode = args.onlySelect

forgettedArgsChecker(allArgs) # Transcation management

# adding prefix for PROCESS_SWITCH function (for no kFlag True situations)
args.process = prefixSuffixSet(args.process, "process", 'Skimmed', True, True)

# Load the configuration file provided as the first parameter
config = {}
with open(args.cfgFileName) as configFile:
    config = json.load(configFile)

jsonTypeChecker(args.cfgFileName)

taskNameInCommandLine = "o2-analysis-dq-efficiency"
taskNameInConfig = "analysis-event-selection"

mainTaskChecker(config, taskNameInConfig)

# Interface Process
logging.info("Only Select Configured as %s", cliMode)
if cliMode == "true":
    logging.info("INTERFACE MODE : JSON Overrider")
if cliMode == "false":
    logging.info("INTERFACE MODE : JSON Additional")

SELECTION_SET(config, analysisSelectionDeps, args.analysis, cliMode) # Set selections

# Iterating in JSON config file
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
                        
            # Interface Logic
            CONFIG_SET(config, key, value, allArgs, cliMode)
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "process", sepParameters, "true/false")
            NOT_CONFIGURED_SET_FALSE(config, key, value, args.process, sepParameters, cliMode)
            MandatoryArgChecker(config, key, value, taskNameInConfig, "processSkimmed")
            
            # analysis-dilepton-track # TODO Discuss naming conventions regarding to string conflicts, dilepton track signals should have unique name
            if key == "analysis-dilepton-track":
                if value == "cfgBarrelMCRecSignals" and args.cfgBarrelDileptonMCRecSignals:
                    multiConfigurableSet(config, key, value, args.cfgBarrelDileptonMCRecSignals, cliMode)
                    logging.debug(" - [%s] %s : %s", key, value, args.cfgBarrelDileptonMCRecSignals)
                
                if value == "cfgBarrelMCGenSignals" and args.cfgBarrelDileptonMCGenSignals:
                    multiConfigurableSet(config, key, value, args.cfgBarrelDileptonMCGenSignals, cliMode)
                    logging.debug(" - [%s] %s : %s", key, value, args.cfgBarrelDileptonMCGenSignals)

PROCESS_DUMMY(config) # dummy automizer

# Transactions
aodFileChecker(args.aod)
oneToMultiDepsChecker(args.process, "sameEventPairing", args.analysis, "analysis")
depsChecker(config, sepDeps, sepKey)
depsChecker(config, dileptonTrackDeps, dileptonTrackKey)

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
dispArgs(allArgs) # Display all args
os.system(commandToRun) # Execute O2 generated commands
runPycacheRemover() # Run pycacheRemover
