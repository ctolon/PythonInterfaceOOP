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
    CentFilterError,
    BarrelSelsNotInBarrelTrackCutsError,
    BarrelTrackCutsNotInBarrelSelsError,
    MuonsCutsNotInMuonSelsError,
    MuonSelsNotInMuonsCutsError,
    MandatoryArgNotFoundError,
)

from commondeps.centralityTable import CentralityTable
from commondeps.eventSelection import EventSelectionTask
from commondeps.multiplicityTable import MultiplicityTable
from commondeps.pidTOFBase import TofEventTime
from commondeps.pidTOFBeta import TofPidBeta
from commondeps.pidTPCTOFFull import TpcTofPidFull
from commondeps.trackPropagation import TrackPropagation
from commondeps.trackselection import TrackSelectionTask

from dqtasks.tableMaker import TableMaker
from dqtasks.v0selector import V0selector

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

tablemakerProcessAllParameters = [
    "processFull",
    "processFullTiny",
    "processFullWithCov",
    "processFullWithCent",
    "processBarrelOnlyWithV0Bits",
    "processBarrelOnlyWithEventFilter",
    "processBarrelOnlyWithQvector",
    "processBarrelOnlyWithCent",
    "processBarrelOnlyWithCov",
    "processBarrelOnly",
    "processMuonOnlyWithCent",
    "processMuonOnlyWithCov",
    "processMuonOnly",
    "processMuonOnlyWithFilter",
    "processMuonOnlyWithQvector",
    "processOnlyBCs",
]

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

booleanSelections = ["true", "false"]

# Centrality Filter for pp systems in tableMaker
isNoDeleteNeedForCent = True
isProcessFuncLeftAfterCentDelete = True

threeSelectedList = []

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

# Predefined values for DQ Logger messages
isDQBarrelSelected = False
isDQBarrelTinySelected = False
isDQMuonSelected = False
isDQEventSelected = True
isDQFullSelected = False
isFilterPPSelected = False
isFilterPPTinySelected = False
isQVectorSelected = False

# Predefined Search Lists
fullSearch = []
barrelSearch = []
muonSearch = []
# bcsSearch = []
covSearch = []
centSearch = []
filterSearch = []
qVectorSearch = []

# After deleting centrality we need to check if we have process function
isProcessFuncLeftAfterCentDelete = True
leftProcessAfterDeleteCent = []

################
# Dependencies #
################

commonDeps = [
    "o2-analysis-timestamp",
    "o2-analysis-event-selection",
    "o2-analysis-multiplicity-table",
]
barrelDeps = [
    "o2-analysis-trackselection",
    "o2-analysis-trackextension",
    "o2-analysis-pid-tof-base",
    "o2-analysis-pid-tof",
    "o2-analysis-pid-tof-full",
    "o2-analysis-pid-tof-beta",
    "o2-analysis-pid-tpc-full",
]
specificDeps = {
    "processFull": [],
    "processFullTiny": [],
    "processFullWithCov": [],
    "processFullWithCent": ["o2-analysis-centrality-table"],
    "processBarrelOnly": [],
    "processBarrelOnlyWithCov": [],
    "processBarrelOnlyWithV0Bits": [
        "o2-analysis-dq-v0-selector",
        "o2-analysis-weak-decay-indices",
    ],
    "processBarrelOnlyWithEventFilter": ["o2-analysis-dq-filter-pp"],
    "processBarrelOnlyWithQvector": [
        "o2-analysis-centrality-table",
        "o2-analysis-dq-flow",
    ],
    "processBarrelOnlyWithCent": ["o2-analysis-centrality-table"],
    "processMuonOnly": [],
    "processMuonOnlyWithCov": [],
    "processMuonOnlyWithCent": ["o2-analysis-centrality-table"],
    "processMuonOnlyWithQvector": [
        "o2-analysis-centrality-table",
        "o2-analysis-dq-flow",
    ],
    "processMuonOnlyWithFilter": ["o2-analysis-dq-filter-pp"]
    # "processFullWithCentWithV0Bits": ["o2-analysis-centrality-table","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
    # "processFullWithEventFilterWithV0Bits": ["o2-analysis-dq-filter-pp","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
}

