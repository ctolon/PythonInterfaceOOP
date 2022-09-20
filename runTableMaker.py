#!/usr/bin/env python
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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMaker.cxx

import json
import logging
import logging.config
import os

from extramodules.monitoring import dispArgs
from extramodules.descriptor import inputDescriptors, outputDescriptors
from extramodules.dqTranscations import MandatoryArgAdder, aodFileChecker, centTranscation, forgettedArgsChecker, jsonTypeChecker, filterSelsTranscation, mainTaskChecker, trackPropTransaction
from extramodules.configSetter import PROCESS_DUMMY, PROCESS_SWITCH, converterSet, CONFIG_SET, debugSettings, tableProducer
from extramodules.pycacheRemover import runPycacheRemover

from dqtasks.tableMaker import TableMaker

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

# Predefined Search Lists
fullSearch = []
barrelSearch = []
muonSearch = []
centSearch = []
filterSearch = []

################
# Dependencies #
################

commonDeps = ["o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table"]
barrelDeps = [
    "o2-analysis-trackselection", "o2-analysis-trackextension", "o2-analysis-pid-tof-base", "o2-analysis-pid-tof",
    "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta", "o2-analysis-pid-tpc-full"
    ]
specificDeps = {
    "processFull": [],
    "processFullTiny": [],
    "processFullWithCov": [],
    "processFullWithCent": ["o2-analysis-centrality-table"],
    "processBarrelOnly": [],
    "processBarrelOnlyWithCov": [],
    "processBarrelOnlyWithV0Bits": ["o2-analysis-dq-v0-selector"],
    "processBarrelOnlyWithEventFilter": ["o2-analysis-dq-filter-pp"],
    "processBarrelOnlyWithQvector": ["o2-analysis-centrality-table", "o2-analysis-dq-flow"],
    "processBarrelOnlyWithCent": ["o2-analysis-centrality-table"],
    "processMuonOnly": [],
    "processMuonOnlyWithCov": [],
    "processMuonOnlyWithCent": ["o2-analysis-centrality-table"],
    "processMuonOnlyWithQvector": ["o2-analysis-centrality-table", "o2-analysis-dq-flow"],
    "processMuonOnlyWithFilter": ["o2-analysis-dq-filter-pp"]
    # "processFullWithCentWithV0Bits": ["o2-analysis-centrality-table","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
    # "processFullWithEventFilterWithV0Bits": ["o2-analysis-dq-filter-pp","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
    }

dummyHasTasks = ["d-q-barrel-track-selection", "d-q-muons-selection", "d-q-filter-p-p-task"]

#############################
# Skimming Table Selections #
#############################

# Definition of all the tables we may write
tables = {
    "ReducedEvents": {
        "table": "AOD/REDUCEDEVENT/0",
        "treename": "ReducedEvents"
        },
    "ReducedEventsExtended": {
        "table": "AOD/REEXTENDED/0",
        "treename": "ReducedEventsExtended",
        },
    "ReducedEventsVtxCov": {
        "table": "AOD/REVTXCOV/0",
        "treename": "ReducedEventsVtxCov",
        },
    "ReducedEventsQvector": {
        "table": "AOD/REQVECTOR/0",
        "treename": "ReducedEventsQvector",
        },
    "ReducedMCEventLabels": {
        "table": "AOD/REMCCOLLBL/0",
        "treename": "ReducedMCEventLabels",
        },
    "ReducedMCEvents": {
        "table": "AOD/REMC/0",
        "treename": "ReducedMCEvents"
        },
    "ReducedTracks": {
        "table": "AOD/REDUCEDTRACK/0",
        "treename": "ReducedTracks"
        },
    "ReducedTracksBarrel": {
        "table": "AOD/RTBARREL/0",
        "treename": "ReducedTracksBarrel",
        },
    "ReducedTracksBarrelCov": {
        "table": "AOD/RTBARRELCOV/0",
        "treename": "ReducedTracksBarrelCov",
        },
    "ReducedTracksBarrelPID": {
        "table": "AOD/RTBARRELPID/0",
        "treename": "ReducedTracksBarrelPID",
        },
    "ReducedTracksBarrelLabels": {
        "table": "AOD/RTBARRELLABELS/0",
        "treename": "ReducedTracksBarrelLabels",
        },
    "ReducedMCTracks": {
        "table": "AOD/RTMC/0",
        "treename": "ReducedMCTracks"
        },
    "ReducedMuons": {
        "table": "AOD/RTMUON/0",
        "treename": "ReducedMuons"
        },
    "ReducedMuonsExtra": {
        "table": "AOD/RTMUONEXTRA/0",
        "treename": "ReducedMuonsExtra",
        },
    "ReducedMuonsCov": {
        "table": "AOD/RTMUONCOV/0",
        "treename": "ReducedMuonsCov"
        },
    "ReducedMuonsLabels": {
        "table": "AOD/RTMUONSLABELS/0",
        "treename": "ReducedMuonsLabels",
        }
    }
