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

from extramodules.regexPatterns import RegexPatterns
from collections import OrderedDict
import logging
from urllib.request import Request, urlopen
import urllib
import ssl
import re
import sys


class ConfigMerger:
    
    def __init__(self, config1: dict, config2: dict):
        self.config1 = config1
        self.config2 = config2
        self.mergedConfig = self.mergeConfigs()
    
    def mergeConfigs(self, showWarnings = False) -> dict:
        """
        Merges two JSON configs, updating the first dict with values from the second dict. If a key is present in both dicts,
        the value from the second dict will be used. If a key is present only in the second dict, it will be added to the first
        dict.

        :return: The merged JSON config.
        """
        # Create a new ordered dictionary to hold the merged configuration
        mergedConfig = OrderedDict()
        
        # Add all keys from config1 to the merged configuration, preserving their order
        for key, value in self.config1.items():
            if isinstance(value, dict):
                # If the value is a dictionary, recursively merge it with the corresponding value from config2
                if key in self.config2 and isinstance(self.config2[key], dict):
                    mergedConfig[key] = ConfigMerger(value, self.config2[key]).mergedConfig
                else:
                    mergedConfig[key] = value
            else:
                # Otherwise, use the value from config1
                mergedConfig[key] = value
        
        # Add any keys from config2 that are not already in the merged configuration
        for key, value in self.config2.items():
            if key not in mergedConfig:
                mergedConfig[key] = value
            elif isinstance(value, dict) and isinstance(mergedConfig[key], dict):
                # If both values are dictionaries, recursively merge them
                mergedConfig[key] = ConfigMerger(mergedConfig[key], value).mergedConfig
            elif isinstance(value, dict) and not isinstance(mergedConfig[key], dict):
                # If the value in config1 is not a dictionary but the value in config2 is, then overwrite it with the value from config2
                mergedConfig[key] = value
            elif value != mergedConfig[key] and showWarnings is True:
                # If both values are not dictionaries and they differ, print a warning
                logging.warning(f"'{key}' has different values in the two configs: '{value}' vs '{mergedConfig[key]}'")
        
        # Return the merged configuration
        return mergedConfig


def defaultValueHandler(dataType, defaultValue):
    defaultValue = defaultValue.replace('"', '') # for json serializing
    if "float" in dataType:
        defaultValue = defaultValue.replace("f", "")
    if "chrono" in defaultValue:
        defaultValue = "epoch"
    return defaultValue


def replaceDictKeys(originalDict: dict, keyMapping: dict):
    """
    Replaces the keys in `keyMapping` dictionary with the corresponding keys in `originalDict`,
    if the value associated with the original key is not an empty string.

    Args:
        originalDict (dict): The dictionary to be used for key replacement.
        keyMapping (dict): A dictionary of keys to replace, where the keys represent the original keys
                            in `originalDict` and the values represent the new keys.

    Returns:
        dict: A new dictionary with replaced keys.
    
    Example:
    >>> originalDict = {'MultiplicityTableTaskIndexed': 'multiplicity-table',
                         'TrackSelectionTask': {'isRun3': 'false',
                                                'produceFBextendedTable': 'false',
                                                'compatibilityIU': 'false',
                                                'itsMatching': '0',
                                                'ptMin': '0.1f',
                                                'ptMax': '1e10f',
                                                'etaMin': '-0.8',
                                                'etaMax': '0.8'}}
    >>> keyMapping = {'MultiplicityTableTaskIndexed': 'multiplicity-table'}
    >>> replaceDictKeys(originalDict, keyMapping)
    {'multiplicity-table': {
        'isRun3': 'false',
        'produceFBextendedTable': 'false',
        'compatibilityIU': 'false',
        'itsMatching': '0',
        'ptMin': '0.1f',
        'ptMax': '1e10f',
        'etaMin': '-0.8',
        'etaMax': '0.8'}
        }
    """
    
    resultDict = keyMapping.copy()
    for key, value in keyMapping.items():
        if key in originalDict and originalDict[key] != '':
            resultDict[originalDict[key]] = value
            resultDict.pop(key)
    return resultDict


