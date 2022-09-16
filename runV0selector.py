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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/v0selector.cxx

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
from extramodules.stringOperations import listToString
from extramodules.dqExceptions import (CfgInvalidFormatError, ForgettedArgsError, NotInAlienvError, TasknameNotFoundInConfigFileError,)

from commondeps.centralityTable import CentralityTable
from commondeps.eventSelection import EventSelectionTask
from commondeps.multiplicityTable import MultiplicityTable
from commondeps.pidTOFBase import TofEventTime
from commondeps.pidTOFBeta import TofPidBeta
from commondeps.pidTPCTOFFull import TpcTofPidFull
from commondeps.trackPropagation import TrackPropagation
from commondeps.trackselection import TrackSelectionTask

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

centralityTableParameters = [
    "estRun2V0M", "estRun2SPDtks", "estRun2SPDcls", "estRun2CL0", "estRun2CL1", "estFV0A", "estFT0M", "estFDDM", "estNTPV"
    ]
# TODO: Add genname parameter

ft0Parameters = ["processFT0", "processNoFT0", "processOnlyFT0", "processRun2"]

pidParameters = ["pid-el", "pid-mu", "pid-pi", "pid-ka", "pid-pr", "pid-de", "pid-tr", "pid-he", "pid-al"]

booleanSelections = ["true", "false"]

# Get system variables in alienv. In alienv we don't have cuts and signal library!!! We need discuss this thing
O2DPG_ROOT = os.environ.get("O2DPG_ROOT")
QUALITYCONTROL_ROOT = os.environ.get("QUALITYCONTROL_ROOT")
O2_ROOT = os.environ.get("O2_ROOT")
O2PHYSICS_ROOT = os.environ.get("O2PHYSICS_ROOT")

################
# Dependencies #
################

commonDeps = [
    "o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table", "o2-analysis-trackselection",
    "o2-analysis-trackextension", "o2-analysis-pid-tof-base", "o2-analysis-pid-tof", "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta",
    "o2-analysis-pid-tpc-full"
    ]

#################
# Init Workflow #
#################