# Tables to be written, per process function
commonTables = ["ReducedEvents", "ReducedEventsExtended", "ReducedEventsVtxCov"]
barrelCommonTables = ["ReducedTracks", "ReducedTracksBarrel", "ReducedTracksBarrelPID"]
muonCommonTables = ["ReducedMuons", "ReducedMuonsExtra"]
specificTables = {
    "processFull": [],
    "processFullTiny": [],
    "processFullWithCov": ["ReducedTracksBarrelCov", "ReducedMuonsCov"],
    "processFullWithCent": [],
    "processBarrelOnly": [],
    "processBarrelOnlyWithCov": ["ReducedTracksBarrelCov"],
    "processBarrelOnlyWithV0Bits": [],
    "processBarrelOnlyWithQvector": ["ReducedEventsQvector"],
    "processBarrelOnlyWithEventFilter": [],
    "processBarrelOnlyWithCent": [],
    "processMuonOnly": [],
    "processMuonOnlyWithCov": ["ReducedMuonsCov"],
    "processMuonOnlyWithCent": [],
    "processMuonOnlyWithQvector": ["ReducedEventsQvector"],
    "processMuonOnlyWithFilter": [],
    }

# init args manually
initArgs = TableMaker()

initArgs.mergeArgs()
initArgs.parseArgs()

args = initArgs.parseArgs()
allArgs = vars(args) # for get args

# Debug Settings
debugSettings(args.debug, args.logFile, fileName = "tableMaker.log")

# if cliMode true, Overrider mode else additional mode
cliMode = args.onlySelect

# Transcation management
forgettedArgsChecker(allArgs)

######################
# PREFIX ADDING PART #
######################

# add prefix for args.process for table-maker/table-maker-m-c and d-q-filter-p-p
if args.process is not None:
    prefix_process = "process"
    args.process = [prefix_process + sub for sub in args.process]

# add prefix for args.pid for pid selection
if args.pid is not None:
    prefix_pid = "pid-"
    args.pid = [prefix_pid + sub for sub in args.pid]

# add prefix for args.est for centrality-table
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

runOverMC = False
logging.info("runOverMC : %s, Reduced Tables will be produced for Data", runOverMC)

taskNameInConfig = "table-maker"
taskNameInCommandLine = "o2-analysis-dq-table-maker"

mainTaskChecker(config, taskNameInConfig)

if args.process:
    fullSearch = [s for s in args.process if "Full" in s]
    barrelSearch = [s for s in args.process if "Barrel" in s]
    muonSearch = [s for s in args.process if "Muon" in s]
    filterSearch = [s for s in args.process if "Filter" in s]
    centSearch = [s for s in args.process if "Cent" in s]

# ===========================
# Start Interface Processes =
# ===========================

logging.info("Only Select Configured as %s", cliMode)
if cliMode == "true":
    logging.info("INTERFACE MODE : JSON Overrider")
