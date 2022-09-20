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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/filterPP.cxx

import json
import logging
import logging.config
import os

from extramodules.configGetter import configGetter
from extramodules.monitoring import dispArgs
from extramodules.dqTranscations import aodFileChecker, forgettedArgsChecker, jsonTypeChecker, filterSelsTranscation, mainTaskChecker, trackPropTransaction
from extramodules.configSetter import PROCESS_SWITCH, SELECTION_SET, converterSet, CONFIG_SET, PROCESS_DUMMY, debugSettings
from extramodules.pycacheRemover import runPycacheRemover

from dqtasks.filterPP import DQFilterPPTask

###################################
# Interface Predefined Selections #
###################################

centralityTableParameters = [
    "estRun2V0M", "estRun2SPDtks", "estRun2SPDcls", "estRun2CL0", "estRun2CL1", "estFV0A", "estFT0M", "estFDDM", "estNTPV",
    ]
# TODO: Add genname parameter

ft0Parameters = ["processFT0", "processNoFT0", "processOnlyFT0", "processRun2"]

pidParameters = ["pid-el", "pid-mu", "pid-pi", "pid-ka", "pid-pr", "pid-de", "pid-tr", "pid-he", "pid-al",]

booleanSelections = ["true", "false"]

covParameters = ["processStandard", "processCovariance"]

sliceParameters = ["processWoSlice", "processWSlice"]

vertexParameters = ["doVertexZeq", "doDummyZeq"]

################
# Dependencies #
################

commonDeps = [
    "o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table", "o2-analysis-trackselection",
    "o2-analysis-trackextension", "o2-analysis-pid-tof-base", "o2-analysis-pid-tof", "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta",
    "o2-analysis-pid-tpc-full",
    ]

selectionDeps = {
    "barrelTrackSelection": ["d-q-barrel-track-selection", "processSelection"],
    "barrelTrackSelectionTiny": ["d-q-barrel-track-selection", "processSelectionTiny"],
    "muonSelection": ["d-q-muons-selection", "processSelection"],
    "filterPPSelectionTiny": ["d-q-filter-p-p-task", "processFilterPPTiny"]
    }

dummyHasTasks = ["d-q-barrel-track-selection", "d-q-muons-selection", "d-q-filter-p-p-task"]

# init args manually
initArgs = DQFilterPPTask()
initArgs.mergeArgs()
initArgs.parseArgs()

args = initArgs.parseArgs()
allArgs = vars(args) # for get args

# if cliMode true, Overrider mode else additional mode
cliMode = args.onlySelect

# Debug Settings
debugSettings(args.debug, args.logFile, fileName = "filterPP.log")

forgettedArgsChecker(allArgs)

processCfg = configGetter(allArgs, "process")

######################
# PREFIX ADDING PART #
######################

# add prefix for args.pid for pid selection
if args.pid is not None:
    prefix_pid = "pid-"
    args.pid = [prefix_pid + sub for sub in args.pid]

# add prefix for args.FT0 for tof-event-time
if args.FT0 is not None:
    prefix_process = "process"
    args.FT0 = prefix_process + args.FT0

######################################################################################

# Load the configuration file provided as the first parameter
config = {}
with open(args.cfgFileName) as configFile:
    config = json.load(configFile)

jsonTypeChecker(args.cfgFileName)

taskNameInConfig = "d-q-filter-p-p-task"
taskNameInCommandLine = "o2-analysis-dq-filter-pp"

mainTaskChecker(config, taskNameInConfig)

#############################
# Start Interface Processes #
#############################

logging.info("Only Select Configured as %s", args.onlySelect)
if args.onlySelect == "true":
    logging.info("INTERFACE MODE : JSON Overrider")
if args.onlySelect == "false":
    logging.info("INTERFACE MODE : JSON Additional")

SELECTION_SET(config, selectionDeps, processCfg, cliMode)

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
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "pid", pidParameters, "1/-1")
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "isCovariance", covParameters, "true/false", True)
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "isWSlice", sliceParameters, "true/false", True)
            if key == "tof-event-time": # we have processRun2 option in tof-event-time and for not overriding it other processRun2 options, we have to specifiy key
                PROCESS_SWITCH(config, key, value, allArgs, "true", "FT0", ft0Parameters, "true/false")
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "isVertexZeq", vertexParameters, "1/0", True)

PROCESS_DUMMY(config, dummyHasTasks)
# Transactions
filterSelsTranscation(args.cfgBarrelSels, args.cfgMuonSels, args.cfgBarrelTrackCuts, args.cfgMuonsCuts, allArgs)
aodFileChecker(args.aod)
trackPropTransaction(args.add_track_prop, commonDeps)
"""
# Regarding to perfomance issues in argcomplete package, we should import later
from extramodules.getTTrees import getTTrees

# Converter Management
if args.aod is not None:
    ttreeList = getTTrees(args.aod)
else:
    ttreeList = config["internal-dpl-aod-reader"]["aod-file"]

converterManager(ttreeList, commonDeps)
trackPropChecker(commonDeps, commonDeps)
"""

###########################
# End Interface Processes #
###########################

# Write the updated configuration file into a temporary file
updatedConfigFileName = "tempConfigFilterPP.json"

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

# Listing Added Commands
dispArgs(allArgs)

os.system(commandToRun)

runPycacheRemover()
