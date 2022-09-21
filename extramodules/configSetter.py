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

# This script includes setter functions for configurables

#from extramodules.dqOperations import listToString
from .stringOperations import listToString, stringToListWithSlash
import logging
from logging import handlers
import sys
import os


# NOTE This will removed when we have unique name for dilepton-track signals
def multiConfigurableSet(config: dict, key: str, value: str, arg: list, onlySelect):
    
    if isinstance(arg, list):
        arg = listToString(arg)
    if onlySelect == "false":
        actualConfig = config[key][value]
        arg = actualConfig + "," + arg
    config[key][value] = arg


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


def converterSet(
        add_mc_conv: bool, add_fdd_conv: bool, add_track_prop: bool, add_weakdecay_ind: bool, updatedConfigFileName: str, commandToRun: str
    ):
    """Converter task setter function

    Args:
        add_mc_conv (bool): o2-analysis-weakdecay-indices CLI argument
        add_fdd_conv (bool): o2-analysis-weakdecay-indices CLI argument
        add_track_prop (bool): o2-analysis-weakdecay-indices CLI argument
        add_weakdecay_ind (bool): o2-analysis-weakdecay-indices CLI argument
        updatedConfigFileName (str): Overrided json config file
        commandToRun (str): Generated command for running in O2
    """
    
    if add_mc_conv:
        logging.debug("o2-analysis-mc-converter added your workflow")
        commandToRun += (" | o2-analysis-mc-converter --configuration json://" + updatedConfigFileName + " -b")
    
    if add_fdd_conv:
        commandToRun += (" | o2-analysis-fdd-converter --configuration json://" + updatedConfigFileName + " -b")
        logging.debug("o2-analysis-fdd-converter added your workflow")
    
    if add_track_prop:
        commandToRun += (" | o2-analysis-track-propagation --configuration json://" + updatedConfigFileName + " -b")
        logging.debug("o2-analysis-track-propagation added your workflow")
    
    if add_weakdecay_ind:
        commandToRun += (" | o2-analysis-weak-decay-indices --configuration json://" + updatedConfigFileName + " -b")
        logging.debug("o2-analysis-weak-decay-indices added your workflow")
    
    return commandToRun


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


def SELECTION_SET(config: dict, deps: dict, targetCfg: list, cliMode: bool):
    """If the arguments are set with very different naming conventions and they are for selection, this function is used to set the values

    Args:
        config (dict): Input as JSON config file
        deps (dict): Dependency list
        targetCfg (list): parameters argument name
        cliMode (bool): CLI mode
    """
    
    for k, v in deps.items():
        if k in targetCfg:
            config[v[0]][v[1]] = "true"
            logging.debug(" - [%s] %s : true", v[0], v[1])
        elif cliMode == "true":
            config[v[0]][v[1]] = "false"
            logging.debug(" - [%s] %s : false", v[0], v[1])


def CONFIG_SET(config, key, value, allArgs, onlySelect):
    """This function provides directly set to argument parameter, if argument naming and json value naming equals

    Args:
        config (_type_): _description_
        key (_type_): _description_
        value (_type_): _description_
        allArgs (_type_): _description_
        onlySelect (_type_): _description_
    """
    
    for keyCfg, valueCfg in allArgs.items():
        if (value == keyCfg) and (valueCfg is not None):
            if isinstance(valueCfg, list):
                valueCfg = listToString(valueCfg)
            if onlySelect == "false":
                actualConfig = config[key][value]
                valueCfg = actualConfig + "," + valueCfg
            config[key][value] = valueCfg
            logging.debug(" - [%s] %s : %s", key, value, valueCfg)


