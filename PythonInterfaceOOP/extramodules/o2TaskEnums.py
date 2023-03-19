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

from enum import Enum


class DQTasksUrlEnum(Enum):
    
    """Enumeration of URLs for tasks related to the Alice O2 group PWG-DQ Main Tasks.

    Attributes:
        TABLE_MAKER (str): URL for the tableMaker.cxx task.
        TABLE_MAKER_MC (str): URL for the tableMakerMC.cxx task.
        DALITZ_SELECTION (str): URL for the DalitzSelection.cxx task.
        DQ_EFFICIENCY (str): URL for the dqEfficiency.cxx task.
        DQ_FLOW (str): URL for the dqFlow.cxx task.
        FILTER_PP (str): URL for the filterPP.cxx task.
        FILTER_PP_WITH_ASSOCIATION (str): URL for the filterPPwithAssociation.cxx task.
        TABLE_READER (str): URL for the tableReader.cxx task.
        V0_SELECTOR (str): URL for the v0selector.cxx task.

    Methods:
        enumToDict: Returns a dictionary representation of the enumeration.

    """
    
    TABLE_MAKER = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMaker.cxx?raw=true"
    TABLE_MAKER_MC = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMakerMC.cxx?raw=true"
    DALITZ_SELECTION = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/DalitzSelection.cxx?raw=true"
    DQ_EFFICIENCY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqEfficiency.cxx?raw=true"
    DQ_FLOW = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqFlow.cxx?raw=true"
    FILTER_PP = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/filterPP.cxx?raw=true"
    FILTER_PP_WITH_ASSOCIATION = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/filterPPwithAssociation.cxx?raw=true"
    TABLE_READER = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/tableReader.cxx?raw=true"
    V0_SELECTOR = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/v0selector.cxx?raw=true"
    
    @classmethod
    def enumToDict(cls):
        """Returns a dictionary representation of the enumeration.

        Returns:
            dict: A dictionary mapping the enumeration item names to their respective URL values.
        """
        return {item.name: item.value
                for item in cls}


class DQCommonDepsUrlEnum(Enum):
    
    """Enumeration of URLs for tasks related to the Alice O2 group PWG-DQ Common Dependency Tasks.

    Attributes:
        TIMESTAMP (str): URL for the timestamp.cxx task.
        EVENT_SELECTION (str): URL for the eventSelection.cxx task.
        MULTİPLICITY_TABLE (str): URL for the multiplicityTable.cxx task.

    Methods:
        enumToDict: Returns a dictionary representation of the enumeration.

    """
    
    TIMESTAMP = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/timestamp.cxx?raw=true"
    EVENT_SELECTION = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/eventSelection.cxx?raw=true"
    MULTİPLICITY_TABLE = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/multiplicityTable.cxx?raw=true"
    
    @classmethod
    def enumToDict(cls):
        """Returns a dictionary representation of the enumeration.

        Returns:
            dict: A dictionary mapping the enumeration item names to their respective URL values.
        """
        return {item.name: item.value
                for item in cls}


class DQBarrelDepsUrlEnum(Enum):
    
    """Enumeration of URLs for tasks related to the Alice O2 group PWG-DQ Barrel Dependency Tasks.

    Attributes:
        TRACK_SELECTION (str): URL for the trackselection.cxx task.
        TRACK_EXTENSION (str): URL for the trackextension.cxx task.
        PID_TOF_BASE (str): URL for the pidTOFBase.cxx task.
        PID_TOF (str): URL for the pidTOF.cxx task.
        PID_TOF_FULL (str): URL for the pidTOFFull.cxx task.
        PID_TOF_BETA (str): URL for the pidTOFbeta.cxx task.
        PID_TPC_FULL (str): URL for the pidTPCFull.cxx task.

    Methods:
        enumToDict: Returns a dictionary representation of the enumeration.

    """
    
    TRACK_SELECTION = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/trackselection.cxx?raw=true"
    TRACK_EXTENSION = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/trackextension.cxx?raw=true"
    PID_TOF_BASE = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/PID/pidTOFBase.cxx?raw=true"
    PID_TOF = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/PID/pidTOF.cxx?raw=true"
    PID_TOF_FULL = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/PID/pidTOFFull.cxx?raw=true"
    PID_TOF_BETA = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/PID/pidTOFbeta.cxx?raw=true"
    PID_TPC_FULL = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/PID/pidTPCFull.cxx?raw=true"
    
    @classmethod
    def enumToDict(cls):
        """Returns a dictionary representation of the enumeration.

        Returns:
            dict: A dictionary mapping the enumeration item names to their respective URL values.
        """
        return {item.name: item.value
                for item in cls}


class DQMuonDepsUrlEnum(Enum):
    
    """Enumeration of URLs for tasks related to the Alice O2 group PWG-DQ Muon Dependency Tasks.

    Attributes:
        FWD_TRACK_EXTENSION (str): URL for the fwdtrackextension.cxx task.

    Methods:
        enumToDict: Returns a dictionary representation of the enumeration.

    """
    
    FWD_TRACK_EXTENSION = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/fwdtrackextension.cxx?raw=true"
    
    @classmethod
    def enumToDict(cls):
        """Returns a dictionary representation of the enumeration.

        Returns:
            dict: A dictionary mapping the enumeration item names to their respective URL values.
        """
        return {item.name: item.value
                for item in cls}


class ConverterTasksUrlEnum(Enum):
    
    """Enumeration of URLs for tasks related to the Alice O2 Converter Tasks.

    Attributes:
        TRACK_PROPAGATION (str): URL for the trackPropagation.cxx task.
        WEAK_DECAY_INDICES (str): URL for the weakDecayIndices.cxx task.
        COLLISION_CONVERTER (str): URL for the collisionConverter.cxx task.
        FDD_CONVERTER (str): URL for the fddConverter.cxx task.
        MC_CONVERTER (str): url for the mcConverter.cxx task.

    Methods:
        enumToDict: Returns a dictionary representation of the enumeration.

    """
    
    TRACK_PROPAGATION = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/trackPropagation.cxx?raw=true"
    WEAK_DECAY_INDICES = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/weakDecayIndices.cxx?raw=true"
    COLLISION_CONVERTER = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/collisionConverter.cxx?raw=true"
    FDD_CONVERTER = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/fddConverter.cxx?raw=true"
    MC_CONVERTER = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/mcConverter.cxx?raw=true"
    
    @classmethod
    def enumToDict(cls):
        """Returns a dictionary representation of the enumeration.

        Returns:
            dict: A dictionary mapping the enumeration item names to their respective URL values.
        """
        return {item.name: item.value
                for item in cls}


class CentralityTaskEnum(Enum):
    
    """Enumeration of URL for tasks related to the Alice O2 group Centrality Table Task.

    Attributes:
        CENTRALITY_TABLE (str): URL for the centralityTable..cxx task.

    Methods:
        enumToDict: Returns a dictionary representation of the enumeration.

    """
    
    CENTRALITY_TABLE = "https://github.com/AliceO2Group/O2Physics/blob/master/Common/TableProducer/centralityTable.cxx?raw=true"
    
    @classmethod
    def enumToDict(cls):
        """Returns a dictionary representation of the enumeration.

        Returns:
            dict: A dictionary mapping the enumeration item names to their respective URL values.
        """
        return {item.name: item.value
                for item in cls}
