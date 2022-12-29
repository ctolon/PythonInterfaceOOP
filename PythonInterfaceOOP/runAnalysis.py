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

# Orginal Task for Data: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/tableReader.cxx
# Orginal Task for MC: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqEfficiency.cxx

import logging
import logging.config
import os
import sys
from extramodules.dqTranscations import depsChecker, mandatoryArgChecker, aodFileChecker, jsonTypeChecker, mainTaskChecker
from extramodules.configSetter import SetArgsToArgumentParser, dispInterfaceMode, dispO2HelpMessage, generateDescriptors, setConfigs, setProcessDummy, debugSettings, dispArgs, setSwitch, tableProducerAnalysis
from extramodules.pycacheRemover import runPycacheRemover
from extramodules.utils import dumpJson, loadJson

# run template: `python3 runAnalysis.py <config.json> --task-name:<configurable|processFunc> parameter ...`
# parameter can be multiple like this:
# --analysis-track-selection:cfgTrackCuts jpsiPID1 jpsiPID2
# For run over MC (run dqEfficiency instead of tableReader) You need to Set runOverMC variable to true, if you don't convert it will work for interface tableReader


def main():
    
    # Switch runOverMC to True if you want work on dqEfficiency for MC else it will run for tableReader for Data
    runOverMC = False
    
    # Simple protection
    if not isinstance(runOverMC, bool):
        raise TypeError("[FATAL] runOverMC have to True or False! (in bool type)")
    
    # Load json config file for create interface arguments as MC or Data
    parsedJsonFile = "configs/configAnalysisData.json"
    if runOverMC is True:
        parsedJsonFile = "configs/configAnalysisMC.json"
    
    # Setting arguments for CLI
    setArgsToArgumentParser = SetArgsToArgumentParser(parsedJsonFile, ["timestamp-task", "tof-event-time", "bc-selection-task", "tof-pid-beta"])
    args = setArgsToArgumentParser.parseArgs()
    dummyHasTasks = setArgsToArgumentParser.dummyHasTasks
    processFuncs = setArgsToArgumentParser.processFuncs
    allArgs = vars(args) # for get args
    
    # yapf: disable
    sameEventPairingTaskName = "analysis-same-event-pairing"
    sameEventPairingDeps = {
        "processDecayToEESkimmed": {"analysis-track-selection": "processSkimmed"},
        "processDecayToEEPrefilterSkimmed": {"analysis-track-selection": "processSkimmed", "analysis-prefilter-selection": "processBarrelSkimmed"},
        "processDecayToMuMuSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processDecayToMuMuVertexingSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processVnDecayToEESkimmed": {"analysis-track-selection": "processSkimmed"},
        "processVnDecayToMuMuSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processElectronMuonSkimmed": {"analysis-track-selection": "processSkimmed", "analysis-muon-selection": "processSkimmed"},
        "processAllSkimmed": {"analysis-track-selection": "processSkimmed", "analysis-muon-selection": "processSkimmed"},
        }
    eventMixingTaskName = "analysis-event-mixing"
    eventMixingDeps = {
        "processBarrelSkimmed": {"analysis-track-selection": "processSkimmed"},
        "processMuonSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processBarrelMuonSkimmed": {"analysis-track-selection": "processSkimmed", "analysis-muon-selection": "processSkimmed"},
        "processBarrelVnSkimmed": {"analysis-track-selection": "processSkimmed"},
        "processMuonVnSkimmed": {"analysis-muon-selection": "processSkimmed"}
        }
    dileptonTrackTaskName = "analysis-dilepton-track"
    dileptonTrackDeps = {
        "processDimuonMuonSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processDielectronKaonSkimmed": {"analysis-track-selection": "processSkimmed"}
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
        "Dileptons": {"table": "AOD/RTDILEPTON/0"},
        "DileptonsExtra": {"table": "AOD/RTDILEPTONEXTRA/0"},
        "DileptonFlow": {"table": "AOD/RTDILEPTONFLOW/0"},
        "DimuonsAll": {"table": "AOD/RTDIMUONALL/0"}
        }
    # yapf: enable
    # Tables to be written, per process function
    commonTables = ["ReducedEvents", "ReducedEventsExtended", "ReducedEventsVtxCov", "Dileptons", "DileptonsExtra"]
    barrelCommonTables = ["ReducedTracks", "ReducedTracksBarrel", "ReducedTracksBarrelPID"]
    muonCommonTables = ["ReducedMuons", "ReducedMuonsExtra"]
    specificTables = {
        "processAllSkimmed": [],
        "processDecayToEESkimmed": [],
        "processDecayToEEVertexingSkimmed": ["ReducedTracksBarrelCov"],
        "processDecayToEEPrefilterSkimmed": [],
        "processDecayToMuMuSkimmed": [],
        "processDecayToMuMuVertexingSkimmed": ["ReducedMuonsCov"],
        "processVnDecayToEEskimmed": ["ReducedEventsQvector", "DileptonFlow"],
        "processVnDecayToMuMuSkimmed": ["ReducedEventsQvector", "DileptonFlow"],
        "processElectronMuonSkimmed": [],
        }
    
    # Debug settings
    fileName = "tableReader.log"
    if runOverMC:
        fileName = "dqEfficiency.log"
    debugSettings(args.debug, args.logFile, fileName)
    
    # if cliMode true, Overrider mode else additional mode
    cliMode = args.override
    
    # Basic validations
    jsonTypeChecker(args.cfgFileName)
    jsonTypeChecker(parsedJsonFile)
    
    # Load the configuration file provided as the first parameter
    config = loadJson(args.cfgFileName)
    
    taskNameInCommandLine = "o2-analysis-dq-table-reader"
    taskNameInConfig = "analysis-event-selection"
    if runOverMC:
        taskNameInCommandLine = "o2-analysis-dq-efficiency"
    
    # Transaction
    mainTaskChecker(config, taskNameInConfig)
    
    # Interface Mode message
    dispInterfaceMode(cliMode)
    
    # Set arguments to config json file
    setConfigs(allArgs, config, cliMode)
    
    # process function automation based on cliMode
    setSwitch(config, processFuncs, allArgs, cliMode, [])
    
    # Transacations
    aodFileChecker(allArgs["internal_dpl_aod_reader:aod_file"])
    depsChecker(config, sameEventPairingDeps, sameEventPairingTaskName)
    depsChecker(config, eventMixingDeps, eventMixingTaskName)
    depsChecker(config, dileptonTrackDeps, dileptonTrackTaskName)
    mandatoryArgChecker(config, taskNameInConfig, "processSkimmed")
    setProcessDummy(config, dummyHasTasks) # dummy automizer
    
    # Write the updated configuration file into a temporary file
    updatedConfigFileName = "tempConfigTableReader.json"
    if runOverMC:
        updatedConfigFileName = "tempConfigDQEfficiency.json"
    
    dumpJson(updatedConfigFileName, config)
    if args.writer == "true":
        tablesToProduce = tableProducerAnalysis(config, "analysis-same-event-pairing", commonTables, barrelCommonTables, muonCommonTables, specificTables, runOverMC)
        
        writerConfigFileName = "aodWriterAnalysisTempConfig.json"
        
        # Generate the aod-writer output descriptor json file
        generateDescriptors("dileptonAOD", tablesToProduce, tables, writerConfigFileName, kFlag = False)
    
    commandToRun = f"{taskNameInCommandLine} --configuration json://{updatedConfigFileName} -b"
    if args.writer == "true":
        #if args.writer is not None:
        #commandToRun = f"{taskNameInCommandLine} --configuration json://{updatedConfigFileName} --aod-writer-json {args.writer} -b"
        commandToRun = f"{taskNameInCommandLine} --configuration json://{updatedConfigFileName} --aod-writer-json {writerConfigFileName} -b"
    
    dispO2HelpMessage(args.helpO2, commandToRun)
    
    if args.runParallel is True:
        dispArgs(allArgs)
        sys.exit()
    print("====================================================================================================================")
    logging.info("Command to run:")
    logging.info(commandToRun)
    print("====================================================================================================================")
    if args.writer == "true":
        print("====================================================================================================================")
        logging.info("Tables to produce:")
        logging.info(tablesToProduce.keys())
        print("====================================================================================================================")
    dispArgs(allArgs) # Display all args
    
    os.system(commandToRun) # Execute O2 generated commands
    runPycacheRemover() # Run pycacheRemover


if __name__ == '__main__':
    sys.exit(main())
