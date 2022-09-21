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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/trackPropagation.cxx

import argparse
from argcomplete.completers import ChoicesCompleter


class TrackPropagation(object):
    
    """
    Class for Interface -> trackPropagation.cxx Task -> Configurable, Process Functions

    Args:
        object (parser_args() object): trackPropagation.cxx Interface
    """
    
    def __init__(self, parserTrackPropagation = argparse.ArgumentParser(add_help = False)):
        super(TrackPropagation, self).__init__()
        self.parserTrackPropagation = parserTrackPropagation
    
    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        booleanSelections = ["true", "false"]
        
        # Interface
        groupTrackPropagation = self.parserTrackPropagation.add_argument_group(title = "Data processor options: track-propagation")
        groupTrackPropagation.add_argument(
            "--isCovariance", help = "track-propagation : If false, Process without covariance, If true Process with covariance",
            action = "store", type = str.lower, choices = (booleanSelections),
            ).completer = ChoicesCompleter(booleanSelections)
    
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserTrackPropagation.parse_args()
