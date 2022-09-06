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

# Orginal Task For tableMaker.cxx: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMaker.cxx
# Orginal Task For tableMakerMC.cxx: https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMakerMC.cxx

import json
import sys
import logging
import logging.config
from logging.handlers import RotatingFileHandler
from logging import handlers
from ast import parse
import os
import argparse
import re
import urllib.request
from urllib.request import Request, urlopen
import ssl

"""
argcomplete - Bash tab completion for argparse
Documentation https://kislyuk.github.io/argcomplete/
Instalation Steps
pip install argcomplete
sudo activate-global-python-argcomplete
Only Works On Local not in O2
Activate libraries in below and activate #argcomplete.autocomplete(parser) line
"""
import argcomplete  
from argcomplete.completers import ChoicesCompleter 

def add_centrality_table( group ):
   group.add_argument('--boo', help='boo help')

if __name__ == "__main__":  
   parser = argparse.ArgumentParser(prog='Centt')


def listToString(s):
    """
    ListToString provides converts lists to strings with commas.
    This function is written to save as string type instead of list


    Args:
        s (list): Input as List

    Returns:
        string: Comma seperated string
    """
    if len(s) > 1:
        # initialize an empty string
        str1 = ","

        # return string
        return str1.join(s)
    else:
        str1 = " "

        return str1.join(s)


def stringToList(string):
    """
    stringToList provides converts strings to list with commas.
    This function is written to save as list type instead of string

    Args:
        string (string): Input as String

    Returns:
        list: Comma separated list
    """
    li = list(string.split(","))
    return li


class NoAction(argparse.Action):
    """
    NoAction class adds dummy positional arguments to an argument,
    so sub helper messages can be created

    Args:
        argparse (Class): Input as args
    """

    def __init__(self, **kwargs):
        kwargs.setdefault("default", argparse.SUPPRESS)
        kwargs.setdefault("nargs", 0)
        super(NoAction, self).__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        pass


class ChoicesAction(argparse._StoreAction):
    """
    ChoicesAction class is used to add extra choices
    to a parseargs choices list

    Args:
        argparse (Class): Input as args
    """

    def add_choice(self, choice, help=""):
        if self.choices is None:
            self.choices = []
        self.choices.append(choice)
        self.container.add_argument(choice, help=help, action="none")


class ChoicesCompleterList(object):
    """
    For the ChoicesCompleterList package argcomplete,
    the TAB key is the class written for autocomplete and validation when an argument can take multiple values.
    By default, the argcomplete package has the ChoicesCompleter Class,
    which can only validate arguments that take an one value and allows autocomplete with the TAB key.

    Args:
        object (list): parserargs choices object as a list
    """

    def __init__(self, choices):
        self.choices = list(choices)

    def __call__(self, **kwargs):
        return self.choices

        
###################################
# Interface Predefined Selections #
###################################
   
centralityTableSelections = {
    "Run2V0M": "Produces centrality percentiles using V0 multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "Run2SPDtks": "Produces Run2 centrality percentiles using SPD tracklets multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "Run2SPDcls": "Produces Run2 centrality percentiles using SPD clusters multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "Run2CL0": "Produces Run2 centrality percentiles using CL0 multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "Run2CL1": "Produces Run2 centrality percentiles using CL1 multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "FV0A": "Produces centrality percentiles using FV0A multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "FT0M": "Produces centrality percentiles using FT0 multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "FDDM": "Produces centrality percentiles using FDD multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
    "NTPV": "Produces centrality percentiles using number of tracks contributing to the PV. -1: auto, 0: don't, 1: yes. Default: auto (-1)"
}
centralityTableSelectionsList = []
for k, v in centralityTableSelections.items():
    centralityTableSelectionsList.append(k)

centralityTableParameters = [
    "estRun2V0M",
    "estRun2SPDtks",
    "estRun2SPDcls",
    "estRun2CL0",
    "estRun2CL1",
    "estFV0A",
    "estFT0M",
    "estFDDM",
    "estNTPV"
]
# TODO: Add genname parameter
    
###################
# Main Parameters #
###################

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Arguments to pass")
parser.register("action", "none", NoAction)
parser.register("action", "store_choice", ChoicesAction)

# centrality-table
groupCentralityTable = parser.add_argument_group(title="Data processor options: centrality-table")
groupCentralityTable.add_argument("--est", help="Produces centrality percentiles parameters", action="store", nargs="*", type=str, metavar="EST", choices=centralityTableSelectionsList).completer = ChoicesCompleterList(centralityTableSelectionsList)

for key,value in centralityTableSelections.items():
    groupCentralityTable.add_argument(key, help=value, action="none")

argcomplete.autocomplete(parser, always_complete_options=False)
extrargs2 = parser.parse_args()
print(parser)
print(parser.parse_args)

configuredCommands = vars(extrargs2) # for get extrargs
    
# add prefix for extrargs.est for centrality-table
if extrargs2.est != None:
    prefix_est = "est"
    extrargs2.est = [prefix_est + sub for sub in extrargs2.est]


    