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

# sys.path.append("/extramodules/sub")

# from extramodules.getTTrees import getTTrees # activate when we have no performance issue
from extramodules.debugSettings import debugSettings
from extramodules.monitoring import dispArgs
from extramodules.descriptor import inputDescriptors, outputDescriptors
from extramodules.dqTranscations import aodFileChecker, centTranscation, forgettedArgsChecker, jsonTypeChecker, filterSelsTranscation, mainTaskChecker, trackPropTransaction
from extramodules.configSetter import multiConfigurableSet
from extramodules.pycacheRemover import runPycacheRemover

from dqtasks.tableMaker import TableMaker

###################################
# Interface Predefined Selections #
###################################

centralityTableParameters = [
    "estRun2V0M", "estRun2SPDtks", "estRun2SPDcls", "estRun2CL0", "estRun2CL1", "estFV0A", "estFT0M", "estFDDM", "estNTPV"
    ]
# TODO Add genname parameter

ft0Parameters = ["processFT0", "processNoFT0", "processOnlyFT0", "processRun2"]

pidParameters = ["pid-el", "pid-mu", "pid-pi", "pid-ka", "pid-pr", "pid-de", "pid-tr", "pid-he", "pid-al"]

booleanSelections = ["true", "false"]

ttreeList = []

# Predefined Search Lists
fullSearch = []
barrelSearch = []
muonSearch = []
covSearch = []
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
configuredCommands = vars(args) # for get args

# Debug Settings
debugSettings(args.debug, args.logFile, fileName = "tableMaker.log")

# Transcation management
forgettedArgsChecker(configuredCommands)

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

# ===========================
# Start Interface Processes =
# ===========================

logging.info("Only Select Configured as %s", args.onlySelect)
if args.onlySelect == "true":
    logging.info("INTERFACE MODE : JSON Overrider")
if args.onlySelect == "false":
    logging.info("INTERFACE MODE : JSON Additional")

# For adding a process function from TableMaker and all process should be added only once so set type used
tableMakerProcessSearch = set()

