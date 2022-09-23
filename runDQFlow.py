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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqFlow.cxx

import json
import logging
import logging.config
import os
from extramodules.dqTranscations import aodFileChecker, forgettedArgsChecker, jsonTypeChecker, mainTaskChecker, trackPropagationChecker
from extramodules.configSetter import setSwitch, setConverters, setConfig, debugSettings, dispArgs, setPrefixSuffix
from extramodules.pycacheRemover import runPycacheRemover
from dqtasks.dqFlow import AnalysisQvector

# Predefined selections for setSwitch function
centralityTableParameters = [
    "estRun2V0M", "estRun2SPDtks", "estRun2SPDcls", "estRun2CL0", "estRun2CL1", "estFV0A", "estFT0M", "estFDDM", "estNTPV",
    ]
ft0Parameters = ["processFT0", "processNoFT0", "processOnlyFT0", "processRun2"]
pidParameters = ["pid-el", "pid-mu", "pid-pi", "pid-ka", "pid-pr", "pid-de", "pid-tr", "pid-he", "pid-al"]
covParameters = ["processStandard", "processCovariance"]
sliceParameters = ["processWoSlice", "processWSlice"]
vertexParameters = ["doVertexZeq", "doDummyZeq"]

# All Dependencies
commonDeps = [
    "o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table", "o2-analysis-centrality-table",
    "o2-analysis-trackselection", "o2-analysis-trackextension", "o2-analysis-pid-tof-base", "o2-analysis-pid-tof-full",
    "o2-analysis-pid-tof-beta", "o2-analysis-pid-tpc-full"
    ]

# init args manually
initArgs = AnalysisQvector()
initArgs.mergeArgs()
initArgs.parseArgs()
args = initArgs.parseArgs()
allArgs = vars(args) # for get args

# Debug Settings
debugSettings(args.debug, args.logFile, fileName = "dqFlow.log")

# if cliMode true, Overrider mode else additional mode
cliMode = args.onlySelect

forgettedArgsChecker(allArgs) # Transaction Management

# adding prefix for setSwitch function (for no kFlag True situations)
args.pid = setPrefixSuffix(args.pid, "pid-", '', True, False)
args.est = setPrefixSuffix(args.est, "est", '', True, False)
args.FTO = setPrefixSuffix(args.FT0, "process", '', True, False)
args.isCovariance = setPrefixSuffix(args.isCovariance, "process", '', True, False)
args.isWSlice = setPrefixSuffix(args.isWSlice, "process", '', True, False)

# Load the configuration file provided as the first parameter
config = {}
with open(args.cfgFileName) as configFile:
    config = json.load(configFile)

jsonTypeChecker(args.cfgFileName)

taskNameInConfig = "analysis-qvector"
taskNameInCommandLine = "o2-analysis-dq-flow"

mainTaskChecker(config, taskNameInConfig)

# Interface Process
logging.info("Only Select Configured as %s", args.onlySelect)
if args.onlySelect == "true":
    logging.info("INTERFACE MODE : JSON Overrider")
if args.onlySelect == "false":
    logging.info("INTERFACE MODE : JSON Additional")

# Iterating in JSON config file
for task, cfgValuePair in config.items():
    if isinstance(cfgValuePair, dict):
        for cfg, value in cfgValuePair.items():
            
            # aod
            if cfg == "aod-file" and args.aod:
                config[task][cfg] = args.aod
                logging.debug(" - [%s] %s : %s", task, cfg, args.aod)
            
            # For don't override tof-pid: pid tables. We use instead of tof-pid-full and tpc-pid-full for pid tables
            if task == "tof-pid" and cfg.startswith("pid"):
                continue
            
            setConfig(config, task, cfg, allArgs, cliMode)
            setSwitch(config, task, cfg, allArgs, cliMode, "est", centralityTableParameters, "1/-1")
            setSwitch(config, task, cfg, allArgs, cliMode, "pid", pidParameters, "1/-1")
            setSwitch(config, task, cfg, allArgs, "true", "isCovariance", covParameters, "true/false")
            setSwitch(config, task, cfg, allArgs, "true", "isWSlice", sliceParameters, "true/false")
            if task == "tof-event-time": # we have processRun2 option in tof-event-time and for not overriding it other processRun2 options, we have to specifiy task
                setSwitch(config, task, cfg, allArgs, "true", "FT0", ft0Parameters, "true/false")
            setSwitch(config, task, cfg, allArgs, cliMode, "isVertexZeq", vertexParameters, "1/0", True)

# Transactions
aodFileChecker(args.aod)
trackPropagationChecker(args.add_track_prop, commonDeps)

# Write the updated configuration file into a temporary file
updatedConfigFileName = "tempConfigDQFlow.json"
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

commandToRun = setConverters(
    args.add_mc_conv, args.add_fdd_conv, args.add_track_prop, args.add_weakdecay_ind, updatedConfigFileName, commandToRun
    )

print("====================================================================================================================")
logging.info("Command to run:")
logging.info(commandToRun)
print("====================================================================================================================")
dispArgs(allArgs) # Display all args
os.system(commandToRun) # Execute O2 generated commands
runPycacheRemover() # Run pycacheRemover
