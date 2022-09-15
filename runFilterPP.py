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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/filterPP.cxx

import json
import sys
import logging
import logging.config
from logging import handlers
import os
import argparse

from extramodules.actionHandler import NoAction
from extramodules.actionHandler import ChoicesAction
from extramodules.debugOptions import DebugOptions
from extramodules.stringOperations import listToString, stringToList, multiConfigurableSet
from extramodules.dqExceptions import (
    CfgInvalidFormatError,
    ForgettedArgsError,
    NotInAlienvError,
    TasknameNotFoundInConfigFileError,
    BarrelSelsNotInBarrelTrackCutsError,
    BarrelTrackCutsNotInBarrelSelsError,
    MuonsCutsNotInMuonSelsError,
    MuonSelsNotInMuonsCutsError,
    MandatoryArgNotFoundError,
)

from commondeps.eventSelection import EventSelectionTask
from commondeps.multiplicityTable import MultiplicityTable
from commondeps.pidTOFBase import TofEventTime
from commondeps.pidTOFBeta import TofPidBeta
from commondeps.pidTPCTOFFull import TpcTofPidFull
from commondeps.trackPropagation import TrackPropagation
from commondeps.trackselection import TrackSelectionTask

from dqtasks.filterPP import DQFilterPPTask

from pycacheRemover import PycacheRemover

"""
argcomplete - Bash tab completion for argparse
Documentation https://kislyuk.github.io/argcomplete/
Instalation Steps
pip install argcomplete
sudo activate-global-python-argcomplete
Only Works On Local not in O2
Activate libraries in below and activate #argcomplete.autocomplete(parser) line
"""
import argcomplete
from argcomplete.completers import ChoicesCompleter

###################################
# Interface Predefined Selections #
###################################

centralityTableParameters = [
    "estRun2V0M",
    "estRun2SPDtks",
    "estRun2SPDcls",
    "estRun2CL0",
    "estRun2CL1",
    "estFV0A",
    "estFT0M",
    "estFDDM",
    "estNTPV",
]
# TODO: Add genname parameter

ft0Parameters = ["processFT0", "processNoFT0", "processOnlyFT0", "processRun2"]

pidParameters = [
    "pid-el",
    "pid-mu",
    "pid-pi",
    "pid-ka",
    "pid-pr",
    "pid-de",
    "pid-tr",
    "pid-he",
    "pid-al",
]

threeSelectedList = []

booleanSelections = ["true", "false"]

# List for Transcation management for FilterPP
muonCutList = []  # List --> transcation management for filterPP
barrelTrackCutList = []  # List --> transcation management for filterPP
barrelSelsList = []
muonSelsList = []
barrelSelsListAfterSplit = []
muonSelsListAfterSplit = []

O2DPG_ROOT = os.environ.get("O2DPG_ROOT")
QUALITYCONTROL_ROOT = os.environ.get("QUALITYCONTROL_ROOT")
O2_ROOT = os.environ.get("O2_ROOT")
O2PHYSICS_ROOT = os.environ.get("O2PHYSICS_ROOT")

################
# Dependencies #
################

commonDeps = [
    "o2-analysis-timestamp",
    "o2-analysis-event-selection",
    "o2-analysis-multiplicity-table",
    "o2-analysis-trackselection",
    "o2-analysis-trackextension",
    "o2-analysis-pid-tof-base",
    "o2-analysis-pid-tof",
    "o2-analysis-pid-tof-full",
    "o2-analysis-pid-tof-beta",
    "o2-analysis-pid-tpc-full",
]

#################
# Init Workflow #
#################


