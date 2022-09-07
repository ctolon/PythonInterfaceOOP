#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*- 
#############################################################################
##  © Copyright CERN 2018. All rights not expressly granted are reserved.  ##
##                   Author: ionut.cristian.arsene@cern.ch                 ##
##               Interface:  cevat.batuhan.tolon@cern.ch                   ## 
## This program is free software: you can redistribute it and/or modify it ##
##  under the terms of the GNU General Public License as published by the  ##
## Free Software Foundation, either version 3 of the License, or (at your  ##
## option) any later version. This program is distributed in the hope that ##
##  it will be useful, but WITHOUT ANY WARRANTY; without even the implied  ##
##     warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    ##
##           See the GNU General Public License for more details.          ##
##    You should have received a copy of the GNU General Public License    ##
##   along with this program. if not, see <https://www.gnu.org/licenses/>. ##
#############################################################################

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/trackPropagation.cxx

import argparse

from argcomplete.completers import ChoicesCompleter

class TrackPropagation(object):
    """
    Class for Interface -> trackPropagation.cxx Task -> Configurable, Process Functions  

    Args:
        object (parser_args() object): trackPropagation.cxx Interface
    """
    
    def __init__(self, parserTrackPropagation=argparse.ArgumentParser(add_help=False)):
        super(TrackPropagation, self).__init__()
        self.parserTrackPropagation = parserTrackPropagation

    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """

        # Predefined Selections
        booleanSelections = ["true", "false"]
    
        # Interface
        groupTrackPropagation = self.parserTrackPropagation.add_argument_group(title="Data processor options: track-propagation")
        groupTrackPropagation.add_argument("--isCovariance", help="track-propagation : If false, Process without covariance, If true Process with covariance", action="store",type=str.lower, choices=(booleanSelections)).completer = ChoicesCompleter(booleanSelections)
            
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserTrackPropagation.parse_args()