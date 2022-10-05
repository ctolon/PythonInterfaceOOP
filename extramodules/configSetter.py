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

from .stringOperations import listToString, stringToListWithSlash
import logging
from logging import handlers
import sys
import os
import json


# NOTE This will removed when we have unique name for dilepton-track signals
def multiConfigurableSet(config: dict, task: str, cfg: str, arg: list, cliMode):
    
    if isinstance(arg, list):
        arg = listToString(arg)
    if cliMode == "false":
        actualConfig = config[task][cfg]
        arg = actualConfig + "," + arg
    config[task][cfg] = arg


def dispArgs(allArgs: dict):
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


def debugSettings(argDebug: bool, argLogFile: bool, fileName: str):
    """Debug settings for CLI

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


def setConverters(allArgs: dict, updatedConfigFileName: str, commandToRun: str):
    """Converter task setter function

    Args:
        allArgs (dict): All provided args in CLI
        updatedConfigFileName (str): Overrided json config file
        commandToRun (str): Generated command for running in O2
    """
    specificTasks = {
        "add_mc_conv": "o2-analysis-mc-converter",
        "add_fdd_conv": "o2-analysis-fdd-converter",
        "add_track_prop": "o2-analysis-track-propagation",
        "add_weakdecay_ind:": "o2-analysis-weak-decay-indices"
        }
    
    for cliArg, cliValue in allArgs.items():
        for converterArg, taskName in specificTasks.items():
            if converterArg == cliArg and cliValue is True:
                logging.debug(taskName + " added your workflow")
                commandToRun += (" | " + taskName + " --configuration json://" + updatedConfigFileName + " -b")
    return commandToRun


def generateDescriptors(
        tablesToProduce: dict, tables: dict, writerConfigFileName = "aodWriterTempConfig.json",
        readerConfigFileName = "aodReaderTempConfig.json", kFlag = False
    ):
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
    print(writerConfig)


def tableProducer(
        config, taskNameInConfig, tablesToProduce, commonTables, barrelCommonTables, muonCommonTables, specificTables, specificDeps,
        runOverMC
    ):
    """Table producer function for tableMaker/tableMakerMC

    Args:
        config (dict): Input as JSON config file
        taskNameInConfig (string): Taskname in config file (table-maker/table-maker-m-c)
        tablesToProduce (dict): Input as which tables are needed
        commonTables (list): Common tables which are always be created
        barrelCommonTables (list): Barrel tables in reduced DQ data model
        muonCommonTables (list): Muon tables in reduced DQ data model
        specificTables (list): Specific Tables for specific tasks
        specificDeps (dict): Specific Dependencies for specific tasks
        runOverMC (bool): Checking to run over MC or Data
    """
    
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


def setSelection(config: dict, deps: dict, targetCfg: list, cliMode: bool):
    """If the arguments are set with very different naming conventions and they are for selection, this function is used to set the values

    Args:
        config (dict): Input as JSON config file
        deps (dict): Dependency list
        targetCfg (list): parameters argument name
        cliMode (bool): CLI mode
    """
    
    for selection, taskNameProcessFuncPair in deps.items():
        if isinstance(taskNameProcessFuncPair, dict):
            for taskName, processFunc in taskNameProcessFuncPair.items():
                if selection in targetCfg:
                    config[taskName][processFunc] = "true"
                    logging.debug(" - [%s] %s : true", taskName, processFunc)
                
                elif cliMode == "true":
                    config[taskName][processFunc] = "false"
                    logging.debug(" - [%s] %s : false", taskName, processFunc)
        else:
            raise TypeError("Taskname - Process Function pair should be a dictionary type")


def setConfig(config: dict, task: str, cfg: str, allArgs: dict, cliMode: bool):
    """This function provides directly set to argument parameter, if argument naming and json cfg naming equals

    Args:
        config (dict): Input as JSON config file
        task (str): Task as argument
        cfg (str): Configurable or Process Func as parameter
        allArgs (dict): Configured args in CLI
        cliMode (bool): CLI mode
    """
    
    for keyCfg, valueCfg in allArgs.items():
        if (cfg == keyCfg) and (valueCfg is not None):
            if isinstance(valueCfg, list):
                valueCfg = listToString(valueCfg)
            if cliMode == "false":
                actualConfig = config[task][cfg]
                valueCfg = actualConfig + "," + valueCfg
            config[task][cfg] = valueCfg
            logging.debug(" - [%s] %s : %s", task, cfg, valueCfg)


def setSwitch(config: dict, task: str, cfg: str, allArgs: dict, cliMode: str, argument: str, parameters: list, switchType: str):
    """This method provides configure parameters with SWITCH_ON/SWITCH_OFF (both for configurables and process functions)

    Args:
        config (dict): JSON config file as input
        task (str): Task
        cfg (str): Configurable or Process Func
        allArgs (dict): Configured args in CLI
        cliMode (bool): CLI mode
        argument (str): Selected argument from configured args
        parameters (list): All available parameters for argument
        switchType (str): Switch type usage in string --> "SWITCH_ON/SWITCHOFF"
    """
    
    possibleSwitchTypes = ["1/-1", "1/0", "true/false"] # you have to add new switch type here if you need
    if switchType not in possibleSwitchTypes:
        logging.error("%s is invalid argument for setSwitch", switchType)
        raise ValueError("Invalid switchType. Expected one of: %s" % possibleSwitchTypes)
    
    switchType = stringToListWithSlash(switchType)
    
    if len(switchType) != 2:
        raise ValueError("Invalid switch Type. Your switch types should be seperated with /. ex: true/false")
    
    SWITCH_ON = switchType[0]
    SWITCH_OFF = switchType[1]
    
    for keyCfg, valueCfg in allArgs.items():
        if isinstance(valueCfg, list) and keyCfg == argument:
            for element in valueCfg:
                if (cfg == element) and (element is not None):
                    config[task][cfg] = SWITCH_ON
                    logging.debug(" - [%s] %s : %s", task, cfg, SWITCH_ON)
            
            if (cliMode == "true"):
                for param in parameters:
                    if param not in valueCfg and param == cfg: # param should equals cfg for getting task info
                        config[task][cfg] = SWITCH_OFF
                        logging.debug(" - [%s] %s : %s", task, cfg, SWITCH_OFF)
                        # print(param)
        
        elif isinstance(valueCfg, str) and keyCfg == argument:
            if (cfg == valueCfg) and (valueCfg is not None):
                config[task][cfg] = SWITCH_ON
                logging.debug(" - [%s] %s : %s", task, cfg, SWITCH_ON)
            
            if (cliMode == "true"):
                for param in parameters:
                    if param != valueCfg and param == cfg: # param should equals cfg for getting task info
                        config[task][param] = SWITCH_OFF
                        logging.debug(" - [%s] %s : %s", task, param, SWITCH_OFF)


def setProcessDummy(config: dict, dummyHasTasks = None):
    """Dummy Automizer

    Args:
        config (dict): json config dict
        dummyHasTasks (list, optional): Define dummy task list, if you don't define it, all task will checked
        
    Note:
        For dummyHasTasks: If other tasks do not have the processDummy function, the workflow will fire. So if you don't have processDummy in each of your tasks, give them a list.
    """
    processFuncFound = ''
    
    for k, v in config.items(): # loop over number of keys
        if isinstance(v, dict): # iterate only possible items in dict keys
            for v, v2 in v.items():
                if dummyHasTasks is None:
                    if (not v.endswith("Dummy")) and (v.startswith("process")):
                        if config[k][v] == "true":
                            config[k]["processDummy"] = "false"
                            #logging.debug(" - [%s] processDummy : false", k)
                            break
                        else:
                            config[k]["processDummy"] = "true"
                            #logging.debug(" - [%s] processDummy : true", k)
                if dummyHasTasks is not None:
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


def setFalseHasDeps(config: dict, task: str, cfg: str, argument: list, parameters: list, cliMode: bool, selectedKey = None):
    """function to pull all process function values false when the argument with dependencies is not configured. Otherwise, the process will crash due to dependencies.

    Args:
        config (dict): Input as JSON config file
        task (str): Config Task
        cfg (str): Config cfg
        argument (list): CLI Argument
        parameters (list): Your parameter list
        cliMode (bool): CLI mode
        selectedKey (str, optional): If you wish, you can define one selected task for more control
    """
    
    if argument is None and cliMode == "true":
        for process in parameters:
            if cfg == process and selectedKey is None: # for getting task info from json
                config[task][cfg] = "false"
                logging.info(" - [%s] %s : false", task, cfg)
            elif cfg == process and task == selectedKey: # also with selected task for more control
                config[task][cfg] = "false"
                logging.info(" - [%s] %s : false", task, cfg)
            else:
                continue


def setPrefixSuffix(argument, prefix = None, suffix = None, kFlagPrefix = None, kFlagSuffix = None):
    """Prefix and/or suffix setter function

    Args:
        argument (str or list): CLI argument
        prefix (str, optional): Prefix as string. Defaults to None.
        suffix (str, optional): Suffix as string. Defaults to None
        kFlagPrefix (bool, optional): Flag for activating prefix setter. Defaults to None.
        kFlagSuffix (bool, optional): Flag for activating suffix setter. Defaults to None.
    """
    
    if argument is not None:
        if kFlagPrefix is True:
            if isinstance(argument, list):
                argument = [prefix + sub for sub in argument]
            else:
                argument = prefix + argument
        if kFlagSuffix is True:
            if isinstance(argument, list):
                argument = [sub + suffix for sub in argument]
            else:
                argument = argument + suffix
        return argument
