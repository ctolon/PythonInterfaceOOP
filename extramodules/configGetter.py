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

from .stringOperations import stringToList


def configGetter(configuredCommands: dict, selectedArg: str):
    """This function get parameters from configured argument in CLI

    Args:
        configuredCommands (dict): All configured arguments in CLI
        selectedArg (str): Selected argument as args

    Returns:
        list or str: Get parameters for selected argument
    """
    for keyCfg, valueCfg in configuredCommands.items():
        if valueCfg is not None: # Skipped None types, because can"t iterate in None type
            if keyCfg == selectedArg:
                if isinstance(valueCfg, str):
                    return stringToList(valueCfg)
                else:
                    return valueCfg