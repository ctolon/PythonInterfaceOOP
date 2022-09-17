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

# This script includes some exceptions and transaction managements for DQ workflows

import sys
import logging
import os


class TasknameNotFoundInConfigFileError(Exception):
    
    """Exception raised if taskname not found in json config file.

    Attributes:
        taskName: input main task name
    """
    
    def __init__(self, taskName):
        self.taskName = taskName
        super().__init__()
    
    def __str__(self):
        return f"The JSON config does not include {self.taskName} task"


class CfgInvalidFormatError(Exception):
    
    """Exception raised for Invalid format json file

    Attributes:
        config: input provided config json file
    """
    
    def __init__(self, configjson):
        self.configjson = configjson
        super().__init__()
    
    def __str__(self):
        return f"Invalid Format for json config file! Your JSON config input: {self.configjson} After the script, you must define your json configuration file \
            The command line should look like this:"


class NotInAlienvError(Exception):
    
    """Exception raised for O2Physics Alienv Loading
    
    Attributes:
        message: error message for forgetting loading alienv
    """
    
    def __init__(self, message = "You must load O2Physics with alienv"):
        self.message = message
        super().__init__(self.message)


class ForgettedArgsError(Exception):
    
    """Exception raised for forgetted args errors in parser args.

    Attributes:
        forgettedArgs: arguments whose configuration is forgotten
    """
    
    def __init__(self, forgettedArgs):
        self.forgettedArgs = forgettedArgs
        super().__init__()
    
    def __str__(self):
        return f"Your forget assign a value to for this parameters: {self.forgettedArgs}"


class CentFilterError(Exception):
    
    """Exception raised if you provide centrality process function for pp system in tableMaker/tableMakerMC"""
    
    def __init__(self):
        super().__init__()
    
    def __str__(self):
        return f"Collision System pp can't be include related task and process function about Centrality. misconfigure for process function in tableMaker/tableMakerMC!"


# Classes for Filter PP Transacation Management
class BarrelSelsNotInBarrelTrackCutsError(Exception):
    
    """Exception raised for if filterPP selection is not valid for BarrelSels

    Attributes:
        barrelSels: In filterPP task, barrel selections for event filtering
        barrelTrackCuts: In DQBarrelTrackSelection, Barrel track cuts
    """
    
    def __init__(self, barrelSels, barrelTrackCuts):
        self.barrelSels = barrelSels
        self.barrelTrackCuts = barrelTrackCuts
        super().__init__()
    
    def __str__(self):
        return f"--cfgBarrelSels <value>: {self.barrelSels} not in --cfgBarrelTrackCuts {self.barrelTrackCuts}"


class MuonSelsNotInMuonsCutsError(Exception):
    
    """Exception raised for if filterPP selection is not valid for MuonSels

    Attributes:
        muonSels: In filterPP task, muon selections for event filtering
        muonsCuts: in DQMuonsSelection, additional muon Cuts
    """
    
    def __init__(self, muonSels, muonsCuts):
        self.muonSels = muonSels
        self.muonsCuts = muonsCuts
        super().__init__()
    
    def __str__(self):
        return (f"--cfgMuonSels <value>: {self.muonSels} not in --cfgBarrelTrackCuts {self.muonsCuts}")


class BarrelTrackCutsNotInBarrelSelsError(Exception):
    
    """Exception raised for if filterPP selection is not valid for BarrelSels

    Attributes:
        barrelSels: In filterPP task, barrel selections for event filtering
        barrelTrackCuts: In DQBarrelTrackSelection, Barrel track cuts
    """
    
    def __init__(self, barrelSels, barrelTrackCuts):
        self.barrelSels = barrelSels
        self.barrelTrackCuts = barrelTrackCuts
        super().__init__()
    
    def __str__(self):
        return f"--cfgBarrelTrackCuts <value>: {self.barrelTrackCuts} not in --cfgBarrelSels {self.barrelSels}"


class MuonsCutsNotInMuonSelsError(Exception):
    
    """Exception raised for if filterPP selection is not valid for MuonSels

    Attributes:
        muonSels: In filterPP task, muon selections for event filtering
        muonsCuts: in DQMuonsSelection, additional muon Cuts
    """
    
    def __init__(self, muonSels, muonsCuts):
        self.muonSels = muonSels
        self.muonsCuts = muonsCuts
        super().__init__()
    
    def __str__(self):
        return f"--cfgMuonsCuts <value>: {self.muonsCuts} not in --cfgMuonSels {self.muonSels}"


class MandatoryArgNotFoundError(Exception):
    
    """Exception raised for if mandatory arg not found

    Attributes:
        arg: mandatory argument
    """
    
    def __init__(self, arg):
        self.arg = arg
    
    def __str__(self):
        return f"Mandatory args not found: {self.arg}"