for key, value in config.items():
    if isinstance(value, dict):
        for value, value2 in value.items():
            
            # aod
            if value == "aod-file" and args.aod:
                config[key][value] = args.aod
                logging.debug(" - [%s] %s : %s", key, value, args.aod)
            
            # table-maker/table-maker-m-c process selections
            # TODO Refactor
            if (value in specificDeps.keys()) and args.process:
                if value in args.process:
                    
                    # processOnlyBCs have to always be true
                    if "processOnlyBCs" not in args.process:
                        args.process.append("processOnlyBCs")
                        logging.warning("You forget to add OnlyBCs value in --process parameter! It will automaticaly added.")
                    value2 = "true"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s", key, value, value2)
                    
                    for s in config[key].keys():
                        if s in specificDeps.keys():
                            tableMakerProcessSearch.add(s)
                    
                    fullSearch = [s for s in args.process if "Full" in s]
                    barrelSearch = [s for s in args.process if "Barrel" in s]
                    muonSearch = [s for s in args.process if "Muon" in s]
                    filterSearch = [s for s in args.process if "Filter" in s]
                    centSearch = [s for s in args.process if "Cent" in s]
                    
                    if len(barrelSearch) > 0 or len(fullSearch) > 0:
                        if args.isBarrelSelectionTiny == "true":
                            config["d-q-barrel-track-selection-task"]["processSelection"] = "false"
                            config["d-q-barrel-track-selection-task"]["processSelectionTiny"] = args.isBarrelSelectionTiny
                    
                    if (len(barrelSearch) == 0 and len(fullSearch) == 0 and args.runData and args.onlySelect == "true"):
                        config["d-q-barrel-track-selection-task"]["processSelection"] = "false"
                        config["d-q-barrel-track-selection-task"]["processSelectionTiny"] = "false"
                        config["d-q-barrel-track-selection-task"]["processDummy"] = "true"
                    
                    if (len(muonSearch) == 0 and len(fullSearch) == 0 and args.runData and args.onlySelect == "true"):
                        config["d-q-muons-selection"]["processSelection"] = "false"
                        config["d-q-muons-selection"]["processDummy"] = "true"
                    
                    if len(filterSearch) > 0 and args.runData:
                        config["d-q-filter-p-p-task"]["processFilterPP"] = "true"
                        config["d-q-filter-p-p-task"]["processFilterPPTiny"] = "false"
                        
                        if args.isFilterPPTiny == "true":
                            config["d-q-filter-p-p-task"]["processFilterPP"] = "false"
                            config["d-q-filter-p-p-task"]["processFilterPPTiny"] = "true"
                    
                    if len(filterSearch) == 0 and args.runData and args.onlySelect == "true":
                        config["d-q-filter-p-p-task"]["processFilterPP"] = "false"
                        config["d-q-filter-p-p-task"]["processFilterPPTiny"] = "false"
                        config["d-q-filter-p-p-task"]["processDummy"] = "false"
                
                elif args.onlySelect == "true":
                    if value == "processOnlyBCs":
                        config[key][value] = "true"
                        logging.debug(" - [%s] %s : true", key, value)
                    else:
                        value2 = "false"
                        config[key][value] = value2
                        logging.debug(" - [%s] %s : %s", key, value, value2)
            
            # filterPP Selections
            if value == "cfgBarrelSels" and args.cfgBarrelSels:
                multiConfigurableSet(config, key, value, args.cfgBarrelSels, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgBarrelSels)
            if value == "cfgMuonSels" and args.cfgMuonSels:
                multiConfigurableSet(config, key, value, args.cfgMuonSels, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgMuonSels)
            
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
            
            # analysis-qvector selections
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
            
            # v0-selector
            if value == "d_bz_input" and args.d_bz_input:
                config[key][value] = args.d_bz_input
                logging.debug(" - [%s] %s : %s", key, value, args.d_bz_input)
            if value == "v0cospa" and args.v0cospa:
                config[key][value] = args.v0cospa
                logging.debug(" - [%s] %s : %s", key, value, args.v0cospa)
            if value == "dcav0dau" and args.dcav0dau:
                config[key][value] = args.dcav0dau
                logging.debug(" - [%s] %s : %s", key, value, args.dcav0dau)
            if value == "v0Rmin" and args.v0Rmin:
                config[key][value] = args.v0Rmin
                logging.debug(" - [%s] %s : %s", key, value, args.v0Rmin)
            if value == "v0Rmax" and args.v0Rmax:
                config[key][value] = args.v0Rmax
                logging.debug(" - [%s] %s : %s", key, value, args.v0Rmax)
            if value == "dcamin" and args.dcamin:
                config[key][value] = args.dcamin
                logging.debug(" - [%s] %s : %s", key, value, args.dcamin)
            if value == "dcamax" and args.dcamax:
                config[key][value] = args.dcamax
                logging.debug(" - [%s] %s : %s", key, value, args.dcamax)
            if value == "mincrossedrows" and args.mincrossedrows:
                config[key][value] = args.mincrossedrows
                logging.debug(" - [%s] %s : %s", key, value, args.mincrossedrows)
            if value == "maxchi2tpc" and args.maxchi2tpc:
                config[key][value] = args.maxchi2tpc
                logging.debug(" - [%s] %s : %s", key, value, args.maxchi2tpc)
            
            # centrality-table
            if (value in centralityTableParameters) and args.est:
                if value in args.est:
                    value2 = "1"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s", key, value, value2)
                elif args.onlySelect == "true":
                    value2 = "-1"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s", key, value, value2)
            
            # table-maker/table-maker-m-c cfg selections
            if value == "cfgEventCuts" and args.cfgEventCuts:
                multiConfigurableSet(config, key, value, args.cfgEventCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgEventCuts)
            if value == "cfgBarrelTrackCuts" and args.cfgBarrelTrackCuts:
                multiConfigurableSet(config, key, value, args.cfgBarrelTrackCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgBarrelTrackCuts)
            if value == "cfgMuonCuts" and args.cfgMuonCuts:
                multiConfigurableSet(config, key, value, args.cfgMuonCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgMuonCuts)
            if value == "cfgBarrelLowPt" and args.cfgBarrelLowPt:
                config[key][value] = args.cfgBarrelLowPt
                logging.debug(" - [%s] %s : %s", key, value, args.cfgBarrelLowPt)
            if value == "cfgMuonLowPt" and args.cfgMuonLowPt:
                config[key][value] = args.cfgMuonLowPt
                logging.debug(" - [%s] %s : %s", key, value, args.cfgMuonLowPt)
            if value == "cfgNoQA" and args.cfgNoQA:
                config[key][value] = args.cfgNoQA
                logging.debug(" - [%s] %s : %s", key, value, args.cfgNoQA)
            if value == "cfgDetailedQA" and args.cfgDetailedQA:
                config[key][value] = args.cfgDetailedQA
                logging.debug(" - [%s] %s : %s", key, value, args.cfgDetailedQA)
            if value == "cfgMinTpcSignal" and args.cfgMinTpcSignal:
                config[key][value] = args.cfgMinTpcSignal
                logging.debug(" - [%s] %s : %s", key, value, args.cfgMinTpcSignal)
            if value == "cfgMaxTpcSignal" and args.cfgMaxTpcSignal:
                config[key][value] = args.cfgMaxTpcSignal
                logging.debug(" - [%s] %s : %s", key, value, args.cfgMaxTpcSignal)
            
            # d-q-muons-selection
            if value == "cfgMuonsCuts" and args.cfgMuonsCuts:
                multiConfigurableSet(config, key, value, args.cfgMuonsCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgMuonsCuts)
            
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
            
            # all d-q tasks and selections
            if (value == "cfgWithQA" or value == "cfgQA") and args.cfgWithQA:
                config[key][value] = args.cfgWithQA
                logging.debug(" - [%s] %s : %s", key, value, args.cfgWithQA)
            
            # track-propagation
            if args.isCovariance:
                if (value == "processStandard" or value == "processCovariance") and args.isCovariance == "false":
                    config[key]["processStandard"] = "true"
                    config[key]["processCovariance"] = "false"
                    logging.debug(" - [%s] processStandart : true", key)
                    logging.debug(" - [%s] processCovariance : false", key)
                if (value == "processStandard" or value == "processCovariance") and args.isCovariance == "true":
                    config[key]["processStandard"] = "false"
                    config[key]["processCovariance"] = "true"
                    logging.debug(" - [%s] processStandart : false", key)
                    logging.debug(" - [%s] processCovariance : true", key)
            
            # track-selection
            if args.itsMatching:
                config[key][value] = args.itsMatching
                logging.debug(" - [%s] %s : %s", key, value, args.itsMatching)

