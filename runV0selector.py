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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/v0selector.cxx

import json
import logging
import logging.config
import os
from extramodules.configSetter import PROCESS_SWITCH, converterSet, CONFIG_SET, debugSettings
from extramodules.monitoring import dispArgs
from extramodules.dqTranscations import aodFileChecker, forgettedArgsChecker, jsonTypeChecker, mainTaskChecker, trackPropTransaction
from extramodules.pycacheRemover import runPycacheRemover
from dqtasks.v0selector import V0selector

# Predefined selections for PROCESS_SWITCH function
centralityTableParameters = [
    "estRun2V0M", "estRun2SPDtks", "estRun2SPDcls", "estRun2CL0", "estRun2CL1", "estFV0A", "estFT0M", "estFDDM", "estNTPV",
    ]

ft0Parameters = ["processFT0", "processNoFT0", "processOnlyFT0", "processRun2"]
pidParameters = ["pid-el", "pid-mu", "pid-pi", "pid-ka", "pid-pr", "pid-de", "pid-tr", "pid-he", "pid-al",]
covParameters = ["processStandard", "processCovariance"]
sliceParameters = ["processWoSlice", "processWSlice"]
vertexParameters = ["doVertexZeq", "doDummyZeq"]

# All Dependencies
commonDeps = [
    "o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table", "o2-analysis-trackselection",
    "o2-analysis-trackextension", "o2-analysis-pid-tof-base", "o2-analysis-pid-tof", "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta",
    "o2-analysis-pid-tpc-full"
    ]

# init args manually
initArgs = V0selector()
initArgs.mergeArgs()
initArgs.parseArgs()
args = initArgs.parseArgs()
allArgs = vars(args) # for get args

# Debug Settings
debugSettings(args.debug, args.logFile, fileName = "v0selector.log")

# if cliMode true, Overrider mode else additional mode
cliMode = args.onlySelect

forgettedArgsChecker(allArgs) # Transaction management

# adding prefix for PROCESS_SWITCH function (for no kFlag True situations)
if args.pid is not None:
    prefix_pid = "pid-"
    args.pid = [prefix_pid + sub for sub in args.pid]

if args.FT0 is not None:
    prefix_process = "process"
    args.FT0 = prefix_process + args.FT0

# Load the configuration file provided as the first parameter
config = {}
with open(args.cfgFileName) as configFile:
    config = json.load(configFile)

jsonTypeChecker(args.cfgFileName)

taskNameInConfig = "v0-selector"
taskNameInCommandLine = "o2-analysis-dq-v0-selector"

mainTaskChecker(config, taskNameInConfig)

# Interface Process
logging.info("Only Select Configured as %s", args.onlySelect)
if args.onlySelect == "true":
    logging.info("INTERFACE MODE : JSON Overrider")
if args.onlySelect == "false":
    logging.info("INTERFACE MODE : JSON Additional")

# Iterating in JSON config file
for key, value in config.items():
    if isinstance(value, dict):
        for value, value2 in value.items():
            
            # aod
            if value == "aod-file" and args.aod:
                config[key][value] = args.aod
                logging.debug(" - [%s] %s : %s", key, value, args.aod)
            
            # For don't override tof-pid. We use instead of tof-pid-full and tpc-pid-full for pid tables
            if key == "tof-pid":
                continue
            
            CONFIG_SET(config, key, value, allArgs, cliMode)
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "est", centralityTableParameters, "1/-1")
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "pid", pidParameters, "1/-1")
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "isCovariance", covParameters, "true/false", True)
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "isWSlice", sliceParameters, "true/false", True)
            if key == "tof-event-time": # we have processRun2 option in tof-event-time and for not overriding it other processRun2 options, we have to specifiy key
                PROCESS_SWITCH(config, key, value, allArgs, "true", "FT0", ft0Parameters, "true/false")
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "isVertexZeq", vertexParameters, "1/0", True)

# Transactions
aodFileChecker(args.aod)
trackPropTransaction(args.add_track_prop, commonDeps)

# Write the updated configuration file into a temporary file
updatedConfigFileName = "tempConfigV0Selector.json"

with open(updatedConfigFileName, "w") as outputFile:
    json.dump(config, outputFile, indent = 2)

# Check which dependencies need to be run
depsToRun = {}
for dep in commonDeps:
    depsToRun[dep] = 1

commandToRun = (
    taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " --severity error --shm-segment-size 12000000000 -b"
    )
for dep in depsToRun.keys():
    commandToRun += " | " + dep + " --configuration json://" + updatedConfigFileName + " -b"
    logging.debug("%s added your workflow", dep)

commandToRun = converterSet(
    args.add_mc_conv, args.add_fdd_conv, args.add_track_prop, args.add_weakdecay_ind, updatedConfigFileName, commandToRun
    )

print("====================================================================================================================")
logging.info("Command to run:")
logging.info(commandToRun)
print("====================================================================================================================")
dispArgs(allArgs) # Display all args
os.system(commandToRun) # Execute O2 generated commands
runPycacheRemover() # Run pycacheRemover
