# Python Scripts And JSON Configs

@tableofcontents

## Main Python Scripts

These scripts are the main python scripts that run the workflows in O2-DQ.

* Script used to run on data the skimming tasks (tableMaker.cxx)
[`runTableMaker.py`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/runTableMaker.py).
* Script used to run on MC the skimming tasks (tableMakerMC.cxx)
[`runTableMakerMC.py`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/runTableMaker.py).
* Analyze DQ skimmed data tables. This workflow runs a few tasks: event selection, barrel track selection, muon track selection etc.
[`runTableReader.py`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/runTableMaker.py).
* Which contains the tasks DQEventSelection for event selection, DQBarrelTrackSelection for barrel track selection and single track MC matching, and the DQQuarkoniumPairing for reconstructed track pairing, MC matching of the pairs and counting of generated MC signals.  
[`runDQEfficiency.py`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/runDQEfficiency..py).
* Produces a decision table for pp collisions. The decisions require that at least a selected pair (or just two tracks) exists for a given event. Currently up to 64 simultaneous decisions can be made, to facilitate studies for optimizing cuts. 
[`runFilterPP.py`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/runFilterPP.py).
* Task to compute Q vectors and other quanitites related from the generic framework. Generic framework O2 version is a port of the AliPhysics version. To be used in the DQ analyses aiming for flow measurements.
[`runDQFlow.py`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/runDQFlow.py).
* V0 Selector makes Loops over a V0Data table and produces some standard analysis output.
[`runV0selector.py`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/runV0selector.py).
* It provides Download needed O2-DQ Libraries (CutsLibrary, MCSignalLibrary, MixingLibrary from O2Physics) for validation and autocompletion in Manual way. You can download libs with version as nightly or you can pull libs from your local alice-software.
[`DownloadLibs.py`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/DownloadLibs.py).

## Config Files

* Contains workflow configuration files
[`Configs`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/Configs)


* JSON workflow configuration files List in Table

Main File | Related Task on O2Physics | Description | W.S
--- | --- | --- | ---
[`configTableMakerDataRun2.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configTableMakerDataRun2.json) | [`TableMaker.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMaker.cxx) | run over Run-2 converted data | `runTableMaker.py` 
[`configTableMakerDataRun3.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configTableMakerDataRun3.json) | [`TableMaker.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMaker.cxx) | run over Run-3 data | `runTableMaker.py` |
[`configTableMakerMCRun2.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configTableMakerMCRun2.json) | [`TableMakerMC.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMakerMC.cxx) | run over Run-2 converted MC | `runTableMakerMC.py`
[`configTableMakerMCRun3.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configTableMakerMCRun3.json) | [`TableMakerMC.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMakerMC.cxx) | run over Run-3 MC | `runTableMakerMC.py`
[`configAnalysisData.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configAnalysisData.json) | [`TableReader.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/tableReader.cxx) | run with tableReader.cxx | `runTableReader.py`
[`configAnalysisMC.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configAnalysisMC.json) | [`dqEfficiency.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqEfficiency.cxx) | run with dqEfficiency.cxx | `runDQEfficiency.py` 
[`configFilterPPDataRun3.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configFilterPPDataRun3.json) | [`filterPP.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/filterPP.cxx) | run with filterPP.cxx on data run 3 | `runFilterPP.py`
[`configFilterPPDataRun2.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configFilterPPDataRun2.json) | [`filterPP.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/filterPP.cxx) | run with filterPP.cxx on data run 2 | `runFilterPP.py`
[`configFlowDataRun2.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configFlowDataRun2.json) | [`dqFlow.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqFlow.cxx) | run with dqFlow.cxx on data run 2 | `runDQFlow.py`
[`configFlowDataRun3.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configFlowDataRun3.json) | [`dqFlow.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqFlow.cxx) | run with dqFlow.cxx on data run 3 | `runDQFlow.py`
[`configV0SelectorDataRun2.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configV0SelectorDataRun2.json) | [`v0selector.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/v0selector.cxx) | run with v0selector.cxx on data run 2 | `runV0selector.py`
[`configV0SelectorDataRun3.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configV0SelectorDataRun3.json) | [`v0selector.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/v0selector.cxx) | run with v0selector.cxx on data run 3 | `runV0selector.py`

W.S : Workflow Script


* JSON Reader Configuations for the Common DQ skimmed tables:

Main File | Data Model | Description
--- | --- | ---
[`readerConfiguration_reducedEvent.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/readerConfiguration_reducedEvent.json) | DQ Skimmed Data Model | For Data
[`readerConfiguration_reducedEventMC.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/readerConfiguration_reducedEventMC.json) | DQ Skimmed Data Model | For MC

* JSON Reader Configuations for the DQ skimmed tables with extra dilepton tables:

