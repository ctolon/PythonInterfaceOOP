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

# run template: `python3 runEMEfficiency.py <config.json> --task-name:<configurable|processFunc> parameter ...`
# parameter can be multiple like this:
# --analysis-track-selection:cfgTrackCuts jpsiPID1 jpsiPID2
# For run over Skimmed (run skimmed EM-Efficiency instead of not skimmed EM-Efficiency) You need to Set runOverSkimmed variable to true, if you don't convert it will work for interface not skimmed EM-Efficiency

import sys
import logging
import logging.config
import os
from extramodules.dqTranscations import mandatoryArgChecker, aodFileChecker, depsChecker, jsonTypeChecker, mainTaskChecker
from extramodules.configSetter import SetArgsToArgumentParser, commonDepsToRun, dispInterfaceMode, dispO2HelpMessage, setConfigs, debugSettings, setConverters, setProcessDummy, dispArgs, setSwitch
from extramodules.pycacheRemover import runPycacheRemover
from extramodules.utils import dumpJson, loadJson


def main():
    
    # Switch runOverSkimmed to True if you want work on skimmed em-efficiency else it will run for not skimmed em-efficiency
    runOverSkimmed = False
    
    # Simple protection
    if not isinstance(runOverSkimmed, bool):
        raise TypeError("[FATAL] runOverSkimmeed have to True or False! (in bool type)")
    
    # Load json config file for create interface arguments as skimmed or not skimmed
    parsedJsonFile = "configs/configAnalysisMCEM.json"
    if runOverSkimmed is True:
        parsedJsonFile = "configs/configAnalysisMCEMNoSkimmed.json"
    
    # All Dependencies
    commonDeps = ["o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table", "o2-analysis-trackselection", "o2-analysis-trackextension", "o2-analysis-pid-tof-base", "o2-analysis-pid-tof", "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta", "o2-analysis-pid-tpc-full"]
    
    # Setting arguments for CLI
    setArgsToArgumentParser = SetArgsToArgumentParser(parsedJsonFile, ["timestamp-task", "tof-event-time", "bc-selection-task", "tof-pid-beta"])
    args = setArgsToArgumentParser.parseArgs()
    dummyHasTasks = setArgsToArgumentParser.dummyHasTasks
    processFuncs = setArgsToArgumentParser.processFuncs
    allArgs = vars(args) # for get args
    
    # yapf: disable
    # All Dependencies
    sameEventPairingTaskName = "analysis-same-event-pairing"
    sameEventPairingDeps = {
        "processToEESkimmed": {"analysis-track-selection": "processSkimmed"}
        }
    # yapf: enable
    
    # Debug Settings
    fileName = "emEfficiencyEE.log"
    if runOverSkimmed is False:
        fileName = "emEfficiencyEENotSkimmed.log"
    debugSettings(args.debug, args.logFile, fileName)
    
    # if cliMode true, Overrider mode else additional mode
    cliMode = args.override
    
    # Basic validations
    jsonTypeChecker(args.cfgFileName)
    jsonTypeChecker(parsedJsonFile)
    
    # Load the configuration file provided as the first parameter
    config = loadJson(args.cfgFileName)
    
    taskNameInCommandLine = "o2-analysis-em-efficiency-ee"
    taskNameInConfig = "analysis-event-selection"
    
    mainTaskChecker(config, taskNameInConfig)
    
    # Interface Mode message
    dispInterfaceMode(cliMode)
    
    # Set arguments to config json file
    setConfigs(allArgs, config, cliMode)
    
    # process function automation based on cliMode
    setSwitch(config, processFuncs, allArgs, cliMode, [])
    
    # Transactions
    aodFileChecker(allArgs["internal_dpl_aod_reader:aod_file"])
    depsChecker(config, sameEventPairingDeps, sameEventPairingTaskName)
    mandatoryArgChecker(config, taskNameInConfig, "processSkimmed")
    setProcessDummy(config, dummyHasTasks) # dummy automizer
    
    if isinstance(args.aod_memory_rate_limit, type(None)):
        args.aod_memory_rate_limit = "6000000000"
    
    # Write the updated configuration file into a temporary file
    updatedConfigFileName = "tempConfigEMEfficiencyEE.json"
    if runOverSkimmed is False:
        updatedConfigFileName = "tempConfigEMEfficiencyEENoSkimmed.json"
    
    dumpJson(updatedConfigFileName, config)
    
    # Check which dependencies need to be run
    if runOverSkimmed is False:
        depsToRun = commonDepsToRun(commonDeps)
    
    commandToRun = f"{taskNameInCommandLine} --configuration json://{updatedConfigFileName} --severity error --shm-segment-size 12000000000 --aod-memory-rate-limit {args.aod_memory_rate_limit} -b"
    if runOverSkimmed is False:
        for dep in depsToRun.keys():
            commandToRun += " | " + dep + " --configuration json://" + updatedConfigFileName + " -b"
            logging.debug("%s added your workflow", dep)
    
    commandToRun = setConverters(allArgs, updatedConfigFileName, commandToRun)
    
    dispO2HelpMessage(args.helpO2, commandToRun)
    
    print("====================================================================================================================")
    logging.info("Command to run:")
    logging.info(commandToRun)
    print("====================================================================================================================")
    if runOverSkimmed is False:
        logging.info("Deps to run:")
        logging.info(depsToRun.keys())
        print("====================================================================================================================")
    dispArgs(allArgs) # Display all args
    os.system(commandToRun) # Execute O2 generated commands
    runPycacheRemover() # Run pycacheRemover


if __name__ == '__main__':
    sys.exit(main())
