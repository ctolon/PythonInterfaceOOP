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
import sys
import logging
import logging.config
import os
from extramodules.dqTranscations import mandatoryArgChecker, aodFileChecker, centralityChecker, forgettedArgsChecker, jsonTypeChecker, filterSelsChecker, mainTaskChecker, trackPropagationChecker
from extramodules.configSetter import setProcessDummy, setSwitch, setConverters, setConfig, debugSettings, dispArgs, generateDescriptors, setPrefixSuffix, tableProducer
from extramodules.pycacheRemover import runPycacheRemover
from dqtasks.tableMaker import TableMaker

def main():

    # Predefined selections for setSwitch function
    centralityTableParameters = [
        "estRun2V0M", "estRun2SPDtks", "estRun2SPDcls", "estRun2CL0", "estRun2CL1", "estFV0A", "estFT0M", "estFDDM", "estNTPV",
        ]
    ft0Parameters = ["processFT0", "processNoFT0", "processOnlyFT0", "processRun2"]
    pidParameters = ["pid-el", "pid-mu", "pid-pi", "pid-ka", "pid-pr", "pid-de", "pid-tr", "pid-he", "pid-al",]
    covParameters = ["processStandard", "processCovariance"]
    sliceParameters = ["processWoSlice", "processWSlice"]
    trackPIDQAParameters = ["processQA"]
    v0GammaQAParameters = ["processNM"]
    fullSearch = []
    barrelSearch = []
    muonSearch = []
    centSearch = []
    filterSearch = []

    # All Dependencies
    commonDeps = ["o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table"]
    barrelDeps = [
        "o2-analysis-trackselection", "o2-analysis-trackextension", "o2-analysis-pid-tof-base", "o2-analysis-pid-tof",
        "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta", "o2-analysis-pid-tpc-full"
        ]
    muonDeps = ["o2-analysis-fwdtrackextension"]
    specificDeps = {
        "processFull": [],
        "processFullTiny": [],
        "processFullWithCov": [],
        "processFullWithCent": ["o2-analysis-centrality-table"],
        "processBarrelOnly": [],
        "processBarrelOnlyWithCov": [],
        "processBarrelOnlyWithV0Bits": ["o2-analysis-dq-v0-selector"],
        "processBarrelOnlyWithDalitzBits" : ["o2-analysis-dq-dalitz-selection"],
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
        "AmbiguousTracksFwd": {"table": "AOD/AMBIGUOUSFWDTR/0"}
        #"DalitzBits": {"table": "AOD/DALITZBITS/0"},
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
        "processBarrelOnlyWithDalitzBits" : [],
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

    #forgettedArgsChecker(allArgs) # Transaction management

    # adding prefix for setSwitch function
    args.process = setPrefixSuffix(args.process, "process", '', True, False)
    args.pid = setPrefixSuffix(args.pid, "pid-", '', True, False)
    args.est = setPrefixSuffix(args.est, "est", '', True, False)
    args.FT0 = setPrefixSuffix(args.FT0, "process", '', True, False)
    args.isCovariance = setPrefixSuffix(args.isCovariance, "process", '', True, False)
    args.isWSlice = setPrefixSuffix(args.isWSlice, "process", '', True, False)
    args.NM = setPrefixSuffix(args.NM, "process", '', True, False)
    args.QA = setPrefixSuffix(args.QA, "process", '', True, False)

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

    # Interface Process
    logging.info("Only Select Configured as %s", cliMode)
    if cliMode == "true":
        logging.info("INTERFACE MODE : JSON Overrider")
    if cliMode == "false":
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
                
                setConfig(config, task, cfg, allArgs, cliMode)
                setSwitch(config, task, cfg, allArgs, cliMode, "est", centralityTableParameters, "1/-1")
                setSwitch(config, task, cfg, allArgs, cliMode, "pid", pidParameters, "1/-1")
                setSwitch(config, task, cfg, allArgs, cliMode, "process", specificDeps.keys(), "true/false")
                setSwitch(config, task, cfg, allArgs, "true", "isCovariance", covParameters, "true/false")
                setSwitch(config, task, cfg, allArgs, "true", "isWSlice", sliceParameters, "true/false")
                setSwitch(config, task, cfg, allArgs, cliMode, "QA", trackPIDQAParameters, "true/false")
                setSwitch(config, task, cfg, allArgs, cliMode, "NM", v0GammaQAParameters, "true/false")
                setSwitch(config, task, cfg, allArgs, "true", "FT0", ft0Parameters, "true/false", "tof-event-time")
                mandatoryArgChecker(config, task, cfg, taskNameInConfig, "processOnlyBCs")

    setProcessDummy(config, dummyHasTasks) # dummy automizer

    # Transactions
    centralityChecker(config, args.process, args.syst, centSearch)
    filterSelsChecker(args.cfgBarrelSels, args.cfgMuonSels, args.cfgBarrelTrackCuts, args.cfgMuonsCuts, allArgs)
    aodFileChecker(args.aod)
    trackPropagationChecker(args.add_track_prop, barrelDeps)

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

    commandToRun = setConverters(allArgs, updatedConfigFileName, commandToRun)

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
