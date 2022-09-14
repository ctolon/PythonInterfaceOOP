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
        groupTofPidbeta = self.parserTofPidBeta.add_argument_group(
            title="Data processor options: tof-pid-beta"
        )
        groupTofPidbeta.add_argument(
            "--tof-expreso",
            help="Expected resolution for the computation of the expected beta",
            action="store",
            type=str,
        )

    def parseArgs(self):
        """
        This function allows to save the obtained arguments to the parser_args() function

        Returns:
            Namespace: returns parse_args()
        """

        return self.parserTofPidBeta.parse_args()