def listToDict(lst):
    """
    Converts a list of key-value pairs into a nested dictionary.

    Args:
    - lst: A list of tuples or lists representing key-value pairs. Each pair
      must have at least two elements, where the first (n-1) elements represent
      keys and the last element represents a value. Keys can be of any hashable
      type, and values can be of any type.

    Returns:
    - A nested dictionary where each key in a pair is a nested dictionary key,
      and the last element in the pair is the value associated with the last
      key in the nested hierarchy. If multiple pairs have the same keys, their
      values will be merged into a list under the same key.

    Example:
    >>> lst = [('a', 'b', 'c', 1), ('a', 'b', 'd', 2), ('a', 'e', 3)]
    >>> listToDict(lst)
    {'a': {'b': {'c': 1, 'd': 2}, 'e': 3}}

    """
    d = {}
    for item in lst:
        currDict = d
        for key in item[:-2]:
            currDict = currDict.setdefault(key, {})
        currDict[item[-2]] = item[-1]
    return d


def newAddedConfigsReport(dict1: dict, dict2: dict):
    """
    Generates a report of new configurations added to a task.

    Given two dictionaries `dict1` and `dict2`, where `dict1` represents the previous configuration
    of a task and `dict2` represents the current configuration, this function compares the two
    dictionaries and returns a list of tuples representing new configurations added to the task.

    Args:
        dict1 (dict): The previous configuration of the task.
        dict2 (dict): The current configuration of the task.

    Returns:
        List[Tuple[str, Optional[None]]]: A list of tuples representing new configurations added
        to the task. Each tuple contains the name of the configuration key and a value of `None`.
    """
    extra = []
    extraKeys = None
    extraParrentKeys = set(dict1.keys() - dict2.keys())
    if len(extraParrentKeys) > 0:
        for key, value in dict1.items():
            if key in extraParrentKeys and isinstance(value, dict):
                logging.info(f"New Task: [{key}]")
                for k,v in value.items():
                    logging.info(f"{k} : {v}")
                    
    for key, value in dict1.items():
        if key in dict2:
            subDict1 = dict1[key]
            subDict2 = dict2[key]
            if isinstance(subDict1, dict) and isinstance(subDict2, dict):
                extraKeys = set(subDict1.keys()) - set(subDict2.keys())
            if extraKeys and isinstance(value, dict):
                logging.info(f"New Added Configs to Task: [{key}]")
                for i in list(extraKeys):
                    configurable = i
                    defaultValue = dict1.get(key).get(i)
                    logging.info(f"{configurable} : {defaultValue}")
        else:
            extra.append((key, None))
    return extra


def transformTaskname(inputStr: str) -> str:
    """
    Transforms the input string according to the required rules:
    - First character converted to lower case
    - Subsequent uppercase characters converted to lower case and prefixed with a hyphen

    Args:
    - inputStr: A string to be transformed

    Returns:
    - The transformed string
    
    Example:
    >>> task = 'DQEventSelectionTask'
    >>> transformTaskname(task)
    d-q-event-selection-task
    """
    outputStr = inputStr[0].lower()
    for c in inputStr[1 :]:
        if c.isupper():
            outputStr += f"-{c.lower()}"
        else:
            outputStr += c
    return outputStr


def transformDictKeys(mergedDict: dict, adaptAnalysisDict: dict) -> dict:
    """
    Transforms the keys of a dictionary according to a set of rules, and returns a new dictionary with the transformed keys.

    Args:
    - mergedDict: A dictionary to be transformed.
    - adaptAnalysisDict: A dictionary containing keys to be excluded from the transformation process.

    Returns:
    - A new dictionary with the transformed keys.
    """
    transformedDict = {}
    for key, value in mergedDict.items():
        if isinstance(key, str) and isinstance(value, dict) and key not in adaptAnalysisDict.values():
            processedTaskname = transformTaskname(key)
            transformedDict[processedTaskname] = value
        else:
            transformedDict[key] = value
    return transformedDict


