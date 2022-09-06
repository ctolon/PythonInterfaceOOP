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

import argparse

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
   
ft0Selections = ["FT0", "NoFT0", "OnlyFT0", "Run2"]

ft0Parameters = ["processFT0", "processNoFT0", "processOnlyFT0", "processRun2"]

    
###################
# Main Parameters #
###################

parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Arguments to pass")
parser.register("action", "none", NoAction)
parser.register("action", "store_choice", ChoicesAction)

# tof-event-time
groupTofEventTime = parser.add_argument_group(title="Data processor options: tof-event-time")
groupTofEventTime.add_argument("--FT0", help="FT0: Process with FT0, NoFT0: Process without FT0, OnlyFT0: Process only with FT0, Run2: Process with Run2 data", action="store", type=str, choices=ft0Selections).completer = ChoicesCompleter(ft0Selections)

argcomplete.autocomplete(parser, always_complete_options=False)
extrargs = parser.parse_args()

configuredCommands = vars(extrargs) # for get extrargs

# add prefix for extrargs.FT0 for tof-event-time
if extrargs.FT0 != None:
    prefix_process = "process"
    extrargs.FT0 = prefix_process + extrargs.FT0
    
