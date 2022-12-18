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
from extramodules.configSetter import SetArgsToArgumentParser, dispInterfaceMode, setConfigs, setProcessDummy, debugSettings, dispArgs
from extramodules.pycacheRemover import runPycacheRemover
from extramodules.utils import dumpJson, loadJson


def main():

    # Switch runOverMC to True if you want work on dqEfficiency for MC else it will run for tableReader for Data
    runOverMC = False    
    
    # Simple protection
    if not isinstance(runOverMC, bool):
        print(f"[FATAL] runOverMC have to true or false!")
        sys.exit()
    
    # Load json config file for create interface arguments as MC or Data
    parsedJsonFile = "configs/configAnalysisData.json"
    if runOverMC is True:
        parsedJsonFile = "configs/configAnalysisMC.json"
    
    # Setting arguments for CLI
    setArgsToArgumentParser = SetArgsToArgumentParser(parsedJsonFile, ["timestamp-task", "tof-event-time", "bc-selection-task", "tof-pid-beta"])
    args = setArgsToArgumentParser.parser.parse_args()
    dummyHasTasks = setArgsToArgumentParser.dummyHasTasks
    allArgs = vars(args) # for get args
    
    # yapf: disable
    sameEventPairingTaskName = "analysis-same-event-pairing"
    sameEventPairingDeps = {
        "processDecayToEESkimmed": {"analysis-track-selection": "processSkimmed"},
        "processDecayToEEPrefilterSkimmed": {"analysis-track-selection": "processSkimmed","analysis-prefilter-selection": "processBarrelSkimmed"},
        "processDecayToMuMuSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processDecayToMuMuVertexingSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processVnDecayToEESkimmed": {"analysis-track-selection": "processSkimmed"},
        "processVnDecayToMuMuSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processElectronMuonSkimmed": {"analysis-track-selection": "processSkimmed","analysis-muon-selection": "processSkimmed"},
        "processAllSkimmed": {"analysis-track-selection": "processSkimmed","analysis-muon-selection": "processSkimmed"},
        }
    eventMixingTaskName = "analysis-event-mixing"
    eventMixingDeps = {
        "processBarrelSkimmed": {"analysis-track-selection": "processSkimmed"},
        "processMuonSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processBarrelMuonSkimmed": {"analysis-track-selection": "processSkimmed","analysis-muon-selection": "processSkimmed"},
        "processBarrelVnSkimmed": {"analysis-track-selection": "processSkimmed"},
        "processMuonVnSkimmed": {"analysis-muon-selection": "processSkimmed"}
        }
    dileptonTrackTaskName = "analysis-dilepton-track"
    dileptonTrackDeps = {
        "processDimuonMuonSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processDielectronKaonSkimmed": {"analysis-track-selection": "processSkimmed"}
        }
    # yapf: enable
    
    # Debug settings
    fileName = "tableReader.log"
    if runOverMC:
        fileName = "dqEfficiency.log"
    debugSettings(args.debug, args.logFile, fileName)
    
    # if cliMode true, Overrider mode else additional mode
    cliMode = args.onlySelect
    
    # Load the configuration file provided as the first parameter
    config = loadJson(args.cfgFileName)
    
    # Transaction
    jsonTypeChecker(args.cfgFileName)
    jsonTypeChecker(parsedJsonFile)
    
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
    
    commandToRun = f"{taskNameInCommandLine} --configuration json://{updatedConfigFileName} -b"
    if args.writer is not None:
        commandToRun = f"{taskNameInCommandLine} --configuration json://{updatedConfigFileName} --aod-writer-json {args.writer} -b"
        
    if args.helpO2 is True:
        commandToRun += " --help full"
        os.system(commandToRun)
        sys.exit()
    print("====================================================================================================================")
    logging.info("Command to run:")
    logging.info(commandToRun)
    print("====================================================================================================================")
    dispArgs(allArgs) # Display all args
    if args.runParallel is True:
        sys.exit()
    os.system(commandToRun) # Execute O2 generated commands
    runPycacheRemover() # Run pycacheRemover


if __name__ == '__main__':
    sys.exit(main())
