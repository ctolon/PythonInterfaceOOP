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
from extramodules.converterManager import converterManager
from extramodules.debugSettings import debugSettings

from extramodules.monitoring import dispArgs
from extramodules.dqTranscations import aodFileChecker, forgettedArgsChecker, jsonTypeChecker, filterSelsTranscation, mainTaskChecker, trackPropChecker, trackPropTransaction
from extramodules.configSetter import multiConfigurableSet
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

pidParameters = ["pid-el", "pid-mu", "pid-pi", "pid-ka", "pid-pr", "pid-de", "pid-tr", "pid-he", "pid-al"]

ttreeList = []

################
# Dependencies #
################

commonDeps = [
    "o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table", "o2-analysis-trackselection",
    "o2-analysis-trackextension", "o2-analysis-pid-tof-base", "o2-analysis-pid-tof", "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta",
    "o2-analysis-pid-tpc-full",
    ]

# init args manually
initArgs = DQFilterPPTask()
initArgs.mergeArgs()
initArgs.parseArgs()

args = initArgs.parseArgs()
configuredCommands = vars(args) # for get args

# Debug Settings
debugSettings(args.debug, args.logFile, fileName = "filterPP.log")

forgettedArgsChecker(configuredCommands)

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

for key, value in config.items():
    if isinstance(value, dict):
        for value, value2 in value.items():
            
            # aod
            if value == "aod-file" and args.aod:
                config[key][value] = args.aod
                logging.debug(" - [%s] %s : %s", key, value, args.aod)
            
            # DQ Selections for muons and barrel tracks
            if value == "processSelection" and args.process:
                for keyCfg, valueCfg in configuredCommands.items():
                    if valueCfg is not None: # Cleaning None types, because can"t iterate in None type
                        if keyCfg == "process": # Only Select key for analysis
                            
                            if key == "d-q-barrel-track-selection":
                                if "barrelTrackSelection" in valueCfg:
                                    config[key][value] = "true"
                                    logging.debug(" - [%s] %s : true", key, value)
                                if ("barrelTrackSelection" not in valueCfg and args.onlySelect == "true"):
                                    config[key][value] = "false"
                                    logging.debug(" - [%s] %s : false", key, value)
                            
                            if key == "d-q-muons-selection":
                                if "muonSelection" in valueCfg:
                                    config[key][value] = "true"
                                    logging.debug(" - [%s] %s : true", key, value)
                                if "muonSelection" not in valueCfg and args.onlySelect == "true":
                                    config[key][value] = "false"
                                    logging.debug(" - [%s] %s : false", key, value)
            
            # DQ Selections event
            if value == "processEventSelection" and args.process:
                for keyCfg, valueCfg in configuredCommands.items():
                    if valueCfg is not None: # Cleaning None types, because can"t iterate in None type
                        if keyCfg == "process": # Only Select key for analysis
                            
                            if key == "d-q-event-selection-task":
                                if "eventSelection" in valueCfg:
                                    config[key][value] = "true"
                                    logging.debug(" - [%s] %s : true", key, value)
                                if "eventSelection" not in valueCfg:
                                    logging.warning(
                                        "YOU MUST ALWAYS CONFIGURE eventSelection value in --process parameter!! It is Missing and this issue will fixed by CLI"
                                        )
                                    config[key][value] = "true"
                                    logging.debug(" - [%s] %s : true", key, value)
            
            # DQ Tiny Selection for barrel track
            if value == "processSelectionTiny" and args.process:
                for keyCfg, valueCfg in configuredCommands.items():
                    if valueCfg is not None: # Cleaning None types, because can"t iterate in None type
                        if keyCfg == "process": # Only Select key for analysis
                            
                            if key == "d-q-barrel-track-selection":
                                if "barrelTrackSelectionTiny" in valueCfg:
                                    config[key][value] = "true"
                                    logging.debug(" - [%s] %s : true", key, value)
                                if ("barrelTrackSelectionTiny" not in valueCfg and args.onlySelect == "true"):
                                    config[key][value] = "false"
                                    logging.debug(" - [%s] %s : false", key, value)
            
            # DQ Tiny Selection for filterPP
            if value == "processFilterPPTiny" and args.process:
                for keyCfg, valueCfg in configuredCommands.items():
                    if valueCfg is not None: # Cleaning None types, because can"t iterate in None type
                        if keyCfg == "process": # Only Select key for analysis
                            
                            if key == "d-q-filter-p-p-task":
                                if "filterPPSelectionTiny" in valueCfg:
                                    config[key][value] = "true"
                                    config[key]["processFilterPP"] = "false"
                                    logging.debug(" - [%s] %s : true", key, value)
                                    logging.debug(" - [%s] processFilterPP : false", key)
                                if ("filterPPSelectionTiny" not in valueCfg and args.onlySelect == "true"):
                                    config[key][value] = "false"
                                    config[key]["processFilterPP"] = "true"
                                    logging.debug(" - [%s] %s : false", key, value)
                                    logging.debug(" - [%s] processFilterPP : true", key)
            
            # Filter PP Selections
            if value == "cfgBarrelSels" and args.cfgBarrelSels:
                multiConfigurableSet(config, key, value, args.cfgBarrelSels, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgBarrelSels)
            if value == "cfgMuonSels" and args.cfgMuonSels:
                multiConfigurableSet(config, key, value, args.cfgMuonSels, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgMuonSels)
            
            # DQ Cuts
            if value == "cfgEventCuts" and args.cfgEventCuts:
                multiConfigurableSet(config, key, value, args.cfgEventCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgEventCuts)
            if value == "cfgBarrelTrackCuts" and args.cfgBarrelTrackCuts:
                multiConfigurableSet(config, key, value, args.cfgBarrelTrackCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgBarrelTrackCuts)
            if value == "cfgMuonsCuts" and args.cfgMuonsCuts:
                multiConfigurableSet(config, key, value, args.cfgMuonsCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgMuonsCuts)
            
            # QA Options
            if value == "cfgWithQA" and args.cfgWithQA:
                config[key][value] = args.cfgWithQA
                logging.debug(" - [%s] %s : %s", key, value, args.cfgWithQA)
            
            # PID Selections
            if (value in pidParameters) and args.pid and key != "tof-pid":
                if value in args.pid:
                    value2 = "1"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s", key, value, value2)
                elif args.onlySelect == "true":
                    value2 = "-1"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s", key, value, value2)
            
            # event-selection
            if value == "syst" and args.syst:
                config[key][value] = args.syst
                logging.debug(" - [%s] %s : %s", key, value, args.syst)
            if value == "muonSelection" and args.muonSelection:
                config[key][value] = args.muonSelection
                logging.debug(" - [%s] %s : %s", key, value, args.muonSelection)
            if value == "customDeltaBC" and args.customDeltaBC:
                config[key][value] = args.customDeltaBC
                logging.debug(" - [%s] %s : %s", key, value, args.customDeltaBC)
            
            # multiplicity-table
            if value == "doVertexZeq" and args.isVertexZeq:
                if args.isVertexZeq == "true":
                    config[key][value] = "1"
                    config[key]["doDummyZeq"] = "0"
                    logging.debug(" - %s %s : 1", key, value)
                    logging.debug(" - [%s] doDummyZeq : 0", key)
                if args.isVertexZeq == "false":
                    config[key][value] = "0"
                    config[key]["doDummyZeq"] = "1"
                    logging.debug(" - %s %s : 0", key, value)
                    logging.debug(" - [%s] doDummyZeq : 1", key)
            
            # tof-pid, tof-pid-full
            if value == "processWSlice" and args.isWSlice:
                if args.isWSlice == "true":
                    config[key][value] = "true"
                    config[key]["processWoSlice"] = "false"
                    logging.debug(" - %s %s : true", key, value)
                    logging.debug(" - [%s] processWoSlice : false", key)
                if args.isWSlice == "false":
                    config[key][value] = "false"
                    config[key]["processWoSlice"] = "true"
                    logging.debug(" - %s %s : false", key, value)
                    logging.debug(" - [%s] processWoSlice : true", key)
            
            # tof-pid-beta
            if value == "tof-expreso" and args.tof_expreso:
                config[key][value] = args.tof_expreso
                logging.debug(" - [%s] %s : %s", key, value, args.tof_expreso)
            
            # tof-event-time
            if (value in ft0Parameters) and args.FT0 and key == "tof-event-time":
                if value == args.FT0:
                    value2 = "true"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s", key, value, value2)
                elif value != args.FT0:
                    value2 = "false"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s", key, value, value2)
            
            # track-selection
            if args.itsMatching:
                config[key][value] = args.itsMatching
                logging.debug(" - [%s] %s : %s", key, value, args.itsMatching)
            
            if value == "processDummy" and args.autoDummy:
                if config["d-q-barrel-track-selection"]["processSelection"] == "true":
                    config["d-q-barrel-track-selection"]["processDummy"] = "false"
                if config["d-q-barrel-track-selection"]["processSelection"] == "false":
                    config["d-q-barrel-track-selection"]["processDummy"] = "true"
                
                if config["d-q-muons-selection"]["processSelection"] == "true":
                    config["d-q-muons-selection"]["processDummy"] = "false"
                if config["d-q-muons-selection"]["processSelection"] == "false":
                    config["d-q-muons-selection"]["processDummy"] = "true"
                
                if config["d-q-event-selection-task"]["processEventSelection"] == "true":
                    config["d-q-event-selection-task"]["processDummy"] = "false"
                if config["d-q-event-selection-task"]["processEventSelection"] == "false":
                    config["d-q-event-selection-task"]["processDummy"] = "true"
                
                if config["d-q-filter-p-p-task"]["processFilterPP"] == "true":
                    config["d-q-filter-p-p-task"]["processDummy"] = "false"
                if config["d-q-filter-p-p-task"]["processFilterPP"] == "false":
                    config["d-q-filter-p-p-task"]["processDummy"] = "true"

