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

# Utility module

import json
import re
import logging


def listToString(s: list):
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


def convertListToStr(s: list) -> str:
    """Alternative List to string method

    Args:
        s (list): input as list

    Returns:
        str: returns string
    """
    
    # initialization of string to ""
    new = ""
    
    # traverse in the string
    for x in s:
        new += x
    
    # return string
    return new


def stringToList(string: str, charType: str) -> list:
    """
    stringToList provides converts strings to list with selected char.
    This function is written to save as list type instead of string

    Args:
        string (st): Input as String
        charType (str): split character as string

    Returns:
        list: merge string elements with selected char
    """
    possibleCharTypes = [",", ":", "/"] # you have to add new charType here if you need
    if charType not in possibleCharTypes:
        logging.error("%s is invalid argument for setSwitch", charType)
        raise ValueError("Invalid switchType. Expected one of: %s" % possibleCharTypes)
    
    li = list(string.split(charType))
    return li


def writeFile(openFile, writeFile):
    with open(openFile, "wb") as f:
        f.write(writeFile)
    f.close()


def loadJson(fileName: str):
    with open(fileName) as configFile:
        return json.load(configFile)


def dumpJson(updatedConfigFileName: str, config: dict) -> None:
    with open(updatedConfigFileName, "w") as outputFile:
        json.dump(config, outputFile, indent = 2)


def getIfStartedInDoubleQuotes(headerFileName: str) -> list:
    mylist = []
    with open(headerFileName) as f:
        stringIfSearch = [x for x in f if "if" in x]
        for i in stringIfSearch:
            mylist.extend(re.findall('"([^"]*)"', i))
        return mylist
    
    #f.close()
