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

from enum import Enum


class RegexPatterns(Enum):
    
    """
    Enum class for defining regex patterns used to extract information from input strings.
    
    Attributes:
        CONFIGURABLE_PATTERN (str): Regex Pattern for selectiong Configurable function features.
        PROCESS_SWITCH_PATTERN (str): Regex Pattern for selecting PROCESS_SWITCH function features
        ADAPT_ANALYSIS_TASK_PATTERN (str): Regex Pattern for selecting struct names.
    """
    CONFIGURABLE_PATTERN = r'^\s*Configurable<(\S+)>\s+(\S+)\s*\{\s*"([^"]+)"\s*,\s*((-?\d+)|(\S+))\s*,\s*((\{\s*"([^"]+)"\s*\})|("([^"]+)"))\s*\}\s*;?\s*(\/\/.*)?(\s*\/\*.*\*\/\s*)?$'
    """
    Regular expression pattern used to capture information from strings containing Configurable objects.
    
    Breakdown:
    - ^\s*Configurable<(\S+)>\s+(\S+)\s*\{\s*"([^"]+)"\s*,\s*((-?\d+)|(\S+))\s*,\s*((\{\s*"([^"]+)"\s*\})|("([^"]+)"))\s*\}\s*;?\s*(\/\/.*)?(\s*\/\*.*\*\/\s*)?$ - 
        Matches the start of the string, the Configurable object name and type (e.g. "MyConfig" and "Configurable<MyConfig>"), 
        allowing for whitespace before and after. Also matches the curly braces containing the Configurable parameters, 
        which consist of:
        - \s*"([^"]+)"\s* - Matches the Configurable parameter name, enclosed in double quotes and allowing for whitespace.
        - ,\s*((-?\d+)|(\S+))\s*, - Matches the parameter value, which can be a number or a string, 
        allowing for negative numbers and non-whitespace characters (e.g. boolean or variable names).
        - \s*((\{\s*"([^"]+)"\s*\})|("([^"]+)"))\s* - Matches the parameter description, which can be enclosed in 
        curly braces (if it's a dictionary) or double quotes (if it's a string), and allows for whitespace.
        - ;?\s*(\/\/.*)? - Matches an optional semicolon and an optional single-line comment at the end of the line.
        - (\s*\/\*.*\*\/\s*)? - Matches an optional multi-line comment at the end of the line.
    
    Example usage:
        >>> import re, RegexPatterns
        >>> pattern = RegexPatterns.CONFIGURABLE_PATTERN.value
        >>> input_string = 'Configurable<std::string> fConfigEventCuts{"cfgEventCuts", "eventStandard", "Event selection"};'
        >>> match = re.match(pattern, input_string)
        
        >>> objectName = match.group(2)
        >>> objectType = match.group(1)
        >>> paramName = match.group(3)
        >>> paramValue = match.group(4)
        >>> paramDescription = match.group(7)
        
        The regex will match:
        - Match 1: "fConfigEventCuts"
        - Match 2: "std::string"
        - Match 3: "cfgEventCuts"
        - Match 4: "eventStandard"
        - Match 7: "Event selection"
        
    The extracted information can then be used for further processing or analysis.
    """
    
    PROCESS_SWITCH_PATTERN = r'^\s*PROCESS_SWITCH\((\S+),\s*(\S+),\s*"([^"]*)",\s*(\S+)\);'
    """
    Regular expression pattern used to capture information from strings containing PROCESS_SWITCH macros.
    
    Breakdown:
    
    - ^\s*PROCESS_SWITCH\((\S+),\s*(\S+),\s*"([^"]*)",\s*(\S+)\); - Matches the PROCESS_SWITCH macro call, allowing for whitespace:
        - (\S+) - Matches the name of the process switch.
        - (\S+) - Matches the boolean value (either "true" or "false") used to enable/disable the switch.
        - "([^"]*)" - Matches the optional description of the process switch, enclosed in double quotes.
        - (\S+) - Matches the optional integer priority value.
    
     Example usage:
        >>> import re, RegexPatterns
        >>> pattern = RegexPatterns.PROCESS_SWITCH_PATTERN.value
        >>> input_string = 'PROCESS_SWITCH(AnalysisDileptonHadron, processSkimmed, "Run dilepton-hadron pairing, using skimmed data", false);'
        >>> match = re.match(pattern, input_string)
    
        >>> taskname = match.group(1)
        >>> processFunctionName = match.group(2)
        >>> description = match.group(3)
        >>> value = match.group(4)
    
        The regex will match:
        - Match 1: "AnalysisDileptonHadron"
        - Match 2: "processSkimmed"
        - Match 3: "Run dilepton-hadron pairing, using skimmed data"
        - Match 4: "false"

    The extracted information can then be used for further processing or analysis.
    """
    
    ADAPT_ANALYSIS_TASK_PATTERN = r'adaptAnalysisTask<([^>]+)>\(([^)]+)\)(?:,\s*(\w+\{[^}]+\}))?'
    """
    Regular expression pattern used to capture information from strings containing adaptAnalysisTask calls.
    
    Breakdown:
    
    - adaptAnalysisTask<  : matches the literal string "adaptAnalysisTask<"
    - ([^>]+)            : matches one or more characters that are not the '>' symbol, and captures them as group 1 (TASK_NAME)
    - >\(                : matches the '>' symbol followed by an opening parenthesis
    - ([^)]+)            : matches one or more characters that are not the ')' symbol, and captures them as group 2 (ARGS)
    - \)                 : matches a closing parenthesis
    - (?:,\s*            : matches a comma followed by zero or more whitespace characters, without capturing the match
    - (\w+\{[^}]+\})?    : optionally matches a string of one or more word characters (\w+), followed by one or more non-'}' characters enclosed in curly braces, and captures it as group 3 (TASK_PARAMS)
    
    Example usage:
    
    >>> import re
    >>> text = "adaptAnalysisTask<MultiplicityTableTaskIndexed>(cfgc, TaskName{\"multiplicity-table\"})"
    >>> match = re.search(ADAPT_ANALYSIS_TASK_PATTERN, text)
    >>> if match:
    >>>     task_name = match.group(1)
    >>>     args = match.group(2)
    >>>     task_params_match = match.group(3)
    >>>     task_params = [task_params_match] if task_params_match else []
    >>>     print(task_name, args, task_params)
    'MultiplicityTableTaskIndexed' 'cfgc, TaskName{"multiplicity-table"}' []
    """
    
    DOUBLE_QUOTES_PATTERN = r'\"([^\"]+)\"'
    """
    This regex pattern matches any substring enclosed in double quotes. The pattern is as follows:
    
    Breakdown:

    - \"      - matches a double quote character
    - (       - start of a capturing group
    - [^\"]+  - matches one or more characters that are not a double quote
    - )       - end of the capturing group
    - \"      - matches another double quote character
    
    Example usage:

    >>> import re
    >>> text = 'Hello "world"! This is a "test" string.'
    >>> matches = re.findall(DOUBLE_QUOTES_PATTERN, text)
    ['world', 'test']
    """
