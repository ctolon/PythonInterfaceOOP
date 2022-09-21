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

import argparse


class O2Converters(object):
    
    """
    Class for Add Converters to workflows

    Args:
        object (parser_args() object): Converter task adder arguments
    """
    
    def __init__(self, parserO2Converters = argparse.ArgumentParser(add_help = False)):
        super(O2Converters, self).__init__()
        self.parserO2Converters = parserO2Converters
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Interface
        groupO2Converters = self.parserO2Converters.add_argument_group(title = "Additional Task Adding Options")
        groupO2Converters.add_argument(
            "--add_mc_conv",
            help = "Add the converter from mcparticle to mcparticle+001 (Adds your workflow o2-analysis-mc-converter task)",
            action = "store_true",
            )
        groupO2Converters.add_argument(
            "--add_fdd_conv", help = "Add the fdd converter (Adds your workflow o2-analysis-fdd-converter task)", action = "store_true",
            )
        groupO2Converters.add_argument(
            "--add_track_prop",
            help = "Add track propagation to the innermost layer (TPC or ITS) (Adds your workflow o2-analysis-track-propagation task)",
            action = "store_true",
            )
        groupO2Converters.add_argument(
            "--add_weakdecay_ind",
            help = "Add Converts V0 and cascade version 000 to 001 (Adds your workflow o2-analysis-weak-decay-indices task)",
            action = "store_true",
            )
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserO2Converters.parse_args()
