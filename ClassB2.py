import argparse
from tokenize import group

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

class B(object):

  def __init__(self, parserB=argparse.ArgumentParser(add_help=False)):
    super(B, self).__init__()
    self.parserB = parserB
    self.parserB.register("action", "none", NoAction)
    self.parserB.register("action", "store_choice", ChoicesAction)


  def addArguments(self):
      
    collisionSystemSelections = ["PbPb", "pp", "pPb", "Pbp", "XeXe"]

    eventMuonSelections = ["0", "1", "2"]
    
    groupB = self.parserB.add_argument_group(title="Data processor options: event-selection-task")
    groupB.add_argument("--syst", help="Collision System Selection ex. pp", action="store", type=str, choices=(collisionSystemSelections)).completer = ChoicesCompleter(collisionSystemSelections)
    groupB.add_argument("--muonSelection", help="0 - barrel, 1 - muon selection with pileup cuts, 2 - muon selection without pileup cuts", action="store", type=str, choices=(eventMuonSelections)).completer = ChoicesCompleter(eventMuonSelections)
    groupB.add_argument("--customDeltaBC", help="custom BC delta for FIT-collision matching", action="store", type=str)
  def parseArgs(self):
    return self.parserB.parse_args()