# Python Scripts And JSON Configs

@tableofcontents

## Main Python Scripts

These scripts are the main python scripts that run the workflows in O2-DQ.

* Script used to run on data or MC the skimming tasks (tableMaker.cxx and tableMakerMC.cxx)
[`runTableMaker.py`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/runTableMaker.py).
* Analyze DQ skimmed data or MC tables. This workflow runs a few tasks: event selection, barrel track selection, muon track selection etc. (tableReader.cxx and dqEfficiency.cxx)
[`runAnalysis.py`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/runAnalysis.py).
* Produces a decision table for pp collisions. The decisions require that at least a selected pair (or just two tracks) exists for a given event. Currently up to 64 simultaneous decisions can be made, to facilitate studies for optimizing cuts. 
[`runFilterPP.py`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/runFilterPP.py).
* Task to compute Q vectors and other quanitites related from the generic framework. Generic framework O2 version is a port of the AliPhysics version. To be used in the DQ analyses aiming for flow measurements.
[`runDQFlow.py`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/runDQFlow.py).
* V0 Selector makes Loops over a V0Data table and produces some standard analysis output.
[`runV0selector.py`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/runV0selector.py).
* Task to select electrons from dalitz decay
[`runDalitzSelection.py`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/runDalitzSelection.py).
* It provides Download needed O2-DQ Libraries (CutsLibrary, MCSignalLibrary, MixingLibrary from O2Physics) for validation and autocompletion in Manual way. You can download libs with version as nightly or you can pull libs from your local alice-software.
[`DownloadLibs.py`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/DownloadLibs.py).

Also We have PWG-EM Dilepton Task, prepared from @rbailhac