#############################
# Skimming Table Selections #
#############################

# Definition of all the tables we may write
tables = {
    "ReducedEvents": {"table": "AOD/REDUCEDEVENT/0", "treename": "ReducedEvents"},
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
    "ReducedMCEvents": {"table": "AOD/REMC/0", "treename": "ReducedMCEvents"},
    "ReducedTracks": {"table": "AOD/REDUCEDTRACK/0", "treename": "ReducedTracks"},
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
    "ReducedMCTracks": {"table": "AOD/RTMC/0", "treename": "ReducedMCTracks"},
    "ReducedMuons": {"table": "AOD/RTMUON/0", "treename": "ReducedMuons"},
    "ReducedMuonsExtra": {
        "table": "AOD/RTMUONEXTRA/0",
        "treename": "ReducedMuonsExtra",
    },
    "ReducedMuonsCov": {"table": "AOD/RTMUONCOV/0", "treename": "ReducedMuonsCov"},
    "ReducedMuonsLabels": {
        "table": "AOD/RTMUONSLABELS/0",
        "treename": "ReducedMuonsLabels",
    },
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


#################
# Init Workflow #
#################


class RunTableMaker(object):
    """
    This class is for managing the workflow by using the interface arguments from
    all other Common dependencies and the tableMaker Task's own arguments in a combined structure.

    Args:
      object (parser_args() object): runTableMaker.py workflow
    """

    def __init__(
        self,
        parserRunTableMaker=argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Example Usage: ./runTableMaker.py <yourConfig.json> --arg value ",
        ),
        eventSelection=EventSelectionTask(),
        centralityTable=CentralityTable(),
        multiplicityTable=MultiplicityTable(),
        tofEventTime=TofEventTime(),
        tofPidBeta=TofPidBeta(),
        tpcTofPidFull=TpcTofPidFull(),
        trackPropagation=TrackPropagation(),
        trackSelection=TrackSelectionTask(),
        v0selector=V0selector(),
        tableMaker=TableMaker(),
        debugOptions=DebugOptions(),
    ):
        super(RunTableMaker, self).__init__()
        self.parserRunTableMaker = parserRunTableMaker
        self.eventSelection = eventSelection
        self.centralityTable = centralityTable
        self.multiplicityTable = multiplicityTable
        self.tofEventTime = tofEventTime
        self.tofPidBeta = tofPidBeta
        self.tpcTofPidFull = tpcTofPidFull
        self.trackPropagation = trackPropagation
        self.trackSelection = trackSelection
        self.v0selector = v0selector
        self.tableMaker = tableMaker
        self.debugOptions = debugOptions
        self.parserRunTableMaker.register("action", "none", NoAction)
        self.parserRunTableMaker.register("action", "store_choice", ChoicesAction)

    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """

        # Core Part
        groupCoreSelections = self.parserRunTableMaker.add_argument_group(
            title="Core configurations that must be configured"
        )
        groupCoreSelections.add_argument(
            "cfgFileName",
            metavar="Config.json",
            default="config.json",
            help="config JSON file name",
        )
        groupCoreSelections.add_argument(
            "-runData", help="Run over Data", action="store_true", default=True
        )
        groupTaskAdders = self.parserRunTableMaker.add_argument_group(
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
        groupDPLReader = self.parserRunTableMaker.add_argument_group(
            title="Data processor options: internal-dpl-aod-reader"
        )
        groupDPLReader.add_argument(
            "--aod", help="Add your AOD File with path", action="store", type=str
        )
        groupDPLReader.add_argument(
            "--aod-memory-rate-limit",
            help="Rate limit AOD processing based on memory",
            action="store",
            type=str,
        )

        # automation params
        groupAutomations = self.parserRunTableMaker.add_argument_group(
            title="Automation Parameters"
        )
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
        # groupAdditionalHelperCommands = self.parserRunTableMaker.add_argument_group(title="Additional Helper Command Options")
        # groupAdditionalHelperCommands.add_argument("--cutLister", help="List all of the analysis cuts from CutsLibrary.h", action="store_true")

    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """

        argcomplete.autocomplete(self.parserRunTableMaker, always_complete_options=False)
        return self.parserRunTableMaker.parse_args()

    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """

        self.eventSelection.parserEventSelectionTask = self.parserRunTableMaker
        self.eventSelection.addArguments()

        self.centralityTable.parserCentralityTable = self.parserRunTableMaker
        self.centralityTable.addArguments()

        self.multiplicityTable.parserMultiplicityTable = self.parserRunTableMaker
        self.multiplicityTable.addArguments()

        self.tofEventTime.parserTofEventTime = self.parserRunTableMaker
        self.tofEventTime.addArguments()

        self.tofPidBeta.parserTofPidBeta = self.parserRunTableMaker
        self.tofPidBeta.addArguments()

        self.tpcTofPidFull.parserTpcTofPidFull = self.parserRunTableMaker
        self.tpcTofPidFull.addArguments()

        self.trackPropagation.parserTrackPropagation = self.parserRunTableMaker
        self.trackPropagation.addArguments()

        self.trackSelection.parserTrackSelectionTask = self.parserRunTableMaker
        self.trackSelection.addArguments()

        self.v0selector.parserV0selector = self.parserRunTableMaker
        self.v0selector.addArguments()

        self.tableMaker.parserTableMaker = self.parserRunTableMaker
        self.tableMaker.addArguments()

        self.debugOptions.parserDebugOptions = self.parserRunTableMaker
        self.debugOptions.addArguments()

        self.addArguments()

    # This function not work should be integrated instead of mergeArgs
    """
    def mergeMultiArgs(self, *objects):
        parser = self.parserRunTableMaker
        for object in objects:
            object.parser = parser
            object.addArguments()
        self.addArguments()
    """


# init args manually
initArgs = RunTableMaker()

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

    loggerFile = "tableMaker.log"
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

# Make some checks on provided arguments
# if len(sys.argv) < 2:
# logging.error("Invalid syntax! The command line should look like this:")
# logging.info("  ./runTableMaker.py <yourConfig.json> <-runData|-runMC> --param value ...")
# sys.exit()

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
        with open(sys.argv[1]) as configFile:
            config = json.load(configFile)
    else:
        # raise ConfigFileInvalidFormat(args.cfgFileName)
        logging.error(
            "Invalid syntax! After the script, you must define your json configuration file!!! \
            The command line should look like this:"
        )
        logging.info("  ./runTableMaker.py <yourConfig.json> <-runData|-runMC> --param value ...")
        sys.exit()

except FileNotFoundError:
    sys.exit()
"""