class RunFilterPP(object):
    """
    This class is for managing the workflow by using the interface arguments from
    all other Common dependencies and the filterPP Task's own arguments in a combined structure.

    Args:
      object (parser_args() object): runFilterPP.py workflow
    """

    def __init__(
        self,
        parserRunFilterPP=argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Example Usage: ./runFilterPP.py <yourConfig.json> --arg value",
        ),
        filterPP=DQFilterPPTask(),
        eventSelection=EventSelectionTask(),
        multiplicityTable=MultiplicityTable(),
        tofEventTime=TofEventTime(),
        tofPidBeta=TofPidBeta(),
        tpcTofPidFull=TpcTofPidFull(),
        trackPropagation=TrackPropagation(),
        trackSelection=TrackSelectionTask(),
        debugOptions=DebugOptions(),
    ):
        super(RunFilterPP, self).__init__()
        self.parserRunFilterPP = parserRunFilterPP
        self.filterPP = filterPP
        self.eventSelection = eventSelection
        self.multiplicityTable = multiplicityTable
        self.tofEventTime = tofEventTime
        self.tofPidBeta = tofPidBeta
        self.tpcTofPidFull = tpcTofPidFull
        self.trackPropagation = trackPropagation
        self.trackSelection = trackSelection
        self.debugOptions = debugOptions
        self.parserRunFilterPP.register("action", "none", NoAction)
        self.parserRunFilterPP.register("action", "store_choice", ChoicesAction)

    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """

        # Core Part
        groupCoreSelections = self.parserRunFilterPP.add_argument_group(
            title="Core configurations that must be configured"
        )
        groupCoreSelections.add_argument(
            "cfgFileName",
            metavar="Config.json",
            default="config.json",
            help="config JSON file name",
        )
        groupTaskAdders = self.parserRunFilterPP.add_argument_group(
            title="Additional Task Adding Options"
        )
        groupTaskAdders.add_argument(
            "--add_mc_conv",
            help="Add the converter from mcparticle to mcparticle+001 (Adds your workflow o2-analysis-mc-converter task)",
            action="store_true",
        )
        groupTaskAdders.add_argument(
            "--add_fdd_conv",
            help="Add the fdd converter (Adds your workflow o2-analysis-fdd-converter task)",
            action="store_true",
        )
        groupTaskAdders.add_argument(
            "--add_track_prop",
            help="Add track propagation to the innermost layer (TPC or ITS) (Adds your workflow o2-analysis-track-propagation task)",
            action="store_true",
        )

        # aod
        groupDPLReader = self.parserRunFilterPP.add_argument_group(
            title="Data processor options: internal-dpl-aod-reader"
        )
        groupDPLReader.add_argument(
            "--aod", help="Add your AOD File with path", action="store", type=str
        )

        # automation params
        groupAutomations = self.parserRunFilterPP.add_argument_group(title="Automation Parameters")
        groupAutomations.add_argument(
            "--onlySelect",
            help="If false JSON Overrider Interface If true JSON Additional Interface",
            action="store",
            default="true",
            type=str.lower,
            choices=booleanSelections,
        ).completer = ChoicesCompleter(booleanSelections)
        groupAutomations.add_argument(
            "--autoDummy",
            help="Dummy automize parameter (don't configure it, true is highly recomended for automation)",
            action="store",
            default="true",
            type=str.lower,
            choices=booleanSelections,
        ).completer = ChoicesCompleter(booleanSelections)

        # helper lister commands
        # groupAdditionalHelperCommands = self.parserRunFilterPP.add_argument_group(title="Additional Helper Command Options")
        # groupAdditionalHelperCommands.add_argument("--cutLister", help="List all of the analysis cuts from CutsLibrary.h", action="store_true")

    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """

        argcomplete.autocomplete(self.parserRunFilterPP, always_complete_options=False)
        return self.parserRunFilterPP.parse_args()

    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """

        self.eventSelection.parserEventSelectionTask = self.parserRunFilterPP
        self.eventSelection.addArguments()

        self.multiplicityTable.parserMultiplicityTable = self.parserRunFilterPP
        self.multiplicityTable.addArguments()

        self.tofEventTime.parserTofEventTime = self.parserRunFilterPP
        self.tofEventTime.addArguments()

        self.tofPidBeta.parserTofPidBeta = self.parserRunFilterPP
        self.tofPidBeta.addArguments()

        self.tpcTofPidFull.parserTpcTofPidFull = self.parserRunFilterPP
        self.tpcTofPidFull.addArguments()

        self.trackPropagation.parserTrackPropagation = self.parserRunFilterPP
        self.trackPropagation.addArguments()

        self.trackSelection.parserTrackSelectionTask = self.parserRunFilterPP
        self.trackSelection.addArguments()

        self.debugOptions.parserDebugOptions = self.parserRunFilterPP
        self.debugOptions.addArguments()

        self.filterPP.parserDQFilterPPTask = self.parserRunFilterPP
        self.filterPP.addArguments()

        self.addArguments()


# init args manually
initArgs = RunFilterPP()
initArgs.mergeArgs()
initArgs.parseArgs()

args = initArgs.parseArgs()
configuredCommands = vars(args)  # for get args

# Debug Settings
if args.debug and (not args.logFile):
    DEBUG_SELECTION = args.debug
    numeric_level = getattr(logging, DEBUG_SELECTION.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % DEBUG_SELECTION)
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=DEBUG_SELECTION)

if args.logFile and args.debug:
    log = logging.getLogger("")
    level = logging.getLevelName(args.debug)
    log.setLevel(level)
    format = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s")

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)

    loggerFile = "filterPP.log"
    if os.path.isfile(loggerFile):
        os.remove(loggerFile)

    fh = handlers.RotatingFileHandler(loggerFile, maxBytes=(1048576 * 5), backupCount=7, mode="w")
    fh.setFormatter(format)
    log.addHandler(fh)

# Transcation management for forgettining assign a value to parameters
forgetParams = []
for key, value in configuredCommands.items():
    if value is not None:
        if (isinstance(value, str) or isinstance(value, list)) and len(value) == 0:
            forgetParams.append(key)
try:
    if len(forgetParams) > 0:
        raise ForgettedArgsError(forgetParams)
except ForgettedArgsError as e:
    logging.exception(e)
    sys.exit()

###################
# HELPER MESSAGES #
###################

"""
if args.cutLister:
    counter = 0
    print("Analysis Cut Options :")
    print("====================")
    temp = ""
    for i in allAnalysisCuts:
        if len(temp) == 0:
            temp = temp + i
        else:
            temp = temp + "," + i
        counter = counter + 1
        if counter == 3:
            temp = stringToList(temp)
            threeSelectedList.append(temp)
            temp = ""
            counter = 0
    for list_ in threeSelectedList:
        print("{:<40s} {:<40s} {:<40s}".format(*list_))
    sys.exit()
