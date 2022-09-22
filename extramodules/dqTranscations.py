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

from .dqExceptions import CentFilterError, CfgInvalidFormatError, DependencyNotFoundError, ForgettedArgsError, MandatoryArgNotFoundError, NotInAlienvError, EventFilterSelectionsError, TasknameNotFoundInConfigFileError, TextListNotStartsWithAtError


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
            try:
                open(argProvidedAod, "r")
                logging.info("%s has valid File Format and Path, File Found", argProvidedAod)
            
            except FileNotFoundError:
                logging.exception("%s Wrong formatted File, check your file extension!", argProvidedAod)
                sys.exit()


def trackPropagationChecker(trackProp: bool, deps: list):
    """This method automatically deletes the o2-analysis-trackextension(for run2) task from your workflow
    when you add the o2-analysis-track-propagation (for run3)
    task to your workflow. Two tasks are not compatible at the same time

    Args:
        trackProp (CLI argument): CLI argument to add the o2-analysis-track-propagation task
        deps (list): Defined dependency list
    """
    
    if trackProp:
        deps.remove("o2-analysis-trackextension")
        logging.info("o2-analysis-trackextension is not valid dep for run 3, It will deleted from your workflow.")


def mainTaskChecker(config: dict, taskNameInConfig: str):
    """1. Checks whether the workflow you want to run in your JSON file has a main task.
    
       2. Checks If you are running the O2Physics environment

    Args:
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
        #sys.exit()


def jsonTypeChecker(cfgFileName: str):
    """Checks if the JSON config file assigned by the CLI is in the correct format

    Args:
        cfgFileName (json): CLI argument as your input json config file

    Raises:
        CfgInvalidFormatError: If the file format is not correct
    """
    
    isConfigJson = cfgFileName.endswith(".json")
    
    try:
        if not isConfigJson:
            raise CfgInvalidFormatError(cfgFileName)
        else:
            logging.info("%s is valid json config file", cfgFileName)
    
    except CfgInvalidFormatError as e:
        logging.exception(e)
        sys.exit()


# Transcation management for forgettining assign a value to parameters
def forgettedArgsChecker(allArgs: dict):
    """Checks for any arguments forgot to assign a value which you provided to command line
    
    E.x. --process --syst PbPb (It will raise)

    Args:
        allArgs (dict): Dictionary of arguments entered from the CLI

    Raises:
        ForgettedArgsError: if there is an argument you forgot to configure
    """
    forgetParams = []
    for key, value in allArgs.items():
        if value is not None:
            if (isinstance(value, str) or isinstance(value, list)) and len(value) == 0:
                forgetParams.append(key)
    try:
        if len(forgetParams) > 0:
            raise ForgettedArgsError(forgetParams)
    except ForgettedArgsError as e:
        logging.exception(e)
        sys.exit()


def centralityChecker(config: dict, process, syst, centSearch):
    """If you assign a centrality-related process function for the pp collision
    system while trying to skim the data, an error will return.

    Args:
        process (CLI argument): process function in tableMaker/tableMakerMC
        centSearch (list): List counting Cent sub strings in process function
        syst (CLI argument): collision system

    Raises:
        CentFilterError: If you assign a centrality-related process function
    """
    if (process and len(centSearch) != 0 and (syst == "pp" or (syst is None and config["event-selection-task"]["syst"] == "pp"))):
        logging.warning(
            "JSON file does not include configs for centrality-table task, It's for DATA. Centrality will removed because you select pp collision system."
            )
        if process is not None:
            processCentralityMatch = [s for s in process if "Cent" in s]
            try:
                if len(processCentralityMatch) > 0:
                    raise CentFilterError
                else:
                    pass
            except CentFilterError as e:
                logging.exception(e)
                sys.exit()


def filterSelsChecker(argBarrelSels: list, argMuonSels: list, argBarrelTrackCuts: list, argMuonsCuts: list, allArgs: dict):
    """It checks whether the event filter selections and analysis cuts in the
    Filter PP task are in the same number and order

    Args:
        argBarrelSels (CLI Argument): Event filter argument for barrel
        argMuonSels (CLI Argument): Event filter argument for muons
        argBarrelTrackCuts (CLI Argument): Analysis cut argument for barrel
        argMuonsCuts (CLI Argument): Analysis cuts argument for muons
        allArgs (dict): Dictionary of all arguments provided by the CLI

    Raises:
        MandatoryArgNotFoundError: If the required argument is not found
        EventFilterSelectionsError : If Filter Selections and analysis cuts not in same number and order
    """
    
    argMuonSelsClean = []
    argBarrelSelsClean = []
    
    if argMuonSels:
        try:
            if argMuonsCuts is None:
                raise MandatoryArgNotFoundError(argMuonsCuts)
            else:
                pass
        
        except MandatoryArgNotFoundError as e:
            logging.exception(e)
            logging.error("For configure to cfgMuonSels (For DQ Filter PP Task), you must also configure cfgMuonsCuts!!!")
            sys.exit()
        
        # remove string values after :
        for i in argMuonSels:
            i = i[0 : i.index(":")]
            argMuonSelsClean.append(i)
        
        try:
            if argMuonSelsClean == argMuonsCuts:
                pass
            else:
                raise EventFilterSelectionsError
        
        except EventFilterSelectionsError as e:
            logging.exception(e)
            logging.info(
                "[INFO] For fixing this issue, you should have the same number of cuts (and in the same order) provided to the cfgMuonsCuts from dq-selection as those provided to the cfgMuonSels in the DQFilterPPTask."
                )
            logging.info(
                "For example, if cfgMuonCuts is muonLowPt,muonHighPt,muonLowPt then the cfgMuonSels has to be something like: muonLowPt::1,muonHighPt::1,muonLowPt:pairNoCut:1"
                )
            sys.exit()
        
        logging.info("Event filter configuration is valid for muons")
    
    if argBarrelSels:
        
        try:
            if argBarrelTrackCuts is None:
                raise MandatoryArgNotFoundError(argBarrelTrackCuts)
            else:
                pass
        
        except MandatoryArgNotFoundError as e:
            logging.exception(e)
            logging.error("For configure to cfgBarrelSels (For DQ Filter PP Task), you must also configure cfgBarrelTrackCuts!!!")
            sys.exit()
        
        # remove string values after :
        for i in argBarrelSels:
            i = i[0 : i.index(":")]
            argBarrelSelsClean.append(i)
        
        try:
            if argBarrelSelsClean == argBarrelTrackCuts:
                pass
            else:
                raise EventFilterSelectionsError
        
        except EventFilterSelectionsError as e:
            logging.exception(e)
            logging.info(
                "For fixing this issue, you should have the same number of cuts (and in the same order) provided to the cfgBarrelTrackCuts from dq-selection as those provided to the cfgBarrelSels in the DQFilterPPTask."
                )
            logging.info(
                "For example, if cfgBarrelTrackCuts is jpsiO2MCdebugCuts,jpsiO2MCdebugCuts2,jpsiO2MCdebugCuts then the cfgBarrelSels has to be something like: jpsiO2MCdebugCuts::1,jpsiO2MCdebugCuts2::1,jpsiO2MCdebugCuts:pairNoCut:1"
                )
            sys.exit()
        
        logging.info("Event filter configuration is valid for barrel")


def depsChecker(config: dict, deps: dict, key: str):
    """This function written to check dependencies for process function

    Args:
        config (dict): Input as JSON config file
        deps (dict): Dependency dict
        key (str): Task name has dependencies

    Raises:
        DependencyNotFoundError: If dependency is not found
    """
    for processFunc, dep in deps.items():
        if isinstance(dep, dict):
            for depTaskName, depProcessFunc in dep.items():
                if config[key][processFunc] == "false":
                    continue
                elif config[key][processFunc] == "true" and config[depTaskName][depProcessFunc] == "false":
                    raise DependencyNotFoundError(processFunc, depTaskName, depProcessFunc)
        else:
            raise TypeError("Dependency dict must be dict (right side) :", dep)


def oneToMultiDepsChecker(argument: list, mandatoryArg: str, targetCfg: dict, argName: str):
    """To configure many arguments in a task to check if a value needs to be defined in another argument

    Args:
        argument (list): Have an dependency CLI argument parameters
        mandatoryArg (str): Needed argument name from another CLI argument
        targetCfg (_type_): mandatoryArg targetCfg
        argName (str): argument name of have an dependency argument 

    Raises:
        MandatoryArgNotFoundError: _description_
    """
    
    try:
        if argument is not None and mandatoryArg not in targetCfg:
            raise MandatoryArgNotFoundError(mandatoryArg)
    
    except MandatoryArgNotFoundError as e:
        logging.exception(e)
        logging.info("For configuring %s you have to specify %s value in --%s argument", argument, mandatoryArg, argName)
        sys.exit()


def mandatoryArgChecker(config: dict, key: str, value: str, selectedKey: str, selectedValue: str):
    """The process function, which must be included in the workflow, if it is missing, the transaction function to include it

    Args:
        config (dict): Input as JSON config file
        key (str): key
        value (str): value
        selectedKey (str): Taskname for mandatory process function
        selectedValue (str): Mandatory process function
    """
    
    if config[key][value] == "false" and key == selectedKey and value == selectedValue:
        logging.warning(
            "You forget the configure an Mandatory -> [%s] %s must always true for this workflow. This will automaticaly converted true.",
            key, value
            )
        logging.info(" - [%s] %s : true", key, value)
    else:
        pass
