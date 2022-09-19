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

# \Author: ionut.cristian.arsene@cern.ch
# \Interface:  cevat.batuhan.tolon@cern.ch

import logging


def converterManager(ttreeList: list, deps: list):
    """This function checks in your AO2D and produces converter tasks automatically if they needed

    Args:
        ttreeList (list): TTree list in AO2D file
        deps (list): Dependency List for running analysis task
    """
    
    logging.info("Converter Manager initialize")
    ttreeList = list(ttreeList) # checking
    
    if ("O2track_iu" in ttreeList):
        logging.info("o2-analysis-track-propagation will added your workflow")
        deps.append("o2-analysis-track-propagation")
    
    if ("O2fdd" in ttreeList) and ("O2fdd_001" not in ttreeList):
        logging.info("o2-analysis-fdd-converter will added your workflow")
        deps.append("o2-analysis-fdd-converter")
    
    # Need to be checked
    if ("O2v0" in ttreeList) and ("O2v0_001" not in ttreeList):
        logging.info("o2-analysis-weak-decay-indices will added your workflow")
        deps.append("o2-analysis-weak-decay-indices")
    
    if ("O2mcparticle" in ttreeList) and ("O2mcparticle_001" not in ttreeList):
        logging.info("o2-analysis-mc-converter will added your workflow")
        deps.append("o2-analysis-mc-converter")
    
    logging.info("Process done")
