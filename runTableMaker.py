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

import sys
import logging
import logging.config
import os
from extramodules.dqTranscations import mandatoryArgChecker, aodFileChecker, jsonTypeChecker, mainTaskChecker, trackPropagationChecker
from extramodules.configSetter import dispInterfaceMode, setArgsToArgParser, setConfigs, setParallelismOnSkimming, setProcessDummy, setConverters, debugSettings, dispArgs, generateDescriptors, tableProducer
from extramodules.pycacheRemover import runPycacheRemover
from extramodules.utils import dumpJson, loadJson


def main():
    
    # Setting arguments for CLI
    parsedJsonFile = "configs/configTableMakerDataRun3.json"
    args = setArgsToArgParser(parsedJsonFile, ["timestamp-task", "tof-event-time", "bc-selection-task", "tof-pid-beta"])
    allArgs = vars(args) # for get args
        
    # All Dependencies
    commonDeps = ["o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table"]
    barrelDeps = ["o2-analysis-trackselection", "o2-analysis-trackextension", "o2-analysis-pid-tof-base", "o2-analysis-pid-tof", "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta", "o2-analysis-pid-tpc-full"]
    muonDeps = ["o2-analysis-fwdtrackextension"]
    specificDeps = {
        "processFull": [],
        "processFullTiny": [],
        "processFullWithCov": [],
        "processFullWithCent": ["o2-analysis-centrality-table"],
        "processBarrelOnly": [],
        "processBarrelOnlyWithCov": [],
        "processBarrelOnlyWithV0Bits": ["o2-analysis-dq-v0-selector"],
        "processBarrelOnlyWithDalitzBits": ["o2-analysis-dq-dalitz-selection"],
        "processBarrelOnlyWithEventFilter": ["o2-analysis-dq-filter-pp"],
        "processBarrelOnlyWithQvector": ["o2-analysis-centrality-table", "o2-analysis-dq-flow"],
        "processBarrelOnlyWithCent": ["o2-analysis-centrality-table"],
        "processMuonOnly": [],
        "processMuonOnlyWithCov": [],
        "processMuonOnlyWithCent": ["o2-analysis-centrality-table"],
        "processMuonOnlyWithQvector": ["o2-analysis-centrality-table", "o2-analysis-dq-flow"],
        "processMuonOnlyWithFilter": ["o2-analysis-dq-filter-pp"],
        "processAmbiguousMuonOnly": [],
        "processAmbiguousBarrelOnly": []
        # "processFullWithCentWithV0Bits": ["o2-analysis-centrality-table","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
        # "processFullWithEventFilterWithV0Bits": ["o2-analysis-dq-filter-pp","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
        }
    
    dummyHasTasks = ["d-q-barrel-track-selection", "d-q-muons-selection", "d-q-filter-p-p-task", "dalitz-pairing", "track-pid-qa", "v0-gamma-qa"]
    
    # yapf: disable
    # Definition of all the tables we may write
    tables = {
        "ReducedEvents": {"table": "AOD/REDUCEDEVENT/0"},
        "ReducedEventsExtended": {"table": "AOD/REEXTENDED/0"},
        "ReducedEventsVtxCov": {"table": "AOD/REVTXCOV/0"},
        "ReducedEventsQvector": {"table": "AOD/REQVECTOR/0"},
        "ReducedMCEventLabels": {"table": "AOD/REMCCOLLBL/0"},
        "ReducedMCEvents": {"table": "AOD/REDUCEDMCEVENT/0"},
        "ReducedTracks": {"table": "AOD/REDUCEDTRACK/0"},
        "ReducedTracksBarrel": {"table": "AOD/RTBARREL/0"},
        "ReducedTracksBarrelCov": {"table": "AOD/RTBARRELCOV/0"},
        "ReducedTracksBarrelPID": {"table": "AOD/RTBARRELPID/0"},
        "ReducedTracksBarrelLabels": {"table": "AOD/RTBARRELLABELS/0"},
        "ReducedMCTracks": {"table": "AOD/REDUCEDMCTRACK/0"},
        "ReducedMuons": {"table": "AOD/RTMUON/0"},
        "ReducedMuonsExtra": {"table": "AOD/RTMUONEXTRA/0"},
        "ReducedMuonsCov": {"table": "AOD/RTMUONCOV/0"},
        "ReducedMuonsLabels": {"table": "AOD/RTMUONSLABELS/0"},
        "AmbiguousTracksMid": {"table": "AOD/AMBIGUOUSTRACK/0"},
        "AmbiguousTracksFwd": {"table": "AOD/AMBIGUOUSFWDTR/0"},
        "DalitzBits": {"table": "AOD/DALITZBITS/0"},
        #"ReducedV0s": {"table": "AOD/REDUCEDV0/0"}, # NOTE V0 Bits cannot save to reduced tables
        #"V0Bits": {"table": "AOD/V0BITS/0"}
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
        "processBarrelOnlyWithDalitzBits": ["DalitzBits"],
        "processBarrelOnlyWithQvector": ["ReducedEventsQvector"],
        "processBarrelOnlyWithEventFilter": [],
        "processBarrelOnlyWithCent": [],
        "processMuonOnly": [],
        "processMuonOnlyWithCov": ["ReducedMuonsCov"],
        "processMuonOnlyWithCent": [],
        "processMuonOnlyWithQvector": ["ReducedEventsQvector"],
        "processMuonOnlyWithFilter": [],
        "processAmbiguousMuonOnly": ["AmbiguousTracksFwd"],
        "processAmbiguousBarrelOnly": ["AmbiguousTracksMid"]
        }
    
    # Debug Settings
    debugSettings(args.debug, args.logFile, fileName = "tableMaker.log")
    
    # if cliMode true, Overrider mode else additional mode
    cliMode = args.onlySelect
    
    # Load the configuration file provided as the first parameter
    config = loadJson(args.cfgFileName)
    
    jsonTypeChecker(args.cfgFileName)
    jsonTypeChecker(parsedJsonFile)
    
    runOverMC = False
    logging.info("runOverMC : %s, Reduced Tables will be produced for Data", runOverMC)
    
    taskNameInConfig = "table-maker"
    taskNameInCommandLine = "o2-analysis-dq-table-maker"
    
    mainTaskChecker(config, taskNameInConfig)
    
    # Interface Mode message
    dispInterfaceMode(cliMode)
    
    # Set arguments to config json file
    setConfigs(allArgs, config, cliMode)
    
    # Transactions
    #centralityChecker(config, args.process, args.syst, centSearch)
    #filterSelsChecker(args.cfgBarrelSels, args.cfgMuonSels, args.cfgBarrelTrackCuts, args.cfgMuonsCuts, allArgs)
    aodFileChecker(allArgs["internal_dpl_aod_reader:aod_file"])
    trackPropagationChecker(args.add_track_prop, barrelDeps)
    mandatoryArgChecker(config, taskNameInConfig, "processOnlyBCs")
    setProcessDummy(config, dummyHasTasks) # dummy automizer
    
    # Write the updated configuration file into a temporary file
    updatedConfigFileName = "tempConfigTableMaker.json"
    
    dumpJson(updatedConfigFileName, config)
    
    # Check which dependencies need to be run
    depsToRun = {}
    for dep in commonDeps:
        depsToRun[dep] = 1
    
    for processFunc in specificDeps.keys():
        if processFunc not in config[taskNameInConfig].keys():
            continue
        if config[taskNameInConfig][processFunc] == "true":
            if "processFull" in processFunc or "processBarrel" in processFunc or "processAmbiguousBarrel" in processFunc:
                for dep in barrelDeps:
                    depsToRun[dep] = 1
            if "processFull" in processFunc or "processMuon" in processFunc or "processAmbiguousMuon" in processFunc:
                for dep in muonDeps:
                    depsToRun[dep] = 1
            for dep in specificDeps[processFunc]:
                depsToRun[dep] = 1
    
    # Check which tables are required in the output
    tablesToProduce = {}
    tableProducer(config, taskNameInConfig, tablesToProduce, commonTables, barrelCommonTables, muonCommonTables, specificTables, specificDeps, runOverMC)
    
    writerConfigFileName = "aodWriterTempConfig.json"
    
    # Generate the aod-writer output descriptor json file
    generateDescriptors(tablesToProduce, tables, writerConfigFileName, kFlag = False)
    
    commandToRun = f"{taskNameInCommandLine} --configuration json://{updatedConfigFileName} --severity error --shm-segment-size 12000000000 --aod-writer-json {writerConfigFileName} -b"
    if args.aod_memory_rate_limit:
        commandToRun = f"{taskNameInCommandLine} --configuration json://{updatedConfigFileName} --severity error --shm-segment-size 12000000000 --aod-memory-rate-limit {args.aod_memory_rate_limit} --aod-writer-json {writerConfigFileName} -b"
    if args.runParallel is True:
        commandToRun = f"{taskNameInCommandLine} --configuration json://{updatedConfigFileName} --severity error --shm-segment-size 12000000000 -b"
    
    for dep in depsToRun.keys():
        commandToRun += " | " + dep + " --configuration json://" + updatedConfigFileName + " -b"
        logging.debug("%s added your workflow", dep)
    
    commandToRun = setConverters(allArgs, updatedConfigFileName, commandToRun)
    
    if args.runParallel is True:
        commandToRun = setParallelismOnSkimming(commandToRun, taskNameInCommandLine, updatedConfigFileName, "o2-analysis-dq-table-reader", "tempConfigTableReader.json", config)
    
    if args.helpO2 is True:
        commandToRun += " --help full"
    
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


if __name__ == '__main__':
    sys.exit(main())
