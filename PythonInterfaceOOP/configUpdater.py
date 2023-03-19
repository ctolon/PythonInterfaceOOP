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

# Script for update json config files

from extramodules.configSetter import MasterLogger
from extramodules.o2TaskEnums import DQTasksUrlEnum, DQBarrelDepsUrlEnum, DQCommonDepsUrlEnum, DQMuonDepsUrlEnum, ConverterTasksUrlEnum, CentralityTaskEnum
from extramodules.utils import loadJson, dumpJson
from extramodules.configUpdaterFramework import ConfigMerger, removeUnmatchedSubkeys, sortDictByKeysAndAddNewTasks, alignDicts, latestConfigFileGenerator, newAddedConfigsReport
from extramodules.choicesHandler import ChoicesCompleterList
import json
import argparse
import argcomplete
import sys
from pathlib import Path
import time

logger = MasterLogger().getAdvancedLogger(f"configUpdater_{int(time.time())}.log", "INFO")


def taskUpdater(taskWithDeps: dict, oldConfigList: list, keepTasks = [], keepSubkeys: list = []):
    """
    Update configuration files for a given task with new dependencies and settings.

    Args:
        taskWithDeps (dict): A dictionary representing the updated task configuration with its dependencies.
        oldConfigList (list): A list of file paths to the existing configuration files to update.
        keepTasks (list, optional): A list of task names to keep from the old configuration. Defaults to an empty list.
        keepSubkeys (list, optional): A list of sub-keys to keep from the old configuration. Defaults to an empty list.

    Returns:
        list: A list of dictionaries representing the latest configuration settings for each updated file.

    Raises:
        FileNotFoundError: If one of the old configuration files does not exist.

    This function updates the configuration files for a given task with new dependencies and settings. It takes the
    updated task configuration as a dictionary and a list of file paths to the existing configuration files to update.
    It returns a list of dictionaries representing the latest configuration settings for each updated file.

    The function reads the old configuration files, merges them with the new dependencies and settings, removes
    deprecated options, and aligns the dictionaries. Then, it reorders the tasks as expected, generates the latest
    configs, and reports any new added configs. The updated configuration files are saved in a new directory named
    'updatedconfigs' in the current working directory.
    """
    
    # buffers
    newConfigsDir = "updatedconfigs/"
    oldConfigsDir = "configs/"
    taskWithDepsJson = latestConfigFileGenerator(taskWithDeps)
    oldConfigJsonList = [loadJson(oldConfig) for oldConfig in oldConfigList]
    mergedConfigs = []
    transformedConfigList = []
    latestConfigList = []
    
    # For debugging
    # dumpJson(f"{int(time.time())}.json", taskWithDepsJson)
    
    # Create new Config dir as updatedconfigs
    Path(newConfigsDir).mkdir(parents = True, exist_ok = True)
    
    configsToCreate = [element.replace(oldConfigsDir, newConfigsDir) for element in oldConfigList]
    
    # Merge config json file with latest version
    for configJson in oldConfigJsonList:
        tempObj = ConfigMerger(configJson, taskWithDepsJson)
        mergedConfigs.append(tempObj.mergeConfigs())
    
    # Remove deprecated options and align Jsons
    for i, mergedConfig in enumerate(mergedConfigs):
        logger.info(f"Key Remove Section for ==> {oldConfigList[i]}")
        transformConfig = removeUnmatchedSubkeys(mergedConfig, taskWithDepsJson, keepTasks, keepSubKeys)
        transformConfig = alignDicts(taskWithDepsJson, transformConfig, keepTasks)
        transformedConfigList.append(transformConfig)
    
    # Re-order Tasks as expected
    for i, (oldConfig, transformedConfig) in enumerate(zip(oldConfigJsonList, transformedConfigList)):
        logger.info(f"Sort Dict By Keys and Add New Tasks Section for ==> {oldConfigList[i]}")
        latestConfigList.append(sortDictByKeysAndAddNewTasks(transformedConfig, oldConfig))
    
    # Generate latest configs
    for oldConfig, oldConfigJson, transformedConfig, configToCreate, latestConfig in zip(oldConfigList, oldConfigJsonList, transformedConfigList, configsToCreate, latestConfigList):
        logger.info(f"New Added Configs Section For ==> {oldConfig}")
        newAddedConfigsReport(latestConfig, oldConfigJson)
        
        dumpJson(configToCreate, latestConfig, 4)
        logger.info(f"{configToCreate} created successfully.")
    
    logger.info("Config Updating process finished.")
    return latestConfigList


