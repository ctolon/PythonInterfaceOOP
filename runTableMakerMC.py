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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMakerMC.cxx

import json
import logging
import logging.config
import os
from extramodules.dqTranscations import mandatoryArgChecker, aodFileChecker, centralityChecker, forgettedArgsChecker, jsonTypeChecker, mainTaskChecker, trackPropagationChecker
from extramodules.configSetter import PROCESS_SWITCH, converterSet, CONFIG_SET, debugSettings, dispArgs, generateDescriptors, prefixSuffixSet, tableProducer
from extramodules.pycacheRemover import runPycacheRemover
from dqtasks.tableMakerMC import TableMakerMC

# Predefined selections for PROCESS_SWITCH function
centralityTableParameters = [
    "estRun2V0M", "estRun2SPDtks", "estRun2SPDcls", "estRun2CL0", "estRun2CL1", "estFV0A", "estFT0M", "estFDDM", "estNTPV",
    ]
ft0Parameters = ["processFT0", "processNoFT0", "processOnlyFT0", "processRun2"]
pidParameters = ["pid-el", "pid-mu", "pid-pi", "pid-ka", "pid-pr", "pid-de", "pid-tr", "pid-he", "pid-al",]
covParameters = ["processStandard", "processCovariance"]
sliceParameters = ["processWoSlice", "processWSlice"]
vertexParameters = ["doVertexZeq", "doDummyZeq"]
centSearch = [] # for centrality transaction

# All Dependencies
commonDeps = ["o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table",]
barrelDeps = [
    "o2-analysis-trackselection", "o2-analysis-trackextension", "o2-analysis-pid-tof-base", "o2-analysis-pid-tof",
    "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta", "o2-analysis-pid-tpc-full",
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
    "processBarrelOnlyWithQvector": ["o2-analysis-centrality-table", "o2-analysis-dq-flow",],
    "processBarrelOnlyWithCent": ["o2-analysis-centrality-table"],
    "processMuonOnly": [],
    "processMuonOnlyWithCov": [],
    "processMuonOnlyWithCent": ["o2-analysis-centrality-table"],
    "processMuonOnlyWithQvector": ["o2-analysis-centrality-table", "o2-analysis-dq-flow",],
    "processMuonOnlyWithFilter": ["o2-analysis-dq-filter-pp"]
    # "processFullWithCentWithV0Bits": ["o2-analysis-centrality-table","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
    # "processFullWithEventFilterWithV0Bits": ["o2-analysis-dq-filter-pp","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
    }

# yapf: disable
# Definition of all the tables we may write
tables = {
    "ReducedEvents": {"table": "AOD/REDUCEDEVENT/0","treename": "ReducedEvents"},
    "ReducedEventsExtended": {"table": "AOD/REEXTENDED/0","treename": "ReducedEventsExtended"},
    "ReducedEventsVtxCov": {"table": "AOD/REVTXCOV/0","treename": "ReducedEventsVtxCov"},
    "ReducedEventsQvector": {"table": "AOD/REQVECTOR/0","treename": "ReducedEventsQvector"},
    "ReducedMCEventLabels": {"table": "AOD/REMCCOLLBL/0","treename": "ReducedMCEventLabels"},
    "ReducedMCEvents": {"table": "AOD/REMC/0","treename": "ReducedMCEvents"},
    "ReducedTracks": {"table": "AOD/REDUCEDTRACK/0","treename": "ReducedTracks"},
    "ReducedTracksBarrel": {"table": "AOD/RTBARREL/0","treename": "ReducedTracksBarrel"},
    "ReducedTracksBarrelCov": {"table": "AOD/RTBARRELCOV/0","treename": "ReducedTracksBarrelCov"},
    "ReducedTracksBarrelPID": {"table": "AOD/RTBARRELPID/0","treename": "ReducedTracksBarrelPID"},
    "ReducedTracksBarrelLabels": {"table": "AOD/RTBARRELLABELS/0","treename": "ReducedTracksBarrelLabels"},
    "ReducedMCTracks": {"table": "AOD/RTMC/0","treename": "ReducedMCTracks"},
    "ReducedMuons": {"table": "AOD/RTMUON/0","treename": "ReducedMuons"},
    "ReducedMuonsExtra": {"table": "AOD/RTMUONEXTRA/0","treename": "ReducedMuonsExtra"},
    "ReducedMuonsCov": {"table": "AOD/RTMUONCOV/0","treename": "ReducedMuonsCov"},
    "ReducedMuonsLabels": {"table": "AOD/RTMUONSLABELS/0","treename": "ReducedMuonsLabels"}
    }
# yapf: enable
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
initArgs = TableMakerMC()
initArgs.mergeArgs()
initArgs.parseArgs()
args = initArgs.parseArgs()
allArgs = vars(args) # for get args

# Debug Settings
debugSettings(args.debug, args.logFile, fileName = "tableMakerMC.log")

# if cliMode true, Overrider mode else additional mode
cliMode = args.onlySelect

forgettedArgsChecker(allArgs) # Transaction management

# adding prefix for PROCESS_SWITCH function (for no kFlag True situations)
args.process = prefixSuffixSet(args.process, "process", '', True, False)
args.pid = prefixSuffixSet(args.pid, "pid-", '', True, False)
args.est = prefixSuffixSet(args.est, "est", '', True, False)
args.FTO = prefixSuffixSet(args.FT0, "process", '', True, False)

# Load the configuration file provided as the first parameter
config = {}
with open(args.cfgFileName) as configFile:
    config = json.load(configFile)

jsonTypeChecker(args.cfgFileName)

runOverMC = True
logging.info("runOverMC : %s, Reduced Tables will be produced for MC", runOverMC)

taskNameInConfig = "table-maker-m-c"
taskNameInCommandLine = "o2-analysis-dq-table-maker-mc"

mainTaskChecker(config, taskNameInConfig)

# Interface Process
logging.info("Only Select Configured as %s", cliMode)
if cliMode == "true":
    logging.info("INTERFACE MODE : JSON Overrider")
if cliMode == "false":
    logging.info("INTERFACE MODE : JSON Additional")

if args.process:
    centSearch = [s for s in args.process if "Cent" in s]

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
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "process", specificDeps.keys(), "true/false")
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "isCovariance", covParameters, "true/false", True)
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "isWSlice", sliceParameters, "true/false", True)
            if key == "tof-event-time": # we have processRun2 option in tof-event-time and for not overriding it other processRun2 options, we have to specifiy key
                PROCESS_SWITCH(config, key, value, allArgs, "true", "FT0", ft0Parameters, "true/false")
            PROCESS_SWITCH(config, key, value, allArgs, cliMode, "isVertexZeq", vertexParameters, "1/0", True)
            mandatoryArgChecker(config, key, value, taskNameInConfig, "processOnlyBCs")

# Transactions
centralityChecker(config, args.process, args.syst, centSearch)
aodFileChecker(args.aod)
trackPropagationChecker(args.add_track_prop, barrelDeps)

# Write the updated configuration file into a temporary file
updatedConfigFileName = "tempConfigTableMakerMC.json"

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

writerConfigFileName = "aodWriterTempConfig.json"

# Generate the aod-writer output descriptor json file
generateDescriptors(tablesToProduce, tables, writerConfigFileName, kFlag = False)

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
dispArgs(allArgs) # Display all args
os.system(commandToRun) # Execute O2 generated commands
runPycacheRemover() # Run pycacheRemover