def listToString(s = list):
    """
    ListToString provides converts lists to strings with commas.
    This function is written to save as string type instead of list


    Args:
        s (list): Input as List

    Returns:
        string: Comma seperated string
    """
    if len(s) > 1:
        # initialize an empty string
        str1 = ","
        
        # return string
        return str1.join(s)
    else:
        str1 = " "
        
        return str1.join(s)


def stringToList(string = str):
    """
    stringToList provides converts strings to list with commas.
    This function is written to save as list type instead of string

    Args:
        string (string): Input as String

    Returns:
        list: merge string elements with comma 
    """
    li = list(string.split(","))
    return li


# AOD File Checker
def aodFileChecker(aod):
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
        else:
            try:
                open(argProvidedAod, "r")
                logging.info("%s has valid File Format and Path, File Found", argProvidedAod)
            
            except FileNotFoundError:
                logging.exception("%s Wrong formatted File, check your file extension!", argProvidedAod)
                sys.exit()


def trackPropTransaction(trackProp = bool, deps = list):
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


def mainTaskChecker(config, taskNameInConfig = str):
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


def jsonTypeChecker(cfgFileName):
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
def forgettedArgsChecker(configuredCommands):
    """Checks for any arguments forgot to assign a value which you provided to command line
    
    E.x. --process --syst PbPb (It will raise)

    Args:
        configuredCommands (dict): Dictionary of arguments entered from the CLI

    Raises:
        ForgettedArgsError: if there is an argument you forgot to configure
    """
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


def centTranscation(config, process, syst, centSearch):
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


def filterSelsTranscation(argBarrelSels, argMuonSels, argBarrelTrackCuts, argMuonsCuts, configuredCommands):
    """It checks whether the event filter selections and analysis cuts in the
    Filter PP task are in the same number and order

    Args:
        argBarrelSels (CLI Argument): Event filter argument for barrel
        argMuonSels (CLI Argument): Event filter argument for muons
        argBarrelTrackCuts (CLI Argument): Analysis cut argument for barrel
        argMuonsCuts (CLI Argument): Analysis cuts argument for muons
        configuredCommands (dict): Dictionary of all arguments provided by the CLI

    Raises:
        MandatoryArgNotFoundError: If the required argument is not found
        MuonSelsNotInMuonsCutsError: If analysis cuts and event filter arguments for muons  do not match in numbers and orders
        MuonsCutsNotInMuonSelsError: When analysis cuts and event filter arguments for muons  do not match in numbers and orders
        MandatoryArgNotFoundError: If forgetting to configure analysis cuts while giving arguments for Event Filter
        BarrelSelsNotInBarrelTrackCutsError: If analysis cuts and event filter arguments for barrel do not match in numbers and orders
        BarrelTrackCutsNotInBarrelSelsError: Analysis cuts and event filter arguments for barrel do not match in numbers and orders
    """
    
    muonCutList = []
    barrelTrackCutList = []
    barrelSelsList = []
    muonSelsList = []
    
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


# We don't need this. config[key][value] = args.<arg> has less verbosity
def singleConfigurableSet(config = dict, key = str, value = str, arg = str):
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
def multiConfigurableSet(config = dict, key = str, value = str, arg = list, onlySelect = bool):
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


# This scripts provides remove pycache files recursively
class PycacheRemover(object):
    
    """This method creates two python commands in order to remove pycache files recursively

    Args:
        object (str): Creates two python command for deleting pycache files
    """
    
    def __init__(self):
        
        super(PycacheRemover, self).__init__()
        
        commandOne = ("python3 -Bc " + '"' + "import pathlib;" + "[p.unlink() for p in pathlib.Path('.').rglob('*.py[co]')]" + '"')
        commandTwo = ("python3 -Bc" + '"' + "import pathlib;" + "[p.rmdir() for p in pathlib.Path('.').rglob('__pycache__')]" + '"')
        
        os.system(commandOne)
        os.system(commandTwo)
        
        # print(commandOne)
        # print(commandTwo)


def runPycacheRemover():
    """This function run two python command and it provides recursively deletes pycache files

    Raises:
        BaseException: If not path exists in OS
    """
    
    pycacheRemover = PycacheRemover()
    
    try:
        parentPath = os.getcwd()
        print(parentPath)
        if os.path.exists(parentPath) and os.path.isfile(parentPath + "/pycacheRemover.py"):
            logging.info("Inserting inside for pycache remove: %s", os.getcwd())
            pycacheRemover.__init__()
            logging.info("pycaches removed succesfully")
        
        elif not os.path.exists(parentPath):
            raise BaseException
    
    # Caching the exception
    except BaseException:
        logging.exception("Something wrong with specified\
            directory. Exception- %s", sys.exc_info(),)
        sys.exit()