def rawConfigProcessor(rawData: list) -> dict:
    """
    Processes the raw configuration data extracted from a web page and returns two dictionaries.
    
    Args:
    - rawData (list of dicts): The raw configuration data to be processed. The expected format is as follows:
    
      [
        {
          "taskName": <str>,
          "configurables": [
            {
              "dataType": <str>,
              "variableName": <str>,
              "defaultValue": <str>,
              "configName": <str>,
              "description": <str>
            },
            ...
          ],
          "processFunc": [
            {
              "taskName": <str>,
              "processFunc": <str>,
              "processFuncDesc": <str>,
              "processFuncDefaultValue": <str>
            },
            ...
          ],
          "adaptAnalysisTask": [
            {
              "adaptAnalysisTaskName": <str>,
              "variables": [<str>, <str>, ...]
            },
            ...
          ]
        },
        ...
      ]
    
    Returns:
    - Dictionary maps configuration names to their default values.
    
    Example usage:
    ```
    >>> rawData = ... # some raw configuration data
    configDict = rawConfigProcessor(rawData)
    ```
    """
    
    buffer = []
    for index in rawData:
        taskName = index["taskName"]
        unprocessedConfigurables = index["configurables"]
        unprocessedProcessFuncs = index["processFunc"]
        for element in unprocessedConfigurables:
            buffer.append([taskName, element["configName"], element["defaultValue"]])
        for element in unprocessedProcessFuncs:
            buffer.append([element["taskName"], element["processFunc"], element["processFuncDefaultValue"]])
    return listToDict(buffer)


def rawAdaptiveTaskProcessor(rawData):
    """
    Processes the raw configuration data extracted from a web page and returns two dictionaries.
    
    Args:
    - rawData (list of dicts): The raw configuration data to be processed. The expected format is as follows:
    
      [
        {
          "taskName": <str>,
          "configurables": [
            {
              "dataType": <str>,
              "variableName": <str>,
              "defaultValue": <str>,
              "configName": <str>,
              "description": <str>
            },
            ...
          ],
          "processFunc": [
            {
              "taskName": <str>,
              "processFunc": <str>,
              "processFuncDesc": <str>,
              "processFuncDefaultValue": <str>
            },
            ...
          ],
          "adaptAnalysisTask": [
            {
              "adaptAnalysisTaskName": <str>,
              "variables": [<str>, <str>, ...]
            },
            ...
          ]
        },
        ...
      ]
    
    Returns:
    - Dictionary maps adaptive analysis task names to the names of the selected adaptive tasks.
    
    Example usage:
    ```
    >>> rawData = ... # some raw configuration data
    processedConfigurables = rawConfigProcessor(rawData)
    ```
    """
    
    buffer = {}
    for index in rawData:
        unprocessedAdaptAnalysisTasks = index["adaptAnalysisTask"]
        for element in unprocessedAdaptAnalysisTasks:
            if element["variables"] is not None and len(element["variables"]) > 1:
                newTaskName = (element["variables"])[1]
                if isinstance(newTaskName, str):
                    selectAdaptiveTaskName = ', '.join(re.findall(RegexPatterns.DOUBLE_QUOTES_PATTERN.value, newTaskName))
                    buffer[element["adaptAnalysisTaskName"]] = selectAdaptiveTaskName
    return buffer



