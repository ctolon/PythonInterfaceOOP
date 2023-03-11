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

# Orginal Task for Data: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMaker.cxx
# Orginal Task for MC: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMakerMC.cxx

# run template: `python3 runTableMaker.py <config.json> --task-name:<configurable|processFunc> parameter ...`
# parameter can be multiple like this:
# --table-maker:cfgBarrelTrackCuts jpsiPID1 jpsiPID2
# For run over MC (run tableMakerMC instead of tableMaker) You need to Set runOverMC variable to true, if you don't convert it will work for interface tableMaker

import sys
import logging
import logging.config
import os
from extramodules.dqTranscations import mandatoryArgChecker, aodFileChecker, jsonTypeChecker, mainTaskChecker, trackPropagationChecker
from extramodules.configSetter import SetArgsToArgumentParser, commonDepsToRun, dispInterfaceMode, dispO2HelpMessage, setConfigs, setParallelismOnSkimming, setProcessDummy, setConverters, debugSettings, dispArgs, generateDescriptors, setSwitch, tableProducerSkimming
from extramodules.pycacheRemover import runPycacheRemover
from extramodules.utils import dumpJson, loadJson


def main():
    
    # Switch runOverMC to True if you want work on tableMakerMC for MC else it will run for tableMaker for Data
    runOverMC = False
    
    # Simple protection
    if not isinstance(runOverMC, bool):
        raise TypeError("[FATAL] runOverMC have to True or False! (in bool type)")
    
    # Load json config file for create interface arguments as MC or Data
    parsedJsonFile = "configs/configTableMakerDataRun3.json"
    if runOverMC is True:
        parsedJsonFile = "configs/configTableMakerMCRun3.json"
    
    # Setting arguments for CLI
    setArgsToArgumentParser = SetArgsToArgumentParser(parsedJsonFile, ["timestamp-task", "tof-event-time", "bc-selection-task", "tof-pid-beta"])
    args = setArgsToArgumentParser.parseArgs()
    dummyHasTasks = setArgsToArgumentParser.dummyHasTasks
    processFuncs = setArgsToArgumentParser.processFuncs
    allArgs = vars(args) # for get args
    
    # All Dependencies
    commonDeps = ["o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table"]
    barrelDeps = ["o2-analysis-trackselection", "o2-analysis-trackextension", "o2-analysis-pid-tof-base", "o2-analysis-pid-tof", "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta", "o2-analysis-pid-tpc-full"]
    muonDeps = ["o2-analysis-fwdtrackextension"]
    specificDeps = {
        "processFull": [],
        "processFullWithCov": [],
        "processFullWithCovAndEventFilter" : ["o2-analysis-dq-filter-pp"],
        "processFullWithCent": ["o2-analysis-centrality-table"],
        "processFullWithCentAndMults": ["o2-analysis-centrality-table"],
        "processBarrelOnly": [],
        "processBarrelOnlyWithCov": [],
        "processBarrelOnlyWithV0Bits": ["o2-analysis-dq-v0-selector"],
        "processBarrelOnlyWithDalitzBits": ["o2-analysis-dq-dalitz-selection"],
        "processBarrelOnlyWithEventFilter": ["o2-analysis-dq-filter-pp"],
        "processBarrelOnlyWithMults": [],
        "processBarrelOnlyWithCovAndEventFilter" : ["o2-analysis-dq-filter-pp"],
        "processBarrelOnlyWithQvector": ["o2-analysis-centrality-table", "o2-analysis-dq-flow"],
        "processBarrelOnlyWithCent": ["o2-analysis-centrality-table"],
        "processBarrelOnlyWithCentAndMults": ["o2-analysis-centrality-table"],
        "processMuonOnly": [],
        "processMuonOnlyWithCov": [],
        "processMuonOnlyWithCent": ["o2-analysis-centrality-table"],
        "processMuonOnlyWithQvector": ["o2-analysis-centrality-table", "o2-analysis-dq-flow"],
        "processMuonOnlyWithFilter": ["o2-analysis-dq-filter-pp"],
        "processAmbiguousMuonOnly": [],
        "processAmbiguousMuonOnlyWithCov": [],
        "processAmbiguousBarrelOnly": []
        # "processFullWithCentWithV0Bits": ["o2-analysis-centrality-table","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
        # "processFullWithEventFilterWithV0Bits": ["o2-analysis-dq-filter-pp","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
        }
    
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
        "processFullWithCov": ["ReducedTracksBarrelCov", "ReducedMuonsCov"],
        "processFullWithCovAndEventFilter": ["ReducedTracksBarrelCov", "ReducedMuonsCov"],
        "processFullWithCent": [],
        "processFullWithCentAndMults": [],
        "processBarrelOnly": [],
        "processBarrelOnlyWithCov": ["ReducedTracksBarrelCov"],
        "processBarrelOnlyWithV0Bits": [],
        "processBarrelOnlyWithDalitzBits": ["DalitzBits"],
        "processBarrelOnlyWithQvector": ["ReducedEventsQvector"],
        "processBarrelOnlyWithEventFilter": [],
        "processBarrelOnlyWithMults": [],
        "processBarrelOnlyWithCovAndEventFilter": [],
        "processBarrelOnlyWithCent": [],
        "processBarrelOnlyWithCentAndMults": [],
        "processMuonOnly": [],
        "processMuonOnlyWithCov": ["ReducedMuonsCov"],
        "processMuonOnlyWithCent": [],
        "processMuonOnlyWithQvector": ["ReducedEventsQvector"],
        "processMuonOnlyWithFilter": [],
        "processAmbiguousMuonOnly": ["AmbiguousTracksFwd"],
        "processAmbiguousMuonOnlyWithCov": ["AmbiguousTracksFwd", "ReducedMuonsCov"],
        "processAmbiguousBarrelOnly": ["AmbiguousTracksMid"]
        }
    
    # Debug Settings
    fileName = "tableMaker.log"
    if args.runParallel:
        fileName = "fullAnalysisData.json"
    if runOverMC:
        fileName = "tableMakerMC.log"
        if args.runParallel:
            fileName = "fullAnalysisMC.log"
    debugSettings(args.debug, args.logFile, fileName)
    
    # if cliMode true, Overrider mode else additional mode
    cliMode = args.override
    
    # Basic validations
    jsonTypeChecker(args.cfgFileName)
    jsonTypeChecker(parsedJsonFile)
    
    # Load the configuration file provided as the first parameter
    config = loadJson(args.cfgFileName)
    
    logging.info("runOverMC : %s, Reduced Tables will be produced...", runOverMC)
    
    taskNameInConfig = "table-maker"
    taskNameInCommandLine = "o2-analysis-dq-table-maker"
    if runOverMC:
        taskNameInConfig = "table-maker-m-c"
        taskNameInCommandLine = "o2-analysis-dq-table-maker-mc"
    
    mainTaskChecker(config, taskNameInConfig)
    
    # Interface Mode message
    dispInterfaceMode(cliMode)
    
    # Set arguments to config json file
    setConfigs(allArgs, config, cliMode)
    
    # process function automation based on cliMode
    setSwitch(config, processFuncs, allArgs, cliMode, ["processOnlyBCs"])
    
    # Transactions
    aodFileChecker(allArgs["internal_dpl_aod_reader:aod_file"])
    trackPropagationChecker(args.add_track_prop, barrelDeps)
    mandatoryArgChecker(config, taskNameInConfig, "processOnlyBCs")
    setProcessDummy(config, dummyHasTasks) # dummy automizer
    
    # Write the updated configuration file into a temporary file
    updatedConfigFileName = "tempConfigTableMaker.json"
    if args.runParallel:
        updatedConfigFileName = "tempConfigFullAnalysisData.json"
    if runOverMC:
        updatedConfigFileName = "tempConfigTableMakerMC.json"
        if args.runParallel:
            updatedConfigFileName = "tempConfigFullAnalysisMC.json"
    
    dumpJson(updatedConfigFileName, config)
    
    # Check which dependencies need to be run
    depsToRun = commonDepsToRun(commonDeps)
    
    for processFunc in specificDeps.keys():
        if processFunc not in config[taskNameInConfig].keys():
            continue
        if config[taskNameInConfig][processFunc] == "true":
            if "processFull" in processFunc or "processBarrel" in processFunc or "processAmbiguousBarrel" in processFunc or "Filter" in processFunc: # NOTE For event filter, we need run all dependencies
                for dep in barrelDeps:
                    depsToRun[dep] = 1
            if "processFull" in processFunc or "processMuon" in processFunc or "processAmbiguousMuon" in processFunc or "Filter" in processFunc:
                for dep in muonDeps:
                    depsToRun[dep] = 1
            for dep in specificDeps[processFunc]:
                depsToRun[dep] = 1
    
    # Check which tables are required in the output
    tablesToProduce = tableProducerSkimming(config, taskNameInConfig, commonTables, barrelCommonTables, muonCommonTables, specificTables, specificDeps, runOverMC)
    
    writerConfigFileName = "aodWriterSkimmingTempConfig.json"
    
    # Generate the aod-writer output descriptor json file
    generateDescriptors("reducedAod", tablesToProduce, tables, writerConfigFileName, kFlag = False)
    
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
        if runOverMC is True:
            commandToRun = setParallelismOnSkimming(commandToRun, updatedConfigFileName, "o2-analysis-dq-efficiency", "tempConfigDQEfficiency.json", config)
        if runOverMC is False:
            commandToRun = setParallelismOnSkimming(commandToRun, updatedConfigFileName, "o2-analysis-dq-table-reader", "tempConfigTableReader.json", config)
    
    dispO2HelpMessage(args.helpO2, commandToRun)
    
    print("====================================================================================================================")
    logging.info("Command to run:")
    logging.info(commandToRun)
    print("====================================================================================================================")
    logging.info("Tables to produce:")
    logging.info(tablesToProduce.keys())
    print("====================================================================================================================")
    logging.info("Deps to run:")
    logging.info(depsToRun.keys())
    print("====================================================================================================================")
    dispArgs(allArgs) # Display all args
    os.system(commandToRun) # Execute O2 generated commands
    runPycacheRemover() # Run pycacheRemover


if __name__ == '__main__':
    sys.exit(main())
