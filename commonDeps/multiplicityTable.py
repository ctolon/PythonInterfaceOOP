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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/multiplicityTable.cxx

import argparse

from argcomplete.completers import ChoicesCompleter

class MultiplicityTable(object):
    """
    Class for Interface -> multiplicityTable.cxx Task -> Configurable, Process Functions  

    Args:
        object (parser_args() object): multiplicityTable.cxx Interface
    """
    
    def __init__(self, parserMultiplicityTable=argparse.ArgumentParser(add_help=False)):
        super(MultiplicityTable, self).__init__()
        self.parserMultiplicityTable = parserMultiplicityTable

    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
        
        # Predefined Selections
        booleanSelections = ["true", "false"]
    
        # Interface
        groupMultiplicityTable = self.parserMultiplicityTable.add_argument_group(title="Data processor options: multiplicity-table")
        groupMultiplicityTable.add_argument("--isVertexZeq", help="if true: do vertex Z eq mult table", action="store", type=str.lower, choices=(booleanSelections)).completer = ChoicesCompleter(booleanSelections)

            
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserMultiplicityTable.parse_args()