runOverMC = False
logging.info("runOverMC : %s, Reduced Tables will be produced for Data", runOverMC)

taskNameInConfig = "table-maker"
taskNameInCommandLine = "o2-analysis-dq-table-maker"

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
    #sys.exit()

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
            if (value in tablemakerProcessAllParameters) and args.process:
                if value in args.process:

                    # processOnlyBCs have to always be true
                    if "processOnlyBCs" not in args.process:
                        args.process.append("processOnlyBCs")
                        logging.warning(
                            "You forget to add OnlyBCs value in --process parameter! It will automaticaly added."
                        )
                    value2 = "true"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s", key, value, value2)

                    # For find all process parameters for TableMaker/TableMakerMC in Orginal JSON
                    for s in config[key].keys():
                        if s in tablemakerProcessAllParameters:
                            tableMakerProcessSearch.add(s)
                    # check extraargs is contain Full Barrel Muon or Bcs
                    fullSearch = [s for s in args.process if "Full" in s]
                    barrelSearch = [s for s in args.process if "Barrel" in s]
                    muonSearch = [s for s in args.process if "Muon" in s]
                    # bcsSearch = [s for s in args.process if "BCs" in s]

                    # check args is contain Cov for transcation management --> add track prop task
                    covSearch = [s for s in args.process if "Cov" in s]

                    # check args is contain Cent for transcation management Centrality Filter
                    centSearch = [s for s in args.process if "Cent" in s]

                    # check args is contain Filter for automatize Filter PP task
                    filterSearch = [s for s in args.process if "Filter" in s]

                    # check args is contain Qvector for automatize dqFlow task
                    qVectorSearch = [s for s in args.process if "Qvector" in s]

                    # Automatization for Activate or Disable d-q barrel, muon and event tasks regarding to process func. in tablemaker
                    if len(fullSearch) > 0 and args.runData:
                        config["d-q-barrel-track-selection-task"]["processSelection"] = "true"
                        isDQFullSelected = True
                        # logging.debug(" - [d-q-barrel-track-selection-task] processSelection : true")

                        if args.isBarrelSelectionTiny == "false":
                            config["d-q-barrel-track-selection-task"]["processSelection"] = "true"
                            config["d-q-barrel-track-selection-task"][
                                "processSelectionTiny"
                            ] = args.isBarrelSelectionTiny
                            # logging.debug(" - [d-q-barrel-track-selection-task] processSelection : true")
                            # logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : false")
                        if args.isBarrelSelectionTiny == "true":
                            config["d-q-barrel-track-selection-task"]["processSelection"] = "false"
                            config["d-q-barrel-track-selection-task"][
                                "processSelectionTiny"
                            ] = args.isBarrelSelectionTiny
                            isDQBarrelTinySelected = True
                            # logging.debug(" - [d-q-barrel-track-selection-task] processSelection : false")
                            # logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : true")

                        config["d-q-muons-selection"]["processSelection"] = "true"
                        isDQMuonSelected = True
                        # logging.debug(" - [d-q-muons-selection] processSelection : true")

                    if len(barrelSearch) > 0 and args.runData:
                        if args.isBarrelSelectionTiny == "false":
                            config["d-q-barrel-track-selection-task"]["processSelection"] = "true"
                            config["d-q-barrel-track-selection-task"][
                                "processSelectionTiny"
                            ] = args.isBarrelSelectionTiny
                            isDQBarrelSelected = True
                            isDQBarrelTinySelected = False
                            # logging.debug(" - [d-q-barrel-track-selection-task] processSelection : true")
                            # logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : false")
                        if args.isBarrelSelectionTiny == "true":
                            config["d-q-barrel-track-selection-task"]["processSelection"] = "false"
                            config["d-q-barrel-track-selection-task"][
                                "processSelectionTiny"
                            ] = args.isBarrelSelectionTiny
                            isDQBarrelSelected = False
                            isDQBarrelTinySelected = True
                            # logging.debug(" - [d-q-barrel-track-selection-task] processSelection : false")
                            # logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : true")

                    if (
                        len(barrelSearch) == 0
                        and len(fullSearch) == 0
                        and args.runData
                        and args.onlySelect == "true"
                    ):
                        config["d-q-barrel-track-selection-task"]["processSelection"] = "false"
                        config["d-q-barrel-track-selection-task"]["processSelectionTiny"] = "false"
                        # logging.debug(" - [d-q-barrel-track-selection-task] processSelection : false")
                        # logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : false")

                    if len(muonSearch) > 0 and args.runData:
                        config["d-q-muons-selection"]["processSelection"] = "true"
                        # logging.debug(" - [d-q-muons-selection] processSelection : true")
                        isDQMuonSelected = True
                    if (
                        len(muonSearch) == 0
                        and len(fullSearch) == 0
                        and args.runData
                        and args.onlySelect == "true"
                    ):
                        config["d-q-muons-selection"]["processSelection"] = "false"
                        # logging.debug(" - [d-q-muons-selection] processSelection : false")

                    # processEventSelection have to always be true
                    if args.runData:
                        config["d-q-event-selection-task"]["processEventSelection"] = "true"
                        isDQEventSelected = True
                        # logging.debug(" - [d-q-event-selection-task] processEventSelection : true")

                    # Automatization for Activate or Disable d-q filter-p-p
                    if len(filterSearch) > 0 and args.runData:
                        config["d-q-filter-p-p-task"]["processFilterPP"] = "true"
                        config["d-q-filter-p-p-task"]["processFilterPPTiny"] = "false"
                        isFilterPPSelected = True
                        isFilterPPTinySelected = False
                        # logging.debug(" - [d-q-filter-p-p-task-task] processFilterPP : true")
                        # logging.debug(" - [d-q-filter-p-p-task-task] processFilterPPTiny : false")
                        if args.isFilterPPTiny == "true":
                            config["d-q-filter-p-p-task"]["processFilterPP"] = "false"
                            config["d-q-filter-p-p-task"]["processFilterPPTiny"] = "true"
                            isFilterPPSelected = False
                            isFilterPPTinySelected = True
                            # logging.debug(" - [d-q-filter-p-p-task-task] processFilterPP : false")
                            # logging.debug(" - [d-q-filter-p-p-task-task] processFilterPPTiny : true")

                    if len(filterSearch) == 0 and args.runData and args.onlySelect == "true":
                        config["d-q-filter-p-p-task"]["processFilterPP"] = "false"
                        config["d-q-filter-p-p-task"]["processFilterPPTiny"] = "false"
                        isFilterPPSelected = False
                        isFilterPPTinySelected = False
                        # logging.debug(" - [d-q-filter-p-p-task-task] processFilterPP : false")
                        # logging.debug(" - [d-q-filter-p-p-task-task] processFilterPPTiny : true")

                    # Automatization for Activate or Disable analysis-qvector
                    if len(qVectorSearch) > 0 and args.runData:
                        config["analysis-qvector"]["processBarrelQvector"] = "true"
                        isQVectorSelected = True

                    if len(qVectorSearch) == 0 and args.runData and args.onlySelect == "true":
                        config["analysis-qvector"]["processBarrelQvector"] = "false"
                        isQVectorSelected = False

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
                if (
                    value == "processStandard" or value == "processCovariance"
                ) and args.isCovariance == "false":
                    config[key]["processStandard"] = "true"
                    config[key]["processCovariance"] = "false"
                    logging.debug(" - [%s] processStandart : true", key)
                    logging.debug(" - [%s] processCovariance : false", key)
                if (
                    value == "processStandard" or value == "processCovariance"
                ) and args.isCovariance == "true":
                    config[key]["processStandard"] = "false"
                    config[key]["processCovariance"] = "true"
                    logging.debug(" - [%s] processStandart : false", key)
                    logging.debug(" - [%s] processCovariance : true", key)

            # track-selection
            if args.itsMatching:
                config[key][value] = args.itsMatching
                logging.debug(" - [%s] %s : %s", key, value, args.itsMatching)

            # dummy automizer
            if value == "processDummy" and args.autoDummy and args.runData:

                if (
                    config["d-q-barrel-track-selection-task"]["processSelection"] == "true"
                    or config["d-q-barrel-track-selection-task"]["processSelectionTiny"] == "true"
                ):
                    config["d-q-barrel-track-selection-task"]["processDummy"] = "false"
                    # logging.debug("d-q-barrel-track-selection-task:processDummy:false")
                if (
                    config["d-q-barrel-track-selection-task"]["processSelection"] == "false"
                    and config["d-q-barrel-track-selection-task"]["processSelectionTiny"] == "false"
                ):
                    config["d-q-barrel-track-selection-task"]["processDummy"] = "true"
                    # logging.debug("d-q-barrel-track-selection-task:processDummy:true")

                if config["d-q-muons-selection"]["processSelection"] == "true":
                    config["d-q-muons-selection"]["processDummy"] = "false"
                    # logging.debug("d-q-muons-selection:processDummy:false")
                if config["d-q-muons-selection"]["processSelection"] == "false":
                    config["d-q-muons-selection"]["processDummy"] = "true"
                    # logging.debug("d-q-muons-selection:processDummy:true")

                if config["d-q-event-selection-task"]["processEventSelection"] == "true":
                    config["d-q-event-selection-task"]["processDummy"] = "false"
                    # logging.debug("d-q-event-selection-task:processDummy:false")
                if config["d-q-event-selection-task"]["processEventSelection"] == "false":
                    config["d-q-event-selection-task"]["processDummy"] = "true"
                    # logging.debug("d-q-event-selection-task:processDummy:true")

                if (
                    config["d-q-filter-p-p-task"]["processFilterPP"] == "true"
                    or config["d-q-filter-p-p-task"]["processFilterPPTiny"] == "true"
                ):
                    config["d-q-filter-p-p-task"]["processDummy"] = "false"
                    # logging.debug("d-q-filter-p-p-task:processDummy:false")
                if (
                    config["d-q-filter-p-p-task"]["processFilterPP"] == "false"
                    and config["d-q-filter-p-p-task"]["processFilterPPTiny"] == "false"
                ):
                    config["d-q-filter-p-p-task"]["processDummy"] = "true"
                    # logging.debug("d-q-filter-p-p-task:processDummy:true")

                if config["analysis-qvector"]["processBarrelQvector"] == "true":
                    config["analysis-qvector"]["processDummy"] = "false"
                if config["analysis-qvector"]["processBarrelQvector"] == "false":
                    config["analysis-qvector"]["processDummy"] = "true"

