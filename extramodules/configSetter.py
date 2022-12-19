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


def dispArgs(allArgs: dict) -> None:
    """Display all configured commands you provided in CLI

    Args:
        allArgs (dict): configured commands in CLI
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




def dispO2HelpMessage(argHelpO2, commandToRun):
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


def setConverters(allArgs: dict, updatedConfigFileName: str, commandToRun: str) -> str:
    """Converter task setter function

    Args:
        allArgs (dict): All provided args in CLI
        updatedConfigFileName (str): Overrided json config file
        commandToRun (str): Generated command for running in O2
        
    Returns:
        str: Command To Run with provided converter task options
    """
    specificTasks = {
        "add_mc_conv": "o2-analysis-mc-converter",
        "add_fdd_conv": "o2-analysis-fdd-converter",
        "add_track_prop": "o2-analysis-track-propagation",
        "add_weakdecay_ind": "o2-analysis-weak-decay-indices"
        }
    
    for cliArg, cliValue in allArgs.items():
        for converterArg, taskName in specificTasks.items():
            if converterArg == cliArg and cliValue is True:
                logging.debug(taskName + " added your workflow")
                commandToRun += (" | " + taskName + " --configuration json://" + updatedConfigFileName + " -b")
    return commandToRun


def generateDescriptors(tablesToProduce: dict, tables: dict, writerConfigFileName = "aodWriterTempConfig.json", readerConfigFileName = "aodReaderTempConfig.json", kFlag = False) -> None:
    """Generates Descriptors for Writing/Reading Tables from AO2D with json config file (input descriptor is optional)

    Args:
        tablesToProduce (dict): Tables are required in the output
        tables (dict): Definition of all the tables can be produced
        writerConfigFileName (str, optional): Output name of writer config. Defaults to "aodWriterTempConfig.json".
        readerConfigFileName (str, optional): Output name of reader config. Defaults to "aodReaderTempConfig.json".
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
        "resfile": "reducedAod",
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
    
    writerConfigFileName = "aodWriterTempConfig.json"
    with open(writerConfigFileName, "w") as writerConfigFile:
        json.dump(writerConfig, writerConfigFile, indent = 2)
    
    if kFlag is True:
        readerConfigFileName = "aodReaderTempConfig.json"
        with open(readerConfigFileName, "w") as readerConfigFile:
            json.dump(readerConfig, readerConfigFile, indent = 2)
    logging.info("aodWriterTempConfig==========")
    logging.info(f"{writerConfig}")


def tableProducer(config: dict, taskNameInConfig: str, commonTables: list, barrelCommonTables: list, muonCommonTables: list, specificTables: list, specificDeps: dict, runOverMC: bool) -> dict:
    """Table producer function for tableMaker/tableMakerMC

    Args:
        config (dict): Input as JSON config file
        taskNameInConfig (str): Taskname in config file (table-maker/table-maker-m-c)
        commonTables (list): Common tables which are always be created
        barrelCommonTables (list): Barrel tables in reduced DQ data model
        muonCommonTables (list): Muon tables in reduced DQ data model
        specificTables (list): Specific Tables for specific tasks
        specificDeps (dict): Specific Dependencies for specific tasks
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


def setProcessDummy(config: dict, dummyHasTasks: list) -> None:
    """Dummy Automizer

    Args:
        config (dict): json config dict
        dummyHasTasks (list): Define dummy task list (get this from SetArgsToArgumentParser class)
        
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


def setParallelismOnSkimming(commandToRun: str, updatedConfigFileName: str, analysisTaskName: str, analysisTaskTempConfig: str, config: dict) -> str:
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
    
    #NOTE: Aod writer json config arg currently not working with parallelism
    #return (analysisTaskName + " --configuration json://" + updatedConfigFileName + " --aod-writer-json aodWriterTempConfig.json " + " -b " + '| ' + skimmingTaskFullCommand)
    return (analysisTaskName + " --configuration json://" + updatedConfigFileName + " -b " + '| ' + skimmingTaskFullCommand)


