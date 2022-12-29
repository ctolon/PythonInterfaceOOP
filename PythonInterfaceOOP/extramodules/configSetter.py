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

# This script includes setter functions for configurables (Developer package)

from extramodules.dqLibGetter import DQLibGetter
from .utils import convertListToStr, listToString, stringToList
import logging
from logging import handlers
import sys
import os
import json
import argparse
from extramodules.choicesHandler import ChoicesCompleterList
import argcomplete
from argcomplete.completers import ChoicesCompleter
from typing import Any


def dispArgs(allArgs: dict[str, Any]) -> None:
    """Display all configured commands you provided in CLI

    Args:
        allArgs (dict[str, Any]): configured commands in CLI
    """
    logging.info("Args provided configurations List")
    print("====================================================================================================================")
    for task, cfg in allArgs.items():
        if cfg is not None:
            if isinstance(cfg, list):
                listToString(cfg)
            logging.info("--%s : %s ", task, cfg)
    print("====================================================================================================================")


def dispInterfaceMode(cliMode: str):
    """Display interface mode in CLI

    Args:
        cliMode (str): Interface mode argument as bool str
    """
    
    logging.info("Only Select Configured as %s", cliMode)
    if cliMode == "true":
        logging.info("INTERFACE MODE : JSON Overrider")
    if cliMode == "false":
        logging.info("INTERFACE MODE : JSON Additional")


def dispO2HelpMessage(argHelpO2: bool, commandToRun: str):
    """Display O2 helper message

    Args:
        argHelpO2 (bool): CLI helpO2 argument
        commandToRun (str): commandToRun as string
    """
    if argHelpO2 is True:
        commandToRun += " --help full"
        os.system(commandToRun)
        sys.exit()


