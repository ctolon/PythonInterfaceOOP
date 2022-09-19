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
from .stringOperations import listToString


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


# TODO: refactor it it should be work in also loop. Only works for tableReader and dqEfficiency
# when key have no process Dummy function, this method will crashes.
def processDummySet(config: dict):
    
    for k, v in config.items(): # loop over number of keys
        if isinstance(v, dict): # iterate only possible items in dict keys
            for v, v2 in v.items():
                if (not v.endswith("Dummy")) and (v.startswith("process")):
                    if config[k][v] == "true":
                        config[k]["processDummy"] = "false"
                        print(k, "dummy converted false")
                        break
                    else:
                        config[k]["processDummy"] = "true"
                        print(k, "dummy converted true")