# Transactions
filterSelsTranscation(args.cfgBarrelSels, args.cfgMuonSels, args.cfgBarrelTrackCuts, args.cfgMuonsCuts, configuredCommands)
aodFileChecker(args.aod)
# trackPropTransaction(args.add_track_prop, commonDeps)

# Regarding to perfomance issues in argcomplete package, we should import later
from extramodules.getTTrees import getTTrees

# Converter Management
if args.aod is not None:
    ttreeList = getTTrees(args.aod)
else:
    ttreeList = config["internal-dpl-aod-reader"]["aod-file"]

converterManager(ttreeList, commonDeps)
trackPropChecker(commonDeps, commonDeps)

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

if args.add_mc_conv:
    logging.debug("o2-analysis-mc-converter added your workflow")
    commandToRun += (" | o2-analysis-mc-converter --configuration json://" + updatedConfigFileName + " -b")

if args.add_fdd_conv:
    commandToRun += (" | o2-analysis-fdd-converter --configuration json://" + updatedConfigFileName + " -b")
    logging.debug("o2-analysis-fdd-converter added your workflow")

if args.add_track_prop:
    commandToRun += (" | o2-analysis-track-propagation --configuration json://" + updatedConfigFileName + " -b")
    logging.debug("o2-analysis-track-propagation added your workflow")

print("====================================================================================================================")
logging.info("Command to run:")
logging.info(commandToRun)
print("====================================================================================================================")

# Listing Added Commands
dispArgs(configuredCommands)

os.system(commandToRun)

runPycacheRemover()