def PROCESS_SWITCH(
        config: dict, key: str, value: str, allArgs: dict, onlySelect: str, argument: str, parameters: list, switchType: str, kFlag = False
    ):
    """This method provides configure parameters with SWITCH_ON/SWITCH_OFF (both for configurables and process functions)

    Args:
        config (dict): JSON config file as input
        key (str): Key
        value (str): Value
        allArgs (dict): Configured args in CLI
        onlySelect (bool): CLI mode
        argument (str): Selected argument from configured args
        parameters (list): All available parameters for argument
        switchType (str): Switch type usage in string --> "SWITCH_ON/SWITCHOFF"
        kFlag (bool): If True -> Key prefix-suffix based instead of value prefix-suffix based PROCESS_SWITCH (Default is value based)
    """
    
    possibleSwitchTypes = ["1/-1", "1/0", "true/false"] # you have to add new switch type here if you need
    if switchType not in possibleSwitchTypes:
        logging.error("%s is invalid argument for PROCESS_SWITCH", switchType)
        raise ValueError("Invalid switchType. Expected one of: %s" % possibleSwitchTypes)
    
    switchType = stringToListWithSlash(switchType)
    
    if len(switchType) != 2:
        raise ValueError("Invalid switch Type. Your switch types should be seperated with /. ex: true/false")
    
    SWITCH_ON = switchType[0]
    SWITCH_OFF = switchType[1]
    
    keyCfgFixed = ''
    
    for keyCfg, valueCfg in allArgs.items():
        if kFlag is False:
            if isinstance(valueCfg, list) and keyCfg == argument:
                for element in valueCfg:
                    if (value == element) and (element is not None):
                        config[key][value] = SWITCH_ON
                        logging.debug(" - [%s] %s : %s", key, value, SWITCH_ON)
                
                if (onlySelect == "true"):
                    for param in parameters:
                        if param not in valueCfg and param == value: # param should equals value for getting key info
                            config[key][value] = SWITCH_OFF
                            logging.debug(" - [%s] %s : %s", key, value, SWITCH_OFF)
                            # print(param)
            
            elif isinstance(valueCfg, str) and keyCfg == argument:
                if (value == valueCfg) and (valueCfg is not None):
                    config[key][value] = SWITCH_ON
                    logging.debug(" - [%s] %s : %s", key, value, SWITCH_ON)
                
                if (onlySelect == "true"):
                    for param in parameters:
                        if param != valueCfg and param == value: # param should equals value for getting key info
                            config[key][param] = SWITCH_OFF
                            logging.debug(" - [%s] %s : %s", key, param, SWITCH_OFF)
        
        # NOTE can be deleted when we have better naming conventions
        if kFlag is True:
            
            if keyCfg.startswith("isVertexZeq") and keyCfg == argument: # TODO REfactor is --> do
                keyCfgFixed = keyCfg[2 ::] # remove 'is'
                keyCfgFixed = "do" + keyCfgFixed # add prefix do
            
            if keyCfg.startswith("is") and keyCfg == argument: # if keyCfg startswith "is", replace it with "process"
                keyCfgFixed = keyCfg[2 ::] # remove 'is'
                keyCfgFixed = "process" + keyCfgFixed # add prefix process
            
            elif keyCfg.startswith("FT0") and keyCfg == argument: #TODO Refactor FT0 to --> isFT0
                keyCfgFixed = "process" + keyCfg
                key = "tof-event-time"
            
            if (valueCfg == SWITCH_ON):
                #print(keyCfg)
                if value == keyCfgFixed and keyCfg == argument: # json value should be equal prefixed arg and keyCfg from allArgs should equals to arg
                    config[key][value] = SWITCH_ON
                    logging.debug(" - [%s] %s : %s", key, value, SWITCH_ON)
                
                for param in parameters:
                    if param != keyCfgFixed and value == param and keyCfg == argument: # for converting other values false
                        config[key][value] = SWITCH_OFF
                        logging.debug(" - [%s] %s : %s", key, value, SWITCH_OFF)
            
            elif (valueCfg == SWITCH_OFF):
                if value == keyCfgFixed and keyCfg == argument:
                    config[key][value] = SWITCH_OFF
                    logging.debug(" - [%s] %s : %s", key, value, SWITCH_OFF)
                
                for param in parameters:
                    if param != keyCfgFixed and value == param and keyCfg == argument:
                        config[key][value] = SWITCH_ON
                        logging.debug(" - [%s] %s : %s", key, value, SWITCH_ON)


def PROCESS_DUMMY(config: dict, dummyHasTasks = None):
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


def NOT_CONFIGURED_SET_FALSE(config: dict, key: str, value: str, argument: list, parameters: list, cliMode: bool, selectedKey = None):
    """function to pull all process function values false when the argument with dependencies is not configured. Otherwise, the process will crash due to dependencies.

    Args:
        config (dict): Input as JSON config file
        key (str): Config Key
        value (str): Config value
        argument (list): CLI Argument
        parameters (list): Your parameter list
        cliMode (bool): CLI mode
        selectedKey (str, optional): If you wish, you can define one selected key for more control
    """
    
    if argument is None and cliMode == "true":
        for process in parameters:
            if value == process and selectedKey is None: # for getting key info from json
                config[key][value] = "false"
                logging.info(" - [%s] %s : false", key, value)
            elif value == process and key == selectedKey: # also with selected key for more control
                config[key][value] = "false"
                logging.info(" - [%s] %s : false", key, value)
            else:
                continue
