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


class TasknameNotFoundInConfigFileError(Exception):
    """Exception raised if taskname not found in json config file.

    Attributes:
        taskName -- input main task name
    """

    def __init__(self, taskName):
        self.taskName = taskName
        super().__init__()

    def __str__(self):
        return f"The JSON config does not include {self.taskName} task"


class CfgInvalidFormatError(Exception):
    """Exception raised for Invalid format json file

    Attributes:
        config -- input provided config json file
    """

    def __init__(self, configjson):
        self.configjson = configjson
        super().__init__()

    def __str__(self):
        return f"Invalid Format for json config file! Your JSON config input: {self.configjson} After the script, you must define your json configuration file \
            The command line should look like this:"


class NotInAlienvError(Exception):
    """Exception raised for O2Physics Alienv Loading
    Attributes:
        message -- error message for forgetting loading alienv
    """

    def __init__(self, message="You must load O2Physics with alienv"):
        self.message = message
        super().__init__(self.message)


class ForgettedArgsError(Exception):
    """Exception raised for forgetted args errors in parser args.

    Attributes:
        forgettedArgs -- arguments whose configuration is forgotten
    """

    def __init__(self, forgettedArgs):
        self.forgettedArgs = forgettedArgs
        super().__init__()

    def __str__(self):
        return f"Your forget assign a value to for this parameters: {self.forgettedArgs}"


class CentFilterError(Exception):
    """Exception raised if no process function left after cent filter for pp system in tableMaker/tableMakerMC task."""

    def __init__(self):
        super().__init__()

    def __str__(self):
        return f"After deleting the process functions related to the centrality table, there are no functions left to process, misconfigure for process function in tableMaker/tableMakerMC!"


# Classes for Filter PP Transacation Management
class BarrelSelsNotInBarrelTrackCutsError(Exception):
    """Exception raised for if filterPP selection is not valid for BarrelSels

    Attributes:
        barrelSels -- FilterPP Barrel Selections
        barrelTrackCuts -- Barrel Track Cuts
    """

    def __init__(self, barrelSels, barrelTrackCuts):
        self.barrelSels = barrelSels
        self.barrelTrackCuts = barrelTrackCuts
        super().__init__()

    def __str__(self):
        return f"--cfgBarrelSels <value>: {self.barrelSels} not in --cfgBarrelTrackCuts {self.barrelTrackCuts}"


class MuonSelsNotInMuonsCutsError(Exception):
    """Exception raised for if filterPP selection is not valid for MuonSels

    Attributes:
        muonSels -- FilterPP Muon Selections
        muonsCuts -- Additional Muon Cuts
    """

    def __init__(self, muonSels, muonsCuts):
        self.muonSels = muonSels
        self.muonsCuts = muonsCuts
        super().__init__()

    def __str__(self):
        return (
            f"--cfgMuonSels <value>: {self.muonSels} not in --cfgBarrelTrackCuts {self.muonsCuts}"
        )


class BarrelTrackCutsNotInBarrelSelsError(Exception):
    """Exception raised for if filterPP selection is not valid for BarrelSels

    Attributes:
        barrelSels -- FilterPP Barrel Selections
        barrelTrackCuts -- Barrel Track Cuts
    """

    def __init__(self, barrelSels, barrelTrackCuts):
        self.barrelSels = barrelSels
        self.barrelTrackCuts = barrelTrackCuts
        super().__init__()

    def __str__(self):
        return f"--cfgBarrelTrackCuts <value>: {self.barrelTrackCuts} not in --cfgBarrelSels {self.barrelSels}"


class MuonsCutsNotInMuonSelsError(Exception):
    """Exception raised for if filterPP selection is not valid for MuonSels

    Attributes:
        muonSels -- FilterPP Muon Selections
        muonsCuts -- Additional Muon Cuts
    """

    def __init__(self, muonSels, muonsCuts):
        self.muonSels = muonSels
        self.muonsCuts = muonsCuts
        super().__init__()

    def __str__(self):
        return f"--cfgMuonsCuts <value>: {self.muonsCuts} not in --cfgMuonSels {self.muonSels}"


class MandatoryArgNotFoundError(Exception):
    """Exception raised for if mandatory arg not found

    Attributes:
        arg -- mandatoryArg
    """

    def __init__(self, arg):
        self.arg = arg

    def __str__(self):
        return f"Mandatory args not found: {self.arg}"
