#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*- 

import argparse
from tokenize import group

import argcomplete  
from argcomplete import autocomplete
from argcomplete.completers import ChoicesCompleter

# Burası init yapıyo
from ClassB2 import B

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
    
    
############################33

class A(object):

  def __init__(self, parserA=argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description="Arguments to pass")):
    super(A, self).__init__()
    self.parserA = parserA
    self.parserA.register("action", "none", NoAction)
    self.parserA.register("action", "store_choice", ChoicesAction)

  def addArguments(self):
      
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
      
    group = self.parserA.add_argument_group(title="Data processor options: centrality-table")
    group.add_argument("--est", help="Produces centrality percentiles parameters", action="store", nargs="*", type=str, metavar="EST", choices=centralityTableSelectionsList).completer = ChoicesCompleterList(centralityTableSelectionsList)
    
    for key,value in centralityTableSelections.items():
        group.add_argument(key, help=value, action="none")

  def parseArgs(self):
    print(self.parserA.parse_args()) 
    autocomplete(self.parserA, always_complete_options=True)  
    return self.parserA.parse_args()


    
  def mergeMultiArgs(self, *objects):
     parser = self.parserA
     for object in objects:
         print(object)
         object.parser = parser
         object.addArguments()
         print(object.addArguments())
     self.addArguments()
     
    



# multi merge çalışşmıyor confilict var.

aCombined = A()
aCombined.mergeMultiArgs(B())
#print(vars(aCombined.parseArgs()))
