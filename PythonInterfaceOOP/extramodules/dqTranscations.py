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

# All transcations managements in DQ Workflows

import logging
import sys
import os

from .dqExceptions import DependencyNotFoundError, NotInAlienvError, TasknameNotFoundInConfigFileError, TextListNotStartsWithAtError


def aodFileChecker(aod: str):
    """This function checks path for AO2D (both for .root and .txt)

    Args:
        aod (CLI argument): Provided arg for AO2D File or text file which includes AO2D list
    """
    
    if aod is not None:
        argProvidedAod = aod
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
        
        elif endsWithTxt and not textAodList:
            try:
                raise TextListNotStartsWithAtError(argProvidedAod)
            
            except TextListNotStartsWithAtError as e:
                logging.exception(e)
                logging.info("Example usage: --aod @%s", argProvidedAod)
                sys.exit()
        
        else:
            logging.error("AOD File Checker: FATAL ERROR")
            raise TypeError(f"{argProvidedAod} is wrong formatted file!!!")


def trackPropagationChecker(trackProp: bool, deps: list[str]):
    """This method automatically deletes the o2-analysis-trackextension(for run2) task from your workflow
    when you add the o2-analysis-track-propagation (for run3)
    task to your workflow. Two tasks are not compatible at the same time

    Args:
        trackProp (CLI argument): CLI argument to add the o2-analysis-track-propagation task
        deps (list[str]): Defined dependency list
    """
    
    if trackProp:
        deps.remove("o2-analysis-trackextension")
        logging.info("o2-analysis-trackextension is not valid dep for run 3, It will deleted from your workflow.")


def mainTaskChecker(config: dict[str, dict], taskNameInConfig: str):
    """1. Checks whether the workflow you want to run in your JSON file has a main task.
    
       2. Checks If you are running the O2Physics environment

    Args:
        config (dict[str, dict]): JSON config file
        taskNameInConfig (string): taskNameInConfig

    Raises:
        TasknameNotFoundInConfigFileError: if taskname not found in json config
        NotInAlienvError: if you are not in O2Physics environment
    """
    
    O2PHYSICS_ROOT = os.environ.get("O2PHYSICS_ROOT")
    
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


def jsonTypeChecker(cfgFileName: str):
    """Checks if the JSON config file assigned by the CLI is in the correct format

    Args:
        cfgFileName (str): CLI argument as your input json config file

    Raises:
        TypeError: If the file format is not correct
        FileNotFoundError: If file not found
    """
    
    isConfigJson = cfgFileName.endswith(".json")
    
    try:
        if not isConfigJson:
            raise TypeError(f"{cfgFileName} hasn't valid extension for json config file as input!")
        else:
            logging.info("%s is valid json config file", cfgFileName)
    except TypeError as e:
        logging.exception(e)
        sys.exit()


def depsChecker(config: dict[str, dict], deps: dict[str, dict], task: str):
    """This function written to check dependencies for process function

    Args:
        config (dict[str, dict]): Input as JSON config file
        deps (dict[str, dict]): Dependency dict
        task (str): Task name has dependencies

    Raises:
        DependencyNotFoundError: If dependency is not found
    """
    if task in config:
        for processFunc, dep in deps.items():
            if isinstance(dep, dict):
                for depTaskName, depProcessFunc in dep.items():
                    if depTaskName not in config or task not in config or processFunc not in config[task] or depProcessFunc not in config[depTaskName]:
                        continue
                    if config[task][processFunc] == "false":
                        continue
                    elif config[task][processFunc] == "true" and config[depTaskName][depProcessFunc] == "false":
                        raise DependencyNotFoundError(processFunc, depTaskName, depProcessFunc)
            else:
                raise TypeError(f"Dependency dict must be dict (right side) : {dep}")


def mandatoryArgChecker(config: dict[str, dict], taskname: str, processFunc: str):
    """The process function, which must be included in the workflow, if it is missing, the transaction function to include it

    Args:
        config (dict[str, dict]): Input as JSON config file
        taskname (str): task
        processFunc (str): cfg
    """
    
    if config[taskname][processFunc] != "true":
        logging.warning("You forget the configure an Mandatory -> [%s] %s must always true for this workflow. This will automaticaly converted true.", taskname, processFunc)
        logging.info(" - [%s] %s : true", taskname, processFunc)
    else:
        pass
