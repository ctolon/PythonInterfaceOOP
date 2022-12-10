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

import argparse


class DplAodReader(object):
    
    """
    Class for Interface -> internal-dpl-aod-reader Task -> Configurables

    Args:
        object (parser_args() object): DplAodReader Interface
    """
    
    def __init__(self, parserDplAodReader = argparse.ArgumentParser(add_help = False)):
        super(DplAodReader, self).__init__()
        self.parserDplAodReader = parserDplAodReader
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Interface
        groupDPLReader = self.parserDplAodReader.add_argument_group(title = "Data processor options: internal-dpl-aod-reader")
        groupDPLReader.add_argument("--aod", help = "Add your AOD File with path", action = "store", type = str)
        groupDPLReader.add_argument("--aod-memory-rate-limit", help = "Rate limit AOD processing based on memory", action = "store", type = str)
        groupDPLReader.add_argument("cfgFileName", metavar = "Config.json", default = "config.json", help = "config JSON file name (mandatory)")
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserDplAodReader.parse_args()
