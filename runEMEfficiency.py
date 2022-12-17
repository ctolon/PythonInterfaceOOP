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
from extramodules.dqTranscations import mandatoryArgChecker, aodFileChecker, depsChecker, jsonTypeChecker, mainTaskChecker
from extramodules.configSetter import setArgsToArgParser, setConfigs, debugSettings, setProcessDummy, dispArgs
from extramodules.pycacheRemover import runPycacheRemover


def main():
    
    # Setting arguments for CLI
    parsedJsonFile = "configs/configAnalysisMCEM.json.json"
    args = setArgsToArgParser(parsedJsonFile)
    allArgs = vars(args) # for get args
        
    # yapf: disable
    # All Dependencies
    sameEventPairingTaskName = "analysis-same-event-pairing"
    sameEventPairingDeps = {
        "processToEESkimmed": {"analysis-track-selection": "processSkimmed"}
        }
    # yapf: enable
    
    # Debug Settings
    debugSettings(args.debug, args.logFile, fileName = "emEfficiencyEE.log")
    
    # if cliMode true, Overrider mode else additional mode
    cliMode = args.onlySelect
    
    # Load the configuration file provided as the first parameter
    config = {}
    with open(args.cfgFileName) as configFile:
        config = json.load(configFile)
    
    jsonTypeChecker(args.cfgFileName)
    jsonTypeChecker(parsedJsonFile)
    
    taskNameInCommandLine = "o2-analysis-em-efficiency-ee"
    taskNameInConfig = "analysis-event-selection"
    
    mainTaskChecker(config, taskNameInConfig)
    
    # Interface Process
    logging.info("Only Select Configured as %s", cliMode)
    if cliMode == "true":
        logging.info("INTERFACE MODE : JSON Overrider")
    if cliMode == "false":
        logging.info("INTERFACE MODE : JSON Additional")
    
    # Set arguments to config json file
    setConfigs(allArgs, config, cliMode)
    
    # Transactions
    aodFileChecker(allArgs["internal_dpl_aod_reader:aod_file"])
    depsChecker(config, sameEventPairingDeps, sameEventPairingTaskName)
    mandatoryArgChecker(config, taskNameInConfig, "processSkimmed")
    setProcessDummy(config) # dummy automizer
    
    if isinstance(args.aod_memory_rate_limit, type(None)):
        args.aod_memory_rate_limit = "6000000000"
    
    # Write the updated configuration file into a temporary file
    updatedConfigFileName = "tempConfigEMEfficiencyEE.json"
    
    with open(updatedConfigFileName, "w") as outputFile:
        json.dump(config, outputFile, indent = 2)
    
    commandToRun = (taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " -b" + " --shm-segment-size 12000000000 --aod-memory-rate-limit " + args.aod_memory_rate_limit)
    
    print("====================================================================================================================")
    logging.info("Command to run:")
    logging.info(commandToRun)
    print("====================================================================================================================")
    dispArgs(allArgs) # Display all args
    os.system(commandToRun) # Execute O2 generated commands
    runPycacheRemover() # Run pycacheRemover


if __name__ == '__main__':
    sys.exit(main())
