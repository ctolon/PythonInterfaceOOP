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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/v0selector.cxx

import argparse

class v0selector(object):
    """
    Class for Interface -> v0selector.cxx Task -> Configurable, Process Functions  

    Args:
        object (parser_args() object): v0selector.cxx Interface
    """
    
    def __init__(self, parserv0selector=argparse.ArgumentParser(add_help=False)):
        super(v0selector, self).__init__()
        self.parserv0selector = parserv0selector

    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """

        # Interface
        groupV0Selector = self.parserv0selector.add_argument_group(title="Data processor options: v0-selector")
        groupV0Selector.add_argument("--d_bz", help="bz field", action="store", type=str)
        groupV0Selector.add_argument("--v0cospa", help="v0cospa", action="store", type=str)
        groupV0Selector.add_argument("--dcav0dau", help="DCA V0 Daughters", action="store", type=str)
        groupV0Selector.add_argument("--v0Rmin", help="v0Rmin", action="store", type=str)
        groupV0Selector.add_argument("--v0Rmax", help="v0Rmax", action="store", type=str)
        groupV0Selector.add_argument("--dcamin", help="dcamin", action="store", type=str)
        groupV0Selector.add_argument("--dcamax", help="dcamax", action="store", type=str)
        groupV0Selector.add_argument("--mincrossedrows", help="Min crossed rows", action="store", type=str)
        groupV0Selector.add_argument("--maxchi2tpc", help="max chi2/NclsTPC", action="store", type=str)
            
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserv0selector.parse_args()