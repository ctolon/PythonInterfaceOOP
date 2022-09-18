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

import logging
from .stringOperations import listToString


def dispArgs(configuredCommands: dict):
    """Display all configured commands you provided in CLI

    Args:
        configuredCommands (dict): configured commands in CLI
    """
    logging.info("Args provided configurations List")
    print("====================================================================================================================")
    for key, value in configuredCommands.items():
        if value is not None:
            if isinstance(value, list):
                listToString(value)
            logging.info("--%s : %s ", key, value)
