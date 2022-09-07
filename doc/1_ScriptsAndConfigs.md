# Python Scripts And JSON Configs

@tableofcontents

## Main Python Scripts

* Script used to run both the skimming tasks (tableMaker.cxx and tableMakerMC.cxx)
[`runTableMaker.py`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/runTableMaker.py).
* Analyze DQ skimmed data tables. This workflow runs a few tasks: event selection, barrel track selection, muon track selection etc.
[`runTableReader.py`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/runTableMaker.py).
* Which contains the tasks DQEventSelection for event selection, DQBarrelTrackSelection for barrel track selection and single track MC matching, and the DQQuarkoniumPairing for reconstructed track pairing, MC matching of the pairs and counting of generated MC signals.  
[`runDQEfficiency.py`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/runDQEfficiency..py).
* Produces a decision table for pp collisions. The decisions require that at least a selected pair (or just two tracks) exists for a given event. Currently up to 64 simultaneous decisions can be made, to facilitate studies for optimizing cuts. 
[`runFilterPP.py`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/runFilterPP.py).
* Task to compute Q vectors and other quanitites related from the generic framework. Generic framework O2 version is a port of the AliPhysics version. To be used in the DQ analyses aiming for flow measurements 
[`runDQFlow.py`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/runDQFlow.py).
* V0 Selector makes Loops over a V0Data table and produces some standard analysis output.
[`runV0selector.py`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/runV0selector.py).
* It provides Download needed O2-DQ Libraries (CutsLibrary, MCSignalLibrary, MixingLibrary from O2Physics) for validation and autocompletion in Manual way. You can download libs with version as nightly
[`DownloadLibs.py`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/DownloadLibs.py).

## Config Files

* Contains workflow configuration files
[`Configs`](https://github.com/ctolon/PythonInterfaceDemo/tree/main/NewAllWorkFlows/Configs)


* JSON workflow configuration files List in Table

Main File | Related Task on O2Physics | Description
--- | --- | ---
[`configTableMakerDataRun2.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/configTableMakerDataRun2.json) | [`TableMaker.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMaker.cxx) | run over Run-2 converted data
[`configTableMakerDataRun3.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/configTableMakerDataRun3.json) | [`TableMaker.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMaker.cxx) | run over Run-3 data
[`configTableMakerMCRun2.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/configTableMakerMCRun2.json) | [`TableMakerMC.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMakerMC.cxx) | run over Run-2 converted MC
[`configTableMakerMCRun3.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/configTableMakerMCRun3.json) | [`TableMakerMC.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/TableProducer/tableMakerMC.cxx) | run over Run-3 MC
[`configAnalysisData.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/configAnalysisData.json) | [`TableReader.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/tableReader.cxx) | run with tableReader.cxx
[`configAnalysisMC.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/configAnalysisMC.json) | [`dqEfficiency.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqEfficiency.cxx) | run with dqEfficiency.cxx
[`configFilterPPDataRun3.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/configFilterPPDataRun3.json) | [`filterPP.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/filterPP.cxx) | run with filterPP.cxx
[`configFilterPPDataRun2.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/configFilterPPDataRun2.json) | [`filterPP.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/filterPP.cxx) | run with filterPP.cxx
[`configFlowDataRun2.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/configFlowDataRun2.json) | [`dqFlow.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqFlow.cxx) | run with dqFlow.cxx
[`configFlowDataRun3.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/configFlowDataRun3.json) | [`dqFlow.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/dqFlow.cxx) | run with dqFlow.cxx
[`configV0SelectorDataRun2.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/configV0SelectorDataRun2.json) | [`v0selector.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/v0selector.cxx) | run with v0selector.cxx
[`configV0SelectorDataRun3.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/configV0SelectorDataRun3.json) | [`v0selector.cxx`](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Tasks/v0selector.cxx) | run with v0selector.cxx


* JSON Reader Configuations for the Common DQ skimmed tables:

Main File | Data Model | Description
--- | --- | ---
[`readerConfiguration_reducedEvent.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/readerConfiguration_reducedEvent.json) | DQ Skimmed Data Model | For Data
[`readerConfiguration_reducedEventMC.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/readerConfiguration_reducedEventMC.json) | DQ Skimmed Data Model | For MC

* JSON Reader Configuations for the DQ skimmed tables with extra dilepton tables:

Main File | Data Model | Description
--- | --- | ---
[`readerConfiguration_dileptons`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/readerConfiguration_dileptons.json) | DQ Skimmed Data Model With Extra Dilepton Tables | For Data
[`readerConfiguration_dileptonMC`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/readerConfiguration_dileptonMC.json) | DQ Skimmed Data Model With Extra Dilepton Tables | For MC

* JSON Writer Configuations for produce extra dilepton tables in DQ skimmed tables:

Main File | Data Model | Description
--- | --- | ---
[`writerConfiguration_dileptons.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/writerConfiguration_dileptons.json) | DQ Skimmed Data Model | For Data
[`writerConfiguration_dileptonMC.json`](https://github.com/ctolon/PythonInterfaceDemo/blob/main/NewAllWorkFlows/Configs/writerConfiguration_dileptonMC.json) | DQ Skimmed Data Model | For MC

[↑ Go to the Table of Content ↑](../README.md) | [Continue to Prerequisites →](2_Prerequisites.md)