"""

######################
# PREFIX ADDING PART #
######################

# add prefix for args.pid for pid selection
if args.pid is not None:
    prefix_pid = "pid-"
    args.pid = [prefix_pid + sub for sub in args.pid]

# add prefix for args.FT0 for tof-event-time
if args.FT0 is not None:
    prefix_process = "process"
    args.FT0 = prefix_process + args.FT0

######################################################################################


# Make some checks on provided arguments
if len(sys.argv) < 2:
    logging.error("Invalid syntax! The command line should look like this:")
    logging.info("  ./runFilterPP.py <yourConfig.json> --param value ...")
    sys.exit()

# Load the configuration file provided as the first parameter
cfgControl = sys.argv[1] == args.cfgFileName
isConfigJson = sys.argv[1].endswith(".json")
config = {}

try:
    if cfgControl:
        if not isConfigJson:
            raise CfgInvalidFormatError(sys.argv[1])
        else:
            logging.info("%s is valid json config file", args.cfgFileName)

except CfgInvalidFormatError as e:
    logging.exception(e)
    sys.exit()


with open(sys.argv[1]) as configFile:
    config = json.load(configFile)


"""
try:
    if cfgControl:
        with open(args.cfgFileName) as configFile:
            config = json.load(configFile)
    else:
        logging.error("Invalid syntax! After the script you must define your json configuration file!!! The command line should look like this:")
        logging.info("  ./runFilterPP.py<yourConfig.json> <-runData|-runMC> --param value ...")
        sys.exit()

except FileNotFoundError:
    isConfigJson = sys.argv[1].endswith(".json")
    if not isConfigJson:
            logging.error("Invalid syntax! After the script you must define your json configuration file!!! The command line should look like this:")
            logging.info(" ./runFilterPP.py <yourConfig.json> --param value ...")
            sys.exit()
    logging.error("Your JSON Config File found in path!!!")
    sys.exit()