def configurableSelectorWithRegex(file):
    """
    Extract configurable values from a file using regular expressions and return a list of dictionaries containing
    these values for each struct in the file.
    
    Args:
    - file (str): The file to extract configurable values from.
    
    Returns:
    - List[Dict]: A list of dictionaries, where each dictionary represents a struct and contains the following keys:
        - 'taskName': (str) The name of the struct.
        - 'configurables': (List[Dict]) A list of dictionaries containing the configurable values for this struct, where each
          dictionary has the following keys:
            - 'dataType': (str) The data type of the configurable.
            - 'variableName': (str) The name of the variable.
            - 'configName': (str) The name of the configurable.
            - 'defaultValue': (str) The default value of the configurable.
            - 'description': (str) A description of the configurable.
        - 'processFunc': (List[Dict]) A list of dictionaries containing the process function values for this struct, where
          each dictionary has the following keys:
            - 'taskName': (str) The name of the task.
            - 'processFunc': (str) The process function name.
            - 'processFuncDesc': (str) A description of the process function.
            - 'processFuncDefaultValue': (str) The default value of the process function.
        - 'adaptAnalysisTask': (List[Dict]) A list of dictionaries containing the adapt analysis task values for this struct,
          where each dictionary has the following keys:
            - 'adaptAnalysisTaskName': (str) The name of the adapt analysis task.
            - 'variables': (List[str]) A list of variable names used in the adapt analysis task.
    """
    
    configurableValues = []
    
    # All Regex Patterns we need
    CONFIGURABLE_PATTERN = RegexPatterns.CONFIGURABLE_PATTERN.value
    PROCESS_SWITCH_PATTERN = RegexPatterns.PROCESS_SWITCH_PATTERN.value
    ADAPT_ANALYSIS_TASK_PATTERN = RegexPatterns.ADAPT_ANALYSIS_TASK_PATTERN.value
    
    # split file with escape char
    lines = file.split("\n")
    
    for line in lines:
        line = line.strip()
        # Check if the line starts with "struct" to identify a new struct
        if line.startswith("struct"):
            structName = line.split()[1]
            # Create a new dictionary for the current struct
            configurableValues.append({
                "taskName": structName,
                "configurables": [],
                "processFunc": [],
                "adaptAnalysisTask": []
                })
        else:
            # Otherwise, try to extract the configurable values using the regex pattern
            configurableMatch = re.match(CONFIGURABLE_PATTERN, line)
            processSwitchMatch = re.match(PROCESS_SWITCH_PATTERN, line)
            adaptAnalysisTaskMatch = re.findall(ADAPT_ANALYSIS_TASK_PATTERN, line)
            
            if configurableMatch:
                # Extract the values from the regex match
                dataType = configurableMatch.group(1)
                variableName = configurableMatch.group(2)
                configName = configurableMatch.group(3)
                defaultValue = configurableMatch.group(4)
                defaultValue = defaultValueHandler(dataType, defaultValue)
                description = configurableMatch.group(7)
                logging.debug("==Configurable Match==")
                logging.debug(f"dataType: {dataType} | group 1")
                logging.debug(f"variableName: {variableName} | group 2")
                logging.debug(f"configName: {configName} | group 3")
                logging.debug(f"defaultValue: {defaultValue} | group 4")
                logging.debug(f"description: {description} | group 7")
                # Add the extracted values to the current struct's dictionary
                if "epoch" not in defaultValue:
                    configurableValues[-1]["configurables"].append({
                        "dataType": dataType,
                        "variableName": variableName,
                        "defaultValue": defaultValue,
                        "configName": configName,
                        "description": description
                        })
            elif processSwitchMatch:
                # Extract the values from the regex match
                taskName = processSwitchMatch.group(1)
                processFunc = processSwitchMatch.group(2)
                processFuncDesc = processSwitchMatch.group(3)
                processFuncDefaultValue = processSwitchMatch.group(4)
                logging.debug("==processSwitchMatch==")
                logging.debug(f"taskName: {taskName} | group 1")
                logging.debug(f"processFunc: {processFunc} | group 2")
                logging.debug(f"processFuncDesc: {processFuncDesc} | group 3")
                logging.debug(f"processFuncDefaultValue: {processFuncDefaultValue} | group 4")
                # Add the extracted values to the current struct's dictionary
                configurableValues[-1]["processFunc"].append({
                    "taskName": taskName,
                    "processFunc": processFunc,
                    "processFuncDesc": processFuncDesc,
                    "processFuncDefaultValue": processFuncDefaultValue,
                    })
            elif adaptAnalysisTaskMatch:
                variables = []
                # Extract the values from the regex match
                for match in adaptAnalysisTaskMatch:
                    adaptAnalysisTaskName = match[0]
                    cfg = match[1]
                    taskParamsMatch = match[2]
                    taskParams = [taskParamsMatch] if taskParamsMatch else []
                    variables.append((adaptAnalysisTaskName, cfg, taskParams))
                    variables = [item for t in variables for item in t]
                    logging.debug("==Adapt Analysis Tasks Match==")
                    logging.debug(f"adaptAnalysisTaskName: {adaptAnalysisTaskMatch} | match 0")
                    logging.debug(f"cfgc: {cfg} | match 1")
                    logging.debug(f"taskParamsMatch: {taskParamsMatch} | match 2")
                    configurableValues[-1]["adaptAnalysisTask"].append({
                        "adaptAnalysisTaskName": adaptAnalysisTaskName,
                        "variables": variables
                        })
    return configurableValues

