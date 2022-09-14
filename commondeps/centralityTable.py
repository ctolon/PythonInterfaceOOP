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

# Orginal Task: https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/centralityTable.cxx

import argparse

from extramodules.choicesCompleterList import ChoicesCompleterList


class CentralityTable(object):
    """
    Class for Interface -> centralityTable.cxx Task -> Configurable, Process Functions

    Args:
        object (parser_args() object): centralityTable.cxx Interface
    """

    def __init__(self, parserCentralityTable=argparse.ArgumentParser(add_help=False)):
        super(CentralityTable, self).__init__()
        self.parserCentralityTable = parserCentralityTable
        # self.parserB.register("action", "none", NoAction)
        # self.parserB.register("action", "store_choice", ChoicesAction)

    def addArguments(self):
        """
        This function allows to add arguments for parser_args() function
        """

        # Predefined Selections
        centralityTableSelections = {
            "Run2V0M": "Produces centrality percentiles using V0 multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
            "Run2SPDtks": "Produces Run2 centrality percentiles using SPD tracklets multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
            "Run2SPDcls": "Produces Run2 centrality percentiles using SPD clusters multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
            "Run2CL0": "Produces Run2 centrality percentiles using CL0 multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
            "Run2CL1": "Produces Run2 centrality percentiles using CL1 multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
            "FV0A": "Produces centrality percentiles using FV0A multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
            "FT0M": "Produces centrality percentiles using FT0 multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
            "FDDM": "Produces centrality percentiles using FDD multiplicity. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
            "NTPV": "Produces centrality percentiles using number of tracks contributing to the PV. -1: auto, 0: don't, 1: yes. Default: auto (-1)",
        }
        centralityTableSelectionsList = []
        for k, v in centralityTableSelections.items():
            centralityTableSelectionsList.append(k)

        # Interface
        groupCentralityTable = self.parserCentralityTable.add_argument_group(
            title="Data processor options: centrality-table"
        )
        groupCentralityTable.add_argument(
            "--est",
            help="Produces centrality percentiles parameters",
            action="store",
            nargs="*",
            type=str,
            metavar="EST",
            choices=centralityTableSelectionsList,
        ).completer = ChoicesCompleterList(centralityTableSelectionsList)

        for key, value in centralityTableSelections.items():
            groupCentralityTable.add_argument(key, help=value, action="none")

    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """

        return self.parserCentralityTable.parse_args()
