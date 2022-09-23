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

# This script includes some exceptions for DQ Workflows


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
        return f"Invalid Format for json config file! Your JSON config input: {self.configjson} After the script, you must define your json configuration file"


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


class EventFilterSelectionsError(Exception):
    
    """Exception raised if Filter Selections and analysis cuts not in same order and same number"""
    
    def __init__(self):
        super().__init__()
    
    def __str__(self):
        return f"Event Filter selections and analysis cuts not in same order and same number"


class MandatoryArgNotFoundError(Exception):
    
    """Exception raised for if mandatory arg not found

    Attributes:
        arg: mandatory argument
    """
    
    def __init__(self, arg):
        self.arg = arg
    
    def __str__(self):
        return f"Mandatory args not found: {self.arg}"


class TextListNotStartsWithAtError(Exception):
    
    """Exception raised for if mandatory arg not found

    Attributes:
        arg: mandatory argument
    """
    
    def __init__(self, arg):
        self.arg = arg
    
    def __str__(self):
        return f"{self.arg} AO2D text lists have to start with @ symbol"


class DependencyNotFoundError(Exception):
    
    """Exception raised for if mandatory arg not found

    Attributes:
        arg: mandatory argument
    """
    
    def __init__(self, checkedDep, task, cfg):
        self.checkedDep = checkedDep
        self.task = task
        self.cfg = cfg
    
    def __str__(self):
        return f"For configuring {self.checkedDep}, you have to specify [{self.task}] {self.cfg} function as true"
