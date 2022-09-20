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

# This script generates Input - Output Descriptors

import json
import logging


def inputDescriptors(tablesToProduce: dict, tables: dict, readerConfigFileName = "aodReaderTempConfig.json"):
    """Generates Input Descriptors for Reading Tables from AO2D with json config file

    Args:
        tablesToProduce (dict): Tables are required in the output
        tables (dict): Definition of all the tables can be produced
        readerConfigFileName (str, optional): Output name of reader config. Defaults to "aodReaderTempConfig.json".
    """
    
    iTable = 0
    
    # Generate the aod-reader output descriptor json file
    readerConfig = {}
    readerConfig["InputDirector"] = {
        "debugmode": True,
        "InputDescriptors": []
        }
    
    for table in tablesToProduce.keys():
        readerConfig["InputDirector"]["InputDescriptors"].insert(iTable, tables[table])
        iTable += 1
    
    readerConfigFileName = "aodReaderTempConfig.json"
    with open(readerConfigFileName, "w") as readerConfigFile:
        json.dump(readerConfig, readerConfigFile, indent = 2)
    
    #logging.info("aodReaderTempConfig==========")
    #print(readerConfig)


def outputDescriptors(tablesToProduce: dict, tables: dict, writerConfigFileName = "aodWriterTempConfig.json"):
    """Generates Output Descriptors for Reading Tables from AO2D with json config file

    Args:
        tablesToProduce (dict): Tables are required in the output
        tables (dict): Definition of all the tables can be produced
        writerConfigFileName (str, optional): Output name of writer config. Defaults to "aodWriterTempConfig.json".
    """
    
    iTable = 0
    
    # Generate the aod-writer output descriptor json file
    writerConfig = {}
    writerConfig["OutputDirector"] = {
        "debugmode": True,
        "resfile": "reducedAod",
        "resfilemode": "RECREATE",
        "ntfmerge": 1,
        "OutputDescriptors": [],
        }
    
    for table in tablesToProduce.keys():
        writerConfig["OutputDirector"]["OutputDescriptors"].insert(iTable, tables[table])
        iTable += 1
    
    writerConfigFileName = "aodWriterTempConfig.json"
    with open(writerConfigFileName, "w") as writerConfigFile:
        json.dump(writerConfig, writerConfigFile, indent = 2)
    
    logging.info("aodWriterTempConfig==========")
    print(writerConfig)
