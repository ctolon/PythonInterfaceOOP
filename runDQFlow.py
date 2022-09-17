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
import sys
import logging
import logging.config
from logging import handlers
import os

from extramodules.dqOperations import listToString, multiConfigurableSet
from extramodules.dqOperations import (
    runPycacheRemover, forgettedArgsChecker, jsonTypeChecker, mainTaskChecker, aodFileChecker, trackPropTransaction
    )

from dqtasks.dqFlow import AnalysisQvector
"""
argcomplete - Bash tab completion for argparse
Documentation https://kislyuk.github.io/argcomplete/
Instalation Steps
pip install argcomplete
sudo activate-global-python-argcomplete
Only Works On Local not in O2
Activate libraries in below and activate #argcomplete.autocomplete(parser) line
"""

###################################
# Interface Predefined Selections #
###################################

centralityTableParameters = [
    "estRun2V0M", "estRun2SPDtks", "estRun2SPDcls", "estRun2CL0", "estRun2CL1", "estFV0A", "estFT0M", "estFDDM", "estNTPV",
    ]
# TODO: Add genname parameter

ft0Parameters = ["processFT0", "processNoFT0", "processOnlyFT0", "processRun2"]

pidParameters = ["pid-el", "pid-mu", "pid-pi", "pid-ka", "pid-pr", "pid-de", "pid-tr", "pid-he", "pid-al",]

threeSelectedList = []

booleanSelections = ["true", "false"]

O2DPG_ROOT = os.environ.get("O2DPG_ROOT")
QUALITYCONTROL_ROOT = os.environ.get("QUALITYCONTROL_ROOT")
O2_ROOT = os.environ.get("O2_ROOT")
O2PHYSICS_ROOT = os.environ.get("O2PHYSICS_ROOT")

################
# Dependencies #
################

commonDeps = [
    "o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table", "o2-analysis-centrality-table",
    "o2-analysis-trackselection", "o2-analysis-trackextension", "o2-analysis-pid-tof-base", "o2-analysis-pid-tof-full",
    "o2-analysis-pid-tof-beta", "o2-analysis-pid-tpc-full",
    ]

# init args manually
initArgs = AnalysisQvector()
initArgs.mergeArgs()
initArgs.parseArgs()

args = initArgs.parseArgs()
configuredCommands = vars(args) # for get args

# Debug Settings
if args.debug and (not args.logFile):
    DEBUG_SELECTION = args.debug
    numeric_level = getattr(logging, DEBUG_SELECTION.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % DEBUG_SELECTION)
    logging.basicConfig(format = "[%(levelname)s] %(message)s", level = DEBUG_SELECTION)

if args.logFile and args.debug:
    log = logging.getLogger("")
    level = logging.getLevelName(args.debug)
    log.setLevel(level)
    format = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s")
    
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)
    
    loggerFile = "dqFlow.log"
    if os.path.isfile(loggerFile):
        os.remove(loggerFile)
    
    fh = handlers.RotatingFileHandler(loggerFile, maxBytes = (1048576 * 5), backupCount = 7, mode = "w")
    fh.setFormatter(format)
    log.addHandler(fh)

forgettedArgsChecker(configuredCommands)

######################
# PREFIX ADDING PART #
######################

# add prefix for args.pid for pid selection
if args.pid is not None:
    prefix_pid = "pid-"
    args.pid = [prefix_pid + sub for sub in args.pid]

# add prefix for args.est for centrality table
if args.est is not None:
    prefix_est = "est"
    args.est = [prefix_est + sub for sub in args.est]

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

taskNameInConfig = "analysis-qvector"
taskNameInCommandLine = "o2-analysis-dq-flow"

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
    if type(value) == type(config):
        for value, value2 in value.items():
            
            # aod
            if value == "aod-file" and args.aod:
                config[key][value] = args.aod
                logging.debug(" - [%s] %s : %s", key, value, args.aod)
            
            # analysis-qvector selections
            if value == "cfgBarrelTrackCuts" and args.cfgBarrelTrackCuts:
                multiConfigurableSet(config, key, value, args.cfgBarrelTrackCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgBarrelTrackCuts)
            if value == "cfgMuonCuts" and args.cfgMuonCuts:
                multiConfigurableSet(config, key, value, args.cfgMuonCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgMuonCuts)
            if value == "cfgEventCuts" and args.cfgEventCuts:
                multiConfigurableSet(config, key, value, args.cfgEventCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgEventCuts)
            if value == "cfgWithQA" and args.cfgWithQA:
                config[key][value] = args.cfgWithQA
                logging.debug(" - [%s] %s : %s", key, value, args.cfgWithQA)
            if value == "cfgCutPtMin" and args.cfgCutPtMin:
                config[key][value] = args.cfgCutPtMin
                logging.debug(" - [%s] %s : %s", key, value, args.cfgCutPtMin)
            if value == "cfgCutPtMax" and args.cfgCutPtMax:
                config[key][value] = args.cfgCutPtMax
                logging.debug(" - [%s] %s : %s", key, value, args.cfgCutPtMax)
            if value == "cfgCutEta" and args.cfgCutEta:
                config[key][value] = args.cfgCutEta
                logging.debug(" - [%s] %s : %s", key, value, args.cfgCutEta)
            if value == "cfgEtaLimit" and args.cfgEtaLimit:
                config[key][value] = args.cfgEtaLimit
                logging.debug(" - [%s] %s : %s", key, value, args.cfgEtaLimit)
            if value == "cfgNPow" and args.cfgNPow:
                config[key][value] = args.cfgNPow
                logging.debug(" - [%s] %s : %s", key, value, args.cfgNPow)
            if value == "cfgEfficiency" and args.cfgEfficiency:
                config[key][value] = args.cfgEfficiency
                logging.debug(" - [%s] %s : %s", key, value, args.cfgEfficiency)
            if value == "cfgAcceptance" and args.cfgAcceptance:
                config[key][value] = args.cfgAcceptance
                logging.debug(" - [%s] %s : %s", key, value, args.cfgAcceptance)
            
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
            
            # centrality table
            if (value in centralityTableParameters) and args.est:
                if value in args.est:
                    value2 = "1"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s", key, value, value2)
                elif args.onlySelect == "true":
                    value2 = "-1"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s", key, value, value2)
            
            # event-selection-task
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

aodFileChecker(args.aod)
trackPropTransaction(args.add_track_prop, commonDeps)

###########################
# End Interface Processes #
###########################

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
logging.info("Args provided configurations List")
print("====================================================================================================================")
for key, value in configuredCommands.items():
    if value is not None:
        if isinstance(value, list):
            listToString(value)
        logging.info("--%s : %s ", key, value)

os.system(commandToRun)

runPycacheRemover()