# LOGGER MESSAGES FOR DQ SELECTIONS

if args.runData and args.process:

    if isDQFullSelected:
        logging.debug(" - [d-q-event-selection-task] processEventSelection : true")

        if isDQBarrelSelected:
            logging.debug(" - [d-q-barrel-track-selection-task] processSelection : true")
            logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : false")
        if isDQBarrelTinySelected:
            logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : true")
            logging.debug(" - [d-q-barrel-track-selection-task] processSelection : false")

        logging.debug(" - [d-q-muons-selection] processSelection : true")

    if isDQEventSelected and (not isDQFullSelected):
        logging.debug(" - [d-q-event-selection-task] processEventSelection : true")
    if (not isDQEventSelected) and (not isDQFullSelected):
        logging.debug(" - [d-q-event-selection-task] processEventSelection : false")
    if isDQBarrelSelected and (not isDQFullSelected):
        logging.debug(" - [d-q-barrel-track-selection-task] processSelection : true")
    if (not isDQBarrelSelected) and (not isDQFullSelected):
        logging.debug(" - [d-q-barrel-track-selection-task] processSelection : false")
    if isDQBarrelTinySelected and (not isDQFullSelected):
        logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : true")
    if (not isDQBarrelTinySelected) and (not isDQFullSelected):
        logging.debug(" - [d-q-barrel-track-selection-task] processSelectionTiny : false")
    if isDQMuonSelected and (not isDQFullSelected):
        logging.debug(" - [d-q-muons-selection] processSelection : true")
    if (not isDQMuonSelected) and (not isDQFullSelected):
        logging.debug(" - [d-q-muons-selection] processSelection : false")
    if isFilterPPSelected:
        logging.debug(" - [d-q-filter-p-p-task-task] processFilterPP : true")
    if not isFilterPPSelected:
        logging.debug(" - [d-q-filter-p-p-task-task] processFilterPP : false")
    if isFilterPPTinySelected:
        logging.debug(" - [d-q-filter-p-p-task-task] processFilterPPTiny : true")
    if not isFilterPPTinySelected:
        logging.debug(" - [d-q-filter-p-p-task-task] processFilterPPTiny : false")
    if isQVectorSelected:
        logging.debug(" - [analysis-qvector] processBarrelQvector : true")
    if not isQVectorSelected:
        logging.debug(" - [analysis-qvector] processBarrelQvector : false")