def alignDicts(dict1: dict, dict2: dict, keepParentKeys=None) -> dict:
    newDict = OrderedDict()
    dict2Ordered = OrderedDict()
    for key, value in dict2.items():
        dict2Ordered[key] = value
    for key in dict2Ordered.keys():
        if key in dict1:
            newValue = {}
            for subKey in dict1[key]:
                if subKey in dict2Ordered[key]:
                    newValue[subKey] = dict2Ordered[key][subKey]
                else:
                    newValue[subKey] = dict1[key][subKey]
            for subKey in dict2Ordered[key]:
                if subKey not in newValue:
                    newValue[subKey] = dict2Ordered[key][subKey]
            newDict[key] = newValue
        elif key in dict2Ordered and (keepParentKeys is None or key in keepParentKeys):
            newDict[key] = dict2Ordered[key]
    return newDict

def removeUnmatchedSubkeys(d1: dict, d2: dict, keepParrentKeys = None, keepSubKeys = None):
    if keepParrentKeys is None:
        keepParrentKeys = set()
    if keepSubKeys is None:
        keepSubKeys = {}
    deprecatedTasks = []
    deprecatedConfigs = {}
    for key in list(d1.keys()):
        if key not in d2 and key not in keepParrentKeys:
            deprecatedTasks.append(key)
            del d1[key]
        else:
            subkeysToRemove = []
            if key in d2:
                if isinstance(d1[key], dict):
                    for subkey in list(d1[key].keys()):
                        if subkey not in d2[key] and subkey not in keepSubKeys:
                            subkeysToRemove.append(subkey)
                    for subkey in subkeysToRemove:
                        deprecatedConfigs[key] = subkey
                        del d1[key][subkey]
    
    if len(deprecatedTasks) > 0:
        logging.info(f"Removed Deprecated Tasks:")
        for task in deprecatedTasks:
            logging.info(f"[{task}]")
    elif len(deprecatedTasks) == 0:
        logging.info("No deprecated task found for this session.")
    
    if len(deprecatedConfigs) > 0:
        logging.info("Removed Deprecated Configurables/Process Functions:")
        for task, configurable in deprecatedConfigs.items():
            logging.info(f"[{task}] - {configurable}")
    elif len(deprecatedTasks) == 0:
        logging.info("No deprecated Configurables/Process Functions found for this session.")
    
    return d1


def latestConfigFileGenerator(input: dict) -> dict:
    """
    Downloads HTML content from the URLs provided in the input dictionary, extracts configurable parameters from the 
    HTML using a configurable selector function, processes and merges the extracted data into a single dictionary, 
    updates dictionary keys according to specific rules, and retrurns the resulting dictionary.

    Args:
    - input: A dictionary containing URLs as values and their corresponding analysis names as keys.

    Returns:
    - mergedConfig: Latest configs in O2
    """
    
    # Some buffer definitions
    configList = []
    mergedConfig = {}
    
    adaptList = []
    mergedAdapt = {}
    
    # header for github download
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
        }
    try:
        context = ssl._create_unverified_context() # prevent ssl problems
    except urllib.error.HTTPError as error:
        logging.error(error)
    
    for url in input.values():
        try:
            htmlContent = urlopen(Request(url, headers = headers), context = context).read().decode("utf-8")
        except urllib.error.HTTPError as error:
            logging.exception(error)
            sys.exit()
        
        # call configurable selector function
        rawConfigurables = configurableSelectorWithRegex(htmlContent)
        
        # process raw datas
        processedConfigurables = rawConfigProcessor(rawConfigurables)
        adaptAnalysisDict = rawAdaptiveTaskProcessor(rawConfigurables)
        
        # Add all processed data to list
        configList.append(processedConfigurables)
        adaptList.append(adaptAnalysisDict)
    
    # Merge all of the processed data into dict
    for taskConfig in configList:
        mergedConfig.update(taskConfig)
    
    for adapt in adaptList:
        mergedAdapt.update(adapt)
    
    # apply transformations
    mergedConfig = replaceDictKeys(mergedAdapt, mergedConfig)
    mergedConfig = transformDictKeys(mergedConfig, mergedAdapt)
    return mergedConfig