if __name__ == "__main__":
    
    mainDQTasks = ["all", "tableMaker", "tableMakerMC", "dqEfficiency", "tableReader", "dqFlow", "dalitzSelection", "filterPP", "filterPPwithAssociation", "v0selector"]
    
    parser = argparse.ArgumentParser(description = "Arguments to pass")
    parser.add_argument("--update", help = "Tasks to Update", action = "store", nargs = "*", type = str, choices = mainDQTasks, required = True).completer = ChoicesCompleterList(mainDQTasks)
    
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    
    # All config json files
    configListTableMakerData = ["configs/configTableMakerDataRun2.json", "configs/configTableMakerDataRun3.json"]
    configListTableMakerMC = ["configs/configTableMakerMCRun2.json", "configs/configTableMakerMCRun3.json"]
    configListTableReader = ["configs/configAnalysisData.json"]
    configListDQEfficiency = ["configs/configAnalysisMC.json"]
    configListDalitzSelection = ["configs/configDalitzSelectionDataRun2.json", "configs/configDalitzSelectionDataRun3.json"]
    configListFilterPP = ["configs/configFilterPPDataRun2.json", "configs/configFilterPPDataRun3.json"]
    configListFilterPPWithAssociation = ["configs/configFilterPPwithAssociationDataRun2.json", "configs/configFilterPPwithAssociationDataRun3.json"]
    configListDQFlow = ["configs/configFlowDataRun2.json", "configs/configFlowDataRun3.json"]
    configListV0selector = ["configs/configV0SelectorDataRun2.json", "configs/configV0SelectorDataRun3.json"]
    
    # All O2 Common Framework Dependency Tasks
    commonDeps = DQCommonDepsUrlEnum.enumToDict()
    barrelDeps = DQBarrelDepsUrlEnum.enumToDict()
    muonDeps = DQMuonDepsUrlEnum.enumToDict()
    allDeps = {
        **commonDeps,
        **barrelDeps,
        **muonDeps
        }
    
    # All O2-DQ Framework Main Tasks
    singleTableMaker = {
        DQTasksUrlEnum.TABLE_MAKER.name: DQTasksUrlEnum.TABLE_MAKER.value
        }
    singleTableMakerMC = {
        DQTasksUrlEnum.TABLE_MAKER_MC.name: DQTasksUrlEnum.TABLE_MAKER_MC.value
        }
    singleDalitzSelection = {
        DQTasksUrlEnum.DALITZ_SELECTION.name: DQTasksUrlEnum.DALITZ_SELECTION.value
        }
    singleDQFlow = {
        DQTasksUrlEnum.DQ_FLOW.name: DQTasksUrlEnum.DQ_FLOW.value
        }
    singleFilterPP = {
        DQTasksUrlEnum.FILTER_PP.name: DQTasksUrlEnum.FILTER_PP.value
        }
    singleFilterPPWithAssociation = {
        DQTasksUrlEnum.FILTER_PP_WITH_ASSOCIATION.name: DQTasksUrlEnum.FILTER_PP_WITH_ASSOCIATION.value
        }
    singleV0selector = {
        DQTasksUrlEnum.V0_SELECTOR.name: DQTasksUrlEnum.V0_SELECTOR.value
        }
    
    # All Converter Tasks
    collisionConverter = {
        ConverterTasksUrlEnum.COLLISION_CONVERTER.name: ConverterTasksUrlEnum.COLLISION_CONVERTER.value
        }
    fddConverter = {
        ConverterTasksUrlEnum.FDD_CONVERTER.name: ConverterTasksUrlEnum.FDD_CONVERTER.value
        }
    mcConverter = {
        ConverterTasksUrlEnum.MC_CONVERTER.name: ConverterTasksUrlEnum.MC_CONVERTER.value
        }
    trackPropagation = {
        ConverterTasksUrlEnum.TRACK_PROPAGATION.name: ConverterTasksUrlEnum.TRACK_PROPAGATION.value
        }
    weakDecayIndices = {
        ConverterTasksUrlEnum.WEAK_DECAY_INDICES.name: ConverterTasksUrlEnum.WEAK_DECAY_INDICES.value
        }
    
    # Centrality Task
    centralityTable = {
        CentralityTaskEnum.CENTRALITY_TABLE.name: CentralityTaskEnum.CENTRALITY_TABLE.value
        }
    
    # Merging DQ Tasks with dependecies
    tableMaker = {
        **singleTableMaker,
        **singleDQFlow,
        **singleFilterPP,
        **singleV0selector,
        **singleDalitzSelection,
        **allDeps,
        **centralityTable,
        **collisionConverter,
        **fddConverter,
        **trackPropagation,
        **weakDecayIndices
        }
    
    tableMakerMC = {
        **singleTableMakerMC,
        **singleDalitzSelection,
        **allDeps,
        **centralityTable,
        **collisionConverter,
        **fddConverter,
        **trackPropagation,
        **mcConverter,
        **weakDecayIndices
        }
    
    dalitzSelection = {
        **singleDalitzSelection,
        **barrelDeps,
        **commonDeps,
        **centralityTable,
        **collisionConverter,
        **fddConverter,
        **trackPropagation
        }
    
    dqFlow = {
        **singleDQFlow,
        **allDeps,
        **centralityTable,
        **collisionConverter,
        **fddConverter,
        **trackPropagation
        }
    filterPP = {
        **singleFilterPP,
        **allDeps,
        **collisionConverter,
        **fddConverter,
        **trackPropagation
        }
    filterPPWithAssociation = {
        **singleFilterPPWithAssociation,
        **allDeps,
        **collisionConverter,
        **fddConverter,
        **trackPropagation
        }
    
    v0selector = {
        **singleV0selector,
        **allDeps,
        **centralityTable,
        **collisionConverter,
        **fddConverter,
        **trackPropagation,
        **weakDecayIndices
        }
    
    # Run over skimming tasks (they don't have any common deps)
    dqEfficiency = {
        DQTasksUrlEnum.DQ_EFFICIENCY.name: DQTasksUrlEnum.DQ_EFFICIENCY.value
        }
    tableReader = {
        DQTasksUrlEnum.TABLE_READER.name: DQTasksUrlEnum.TABLE_READER.value
        }
    
    #################################################################
    
    # Keep some Tasks and configurables/Process Function
    keepTasks = ["internal-dpl-aod-reader", "internal-dpl-clock", "internal-dpl-aod-spawner", "internal-dpl-aod-index-builder", "internal-dpl-aod-global-analysis-file-sink", "internal-dpl-aod-writer", "internal-dpl-injected-dummy-sink"]
    keepSubKeys = ["processBarrelOnlyWithQvector", "processMuonOnlyWithQvector", "genname"]
    
    if "all" in args.update:
        logger.info("Report Generation for All PWG-DQ Configs...")
        
        logger.info("Generating Report For TableMaker===")
        taskUpdater(tableMaker, configListTableMakerData, keepTasks, keepSubKeys)
        
        logger.info("Generating Report For TableMakerMC===")
        taskUpdater(tableMakerMC, configListTableMakerMC, keepTasks)
        
        logger.info("Generating Report For dqEfficiency===")
        taskUpdater(dqEfficiency, configListDQEfficiency, keepTasks)
        
        logger.info("Generating Report for TableReader===")
        taskUpdater(tableReader, configListTableReader, keepTasks)
        
        logger.info("Generating Report For dqFlow===")
        taskUpdater(dqFlow, configListDQFlow, keepTasks)
        
        logger.info("Generating Report For dalitzSelection===")
        taskUpdater(dalitzSelection, configListDalitzSelection, keepTasks)
        
        logger.info("Generating Report For filterPP===")
        taskUpdater(filterPP, configListFilterPP, keepTasks)
        
        logger.info("Generating Report For filterPPwithAssociation===")
        taskUpdater(filterPPWithAssociation, configListFilterPPWithAssociation, keepTasks)
        
        logger.info("Generating Report For v0selector===")
        taskUpdater(v0selector, configListV0selector, keepTasks)
        sys.exit()
    
    if "tableMaker" in args.update:
        logger.info("Generating Report For TableMaker===")
        taskUpdater(tableMaker, configListTableMakerData, keepTasks, keepSubKeys)
    
    if "tableMakerMC" in args.update:
        logger.info("Generating Report For TableMakerMC===")
        taskUpdater(tableMakerMC, configListTableMakerMC, keepTasks)
    
    if "dqEfficiency" in args.update:
        logger.info("Generating Report For dqEfficiency===")
        taskUpdater(dqEfficiency, configListDQEfficiency, keepTasks)
    
    if "tableReader" in args.update:
        logger.info("Generating Report for TableReader===")
        taskUpdater(tableReader, configListTableReader, keepTasks)
    
    if "dqFlow" in args.update:
        logger.info("Generating Report For dqFlow===")
        taskUpdater(dqFlow, configListDQFlow, keepTasks)
    
    if "dalitzSelection" in args.update:
        logger.info("Generating Report For dalitzSelection===")
        taskUpdater(dalitzSelection, configListDalitzSelection, keepTasks)
    
    if "filterPP" in args.update:
        logger.info("Generating Report For filterPP===")
        taskUpdater(filterPP, configListFilterPP, keepTasks)
    
    if "filterPPwithAssociation" in args.update:
        logger.info("Generating Report For filterPPwithAssociation===")
        taskUpdater(filterPPWithAssociation, configListFilterPPWithAssociation, keepTasks)
    
    if "v0selector" in args.update:
        logger.info("Generating Report For v0selector===")
        taskUpdater(v0selector, configListV0selector, keepTasks)
