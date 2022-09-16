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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/v0selector.cxx

import argparse


class V0selector(object):
    
    """
    Class for Interface -> v0selector.cxx Task -> Configurable, Process Functions

    Args:
        object (parser_args() object): v0selector.cxx Interface
    """
    
    def __init__(self, parserV0selector = argparse.ArgumentParser(add_help = False)):
        super(V0selector, self).__init__()
        self.parserV0selector = parserV0selector
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Interface
        groupV0Selector = self.parserV0selector.add_argument_group(title = "Data processor options: v0-selector")
        groupV0Selector.add_argument("--d_bz_input", help = "bz field in kG, -999 is automatic", action = "store", type = str)
        groupV0Selector.add_argument("--v0cospa", help = "v0cospa", action = "store", type = str)
        groupV0Selector.add_argument("--dcav0dau", help = "DCA V0 Daughters", action = "store", type = str)
        groupV0Selector.add_argument("--v0Rmin", help = "v0Rmin", action = "store", type = str)
        groupV0Selector.add_argument("--v0Rmax", help = "v0Rmax", action = "store", type = str)
        groupV0Selector.add_argument("--dcamin", help = "dcamin", action = "store", type = str)
        groupV0Selector.add_argument("--dcamax", help = "dcamax", action = "store", type = str)
        groupV0Selector.add_argument("--mincrossedrows", help = "Min crossed rows", action = "store", type = str)
        groupV0Selector.add_argument("--maxchi2tpc", help = "max chi2/NclsTPC", action = "store", type = str)
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserV0selector.parse_args()
