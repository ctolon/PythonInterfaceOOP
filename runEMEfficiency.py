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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGEM/Dilepton/Tasks/emEfficiencyEE.cxx

import json
import sys
import logging
import logging.config
import os
from extramodules.dqTranscations import mandatoryArgChecker, aodFileChecker, depsChecker, forgettedArgsChecker, jsonTypeChecker, mainTaskChecker, oneToMultiDepsChecker
from extramodules.configSetter import setConfig, setFalseHasDeps, setSwitch, setSelection, debugSettings, setProcessDummy, dispArgs, multiConfigurableSet, setPrefixSuffix
from extramodules.pycacheRemover import runPycacheRemover
from dqtasks.emEfficiency import EMEfficiency

def main():

    # Predefined selections for setSwitch function
    sameEventPairingParameters = ["processToEESkimmed"]
    # yapf: disable
    # All Dependencies
    analysisSelectionDeps = {
        "trackSelection": {"analysis-track-selection": "processSkimmed"},
        "eventSelection": {"analysis-event-selection": "processSkimmed"},
        "eventQA": {"analysis-event-qa": "processSkimmed"}
        }
    sameEventPairingTaskName = "analysis-same-event-pairing"
    sameEventPairingDeps = {
        "processToEESkimmed": {"analysis-track-selection": "processSkimmed"}
        }
    # yapf: enable
    # init args manually
    initArgs = EMEfficiency()
    initArgs.mergeArgs()
    initArgs.parseArgs()
    args = initArgs.parseArgs()
    allArgs = vars(args) # for get args

    # Debug Settings
    debugSettings(args.debug, args.logFile, fileName = "emEfficiencyEE.log")

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

    taskNameInCommandLine = "o2-analysis-em-efficiency-ee"
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

    setProcessDummy(config) # dummy automizer

    # Transactions
    aodFileChecker(args.aod)
    oneToMultiDepsChecker(args.process, "sameEventPairing", args.analysis, "analysis")
    depsChecker(config, sameEventPairingDeps, sameEventPairingTaskName)
    

    # TODO Prepare global options
    # disable writer for dilepton producing
    args.writer = "false"
    
    if isinstance(args.aod_memory_rate_limit, type(None)):
        args.aod_memory_rate_limit = "6000000000"

    # Write the updated configuration file into a temporary file
    updatedConfigFileName = "tempConfigEMEfficiencyEE.json"

    with open(updatedConfigFileName, "w") as outputFile:
        json.dump(config, outputFile, indent = 2)

    # NOTE: writer options is now always false for memory optimization (don't need produce any dileptonAod)
    # commandToRun = (taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " -b" + " --aod-writer-json " + args.writer)
    if args.writer == "false":
        commandToRun = (taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " -b" + " --shm-segment-size 12000000000 \
        --aod-memory-rate-limit " + args.aod_memory_rate_limit)
        

    print("====================================================================================================================")
    logging.info("Command to run:")
    logging.info(commandToRun)
    print("====================================================================================================================")
    dispArgs(allArgs) # Display all args
    os.system(commandToRun) # Execute O2 generated commands
    runPycacheRemover() # Run pycacheRemover
    
if __name__ == '__main__':
    sys.exit(main())
