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
from extramodules.dqTranscations import mandatoryArgChecker, aodFileChecker, depsChecker, forgettedArgsChecker, jsonTypeChecker, mainTaskChecker, oneToMultiDepsChecker
from extramodules.configSetter import setConfig, setFalseHasDeps, setSwitch, setSelection, debugSettings, setProcessDummy, dispArgs, multiConfigurableSet, setPrefixSuffix
from extramodules.pycacheRemover import runPycacheRemover
from dqtasks.dqEfficiency import DQEfficiency

# Predefined selections for setSwitch function
sameEventPairingParameters = ["processDecayToEESkimmed", "processDecayToMuMuSkimmed", "processDecayToMuMuVertexingSkimmed"]
# yapf: disable
# All Dependencies
analysisSelectionDeps = {
    "trackSelection": {"analysis-track-selection": "processSkimmed"},
    "eventSelection": {"analysis-event-selection": "processSkimmed"},
    "muonSelection": {"analysis-muon-selection": "processSkimmed"},
    "dileptonTrackDimuonMuonSelection": {"analysis-dilepton-track": "processDimuonMuonSkimmed"},
    "dileptonTrackDielectronKaonSelection": {"analysis-dilepton-track": "processDielectronKaonSkimmed"}
    }
sameEventPairingTaskName = "analysis-same-event-pairing"
sameEventPairingDeps = {
    "processDecayToEESkimmed": {"analysis-track-selection": "processSkimmed"},
    "processDecayToEEVertexingSkimmed": {"analysis-track-selection": "processSkimmed"},
    "processDecayToMuMuSkimmed": {"analysis-muon-selection": "processSkimmed"},
    "processDecayToMuMuVertexingSkimmed": {"analysis-muon-selection": "processSkimmed"}
    }
dileptonTrackTaskName = "analysis-dilepton-track"
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

#forgettedArgsChecker(allArgs) # Transaction management

# adding prefix for setSwitch function
args.process = setPrefixSuffix(args.process, "process", 'Skimmed', True, True)

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

setSelection(config, analysisSelectionDeps, args.analysis, cliMode) # Set selections

# Iterating in JSON config file
for task, cfgValuePair in config.items():
    if isinstance(cfgValuePair, dict):
        for cfg, value in cfgValuePair.items():
            
            # aod
            if cfg == "aod-file" and args.aod:
                config[task][cfg] = args.aod
                logging.debug(" - [%s] %s : %s", task, cfg, args.aod)
            # reader
            if cfg == "aod-reader-json" and args.reader:
                config[task][cfg] = args.reader
                logging.debug(" - [%s] %s : %s", task, cfg, args.reader)
            
            # Interface Logic
            setConfig(config, task, cfg, allArgs, cliMode)
            setSwitch(config, task, cfg, allArgs, cliMode, "process", sameEventPairingParameters, "true/false")
            setFalseHasDeps(config, task, cfg, args.process, sameEventPairingParameters, cliMode)
            mandatoryArgChecker(config, task, cfg, taskNameInConfig, "processSkimmed")
            
            # analysis-dilepton-track # TODO Discuss naming conventions regarding to string conflicts, dilepton track signals should have unique name
            if task == "analysis-dilepton-track":
                if cfg == "cfgBarrelMCRecSignals" and args.cfgBarrelDileptonMCRecSignals:
                    multiConfigurableSet(config, task, cfg, args.cfgBarrelDileptonMCRecSignals, cliMode)
                    logging.debug(" - [%s] %s : %s", task, cfg, args.cfgBarrelDileptonMCRecSignals)
                
                if cfg == "cfgBarrelMCGenSignals" and args.cfgBarrelDileptonMCGenSignals:
                    multiConfigurableSet(config, task, cfg, args.cfgBarrelDileptonMCGenSignals, cliMode)
                    logging.debug(" - [%s] %s : %s", task, cfg, args.cfgBarrelDileptonMCGenSignals)

setProcessDummy(config) # dummy automizer

# Transactions
aodFileChecker(args.aod)
oneToMultiDepsChecker(args.process, "sameEventPairing", args.analysis, "analysis")
depsChecker(config, sameEventPairingDeps, sameEventPairingTaskName)
depsChecker(config, dileptonTrackDeps, dileptonTrackTaskName)

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
