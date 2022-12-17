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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqEfficiency.cxx

import sys
import logging
import logging.config
import os
from extramodules.dqTranscations import mandatoryArgChecker, aodFileChecker, depsChecker, jsonTypeChecker, mainTaskChecker
from extramodules.configSetter import dispInterfaceMode, setArgsToArgParser, setConfigs, debugSettings, setProcessDummy, dispArgs
from extramodules.pycacheRemover import runPycacheRemover
from extramodules.utils import dumpJson, loadJson


def main():
    
    # Setting arguments for CLI
    parsedJsonFile = "configs/configAnalysisMC.json"
    args = setArgsToArgParser(parsedJsonFile)
    allArgs = vars(args) # for get args
    
    # yapf: disable
    sameEventPairingTaskName = "analysis-same-event-pairing"
    sameEventPairingDeps = {
        "processDecayToEESkimmed": {"analysis-track-selection": "processSkimmed"},
        "processDecayToEEVertexingSkimmed": {"analysis-track-selection": "processSkimmed"},
        "processDecayToMuMuSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processDecayToMuMuVertexingSkimmed": {"analysis-muon-selection": "processSkimmed"}
        }
    dileptonTrackTaskName = "analysis-dilepton-track"
    dileptonTrackDeps = {
        "processDimuonMuonSkimmed": {"analysis-muon-selection": "processSkimmed"},
        "processDielectronKaonSkimmed": {"analysis-track-selection": "processSkimmed"}
        }
    # yapf: enable
    
    # Debug Settings
    debugSettings(args.debug, args.logFile, fileName = "dqEfficiency.log")
    
    # if cliMode true, Overrider mode else additional mode
    cliMode = args.onlySelect
    
    # Load the configuration file provided as the first parameter
    config = loadJson(args.cfgFileName)
    
    jsonTypeChecker(args.cfgFileName)
    jsonTypeChecker(parsedJsonFile)
    
    taskNameInCommandLine = "o2-analysis-dq-efficiency"
    taskNameInConfig = "analysis-event-selection"
    
    mainTaskChecker(config, taskNameInConfig)
    
    # Interface Mode message
    dispInterfaceMode(cliMode)
    
    # Set arguments to config json file
    setConfigs(allArgs, config, cliMode)
    
    # Transacations
    aodFileChecker(allArgs["internal_dpl_aod_reader:aod_file"])
    depsChecker(config, sameEventPairingDeps, sameEventPairingTaskName)
    depsChecker(config, dileptonTrackDeps, dileptonTrackTaskName)
    mandatoryArgChecker(config, taskNameInConfig, "processSkimmed")
    setProcessDummy(config) # dummy automizer
    
    # Write the updated configuration file into a temporary file
    updatedConfigFileName = "tempConfigDQEfficiency.json"
    
    dumpJson(updatedConfigFileName, config)
    
    commandToRun = f"{taskNameInCommandLine} --configuration json://{updatedConfigFileName} -b"
    if args.writer is not None:
        commandToRun = f"{taskNameInCommandLine} --configuration json://{updatedConfigFileName} --aod-writer-json {args.writer} -b"
    
    print("====================================================================================================================")
    logging.info("Command to run:")
    logging.info(commandToRun)
    print("====================================================================================================================")
    dispArgs(allArgs) # Display all args
    
    if args.runParallel is False:
        os.system(commandToRun) # Execute O2 generated commands
        runPycacheRemover() # Run pycacheRemover


if __name__ == '__main__':
    sys.exit(main())