if cliMode == "false":
    logging.info("INTERFACE MODE : JSON Additional")

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
            
            if len(barrelSearch) > 0 or len(fullSearch) > 0:
                if args.isBarrelSelectionTiny == "true":
                    config["d-q-barrel-track-selection-task"]["processSelection"] = "false"
                    config["d-q-barrel-track-selection-task"]["processSelectionTiny"] = args.isBarrelSelectionTiny
            
            if (len(barrelSearch) == 0 and len(fullSearch) == 0 and args.runData and cliMode == "true"):
                config["d-q-barrel-track-selection-task"]["processSelection"] = "false"
                config["d-q-barrel-track-selection-task"]["processSelectionTiny"] = "false"
                config["d-q-barrel-track-selection-task"]["processDummy"] = "true"
            
            if (len(muonSearch) == 0 and len(fullSearch) == 0 and args.runData and cliMode == "true"):
                config["d-q-muons-selection"]["processSelection"] = "false"
                config["d-q-muons-selection"]["processDummy"] = "true"
            
            if len(filterSearch) > 0 and args.runData:
                config["d-q-filter-p-p-task"]["processFilterPP"] = "true"
                config["d-q-filter-p-p-task"]["processFilterPPTiny"] = "false"
                
                if args.isFilterPPTiny == "true":
                    config["d-q-filter-p-p-task"]["processFilterPP"] = "false"
                    config["d-q-filter-p-p-task"]["processFilterPPTiny"] = "true"
            
            if len(filterSearch) == 0 and args.runData and cliMode == "true":
                config["d-q-filter-p-p-task"]["processFilterPP"] = "false"
                config["d-q-filter-p-p-task"]["processFilterPPTiny"] = "false"
                config["d-q-filter-p-p-task"]["processDummy"] = "false"
            
            CONFIG_SET(config, key, value, allArgs, cliMode)
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "est", centralityTableParameters, "1/-1")
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "pid", pidParameters, "1/-1")
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "process", specificDeps.keys(), "true/false")
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "isCovariance", covParameters, "true/false", True)
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "isWSlice", sliceParameters, "true/false", True)
            if key == "tof-event-time": # we have processRun2 option in tof-event-time and for not overriding it other processRun2 options, we have to specifiy key
                PROCESS_SWITCH(config, key, value, allArgs, "true", "FT0", ft0Parameters, "true/false")
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "isVertexZeq", vertexParameters, "1/0", True)
            MandatoryArgAdder(config, key, value, taskNameInConfig, "processOnlyBCs")

# Transactions
centTranscation(config, args.process, args.syst, centSearch)
filterSelsTranscation(args.cfgBarrelSels, args.cfgMuonSels, args.cfgBarrelTrackCuts, args.cfgMuonsCuts, allArgs)
aodFileChecker(args.aod)
trackPropTransaction(args.add_track_prop, barrelDeps)
PROCESS_DUMMY(config, dummyHasTasks)
"""
# Regarding to perfomance issues in argcomplete package, we should import later
from extramodules.getTTrees import getTTrees

# Converter Management
if args.aod is not None:
    ttreeList = getTTrees(args.aod)
else:
    ttreeList = config["internal-dpl-aod-reader"]["aod-file"]

converterManager(ttreeList, commonDeps)
trackPropChecker(commonDeps, barrelDeps)
"""
###########################
# End Interface Processes #
###########################

# Write the updated configuration file into a temporary file
updatedConfigFileName = "tempConfigTableMaker.json"

with open(updatedConfigFileName, "w") as outputFile:
    json.dump(config, outputFile, indent = 2)

# Check which dependencies need to be run
depsToRun = {}
for dep in commonDeps:
    depsToRun[dep] = 1

for processFunc in specificDeps.keys():
    if processFunc not in config[taskNameInConfig].keys():
        continue
    if config[taskNameInConfig][processFunc] == "true":
        if "processFull" in processFunc or "processBarrel" in processFunc:
            for dep in barrelDeps:
                depsToRun[dep] = 1
        for dep in specificDeps[processFunc]:
            depsToRun[dep] = 1

# Check which tables are required in the output
tablesToProduce = {}
tableProducer(
    config, taskNameInConfig, tablesToProduce, commonTables, barrelCommonTables, muonCommonTables, specificTables, specificDeps, runOverMC
    )

readerConfigFileName = "aodReaderTempConfig.json"
writerConfigFileName = "aodWriterTempConfig.json"

# Generate the aod-writer output descriptor json file
outputDescriptors(tablesToProduce, tables)
inputDescriptors(tablesToProduce, tables)

commandToRun = (
    taskNameInCommandLine + " --configuration json://" + updatedConfigFileName +
    " --severity error --shm-segment-size 12000000000 --aod-writer-json " + writerConfigFileName + " -b"
    )
if args.aod_memory_rate_limit:
    commandToRun = (
        taskNameInCommandLine + " --configuration json://" + updatedConfigFileName +
        " --severity error --shm-segment-size 12000000000 --aod-memory-rate-limit " + args.aod_memory_rate_limit + " --aod-writer-json " +
        writerConfigFileName + " -b"
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
logging.info("Tables to produce:")
logging.info(tablesToProduce.keys())
print("====================================================================================================================")

# Listing Added Commands
dispArgs(allArgs)

os.system(commandToRun)

runPycacheRemover()