class RunV0selector(object):
    
    """
    This class is for managing the workflow by using the interface arguments from
    all other Common dependencies and the v0selector Task's own arguments in a combined structure.

    Args:
      object (parser_args() object): runV0selector.py workflow
    """
    
    def __init__(
            self, parserRunV0selector = argparse.ArgumentParser(
                formatter_class = argparse.ArgumentDefaultsHelpFormatter,
                description = "Example Usage: ./runV0selector.py <yourConfig.json> --arg value"
                ), v0selector = V0selector(), eventSelection = EventSelectionTask(), centralityTable = CentralityTable(),
            multiplicityTable = MultiplicityTable(), tofEventTime = TofEventTime(), tofPidBeta = TofPidBeta(),
            tpcTofPidFull = TpcTofPidFull(), trackPropagation = TrackPropagation(), trackSelection = TrackSelectionTask(),
            debugOptions = DebugOptions(),
        ):
        super(RunV0selector, self).__init__()
        self.parserRunV0selector = parserRunV0selector
        self.v0selector = v0selector
        self.eventSelection = eventSelection
        self.centralityTable = centralityTable
        self.multiplicityTable = multiplicityTable
        self.tofEventTime = tofEventTime
        self.tofPidBeta = tofPidBeta
        self.tpcTofPidFull = tpcTofPidFull
        self.trackPropagation = trackPropagation
        self.trackSelection = trackSelection
        self.debugOptions = debugOptions
        self.parserRunV0selector.register("action", "none", NoAction)
        self.parserRunV0selector.register("action", "store_choice", ChoicesAction)
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Core Part
        groupCoreSelections = self.parserRunV0selector.add_argument_group(title = "Core configurations that must be configured")
        groupCoreSelections.add_argument("cfgFileName", metavar = "Config.json", default = "config.json", help = "config JSON file name",)
        groupTaskAdders = self.parserRunV0selector.add_argument_group(title = "Additional Task Adding Options")
        groupTaskAdders.add_argument(
            "--add_mc_conv",
            help = "Add the converter from mcparticle to mcparticle+001 (Adds your workflow o2-analysis-mc-converter task)",
            action = "store_true",
            )
        groupTaskAdders.add_argument(
            "--add_fdd_conv", help = "Add the fdd converter (Adds your workflow o2-analysis-fdd-converter task)", action = "store_true",
            )
        groupTaskAdders.add_argument(
            "--add_track_prop",
            help = "Add track propagation to the innermost layer (TPC or ITS) (Adds your workflow o2-analysis-track-propagation task)",
            action = "store_true",
            )
        groupTaskAdders.add_argument(
            "--add_weakdecay_ind",
            help = "Add Converts V0 and cascade version 000 to 001 (Adds your workflow o2-analysis-weak-decay-indices task)",
            action = "store_true",
            )
        
        # aod
        groupDPLReader = self.parserRunV0selector.add_argument_group(title = "Data processor options: internal-dpl-aod-reader")
        groupDPLReader.add_argument("--aod", help = "Add your AOD File with path", action = "store", type = str)
        
        # automation params
        groupAutomations = self.parserRunV0selector.add_argument_group(title = "Automation Parameters")
        groupAutomations.add_argument(
            "--onlySelect", help = "If false JSON Overrider Interface If true JSON Additional Interface", action = "store",
            default = "true", type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        groupAutomations.add_argument(
            "--autoDummy", help = "Dummy automize parameter (don't configure it, true is highly recomended for automation)",
            action = "store", default = "true", type = str.lower, choices = booleanSelections,
            ).completer = ChoicesCompleter(booleanSelections)
        
        # helper lister commands
        # groupAdditionalHelperCommands = self.parserRunV0selector.add_argument_group(title="Additional Helper Command Options")
        # groupAdditionalHelperCommands.add_argument("--cutLister", help="List all of the analysis cuts from CutsLibrary.h", action="store_true")
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        
        argcomplete.autocomplete(self.parserRunV0selector, always_complete_options = False)
        return self.parserRunV0selector.parse_args()
    
    def mergeArgs(self):
        """
        This function allows to merge parser_args argument information from different classes
        """
        
        self.eventSelection.parserEventSelectionTask = self.parserRunV0selector
        self.eventSelection.addArguments()
        
        self.centralityTable.parserCentralityTable = self.parserRunV0selector
        self.centralityTable.addArguments()
        
        self.multiplicityTable.parserMultiplicityTable = self.parserRunV0selector
        self.multiplicityTable.addArguments()
        
        self.tofEventTime.parserTofEventTime = self.parserRunV0selector
        self.tofEventTime.addArguments()
        
        self.tofPidBeta.parserTofPidBeta = self.parserRunV0selector
        self.tofPidBeta.addArguments()
        
        self.tpcTofPidFull.parserTpcTofPidFull = self.parserRunV0selector
        self.tpcTofPidFull.addArguments()
        
        self.trackPropagation.parserTrackPropagation = self.parserRunV0selector
        self.trackPropagation.addArguments()
        
        self.trackSelection.parserTrackSelectionTask = self.parserRunV0selector
        self.trackSelection.addArguments()
        
        self.debugOptions.parserDebugOptions = self.parserRunV0selector
        self.debugOptions.addArguments()
        
        self.v0selector.parserV0selector = self.parserRunV0selector
        self.v0selector.addArguments()
        
        self.addArguments()


# init args manually
initArgs = RunV0selector()
initArgs.mergeArgs()
initArgs.parseArgs()

args = initArgs.parseArgs()
configuredCommands = vars(args) # for get args

# Debug Settings
if args.debug and (not args.logFile):
    DEBUG_SELECTION = args.debug
    numeric_level = getattr(logging, DEBUG_SELECTION.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % DEBUG_SELECTION)
    logging.basicConfig(format = "[%(levelname)s] %(message)s", level = DEBUG_SELECTION)

if args.logFile and args.debug:
    log = logging.getLogger("")
    level = logging.getLevelName(args.debug)
    log.setLevel(level)
    format = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s")
    
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)
    
    loggerFile = "v0selector.log"
    if os.path.isfile(loggerFile):
        os.remove(loggerFile)
    
    fh = handlers.RotatingFileHandler(loggerFile, maxBytes = (1048576 * 5), backupCount = 7, mode = "w")
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
# if len(sys.argv) < 2:
# logging.error("Invalid syntax! The command line should look like this:")
# logging.info("  ./runV0selector.py <yourConfig.json> --param value ...")
# sys.exit()

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
        logging.info("  ./runV0selector.py<yourConfig.json> <-runData|-runMC> --param value ...")
        sys.exit()