def debugSettings(argDebug: bool, argLogFile: bool, fileName: str) -> None:
    """Set Debug settings for CLI

    Args:
        argDebug (bool): Debug Level
        argLogFile (bool): CLI argument as logFile
        fileName (str): Output name of log file

    Raises:
        ValueError: If selected invalid log level
    """
    
    if argDebug and (not argLogFile):
        DEBUG_SELECTION = argDebug
        numeric_level = getattr(logging, DEBUG_SELECTION.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError("Invalid log level: %s" % DEBUG_SELECTION)
        logging.basicConfig(format = "[%(levelname)s] %(message)s", level = DEBUG_SELECTION)
    
    if argLogFile and argDebug:
        log = logging.getLogger("")
        level = logging.getLevelName(argDebug)
        log.setLevel(level)
        format = logging.Formatter("[%(levelname)s] %(message)s")
        
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(format)
        log.addHandler(ch)
        
        loggerFile = fileName
        if os.path.isfile(loggerFile):
            os.remove(loggerFile)
        
        fh = handlers.RotatingFileHandler(loggerFile, maxBytes = (1048576 * 5), backupCount = 7, mode = "w")
        fh.setFormatter(format)
        log.addHandler(fh)


def setConverters(allArgs: dict[str, Any], updatedConfigFileName: str, commandToRun: str) -> str:
    """Converter task setter function

    Args:
        allArgs (dict[str, Any]): All provided args in CLI
        updatedConfigFileName (str): Overrided json config file
        commandToRun (str): Generated command for running in O2
        
    Returns:
        str: Command To Run with provided converter task options
    """
    specificTasks = {
        "add_mc_conv": "o2-analysis-mc-converter",
        "add_fdd_conv": "o2-analysis-fdd-converter",
        "add_track_prop": "o2-analysis-track-propagation",
        "add_weakdecay_ind": "o2-analysis-weak-decay-indices",
        "add_col_conv": "o2-analysis-collision-converter"
        }
    
    for cliArg, cliValue in allArgs.items():
        for converterArg, taskName in specificTasks.items():
            if converterArg == cliArg and cliValue is True:
                logging.debug(taskName + " added your workflow")
                commandToRun += (" | " + taskName + " --configuration json://" + updatedConfigFileName + " -b")
    return commandToRun


def generateDescriptors(resfilename: str, tablesToProduce: dict, tables: dict[str, dict], writerConfigFileName: str, readerConfigFileName = 'aodReaderTempConfig', kFlag = False) -> None:
    """Generates Descriptors for Writing/Reading Tables from AO2D with json config file (input descriptor is optional)

    Args:
        resfilename (str): Name of aod file which will be produced
        tablesToProduce (dict): Tables are required in the output
        tables (dict[str, dict]): Definition of all the tables can be produced
        writerConfigFileName (str): Output name of writer config
        readerConfigFileName (str, optional): Output name of reader config. Defaults to aodReaderTempConfig.json
        kFlag (bool, optional): if True also generates input descriptors. Defaults to False.
    """
    
    iTable = 0
    iTableReader = 0
    # Generate the aod-reader output descriptor json file
    readerConfig = {}
    readerConfig["InputDirector"] = {
        "debugmode": True,
        "InputDescriptors": []
        }
    # Generate the aod-writer output descriptor json file
    writerConfig = {}
    writerConfig["OutputDirector"] = {
        "debugmode": True,
        "resfile": resfilename,
        "resfilemode": "RECREATE",
        "ntfmerge": 1,
        "OutputDescriptors": [],
        }
    
    for table in tablesToProduce.keys():
        writerConfig["OutputDirector"]["OutputDescriptors"].insert(iTable, tables[table])
        iTable += 1
    if kFlag is True:
        for table in tablesToProduce.keys():
            readerConfig["InputDirector"]["InputDescriptors"].insert(iTableReader, tables[table])
            iTableReader += 1
    
    # writerConfigFileName = "aodWriterTempConfig.json"
    with open(writerConfigFileName, "w") as writerConfigFile:
        json.dump(writerConfig, writerConfigFile, indent = 2)
    
    if kFlag is True:
        readerConfigFileName = "aodReaderTempConfig.json"
        with open(readerConfigFileName, "w") as readerConfigFile:
            json.dump(readerConfig, readerConfigFile, indent = 2)
    logging.info("aodWriterTempConfig==========")
    logging.info(f"{writerConfig}")


def tableProducerSkimming(config: dict[str, dict], taskNameInConfig: str, commonTables: list[str], barrelCommonTables: list[str], muonCommonTables: list[str], specificTables: list[str], specificDeps: dict[str, list], runOverMC: bool) -> dict:
    """Table producer function for tableMaker/tableMakerMC

    Args:
        config (dict[str, dict]): Input as JSON config file
        taskNameInConfig (str): Taskname in config file (table-maker/table-maker-m-c)
        commonTables (list[str]): Common tables which are always be created
        barrelCommonTables (list[str]): Barrel tables in reduced DQ data model
        muonCommonTables (list[str]): Muon tables in reduced DQ data model
        specificTables (list[str]): Specific Tables for specific tasks
        specificDeps (dict[str, list]): Specific Dependencies for specific tasks
        runOverMC (bool): Checking to run over MC or Data
        
    Returns:
        dict: Tables to produce dict
    """
    
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
            if "processFull" in processFunc or "processBarrel" in processFunc or "processAmbiguousBarrel" in processFunc:
                logging.info("common barrel tables==========")
                for table in barrelCommonTables:
                    logging.info("%s", table)
                    tablesToProduce[table] = 1
                if runOverMC:
                    tablesToProduce["ReducedTracksBarrelLabels"] = 1
            if "processFull" in processFunc or "processMuon" in processFunc or "processAmbiguousMuon" in processFunc:
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
    return tablesToProduce


def tableProducerAnalysis(config: dict[str, dict], taskNameInConfig: str, commonTables: list[str], barrelCommonTables: list[str], muonCommonTables: list[str], specificTables: dict[str, list], runOverMC: bool) -> dict:
    """Table producer function for tableReader/dqEfficiency
    This method allows produce extra dilepton tables.

    Args:
        config (dict[str, dict]): Input as JSON config file
        taskNameInConfig (str): Taskname in config file (for tableReader and dqEfficiency)
        commonTables (list[str]): Common tables which are always be created
        barrelCommonTables (list[str]): Barrel tables in reduced DQ data model
        muonCommonTables (list[str]): Muon tables in reduced DQ data model
        specificTables (list[str]): Specific Tables for specific tasks
        specificDeps (dict[str, list]): Specific Dependencies for specific tasks
        runOverMC (bool): Checking to run over MC or Data
        
    Returns:
        dict: Tables to produce dict
    """
    
    tablesToProduce = {}
    
    for table in commonTables:
        tablesToProduce[table] = 1
    
    if runOverMC:
        tablesToProduce["ReducedMCEvents"] = 1
        tablesToProduce["ReducedMCEventLabels"] = 1
    
    for processFunc in specificTables.keys():
        if processFunc not in config[taskNameInConfig].keys():
            continue
        if config[taskNameInConfig][processFunc] == "true":
            logging.info("processFunc ========")
            logging.info("%s", processFunc)
            if "processAll" in processFunc or "processDecayToEE":
                logging.info("common barrel tables==========")
                for table in barrelCommonTables:
                    logging.info("%s", table)
                    tablesToProduce[table] = 1
                if runOverMC:
                    tablesToProduce["ReducedTracksBarrelLabels"] = 1
            if "processAll" in processFunc or "processDecayToMuMu":
                logging.info("common muon tables==========")
                for table in muonCommonTables:
                    logging.info("%s", table)
                    tablesToProduce[table] = 1
                if runOverMC:
                    tablesToProduce["ReducedMuonsLabels"] = 1
                    tablesToProduce["DimuonsAll"] = 1
            if runOverMC:
                tablesToProduce["ReducedMCTracks"] = 1
            logging.info("specific tables==========")
            for table in specificTables[processFunc]:
                logging.info("%s", table)
                tablesToProduce[table] = 1
    return tablesToProduce


def setProcessDummy(config: dict[str, dict], dummyHasTasks: list[str]) -> None:
    """Dummy Automizer

    Args:
        config (dict[str, dict]): json config dict
        dummyHasTasks (list[str]): Define dummy task list (get this from SetArgsToArgumentParser class)
        
    """
    processFuncFound = ''
    
    for k, v in config.items(): # loop over number of keys
        if isinstance(v, dict): # iterate only possible items in dict keys
            for v, v2 in v.items():
                if dummyHasTasks is not None and len(dummyHasTasks) > 0:
                    for task in dummyHasTasks:
                        if processFuncFound == k:
                            continue
                        if task not in dummyHasTasks:
                            continue
                        if (not v.endswith("Dummy")) and (v.startswith("process")) and (task == k):
                            if config[k][v] == "true":
                                config[k]["processDummy"] = "false"
                                #logging.debug(" - [%s] processDummy : false", k)
                                processFuncFound = k # save the task and not check in iteration
                                break
                            else:
                                config[k]["processDummy"] = "true"
                                #logging.debug(" - [%s] processDummy : true", k)


def setParallelismOnSkimming(commandToRun: str, updatedConfigFileName: str, analysisTaskName: str, analysisTaskTempConfig: str, config: dict[str, dict]) -> str:
    """Setter method for activate parallel sesion run in O2

    Args:
        commandToRun (str): Command To Run
        updatedConfigFileName (str): Skimming task temp JSON config file name
        analysisTaskName (str): Command to Run for Analysis Task in O2
        analysisTaskTempConfig (dict): Analysis task temp JSON config file name
        config (dict): Skimming task JSON config file

    Returns:
        str: Command To Run for run analysis and skimming task at same time
    """
    
    # save skimming task command to run string to another variable (not mandatory but more readable)
    skimmingTaskFullCommand = commandToRun
    
    # open analysis temp config
    with open(analysisTaskTempConfig) as configAnalysisTask:
        config2 = json.load(configAnalysisTask)
    
    # merge configs
    mergedConfigs = {
        **config2,
        **config
        }
    
    #save merged configs (skimming/analysis)
    with open(updatedConfigFileName, "w") as outputFile:
        json.dump(mergedConfigs, outputFile, indent = 2)
    analysisjson = "aodWriterAnalysisTempConfig.json"
    skimmingjson = "aodWriterSkimmingTempConfig.json"
    
    return f"{skimmingTaskFullCommand} | {analysisTaskName} --configuration json://{updatedConfigFileName} --aod-writer-json {skimmingjson} -b"


class SetArgsToArgumentParser(object):
    
    """This class provides parsing the json file and generates CLI arguments from json config file

    Args:
        cfgJsonName (str): Path to Json config file for creating CLI arguments with parsing
        tasksToPassList (list[str]): If you don't want to include and provide some tasks from the JSON config file to CLI arguments you can define them in a list type
        parser (object): For getting args from ArgumentParser 
        dummyHasTasks (Optional, list[str]): If there are tasks with processDummy in the json, it will save them to the list (for dummy automizer)
        processFuncs: (dict[str, list]): Creating task-processFunctions dependency tree for automations
        
    """
    
    def __init__(self, cfgJsonName: str, tasksToPassList: list, parser = None, dummyHasTasks: list[str] = [], processFuncs: dict[str, list] = {}) -> None:
        
        self.cfgJsonName = cfgJsonName
        self.tasksToPassList = list(tasksToPassList)
        self.parser = argparse.ArgumentParser(description = 'Arguments to pass', formatter_class = argparse.ArgumentDefaultsHelpFormatter)
        self.dummyHasTasks = dummyHasTasks
        self.processFuncs = processFuncs
        
        # Load the configuration file for creating parser args (hard coded)
        configForParsing = {}
        with open(cfgJsonName) as configFile:
            configForParsing = json.load(configFile)
        
        # Dependency injection
        dqLibGetter = DQLibGetter()
        
        # Get All Configurables for DQ Framework from DQ header files
        allAnalysisCuts = dqLibGetter.allAnalysisCuts
        allMCSignals = dqLibGetter.allMCSignals
        allSels = dqLibGetter.allSels
        allMixing = dqLibGetter.allMixing
        
        # Get all histogram groups for DQ Framework from histogram library
        # NOTE Now we use only all histos for backward comp.
        allHistos = dqLibGetter.allHistos
        # allEventHistos = dqLibGetter.allEventHistos
        # allTrackHistos = dqLibGetter.allTrackHistos
        # allMCTruthHistos = dqLibGetter.allMCTruthHistos
        # allPairHistos = dqLibGetter.allPairHistos
        # allDileptonHistos = dqLibGetter.allDileptonHistos
        
        # Predefined lists for autocompletion
        booleanSelections = ["true", "false"]
        itsMatchingSelections = ["0", "1", "2", "3"]
        binarySelection = ["0", "1"]
        tripletSelection = ["-1", "0", "1"]
        collisionSystemSelections = ["PbPb", "pp", "pPb", "Pbp", "XeXe"]
        eventMuonSelections = ["0", "1", "2"]
        debugLevelSelectionsList = ["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        # list for save all arguments (template --> taskname:configuration)
        arglist = []
        
        # Iterating in JSON config file
        for task, cfgValuePair in configForParsing.items():
            if isinstance(cfgValuePair, dict):
                for argument in cfgValuePair.keys():
                    arglist.append(task + ":" + argument) # Set CLI argument as --> taskname:config
        
        # We can define hard coded global arguments
        self.parser.add_argument("cfgFileName", metavar = "Config.json", default = "config.json", help = "config JSON file name (mandatory)")
        self.parser.add_argument("-runParallel", help = "Run parallel in session", action = "store_true", default = False)
        
        # GLOBAL OPTIONS
        groupGlobal = self.parser.add_argument_group(title = f"Global workflow options")
        groupGlobal.add_argument("--aod-memory-rate-limit", help = "Rate limit AOD processing based on memory", action = "store", type = str)
        groupGlobal.add_argument("--writer", help = "Argument for producing extra reduced tables", action = "store", type = str).completer = ChoicesCompleter(booleanSelections)
        groupGlobal.add_argument("--helpO2", help = "Display help message on O2", action = "store_true", default = False)
        
        # Converter Task Options
        groupO2Converters = self.parser.add_argument_group(title = f"Add to workflow O2 Converter task options")
        groupO2Converters.add_argument("--add_mc_conv", help = "Add the converter from mcparticle to mcparticle+001 (Adds your workflow o2-analysis-mc-converter task)", action = "store_true",)
        groupO2Converters.add_argument("--add_fdd_conv", help = "Add the fdd converter (Adds your workflow o2-analysis-fdd-converter task)", action = "store_true",)
        groupO2Converters.add_argument("--add_track_prop", help = "Add track propagation to the innermost layer (TPC or ITS) (Adds your workflow o2-analysis-track-propagation task)", action = "store_true",)
        groupO2Converters.add_argument("--add_weakdecay_ind", help = "Add Converts V0 and cascade version 000 to 001 (Adds your workflow o2-analysis-weak-decay-indices task)", action = "store_true",)
        groupO2Converters.add_argument("--add_col_conv", help = "Add the converter from collision to collision+001", action = "store_true")
        
        # Helper Options
        groupHelper = self.parser.add_argument_group(title = f"Helper Options")
        groupHelper.add_argument("--debug", help = "execute with debug options", action = "store", type = str.upper, default = "INFO", choices = debugLevelSelectionsList,).completer = ChoicesCompleterList(debugLevelSelectionsList)
        groupHelper.add_argument("--logFile", help = "Enable logger for both file and CLI", action = "store_true")
        groupHelper.add_argument("--override", help = "If true JSON Overrider Interface If false JSON Additional Interface", action = "store", default = "true", type = str.lower, choices = booleanSelections,).completer = ChoicesCompleter(booleanSelections)
        
        # Create argument group for iterating json options
        groupJsonParser = self.parser.add_argument_group(title = f"JSON configuration options")
        
        # save args to parser(template --> --taskname:config)
        for arg in arglist:
            # seperate the template to list --> taskname:config to [taskname, configurable]
            seperatedArg = stringToList(arg, ":")
            configurable: str = seperatedArg[1] # configurable as second index
            taskname: str = seperatedArg[0] # taskname as first index
            if "process" in configurable and "Dummy" not in configurable:
                self.processFuncs.setdefault(taskname, []).append(configurable)
            
            # Tasks to pass
            if taskname in tasksToPassList:
                continue
            
            # Get has processDummy tasks from json
            if configurable == "processDummy":
                self.dummyHasTasks.append(taskname)
            
            # We may define posible all autocompletions as semi hard-coded with substring search (according to naming conventions)
            # Define some autocompletion rules for match-case (for O2-DQ Framework)
            containsCuts = "Cuts" in configurable
            containsSignals = configurable.endswith("Signals") or configurable.endswith("signals")
            containsHistogram = "Histogram" in configurable
            containsSels = configurable.endswith("BarrelSels") or configurable.endswith("MuonSels")
            containsMixingVars = "MixingVars" in configurable
            containsQA = configurable.startswith("cfg") and "QA" in configurable
            containsAmbiguous = configurable == "cfgIsAmbiguous"
            containsFillCandidateTable = configurable == "cfgFillCandidateTable"
            containsFlatTables = configurable == "cfgFlatTables"
            containsTPCpostCalib = configurable == "cfgTPCpostCalib"
            containsProcess = configurable.startswith("process")
            
            # Create arguments with possible autocompletions for DQ Framework
            if containsCuts:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allAnalysisCuts)
            elif containsSignals:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allMCSignals)
            elif containsHistogram:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allHistos)
            elif containsSels:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allSels)
            elif containsMixingVars:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allMixing)
            elif containsQA:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
            elif containsAmbiguous:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
            elif containsFillCandidateTable:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
            elif containsFlatTables:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
            elif containsTPCpostCalib:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
            elif configurable == "processDummy": # NOTE we don't need configure processDummy since we have dummy automizer
                continue
            
            # Create arguments with possible autocompletions for Common Framework
            elif containsProcess: # NOTE This is an global definition in O2 Analysis framework, all process functions startswith "process"
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
            elif configurable == "syst":
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str, metavar = "\b").completer = ChoicesCompleter(collisionSystemSelections)
            elif configurable == "doVertexZeq":
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str, metavar = "\b").completer = ChoicesCompleter(binarySelection)
            elif configurable.startswith("pid-") or configurable.startswith("est"):
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(tripletSelection)
            elif configurable == "muonSelection":
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str, metavar = "\b").completer = ChoicesCompleter(eventMuonSelections)
            elif configurable == "itsMatching":
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str, metavar = "\b").completer = ChoicesCompleter(itsMatchingSelections)
            elif configurable == "compatibilityIU":
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
            else:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str, metavar = "\b") # Create other arguments without autocompletion
    
    def parseArgs(self, testString = None):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace as argument, parameter: returns parse_args() with autocomplete generated arguments and parameters
        """
        
        argcomplete.autocomplete(self.parser, always_complete_options = False)
        return self.parser.parse_args()


def setConfigs(allArgs: dict[str, Any], config: dict[str, dict], cliMode: str) -> None:
    """Setter function for CLI arguments to JSON config file

    Args:
        allArgs (dict): All provided arguments from CLI
        config (dict[str, dict]): Input as JSON config file
        cliMode (str): CLI mode selection (true or false in string type)
    """
    for argument, parameter in allArgs.items():
        if parameter is not None: # NOTE We can't iterate in None types
            if ":" in argument: # protection, we need seperate only core O2 interface args
                
                # Seperating for taskname and configurable
                tasknameConfigurablePair = stringToList(argument, ":") # taskname:Configurable --> [taskname, configurable]
                taskname = tasknameConfigurablePair[0] # get taskname as first index
                configurable = tasknameConfigurablePair[1] # get configurable as second index
                taskname = [char.replace("_", "-") for char in taskname] # replace _ to - (list comprehension)
                taskname = convertListToStr(taskname) # convert list to string after list comprehension
                configurable = [char.replace("_", "-") for char in configurable] # replace _ to - (list comprehension)
                configurable = convertListToStr(configurable) # convert list to string after list comprehension
                
                if isinstance(parameter, list): # for list to comma seperated strings
                    parameter = listToString(parameter)
                if cliMode == "false":
                    actualConfig = config[taskname][configurable]
                    parameter = actualConfig + "," + parameter
                config[taskname][configurable] = parameter
                logging.info(" - [%s] %s : %s", taskname, configurable, parameter)


def setSwitch(config: dict[str, dict], processFuncs: dict[str, list], allArgs: dict, cliMode: str, processFuncToPass: list[str] = []) -> None:
    """This method providees Process function automation for overrider mode

    Args:
        config (dict): Input as json config file
        processFuncs (dict): All process function deps list (taskname - process Functions)
        allArgs (dict): All provided args from CLI
        cliMode (str): cliMode as argument
        processFuncToPass (list[str], optional): List to pass configuration on mandatory arguments. Defaults to [].
    """
    
    processDepsDict = {} # save all true configured task - process function pairs to dict --> typeof dict[str, list]
    
    if cliMode == "true":
        for taskProcessPair, parameter in allArgs.items():
            if "process" in taskProcessPair and (parameter == "true" or parameter == "false" or parameter is None):
                taskProcessPairNew = [char.replace("_", "-") for char in taskProcessPair] # replace _ to - (list comprehension)
                taskProcessPairNew = convertListToStr(taskProcessPairNew) # convert list to string after list comprehension
                seperatedTaskProcessPair = stringToList(taskProcessPairNew, ":") # seperate as taskname process function
                taskName = seperatedTaskProcessPair[0] # taskname in args
                processFunc = seperatedTaskProcessPair[1] # processFunc in args
                if taskName in processFuncs.keys() and processFunc in processFuncs[taskName] and parameter == "true":
                    processDepsDict.setdefault(taskName, []).append(processFunc)
        
        if len(processDepsDict.keys()) > 0:
            logging.info("Process function automation for JSON overrider mode starting..")
            for taskProcessPair, parameter in allArgs.items():
                if "process" in taskProcessPair and (parameter == "true" or parameter == "false" or parameter is None):
                    taskProcessPairNew = [char.replace("_", "-") for char in taskProcessPair] # replace _ to - (list comprehension)
                    taskProcessPairNew = convertListToStr(taskProcessPairNew) # convert list to string after list comprehension
                    seperatedTaskProcessPair = stringToList(taskProcessPairNew, ":") # seperate as taskname process function
                    taskName = seperatedTaskProcessPair[0] # taskname in args
                    processFunc = seperatedTaskProcessPair[1] # processFunc in args
                    if taskName in processDepsDict.keys() and parameter != "true" and processFunc not in processFuncToPass and "Dummy" not in processFunc: # TODO fix duplicated messages for false
                        config[taskName][processFunc] = "false"
                        logging.info(" - [%s] %s : %s", taskName, processFunc, "false")


def commonDepsToRun(commonDeps: list[str]) -> dict:
    """Produces common deps to run dict

    Args:
        commonDeps (list[str]): common deps to run list

    Returns:
        dict: common deps to run dict
    """
    
    depsToRun = {}
    for dep in commonDeps:
        depsToRun[dep] = 1
    return depsToRun