Main File | Data Model | Description
--- | --- | ---
[`readerConfiguration_dileptons`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/readerConfiguration_dileptons.json) | DQ Skimmed Data Model With Extra Dilepton Tables | For Data
[`readerConfiguration_dileptonMC`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/readerConfiguration_dileptonMC.json) | DQ Skimmed Data Model With Extra Dilepton Tables | For MC

* JSON Writer Configuations for produce extra dilepton tables in DQ skimmed tables:

Main File | Data Model | Description
--- | --- | ---
[`writerConfiguration_dileptons.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/writerConfiguration_dileptons.json) | DQ Skimmed Data Model | For Data
[`writerConfiguration_dileptonMC.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/writerConfiguration_dileptonMC.json) | DQ Skimmed Data Model | For MC


## DQ Interface Scripts

These scripts are interface scripts with arguments provided by parser_args to configure DQ tasks analysis side.

* Contains DQ Interface Scripts
[`dqtasks`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs)

Interface Script | Workflow Script
--- | --- 
`tableMaker.py`      | `runTableMaker.py`
`tableMakerMC.py`    | `runTablemakerMC.py`
`tableReader.py`     | `runTableReader.py`
`dqEfficiency.py`    | `runDQEfficiency.py`
`filterPP.py`        | `filterPP.py`
 `dqFlow.py`         | `runDQFlow.py`
`v0selector.py`      | `runV0selector.py`

* Important P.S!!! In order to avoid conflicts in the tableMaker Interface, the arguments in the filterPP and dqFlow interfaces have been reduced and moved to the tableMaker interface. That is, although filterPP and dqFlow interfaces have their own interfaces, the tableMaker interface has both its own interface and the reduced interfaces of these 2 scripts (tableMaker + reduced dqFlow + reduced filterPP). It should be considered when configuring the interface for tableMaker, and the original interfaces of dqFlow and filterPP should never be connected to this interface, their reduced versions in tableMaker should be used.

## Common Deps Interface Scripts

These scripts are interface scripts with arguments provided by parser_args to configure DQ tasks common side.

* Contains DQ Interface Scripts
[`commondeps`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/commondeps)

Interface Script | Used in
--- | --- 
`centralityTable.py`      | `runTablemakerMC.py` <br> `runTableMaker.py` <br>  `runV0selector.py` <br> `runDQFlow.py`
`dplAodReader.py`      | `runTablemakerMC.py` <br> `runTableMaker.py` <br>  `runV0selector.py` <br> `runDQFlow.py` <br> `tableReader.py`  <br>  `dqEfficiency.py` 
`eventSelection.py`    | `runTablemakerMC.py` <br> `runTableMaker.py`  <br> `filterPP.py`  <br> `runDQFlow.py`  <br> `runV0selector.py`  
`multiplicityTable.py`     | `runTablemakerMC.py` <br> `runTableMaker.py`  <br> `filterPP.py`  <br> `runDQFlow.py`  <br> `runV0selector.py`
`pidTOFBase.py`    |  `runTablemakerMC.py` <br> `runTableMaker.py`  <br> `filterPP.py`  <br> `runDQFlow.py`  <br> `runV0selector.py`
`pidTOFBeta.py`        | `runTablemakerMC.py` <br> `runTableMaker.py`  <br> `filterPP.py`  <br> `runDQFlow.py`  <br> `runV0selector.py`
`pidTPCTOFFull.py`         | `runTablemakerMC.py` <br> `runTableMaker.py`  <br> `filterPP.py`  <br> `runDQFlow.py`  <br> `runV0selector.py`
`trackPropagation.py`      |  `runTablemakerMC.py` <br> `runTableMaker.py`  <br> `filterPP.py`  <br> `runDQFlow.py`  <br> `runV0selector.py`
`trackselection.py`      |  `runTablemakerMC.py` <br> `runTableMaker.py`  <br> `filterPP.py`  <br> `runDQFlow.py`  <br> `runV0selector.py`

## Extra Modules

Extra modules include some external scripts not related to O2, which are prepared as an support for configuring the workflow and interface

* Contains Extra Modules
[`extramodules`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/extramodules)

Extra Script | Desc
--- | --- 
`ChoicesHandler.py`      | Contains some classes for printing sub helper messages to the screen and autocompletion class for which argument can multiple configurable
`configSetter.py`    | Contains methods that manage JSON configurations via interfaces and helper setter methods (developer package)
`converters.py`     | Contains Interface arguments for O2 converters (ex. o2-analysis-trackpropagation)
`dqExceptions.py`     | Contains some customized exceptions for transaction managements
`dqLibGetter.py`     | To automatically download python libraries in run scripts
`dqTranscations.py`     | To manage dependencies and misconfigurations in the DQ workflow
`helperOptions.py`     | Includes Interface arguments for debug and interface mode options
`pycacheRemover.py`        | For automatically removing pycache files when workflow is finished
`stringOperations.py`        | For managing string operations of multiple arguments in workflows

[↑ Go to the Table of Content ↑](../README.md) | [Continue to Prerequisites →](2_Prerequisites.md)