* Analysis task for calculating single electron and dielectron efficiency, skimmed or not skimmed version.
[`runEMEfficiency.py`](https://github.com/ctolon/PythonInterfaceOOP/blob/main/runEMEfficiency.py).

They have standard template for running:

`python3 <script.py> <config.json> --task-name:<configurable|processFunc> parameter ...`

ex. for tableMaker:
```ruby
  python3 runTableMaker.py configs/configTableMakerDataRun3.json --internal-dpl-aod-reader:aod-file Datas/AO2D_ppDataRun3_LHC22c.root --table-maker:processMuonOnlyWithCov true --table-maker:processBarrelOnlyWithCov true --event-selection-task:syst pp --table-maker:cfgQA true --table-maker:cfgMuonCuts muonQualityCuts muonTightQualityCutsForTests --table-maker:cfgBarrelTrackCuts jpsiPID1 jpsiPID2 jpsiO2MCdebugCuts --add_track_prop --logFile
```
## Config Files

* Contains workflow configuration files
[`Configs`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/Configs)


* JSON workflow configuration files List in Table (DQ)

Main File | Related Task on O2Physics | Description | W.S
--- | --- | --- | ---
[`configTableMakerDataRun2.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configTableMakerDataRun2.json) | [`TableMaker.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMaker.cxx) | run over Run-2 converted data | `runTableMaker.py` 
[`configTableMakerDataRun3.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configTableMakerDataRun3.json) | [`TableMaker.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMaker.cxx) | run over Run-3 data | `runTableMaker.py` |
[`configTableMakerMCRun2.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configTableMakerMCRun2.json) | [`TableMakerMC.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMakerMC.cxx) | run over Run-2 converted MC | `runTableMaker.py`
[`configTableMakerMCRun3.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configTableMakerMCRun3.json) | [`TableMakerMC.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMakerMC.cxx) | run over Run-3 MC | `runTableMaker.py`
[`configAnalysisData.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configAnalysisData.json) | [`TableReader.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/tableReader.cxx) | run with tableReader.cxx | `runAnalysis.py`
[`configAnalysisMC.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configAnalysisMC.json) | [`dqEfficiency.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqEfficiency.cxx) | run with dqEfficiency.cxx | `runAnalysis.py` 
[`configFilterPPDataRun3.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configFilterPPDataRun3.json) | [`filterPP.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/filterPP.cxx) | run with filterPP.cxx on data run 3 | `runFilterPP.py`
[`configFilterPPDataRun2.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configFilterPPDataRun2.json) | [`filterPP.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/filterPP.cxx) | run with filterPP.cxx on data run 2 | `runFilterPP.py`
[`configFlowDataRun2.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configFlowDataRun2.json) | [`dqFlow.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqFlow.cxx) | run with dqFlow.cxx on data run 2 | `runDQFlow.py`
[`configFlowDataRun3.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configFlowDataRun3.json) | [`dqFlow.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqFlow.cxx) | run with dqFlow.cxx on data run 3 | `runDQFlow.py`
[`configV0SelectorDataRun2.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configV0SelectorDataRun2.json) | [`v0selector.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/v0selector.cxx) | run with v0selector.cxx on data run 2 | `runV0selector.py`
[`configV0SelectorDataRun3.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configV0SelectorDataRun3.json) | [`v0selector.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/v0selector.cxx) | run with v0selector.cxx on data run 3 | `runV0selector.py`
[`configDalitzSelectionDataRun2`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configDalitzSelectionDataRun2.json) | [`DalitzSelection.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/DalitzSelection.cxx) | run with DalitzSelection.cxx.cxx on data run 2 | `runDalitzSelection.py`
[`configDalitzSelectionDataRun3`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/configDalitzSelectionDataRun3.json) | [`DalitzSelection.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/DalitzSelection.cxx) | run with DalitzSelection.cxx.cxx on data run 3 | `runDalitzSelection.py`

* JSON workflow configuration files List in Table (PWG-EM Dilepton)

Main File | Related Task on O2Physics | Description | W.S
--- | --- | --- | ---
[`configAnalysisMCEM.json`](https://github.com/ctolon/PythonInterfaceOOP/blob/main/configs/configAnalysisMCEM.json) | [`emEfficiencyEE.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGEM/Dilepton/Tasks/emEfficiencyEE.cxx) | run with emEfficiencyEE.cxx on MC run 3 (skimmed) | `runEMEfficiency.py`
[`configAnalysisMCEMNoSkimmed.json`](https://github.com/ctolon/PythonInterfaceOOP/blob/main/configs/configAnalysisMCEMNoSkimmed.json) | [`emEfficiencyEE.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGEM/Dilepton/Tasks/emEfficiencyEE.cxx) | run with emEfficiencyEE.cxx on MC run 3 (not skimmed) | `runEMEfficiency.py`

W.S : Workflow Script


* JSON Reader Configuations for the Common DQ skimmed tables:

Main File | Data Model | Description
--- | --- | ---
[`readerConfiguration_reducedEvent.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/readerConfiguration_reducedEvent.json) | DQ Skimmed Data Model | For Data
[`readerConfiguration_reducedEventMC.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/readerConfiguration_reducedEventMC.json) | DQ Skimmed Data Model | For MC

**NOTE**: JSON Reader Configuations also includes extra dilepton tables.


* JSON Writer Configuations for produce extra dilepton tables in DQ skimmed tables:

Main File | Data Model | Description
--- | --- | ---
[`writerConfiguration_dileptons.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/writerConfiguration_dileptons.json) | DQ Skimmed Data Model | For Data
[`writerConfiguration_dileptonMC.json`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/configs/writerConfiguration_dileptonMC.json) | DQ Skimmed Data Model | For MC

## Extra Modules

Extra modules include some external scripts not related to O2, which are prepared as an support for configuring the workflow and interface.

* Contains Extra Modules
[`extramodules`](https://github.com/ctolon/PythonInterfaceOOP/tree/main/extramodules)

Extra Script | Desc
--- | --- 
`ChoicesHandler.py`      | Contains extra autocompletion class for which argument can multiple configurable
`configSetter.py`    | Contains methods that manage JSON configurations via interfaces and helper setter methods (developer package)
`converters.py`     | Contains Interface arguments for O2 converters (ex. o2-analysis-trackpropagation)
`dqExceptions.py`     | Contains some customized exceptions for transaction managements
`dqLibGetter.py`     | To automatically download DQ libraries as headers with dependency injection in run scripts
`dqTranscations.py`     | To manage dependencies and misconfigurations in the DQ workflow
`pycacheRemover.py`        | For automatically removing pycache files when workflow is finished (For cache protection)
`utils.py`        | For managing basic operations with simple methods.

[↑ Go to the Table of Content ↑](../README.md) | [Continue to Prerequisites →](2_Prerequisites.md)