# Centrality table delete for pp processes
if (
    args.process
    and len(centSearch) != 0
    and (
        args.syst == "pp" or (args.syst is None and config["event-selection-task"]["syst"] == "pp")
    )
):
    # delete centrality-table configurations for data. If it"s MC don't delete from JSON
    # Firstly try for Data then if not data it gives warning message for MC
    isNoDeleteNeedForCent = False
    logging.warning(
        "JSON file does not include configs for centrality-table task, It's for DATA. Centrality will removed because you select pp collision system."
    )
    # del(config["centrality-table"])

    # check for is TableMaker includes task related to Centrality?
    if args.process is not None:
        processCentralityMatch = [s for s in args.process if "Cent" in s]
        if len(processCentralityMatch) > 0:
            logging.warning(
                "Collision System pp can't be include related task about Centrality. They Will be removed in automation. Check your JSON configuration file for Tablemaker process function!!!"
            )
            for paramValueTableMaker in processCentralityMatch:
                # Centrality process should be false
                config[taskNameInConfig][paramValueTableMaker] = "false"
                logging.warning(
                    "- [%s] %s will converted to false in json config file",
                    taskNameInConfig,
                    paramValueTableMaker,
                )

    else:
        logging.warning(
            "No process function provided so no need delete related to centrality-table dependency"
        )

    for deletedParamTableMaker in config[taskNameInConfig]:
        if "process" not in deletedParamTableMaker:
            continue
        elif config[taskNameInConfig].get(deletedParamTableMaker) == "true":
            isProcessFuncLeftAfterCentDelete = True
            leftProcessAfterDeleteCent.append(deletedParamTableMaker)

