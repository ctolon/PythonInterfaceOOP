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


# We don't need this. config[key][value] = args.<arg> has less verbosity
def singleConfigurableSet(config: dict, key: str, value: str, arg: str):
    """
    singleConfigurableSet method allows to assign value
    to single configurable value arguments in JSON with overriding.
    This method is used for single value arguments
    as JSONs will be assigned only by overriding for single value arguments.


    Args:
        config (dict): Input as JSON config file
        key (string): Sub key from upper key in provided JSON config file
        value (string): Value from key in provided JSON config file (sub-level)
        arg (any): Argument from parserargs or manual for some situations ("-1" or "true" or "false" etc.)
        
        
    Assignment:
        string: Assigned as a direct string

    """
    
    config[key][value] = arg
    #logging.debug(" - [%s] %s : %s", key, value, args.v0Rmax)


# For multiple configurables in JSON, always use this method for less verbosity
def multiConfigurableSet(config: dict, key: str, value: str, arg: list, onlySelect):
    """
    multiConfigurableSet method allows to assign values
    for multiple configurable value arguments in JSON with/without overriding
    depending on interface mode. The onlySelect parameter decides for
    interface mode.if the argument contains more than one value, it is saved as list type by default 
    and this method converts them to comma separated string, otherwise assigns them as string value directly


    Args:
        config (dict): Input as JSON config file
        key (string): Sub key from upper key in provided config JSON config file
        value (string): Value from key in provided JSON config file (sub-level)
        arg (any): Argument from parserargs
        onlySelect (boolean): Input as args.onlySelect for selecting interface mode.
        true for Overrider Mode and false for Additional mode
        
        
    Assignment :
        string or comma seperated string: If the argument is of list type, 
        it assign as a comma separated string,
        otherwise it assign directly as a string.

    """
    
    if isinstance(arg, list):
        arg = listToString(arg)
    if onlySelect == "false":
        actualConfig = config[key][value]
        arg = actualConfig + "," + arg
    config[key][value] = arg


def processDummySet(config: dict, dummyHasTasks = None):
    """Dummy Automizer for dqEfficiency and tableReader

    Args:
        config (dict): json config dict
        dummyHasTasks (list, optional): Define dummy task list, if you don't define it, all task will checked
    """
    processFuncFound = ''
    
    for k, v in config.items(): # loop over number of keys
        if isinstance(v, dict): # iterate only possible items in dict keys
            for v, v2 in v.items():
                if dummyHasTasks is None:
                    if (not v.endswith("Dummy")) and (v.startswith("process")):
                        if config[k][v] == "true":
                            config[k]["processDummy"] = "false"
                            logging.debug(" - [%s] processDummy : false", k)
                            break
                        else:
                            config[k]["processDummy"] = "true"
                            logging.debug(" - [%s] processDummy : true", k)
                if dummyHasTasks is not None:
                    for task in dummyHasTasks:
                        if processFuncFound == k:
                            continue
                        if task not in dummyHasTasks:
                            continue
                        if (not v.endswith("Dummy")) and (v.startswith("process")) and (task == k):
                            if config[k][v] == "true":
                                config[k]["processDummy"] = "false"
                                logging.debug(" - [%s] processDummy : false", k)
                                processFuncFound = k # save the task and not check in iteration
                                break
                            else:
                                config[k]["processDummy"] = "true"
                                logging.debug(" - [%s] processDummy : true", k)


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
        config (dict): json config file
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


def CONFIG_SET(config, key, value, allArgs, onlySelect):
    """This function provides directly set to argument parameter, if argument naming and json key naming equals

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
        key (str): key in JSON config
        value (str): value in JSON Config
        allArgs (dict): Configured args in CLI
        onlySelect (bool): cliMode
        argument (str): Selected argument from configured args
        parameters (list): All available parameters for argument
        switchType (str): Switch type usage in string --> "SWITCH_ON/SWITCHOFF"
        kFlag (bool): This parameter for only one PROCESS_SWITCH activation. If true, only one process function will be true, the others will be converted false
    """
    
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
                
                if (onlySelect == "true"): # TODO bir indent TAB kadar sag kaydırılabilir test edilmesi lazım.
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