except FileNotFoundError:
    isConfigJson = sys.argv[1].endswith(".json")
    if not isConfigJson:
            logging.error("Invalid syntax! After the script you must define your json configuration file!!! The command line should look like this:")
            logging.info(" ./runV0selector.py <yourConfig.json> --param value ...")
            sys.exit()
    logging.error("Your JSON Config File found in path!!!")
    sys.exit()
"""

taskNameInConfig = "v0-selector"
taskNameInCommandLine = "o2-analysis-dq-v0-selector"

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
                elif value is not args.FT0:
                    value2 = "false"
                    config[key][value] = value2
                    logging.debug(" - [%s] %s : %s", key, value, value2)
            
            # track-selection
            if args.itsMatching:
                config[key][value] = args.itsMatching
                logging.debug(" - [%s] %s : %s", key, value, args.itsMatching)

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
# More Information : https://aliceo2group.github.io/analysis-framework/docs/basics-usage/HelperTasks.html#track-propagation

"""
Some of the track parameters used in the track selection require additional calculation effort and are then stored in a table called TracksExtended
which is produced by either the o2-analysis-trackextension task (Run 2) or o2-analysis-track-propagation (Run 3).
The quantities contained in this table can also be directly used in the analysis.
"""
if args.add_track_prop:
    commonDeps.remove("o2-analysis-trackextension")
    logging.info("o2-analysis-trackextension is not valid dep for run 3, It will deleted from your workflow.")

###########################
# End Interface Processes #
###########################

# Write the updated configuration file into a temporary file
updatedConfigFileName = "tempConfigV0Selector.json"

with open(updatedConfigFileName, "w") as outputFile:
    json.dump(config, outputFile, indent = 2)

# Check which dependencies need to be run
depsToRun = {}
for dep in commonDeps:
    depsToRun[dep] = 1

commandToRun = (
    taskNameInCommandLine + " --configuration json://" + updatedConfigFileName + " --severity error --shm-segment-size 12000000000 -b"
    )
for dep in depsToRun.keys():
    commandToRun += " | " + dep + " --configuration json://" + updatedConfigFileName + " -b"
    logging.debug("%s added your workflow", dep)

if args.add_mc_conv:
    logging.debug("o2-analysis-mc-converter added your workflow")
    commandToRun += (" | o2-analysis-mc-converter --configuration json://" + updatedConfigFileName + " -b")

if args.add_fdd_conv:
    commandToRun += (" | o2-analysis-fdd-converter --configuration json://" + updatedConfigFileName + " -b")
    logging.debug("o2-analysis-fdd-converter added your workflow")

if args.add_track_prop:
    commandToRun += (" | o2-analysis-track-propagation --configuration json://" + updatedConfigFileName + " -b")
    logging.debug("o2-analysis-track-propagation added your workflow")

if args.add_weakdecay_ind:
    commandToRun += (" | o2-analysis-weak-decay-indices --configuration json://" + updatedConfigFileName + " -b")
    logging.debug("o2-analysis-weak-decay-indices added your workflow")

print("====================================================================================================================")
logging.info("Command to run:")
logging.info(commandToRun)
print("====================================================================================================================")

# Listing Added Commands
logging.info("Args provided configurations List")
print("====================================================================================================================")
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
    logging.exception("Something wrong with specified\
          directory. Exception- %s", sys.exc_info(),)
    sys.exit()