# logging Message for Centrality
if not isNoDeleteNeedForCent:
    logging.info(
        "After deleting the process functions related to the centrality table (for collision system pp), the remaining processes: %s",
        leftProcessAfterDeleteCent,
    )
try:
    if len(leftProcessAfterDeleteCent) > 1 or len(leftProcessAfterDeleteCent) == 0:
        logging.info("Process will continue after Centrality filter")
    else:
        raise CentFilterError
except CentFilterError as e:
    logging.exception(e)
    sys.exit()


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
if args.add_track_prop:
    barrelDeps.remove("o2-analysis-trackextension")
    logging.info("o2-analysis-trackextension is not valid dep for run 3, It will deleted from your workflow.")


###########################
# End Interface Processes #
###########################

# Write the updated configuration file into a temporary file
updatedConfigFileName = "tempConfigTableMaker.json"

with open(updatedConfigFileName, "w") as outputFile:
    json.dump(config, outputFile, indent=2)

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

# Generate the aod-writer output descriptor json file
writerConfig = {}
writerConfig["OutputDirector"] = {
    "debugmode": True,
    "resfile": "reducedAod",
    "resfilemode": "RECREATE",
    "ntfmerge": 1,
    "OutputDescriptors": [],
}

# Generate the aod-reader output descriptor json file
readerConfig = {}
readerConfig["InputDirector"] = {"debugmode": True, "InputDescriptors": []}