# Transactions
centTranscation(config, args.process, args.syst, centSearch)
filterSelsTranscation(args.cfgBarrelSels, args.cfgMuonSels, args.cfgBarrelTrackCuts, args.cfgMuonsCuts, configuredCommands)
aodFileChecker(args.aod)
trackPropTransaction(args.add_track_prop, barrelDeps)
"""
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
for table in commonTables:
    tablesToProduce[table] = 1

if runOverMC:
    tablesToProduce["ReducedMCEvents"] = 1
    tablesToProduce["ReducedMCEventLabels"] = 1

for processFunc in specificDeps.keys():
    if processFunc not in config[taskNameInConfig].keys():
        continue
    if config[taskNameInConfig][processFunc] == "true":
        logging.info("processFunc ========")
        logging.info("%s", processFunc)
        if "processFull" in processFunc or "processBarrel" in processFunc:
            logging.info("common barrel tables==========")
            for table in barrelCommonTables:
                logging.info("%s", table)
                tablesToProduce[table] = 1
            if runOverMC:
                tablesToProduce["ReducedTracksBarrelLabels"] = 1
        if "processFull" in processFunc or "processMuon" in processFunc:
            logging.info("common muon tables==========")
            for table in muonCommonTables:
                logging.info("%s", table)
                tablesToProduce[table] = 1
            if runOverMC:
                tablesToProduce["ReducedMuonsLabels"] = 1
        if runOverMC:
            tablesToProduce["ReducedMCTracks"] = 1
        logging.info("specific tables==========")
        for table in specificTables[processFunc]:
            logging.info("%s", table)
            tablesToProduce[table] = 1

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

# TODO: Append ile ekle
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
logging.info("Tables to produce:")
logging.info(tablesToProduce.keys())
print("====================================================================================================================")

# Listing Added Commands
dispArgs(configuredCommands)

os.system(commandToRun)

runPycacheRemover()