class SetArgsToArgumentParser(object):
    """This class provides parsing the json file and generates CLI arguments from json config file

    Args:
        cfgJsonName (str): Path to Json config file for creating CLI arguments with parsing
        tasksToPassList (list): If you don't want to include and provide some tasks from the JSON config file to CLI arguments you can define them in a list type
        parser (object): For getting args from ArgumentParser 
        dummyHasTasks (Optional, list): If there are tasks with processDummy in the json, it will save them to the list (for dummy automizer)

    Returns:
        dict: namespace, argument
    """
    
    
    def __init__(self, cfgJsonName, tasksToPassList: list, parser = None, dummyHasTasks = []) -> dict:
        
        self.cfgJsonName = cfgJsonName
        self.tasksToPassList = list(tasksToPassList)
        self.parser = argparse.ArgumentParser(description = 'Arguments to pass', formatter_class = argparse.ArgumentDefaultsHelpFormatter)
        self.dummyHasTasks = dummyHasTasks
            
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
                
        self.parser.add_argument("cfgFileName", metavar = "Config.json", default = "config.json", help = "config JSON file name (mandatory)")
        self.parser.add_argument("-runParallel", help = "Run parallel sessions", action = "store_true", default = False)
        
        # Special Configs
        # parser.add_argument("-runData", help = "Run over Data", action = "store_true", default = True)
        
        # GLOBAL OPTIONS
        # TODO extend them
        groupGlobal = self.parser.add_argument_group(title = f"Global workflow options")
        groupGlobal.add_argument("--aod-memory-rate-limit", help = "Rate limit AOD processing based on memory", action = "store", type = str)
        groupGlobal.add_argument("--writer", help = "Argument for producing extra reduced tables", action = "store", type = str)
        groupGlobal.add_argument("--helpO2", help = "Display help message on O2", action = "store_true", default = False)
        
        # Converter Task Options
        groupO2Converters = self.parser.add_argument_group(title = f"Add to workflow O2 Converter task options")
        groupO2Converters.add_argument("--add_mc_conv", help = "Add the converter from mcparticle to mcparticle+001 (Adds your workflow o2-analysis-mc-converter task)", action = "store_true",)
        groupO2Converters.add_argument("--add_fdd_conv", help = "Add the fdd converter (Adds your workflow o2-analysis-fdd-converter task)", action = "store_true",)
        groupO2Converters.add_argument("--add_track_prop", help = "Add track propagation to the innermost layer (TPC or ITS) (Adds your workflow o2-analysis-track-propagation task)", action = "store_true",)
        groupO2Converters.add_argument("--add_weakdecay_ind", help = "Add Converts V0 and cascade version 000 to 001 (Adds your workflow o2-analysis-weak-decay-indices task)", action = "store_true",)
        
        # Helper Options
        groupHelper = self.parser.add_argument_group(title = f"Helper Options")
        groupHelper.add_argument("--debug", help = "execute with debug options", action = "store", type = str.upper, default = "INFO", choices = debugLevelSelectionsList,).completer = ChoicesCompleterList(debugLevelSelectionsList)
        groupHelper.add_argument("--logFile", help = "Enable logger for both file and CLI", action = "store_true")
        groupHelper.add_argument("--onlySelect", help = "If false JSON Overrider Interface If true JSON Additional Interface", action = "store", default = "true", type = str.lower, choices = booleanSelections,).completer = ChoicesCompleter(booleanSelections)
        
        # Create argument group for iterating json options
        groupJsonParser = self.parser.add_argument_group(title = f"JSON configuration options")
        
        # save args to parser(template --> --taskname:config)
        for arg in arglist:
            
            # seperate the template to list --> taskname:config to [taskname, configurable]
            seperatedArg = stringToList(arg, ":")
            configurable = seperatedArg[1] # configurable as second index
            taskname = seperatedArg[0] # taskname as first index
            
            # Tasks to pass
            if taskname in tasksToPassList:
                continue
            
            # Get has processDummy tasks from json
            if configurable == "processDummy":
                self.dummyHasTasks.append(taskname)
            
            # We may define posible all autocompletions as semi hard-coded with substring search (according to naming conventions)
            # DQ Framework
            if "Cuts" in configurable:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allAnalysisCuts)
            elif configurable.endswith("Signals") or configurable.endswith("signals"):
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allMCSignals)
            elif "Histogram" in configurable:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allHistos)
            elif configurable.endswith("BarrelSels") or configurable.endswith("MuonSels"):
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allSels)
            elif "MixingVars" in configurable:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allMixing)
            elif configurable.startswith("cfg") and "QA" in configurable:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
            elif configurable == "cfgIsAmbiguous":
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
            elif configurable == "cfgFillCandidateTable":
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
            elif configurable == "cfgFlatTables":
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
            elif configurable == "cfgTPCpostCalib":
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
            #elif configurable == "processDummy": # NOTE we don't need configure processDummy since we have dummy automizer
                #continue
            
            # NOTE maybe need define also task name except process for protection
            # Common Framework
            elif configurable.startswith("process"):
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
            elif configurable == "syst":
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str, metavar = "\b").completer = ChoicesCompleter(collisionSystemSelections)
            elif configurable == "doVertexZeq":
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str, metavar = "\b").completer = ChoicesCompleter(binarySelection)
            elif configurable.startswith("pid-") or configurable.startswith("est"):
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs="*", type = str, metavar = "\b").completer = ChoicesCompleterList(tripletSelection)
            elif configurable == "muonSelection":
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str, metavar = "\b").completer = ChoicesCompleter(eventMuonSelections)
            elif configurable == "itsMatching":
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str, metavar = "\b").completer = ChoicesCompleter(itsMatchingSelections)
            elif configurable == "compatibilityIU":
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
            else:
                groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str, metavar = "\b") # Has no autocompletion
        
        argcomplete.autocomplete(self.parser, always_complete_options = False)
        self.parser.parse_args()
    
def setConfigs(allArgs: dict, config: dict, climode: str) -> None:
    """Setter function for CLI arguments to JSON config file

    Args:
        allArgs (dict): All provided arguments from CLI
        config (dict): Input as JSON config file
        climode (str): CLI mode selection (true or false in string type)
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
                if climode == "false":
                    actualConfig = config[taskname][configurable]
                    valueCfg = actualConfig + "," + valueCfg
                config[taskname][configurable] = parameter
                logging.info(" - [%s] %s : %s", taskname, configurable, parameter)
    
def commonDepsToRun(commonDeps: list) -> dict:
    """Produces common deps to run dict

    Args:
        commonDeps (list): common deps to run list

    Returns:
        dict: common deps to run dict
    """
           
    depsToRun = {}
    for dep in commonDeps:
        depsToRun[dep] = 1
    return depsToRun
