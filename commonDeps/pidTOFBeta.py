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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/PID/pidTOFbeta.cxx

import argparse

class TofPidBeta(object):
    """
    Class for Interface -> pidTOFbeta.cxx Task -> Configurable, Process Functions  

    Args:
        object (parser_args() object): pidTOFbeta.cxx Interface
    """
    
    def __init__(self, parserTofPidBeta=argparse.ArgumentParser(add_help=False)):
        super(TofPidBeta, self).__init__()
        self.parserTofPidBeta = parserTofPidBeta

    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """
    
        # Interface
        groupTofPidbeta = self.parserTofPidBeta.add_argument_group(title="Data processor options: tof-pid-beta")
        groupTofPidbeta.add_argument("--tof-expreso", help="Expected resolution for the computation of the expected beta", action="store", type=str)
            
    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function
        
        Returns:
            Namespace: returns parse_args()
        """
        
        return self.parserTofPidBeta.parse_args()