"""

taskNameInConfig = "d-q-filter-p-p-task"
taskNameInCommandLine = "o2-analysis-dq-filter-pp"

# Check dependencies
try:
    if taskNameInConfig not in config:
        raise TasknameNotFoundInConfigFileError(taskNameInConfig)
    else:
        logging.info("%s is in your JSON Config File", taskNameInConfig)
except TasknameNotFoundInConfigFileError as e:
    logging.exception(e)
    sys.exit()

# Check alienv
try:
    if O2PHYSICS_ROOT is None:
        raise NotInAlienvError
    else:
        logging.info("You are in %s alienv", O2PHYSICS_ROOT)
except NotInAlienvError as e:
    logging.exception(e)
    sys.exit()

#############################
# Start Interface Processes #
#############################

logging.info("Only Select Configured as %s", args.onlySelect)
if args.onlySelect == "true":
    logging.info("INTERFACE MODE : JSON Overrider")
if args.onlySelect == "false":
    logging.info("INTERFACE MODE : JSON Additional")

for key, value in config.items():
    if isinstance(value, dict):
        for value, value2 in value.items():

            # aod
            if value == "aod-file" and args.aod:
                config[key][value] = args.aod
                logging.debug(" - [%s] %s : %s", key, value, args.aod)

            # DQ Selections for muons and barrel tracks
            if value == "processSelection" and args.process:
                for keyCfg, valueCfg in configuredCommands.items():
                    if valueCfg is not None:  # Cleaning None types, because can"t iterate in None type
                        if keyCfg == "process":  # Only Select key for analysis

                            if key == "d-q-barrel-track-selection":
                                if "barrelTrackSelection" in valueCfg:
                                    config[key][value] = "true"
                                    logging.debug(" - [%s] %s : true", key, value)
                                if (
                                    "barrelTrackSelection" not in valueCfg
                                    and args.onlySelect == "true"
                                ):
                                    config[key][value] = "false"
                                    logging.debug(" - [%s] %s : false", key, value)

                            if key == "d-q-muons-selection":
                                if "muonSelection" in valueCfg:
                                    config[key][value] = "true"
                                    logging.debug(" - [%s] %s : true", key, value)
                                if "muonSelection" not in valueCfg and args.onlySelect == "true":
                                    config[key][value] = "false"
                                    logging.debug(" - [%s] %s : false", key, value)

            # DQ Selections event
            if value == "processEventSelection" and args.process:
                for keyCfg, valueCfg in configuredCommands.items():
                    if valueCfg is not None:  # Cleaning None types, because can"t iterate in None type
                        if keyCfg == "process":  # Only Select key for analysis

                            if key == "d-q-event-selection-task":
                                if "eventSelection" in valueCfg:
                                    config[key][value] = "true"
                                    logging.debug(" - [%s] %s : true", key, value)
                                if "eventSelection" not in valueCfg:
                                    logging.warning(
                                        "YOU MUST ALWAYS CONFIGURE eventSelection value in --process parameter!! It is Missing and this issue will fixed by CLI"
                                    )
                                    config[key][value] = "true"
                                    logging.debug(" - [%s] %s : true", key, value)

            # DQ Tiny Selection for barrel track
            if value == "processSelectionTiny" and args.process:
                for keyCfg, valueCfg in configuredCommands.items():
                    if valueCfg is not None:  # Cleaning None types, because can"t iterate in None type
                        if keyCfg == "process":  # Only Select key for analysis

                            if key == "d-q-barrel-track-selection":
                                if "barrelTrackSelectionTiny" in valueCfg:
                                    config[key][value] = "true"
                                    logging.debug(" - [%s] %s : true", key, value)
                                if (
                                    "barrelTrackSelectionTiny" not in valueCfg
                                    and args.onlySelect == "true"
                                ):
                                    config[key][value] = "false"
                                    logging.debug(" - [%s] %s : false", key, value)

            # DQ Tiny Selection for filterPP
            if value == "processFilterPPTiny" and args.process:
                for keyCfg, valueCfg in configuredCommands.items():
                    if valueCfg is not None:  # Cleaning None types, because can"t iterate in None type
                        if keyCfg == "process":  # Only Select key for analysis

                            if key == "d-q-filter-p-p-task":
                                if "filterPPSelectionTiny" in valueCfg:
                                    config[key][value] = "true"
                                    config[key]["processFilterPP"] = "false"
                                    logging.debug(" - [%s] %s : true", key, value)
                                    logging.debug(" - [%s] processFilterPP : false", key)
                                if (
                                    "filterPPSelectionTiny" not in valueCfg
                                    and args.onlySelect == "true"
                                ):
                                    config[key][value] = "false"
                                    config[key]["processFilterPP"] = "true"
                                    logging.debug(" - [%s] %s : false", key, value)
                                    logging.debug(" - [%s] processFilterPP : true", key)

            # Filter PP Selections
            if value == "cfgBarrelSels" and args.cfgBarrelSels:
                multiConfigurableSet(config, key, value, args.cfgBarrelSels, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgBarrelSels)
            if value == "cfgMuonSels" and args.cfgMuonSels:
                multiConfigurableSet(config, key, value, args.cfgMuonSels, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgMuonSels)

            # DQ Cuts
            if value == "cfgEventCuts" and args.cfgEventCuts:
                multiConfigurableSet(config, key, value, args.cfgEventCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgEventCuts)
            if value == "cfgBarrelTrackCuts" and args.cfgBarrelTrackCuts:
                multiConfigurableSet(config, key, value, args.cfgBarrelTrackCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgBarrelTrackCuts)
            if value == "cfgMuonsCuts" and args.cfgMuonsCuts:
                multiConfigurableSet(config, key, value, args.cfgMuonsCuts, args.onlySelect)
                logging.debug(" - [%s] %s : %s", key, value, args.cfgMuonsCuts)

            # QA Options
            if value == "cfgWithQA" and args.cfgWithQA:
                config[key][value] = args.cfgWithQA
                logging.debug(" - [%s] %s : %s", key, value, args.cfgWithQA)

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

            # event-selection
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

            if value == "processDummy" and args.autoDummy:
                if config["d-q-barrel-track-selection"]["processSelection"] == "true":
                    config["d-q-barrel-track-selection"]["processDummy"] = "false"
                if config["d-q-barrel-track-selection"]["processSelection"] == "false":
                    config["d-q-barrel-track-selection"]["processDummy"] = "true"

                if config["d-q-muons-selection"]["processSelection"] == "true":
                    config["d-q-muons-selection"]["processDummy"] = "false"
                if config["d-q-muons-selection"]["processSelection"] == "false":
                    config["d-q-muons-selection"]["processDummy"] = "true"

                if config["d-q-event-selection-task"]["processEventSelection"] == "true":
                    config["d-q-event-selection-task"]["processDummy"] = "false"
                if config["d-q-event-selection-task"]["processEventSelection"] == "false":
                    config["d-q-event-selection-task"]["processDummy"] = "true"

                if config["d-q-filter-p-p-task"]["processFilterPP"] == "true":
                    config["d-q-filter-p-p-task"]["processDummy"] = "false"
                if config["d-q-filter-p-p-task"]["processFilterPP"] == "false":
                    config["d-q-filter-p-p-task"]["processDummy"] = "true"


# ================================================================
# Transcation Management for barrelsels and muonsels in filterPP
# ================================================================

for key, value in configuredCommands.items():
    if value is not None:
        if key == "cfgMuonsCuts":
            muonCutList.append(value)
        if key == "cfgBarrelTrackCuts":
            barrelTrackCutList.append(value)
        if key == "cfgBarrelSels":
            barrelSelsList.append(value)
        if key == "cfgMuonSels":
            muonSelsList.append(value)

##############################
# For MuonSels From FilterPP #
##############################
if args.cfgMuonSels:

    try:
        if args.cfgMuonsCuts is None:
            raise MandatoryArgNotFoundError(args.cfgMuonsCuts)
        else:
            pass

    except MandatoryArgNotFoundError as e:
        logging.exception(e)
        logging.error(
            "For configure to cfgMuonSels (For DQ Filter PP Task), you must also configure cfgMuonsCuts!!!"
        )
        sys.exit()

    # Convert List Muon Cuts
    for muonCut in muonCutList:
        muonCut = stringToList(muonCut)

    # seperate string values to list with comma
    for muonSels in muonSelsList:
        muonSels = muonSels.split(",")

    # remove string values after :
    for i in muonSels:
        i = i[0 : i.index(":")]
        muonSelsListAfterSplit.append(i)

    # Remove duplicated values with set convertion
    muonSelsListAfterSplit = set(muonSelsListAfterSplit)
    muonSelsListAfterSplit = list(muonSelsListAfterSplit)

    for i in muonSelsListAfterSplit:
        try:
            if i in muonCut:
                pass
            else:
                raise MuonSelsNotInMuonsCutsError(i, muonCut)

        except MuonSelsNotInMuonsCutsError as e:
            logging.exception(e)
            logging.info(
                "For fixing this issue, you should have the same number of cuts (and in the same order) provided to the cfgMuonsCuts from dq-selection as those provided to the cfgMuonSels in the DQFilterPPTask."
            )
            logging.info(
                "For example, if cfgMuonCuts is muonLowPt,muonHighPt, then the cfgMuonSels has to be something like: muonLowPt::1,muonHighPt::1,muonLowPt:pairNoCut:1"
            )
            sys.exit()

    for i in muonCut:
        try:
            if i in muonSelsListAfterSplit:
                pass
            else:
                raise MuonsCutsNotInMuonSelsError(i, muonSelsListAfterSplit)

        except MuonsCutsNotInMuonSelsError as e:
            logging.exception(e)
            logging.info(
                "[INFO] For fixing this issue, you should have the same number of cuts (and in the same order) provided to the cfgMuonsCuts from dq-selection as those provided to the cfgMuonSels in the DQFilterPPTask."
            )
            logging.info(
                "For example, if cfgMuonCuts is muonLowPt,muonHighPt,muonLowPt then the cfgMuonSels has to be something like: muonLowPt::1,muonHighPt::1,muonLowPt:pairNoCut:1"
            )
            sys.exit()


################################
# For BarrelSels from FilterPP #
################################
if args.cfgBarrelSels:

    try:
        if args.cfgBarrelTrackCuts is None:
            raise MandatoryArgNotFoundError(args.cfgBarrelTrackCuts)
        else:
            pass

    except MandatoryArgNotFoundError as e:
        logging.exception(e)
        logging.error(
            "For configure to cfgBarrelSels (For DQ Filter PP Task), you must also configure cfgBarrelTrackCuts!!!"
        )
        sys.exit()

    # Convert List Barrel Track Cuts
    for barrelTrackCut in barrelTrackCutList:
        barrelTrackCut = stringToList(barrelTrackCut)

    # seperate string values to list with comma
    for barrelSels in barrelSelsList:
        barrelSels = barrelSels.split(",")

    # remove string values after :
    for i in barrelSels:
        i = i[0 : i.index(":")]
        barrelSelsListAfterSplit.append(i)

    # Remove duplicated values with set convertion
    barrelSelsListAfterSplit = set(barrelSelsListAfterSplit)
    barrelSelsListAfterSplit = list(barrelSelsListAfterSplit)

    for i in barrelSelsListAfterSplit:
        try:
            if i in barrelTrackCut:
                pass
            else:
                raise BarrelSelsNotInBarrelTrackCutsError(i, barrelTrackCut)

        except BarrelSelsNotInBarrelTrackCutsError as e:
            logging.exception(e)
            logging.info(
                "For fixing this issue, you should have the same number of cuts (and in the same order) provided to the cfgBarrelTrackCuts from dq-selection as those provided to the cfgBarrelSels in the DQFilterPPTask."
            )
            logging.info(
                "For example, if cfgBarrelTrackCuts is jpsiO2MCdebugCuts,jpsiO2MCdebugCuts2,jpsiO2MCdebugCuts then the cfgBarrelSels has to be something like: jpsiO2MCdebugCuts::1,jpsiO2MCdebugCuts2::1,jpsiO2MCdebugCuts:pairNoCut:1"
            )
            sys.exit()

    for i in barrelTrackCut:
        try:
            if i in barrelSelsListAfterSplit:
                pass
            else:
                raise BarrelTrackCutsNotInBarrelSelsError(i, barrelSelsListAfterSplit)

        except BarrelTrackCutsNotInBarrelSelsError as e:
            logging.exception(e)
            logging.info(
                "For fixing this issue, you should have the same number of cuts (and in the same order) provided to the cfgBarrelTrackCuts from dq-selection as those provided to the cfgBarrelSels in the DQFilterPPTask."
            )
            logging.info(
                "For example, if cfgBarrelTrackCuts is jpsiO2MCdebugCuts,jpsiO2MCdebugCuts2,jpsiO2MCdebugCuts then the cfgBarrelSels has to be something like: jpsiO2MCdebugCuts::1,jpsiO2MCdebugCuts2::1,jpsiO2MCdebugCuts:pairNoCut:1"
            )
            sys.exit()


# AOD File Checker
if args.aod is not None:
    argProvidedAod = args.aod
    textAodList = argProvidedAod.startswith("@")
    endsWithRoot = argProvidedAod.endswith(".root")
    endsWithTxt = argProvidedAod.endswith("txt") or argProvidedAod.endswith("text")
    if textAodList and endsWithTxt:
        argProvidedAod = argProvidedAod.replace("@", "")
        logging.info("You provided AO2D list as text file : %s", argProvidedAod)
        try:
            open(argProvidedAod, "r")
            logging.info("%s has valid File Format and Path, File Found", argProvidedAod)

        except FileNotFoundError:
            logging.exception("%s AO2D file text list not found in path!!!", argProvidedAod)
            sys.exit()

    elif endsWithRoot:
        logging.info("You provided single AO2D root file : %s", argProvidedAod)
        try:
            open(argProvidedAod, "r")
            logging.info("%s has valid File Format and Path, File Found", argProvidedAod)

        except FileNotFoundError:
            logging.exception("%s AO2D single root file not found in path!!!", argProvidedAod)
            sys.exit()
    else:
        try:
            open(argProvidedAod, "r")
            logging.info("%s has valid File Format and Path, File Found", argProvidedAod)

        except FileNotFoundError:
            logging.exception("%s Wrong formatted File, check your file extension!", argProvidedAod)
            sys.exit()

#####################
# Deps Transcations #
#####################

# In extended tracks, o2-analysis-trackextension is not a valid dep for run 3
# More Information : https://aliceo2group.github.io/analysis-framework/docs/helperTasks/trackselection.html?highlight=some%20of%20the%20track%20parameters
"""
Some of the track parameters used in the track selection require additional calculation effort and are then stored in a table called TracksExtended
which is produced by either the o2-analysis-trackextension task (Run 2) or o2-analysis-track-propagation (Run 3).
The quantities contained in this table can also be directly used in the analysis.
"""
# if config["bc-selection-task"]["processRun3"] == "true":
# commonDeps.remove("o2-analysis-trackextension")
# logging.info("o2-analysis-trackextension is not valid dep for run 3, It will deleted from your workflow.")

###########################
# End Interface Processes #
###########################

# Write the updated configuration file into a temporary file
updatedConfigFileName = "tempConfigFilterPP.json"

with open(updatedConfigFileName, "w") as outputFile:
    json.dump(config, outputFile, indent=2)

# Check which dependencies need to be run
depsToRun = {}
for dep in commonDeps:
    depsToRun[dep] = 1

commandToRun = (
    taskNameInCommandLine
    + " --configuration json://"
    + updatedConfigFileName
    + " --severity error --shm-segment-size 12000000000 -b"
)
for dep in depsToRun.keys():
    commandToRun += " | " + dep + " --configuration json://" + updatedConfigFileName + " -b"
    logging.debug("%s added your workflow", dep)

if args.add_mc_conv:
    logging.debug("o2-analysis-mc-converter added your workflow")
    commandToRun += (
        " | o2-analysis-mc-converter --configuration json://" + updatedConfigFileName + " -b"
    )

if args.add_fdd_conv:
    commandToRun += (
        " | o2-analysis-fdd-converter --configuration json://" + updatedConfigFileName + " -b"
    )
    logging.debug("o2-analysis-fdd-converter added your workflow")

if args.add_track_prop:
    commandToRun += (
        " | o2-analysis-track-propagation --configuration json://" + updatedConfigFileName + " -b"
    )
    logging.debug("o2-analysis-track-propagation added your workflow")

print(
    "===================================================================================================================="
)
logging.info("Command to run:")
logging.info(commandToRun)
print(
    "===================================================================================================================="
)

# Listing Added Commands
logging.info("Args provided configurations List")
print(
    "===================================================================================================================="
)
for key, value in configuredCommands.items():
    if value is not None:
        if isinstance(value, list):
            listToString(value)
        logging.info("--%s : %s ", key, value)

os.system(commandToRun)

# Pycache remove after running in O2
# getParrentDir = sys.path[-1]

# trying to insert to false directory
try:
    parentPath = os.getcwd()
    if os.path.exists(parentPath) and os.path.isfile(parentPath + "/pycacheRemover.py"):
        logging.info("Inserting inside for pycache remove: %s", os.getcwd())
        pycacheRemover = PycacheRemover()
        pycacheRemover.__init__()
        logging.info("pycaches removed succesfully")

    elif not os.path.exists(parentPath):
        logging.error("OS Path is not valid for pycacheRemover. Fatal Error.")
        sys.exit()
    elif not os.path.isfile(parentPath + "/pycacheRemover.py"):
        raise FileNotFoundError

# Caching the exception
except FileNotFoundError:
    logging.exception(
        "Something wrong with specified\
          directory. Exception- %s",
        sys.exc_info(),
    )
    sys.exit()
