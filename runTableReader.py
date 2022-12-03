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
import logging
import logging.config
import os
import sys
from extramodules.dqTranscations import mandatoryArgChecker, aodFileChecker, depsChecker, forgettedArgsChecker, jsonTypeChecker, mainTaskChecker, oneToMultiDepsChecker
from extramodules.configSetter import setConfig, setFalseHasDeps, setSwitch, setSelection, setProcessDummy, debugSettings, dispArgs, setPrefixSuffix
from extramodules.pycacheRemover import runPycacheRemover
from dqtasks.tableReader import TableReader

def main():
    # Predefined selections for setSwitch function
    sameEventPairingParameters = [
        "processDecayToEESkimmed", "processDecayToMuMuSkimmed", "processDecayToMuMuVertexingSkimmed", "processVnDecayToEESkimmed",
        "processVnDecayToMuMuSkimmed", "processElectronMuonSkimmed", "processAllSkimmed", "processDecayToEEPrefilterSkimmed"
        ]

    eventMixingParameters = [
        "processBarrelSkimmed", "processMuonSkimmed", "processBarrelMuonSkimmed", "processBarrelVnSkimmed", "processMuonVnSkimmed"
        ]
    # yapf: disable
    # All Dependencies
    analysisSelectionDeps = {
        "trackSelection": {"analysis-track-selection": "processSkimmed"},
        "prefilterSelection": {"analysis-prefilter-selection": "processBarrelSkimmed"},
        "eventSelection": {"analysis-event-selection": "processSkimmed"},
        "muonSelection": {"analysis-muon-selection": "processSkimmed"},
        "dileptonHadron": {"analysis-dilepton-hadron": "processSkimmed"}
        }
    sameEventTaskName = "analysis-same-event-pairing"
    sameEventPairingDeps = {
        "processDecayToEESkimmed": {"analysis-track-selection": "processSkimmed"},
        "processDecayToEEPrefilterSkimmed": {"analysis-track-selection": "processSkimmed","analysis-prefilter-selection" : "processBarrelSkimmed"},
        "processDecayToMuMuSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processDecayToMuMuVertexingSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processVnDecayToEESkimmed": {"analysis-track-selection": "processSkimmed"},
        "processVnDecayToMuMuSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processElectronMuonSkimmed": {"analysis-track-selection": "processSkimmed","analysis-muon-selection": "processSkimmed"},
        "processAllSkimmed": {"analysis-track-selection": "processSkimmed","analysis-muon-selection": "processSkimmed"},
        }
    eventMixingTaskName = "analysis-event-mixing"
    eventMixingDeps = {
        "processBarrelSkimmed": {"analysis-track-selection": "processSkimmed"},
        "processMuonSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processBarrelMuonSkimmed": {"analysis-track-selection": "processSkimmed","analysis-muon-selection": "processSkimmed"},
        "processBarrelVnSkimmed": {"analysis-track-selection": "processSkimmed"},
        "processMuonVnSkimmed": {"analysis-muon-selection": "processSkimmed"}
        }
    # yapf: enable

    # init args manually
    initArgs = TableReader()
    initArgs.mergeArgs()
    initArgs.parseArgs()
    args = initArgs.parseArgs()
    allArgs = vars(args) # for get args

    # Debug settings
    debugSettings(args.debug, args.logFile, fileName = "tableReader.log")

    # if cliMode true, Overrider mode else additional mode
    cliMode = args.onlySelect

    # Transaction
    #forgettedArgsChecker(allArgs) # Transaction Management

    # adding prefix for setSwitch function
    args.process = setPrefixSuffix(args.process, "process", 'Skimmed', True, True)
    args.mixing = setPrefixSuffix(args.mixing, "process", 'Skimmed', True, True)

    # Load the configuration file provided as the first parameter
    config = {}
    with open(args.cfgFileName) as configFile:
        config = json.load(configFile)

    # Transaction
    jsonTypeChecker(args.cfgFileName)

    taskNameInCommandLine = "o2-analysis-dq-table-reader"
    taskNameInConfig = "analysis-event-selection"

    # Transaction
    mainTaskChecker(config, taskNameInConfig)

    # Interface Process
    logging.info("Only Select Configured as %s", args.onlySelect)
    if args.onlySelect == "true":
        logging.info("INTERFACE MODE : JSON Overrider")
    if args.onlySelect == "false":
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
                setSwitch(config, task, cfg, allArgs, cliMode, "mixing", eventMixingParameters, "true/false")
                setFalseHasDeps(config, task, cfg, args.process, sameEventPairingParameters, cliMode)
                if task != "analysis-prefilter-selection": # we have processBarrelSkimmed option in analysis-prefilter-selection and for not overriding it other processBarrelSkimmed option, we have to specifiy task
                    setFalseHasDeps(config, task, cfg, args.mixing, eventMixingParameters, cliMode)
                mandatoryArgChecker(config, task, cfg, taskNameInConfig, "processSkimmed")

    setProcessDummy(config) # dummy automizer

    # Transacations
    aodFileChecker(args.aod)
    oneToMultiDepsChecker(args.mixing, "eventMixing", args.analysis, "analysis")
    oneToMultiDepsChecker(args.process, "sameEventPairing", args.analysis, "analysis")
    depsChecker(config, sameEventPairingDeps, sameEventTaskName)
    depsChecker(config, eventMixingDeps, eventMixingTaskName)

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
    dispArgs(allArgs) # Display all args
    os.system(commandToRun) # Execute O2 generated commands
    runPycacheRemover() # Run pycacheRemover
    
if __name__ == '__main__':
    sys.exit(main())