iTable = 0
for table in tablesToProduce.keys():
    writerConfig["OutputDirector"]["OutputDescriptors"].insert(iTable, tables[table])
    readerConfig["InputDirector"]["InputDescriptors"].insert(iTable, tables[table])
    iTable += 1

writerConfigFileName = "aodWriterTempConfig.json"
with open(writerConfigFileName, "w") as writerConfigFile:
    json.dump(writerConfig, writerConfigFile, indent=2)


readerConfigFileName = "aodReaderTempConfig.json"
with open(readerConfigFileName, "w") as readerConfigFile:
    json.dump(readerConfig, readerConfigFile, indent=2)

logging.info("aodWriterTempConfig==========")
print(writerConfig)
# sys.exit()
logging.info("aodReaderTempConfig==========")
print(readerConfig)

commandToRun = (
    taskNameInCommandLine
    + " --configuration json://"
    + updatedConfigFileName
    + " --severity error --shm-segment-size 12000000000 --aod-writer-json "
    + writerConfigFileName
    + " -b"
)
if args.aod_memory_rate_limit:
    commandToRun = (
        taskNameInCommandLine
        + " --configuration json://"
        + updatedConfigFileName
        + " --severity error --shm-segment-size 12000000000 --aod-memory-rate-limit "
        + args.aod_memory_rate_limit
        + " --aod-writer-json "
        + writerConfigFileName
        + " -b"
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
logging.info("Tables to produce:")
logging.info(tablesToProduce.keys())
print(
    "===================================================================================================================="
)
# sys.exit()

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
