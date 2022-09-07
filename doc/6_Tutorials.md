# Tutorial Part

@tableofcontents

Firstly, clone repository in your workspace

`git clone https://github.com/ctolon/PythonInterfaceDemo.git`

Before you start, you need to do the installations in the readme file

P.S. Don't forget to install the O2 enviroment before running the scripts

Ex. `alienv enter O2Physics/latest,QualityControl/latest`

Assuming you have installed the argcomplete package, don't forget to source the bash script again in your O2 enviroment.

`source argcomplete.sh`

If you don't have time to read the documentation follow these steps:

For Linux Based System:

* `alienv enter O2Physics/latest,QualityControl/latest` (Load Your alienv, if you want you can install lxplus version without using QC)
* `pip install argcomplete` and `pip3 install argcomplete`
* `source argcomplete.sh`

For MacOS Based System:

* `brew install bash`
* `alienv enter O2Physics/latest,QualityControl/latest` (Load Your alienv, if you want you can install lxplus version without using QC)
* `pip install argcomplete` and `pip3 install argcomplete`
* `exec bash` (temporary bash shell)
* `source argcomplete.sh`

if not works:

* `sudo chsh -s /bin/bash <username>`
* `source argcomplete.sh`

if you used the command `sudo chsh -s /bin/bash <username>` after you are done with the scripts (It converts your system shell zsh to bash):

* `sudo chsh -s /bin/zsh <username>` (It converts your system shell bash to zsh)


if you used the command `exec bash` you don't need to do anything.

## Download Datas For Tutorials

You can Found MC Datas, pre-made JSON config files and DQ Skimmed datas for tutorial at: [Click Here](https://cernbox.cern.ch/index.php/s/XWOFJVaBxiIw0Ft) password: DQ

Create a new folder in NewAllWorkflows directory with `mkdir Datas` and move the downloaded datas here.

You can found Real Data for pp at : [Click Here](https://alimonitor.cern.ch/catalogue/index.jsp?path=%2Falice%2Fdata%2F2022%2FLHC22c%2F517616%2Fapass1#/alice/data/2022/LHC22c/517616/apass1)

You can found Real Data for PbPb at : [Click Here](https://alimonitor.cern.ch/prod/jobs.jsp?t=20117&outputdir=PWGZZ/Run3_Conversion/242_20211215-1006_child_2$)

or [Click Here](https://cernbox.cern.ch/index.php/s/6KLIdQdAlNXj5n1)

P.S: Dont forget the change name of AO2D.root files for interface and Move this datas to you previously create Datas Folder.

For PbPb Data : AO2D.root to AO2D_PbPbDataRun2_LHC15o.root

For pp Data : AO2D.root to AO2D_ppDataRun3_LHC22c.root

If you downloaded these datasets, you can start.

## Workflows In Tutorials

* For MC:

Workflow | Dataset | Skimmed | Process | Type | Col Syst
--- | --- | --- | --- | --- | --- |
`tableMakerMC` | `LHC21i3d2` | `No` | `MuonOnlyWithCov`<br>`OnlyBCs` | J/ψ → μ<sup>+</sup> μ<sup>−</sup> | `pp`
`dqEfficiency` | `LHC21i3d2` | `Yes`  | `JpsiToMuMu` | J/ψ → μ<sup>+</sup> μ<sup>−</sup> | `pp`
`tableMakerMC` | `LHC21i3b` | `No` | `BarrelOnly`<br>`OnlyBCs` | J/ψ → e<sup>+</sup> e<sup>−</sup> | `pp`
`dqEfficiency` | `LHC21i3b` | `Yes` | `JpsiToEE` | J/ψ → e<sup>+</sup> e<sup>−</sup>  | `pp`
`tableMakerMC` | `LHC21i3f2` | `No` | `BarrelOnly`<br>`OnlyBCs` | h<sub>B</sub> →  J/ψ + *X*, J/ψ → e<sup>+</sup> e<sup>−</sup>  | `pp`
`dqEfficiency` | `LHC21i3f2` | `Yes` | `JpsiToEE` | h<sub>B</sub> →  J/ψ + *X*, J/ψ → e<sup>+</sup> e<sup>−</sup>  | `pp`

* For Data:

Workflow | Dataset | Skimmed | Process | Selection | Col Syst
--- | --- | --- | --- | --- | --- |
`tableMaker` | `LHC15o` | `No` | `BarrelOnlyWithCent`<br>`OnlyBCs` | J/ψ → e<sup>+</sup> e<sup>−</sup> | `PbPb`
`tableReader`  | `LHC15o` | `Yes`  | `JpsiToEE` | J/ψ → e<sup>+</sup> e<sup>−</sup> | `PbPb`
`tableMaker` | `LHC15o` | `No` | `FullWithCent`<br>`BarrelOnlyWithQvector`<br>`OnlyBCs` | J/ψ → e<sup>+</sup> e<sup>−</sup> | `PbPb`
`tableReader` | `LHC15o` | `Yes`  | `VnJpsiToEE` | J/ψ → e<sup>+</sup> e<sup>−</sup> | `PbPb`
`dqFlow` | `LHC15o` | `No` | - | - | `PbPb`
`v0Selector` | `LHC15o` | `No`  | - | - | `PbPb`
`tableMaker` | `LHC22c` | `No` | `MuonOnlyWithCov`<br>`OnlyBCs` | J/ψ → μ<sup>+</sup> μ<sup>−</sup> | `pp`
`tableReader` | `LHC22c` | `Yes`  | `JpsiToMuMuVertexing` | J/ψ → μ<sup>+</sup> μ<sup>−</sup> | `pp`
`filterPP` | `fwdprompt` | `No`  | `eventSelection` <br> `barrelTrackSelection`  <br> `muonSelection` | All Events | `pp`


Workflow | Dataset | Process | Type | Col Syst
--- | --- | --- | --- | --- |
`dqEfficiency` | `AO2D_Bc100` | `JpsiToMuMuVertexing`<br>`dileptonTrackDimuonMuonSelection`  | B<sub>c</sub> → J/ψ → (μ<sup>+</sup> μ<sup>−</sup>) + μ | `pp`
`tableReader`  | `LHC15o` | `JpsiToEE`<br>`dileptonHadron` | `dileptonhadron` | `PbPb`


TO BE ADDED IN TUTORIALS (Not Prepared Yet): 

Workflow | Dataset | Process | Type | Col Syst
--- | --- | --- | --- | --- |
`dqEfficiency` | `AO2D_Bplus` | `JpsiToMuMuVertexing`<br>`dileptonTrackDimuonMuonSelection`  |B<sup>+</sup> → J/ψ + K, → J/ψ → e<sup>+</sup> e<sup>−</sup> | `pp`

## Skimmed Datas In Tutorials

Reduced DQ skimmed data list created with tableMaker/tableMakerMC:

Data | Dataset | Used Workflow | Selected Processes (from tableMaker) |
--- | --- | --- | --- |
`reducedAod_ppMC_LHC21i3d2.root` | `LHC21i3d2` | `tableMakerMC` | `MuonOnlyWithCov`<br>`OnlyBCs`
`reducedAod_ppMC_LHC21i3b.root` | `LHC21i3b` | `tableMakerMC` | `BarrelOnly`<br>`OnlyBCs`
`reducedAod_ppMC_LHC21i3f2.root` | `LHC21i3f2` | `tableMakerMC` | `BarrelOnly`<br>`OnlyBCs`
`reducedAod_ppMC_Bc100.root` | `Bc100` | `tableMakerMC` | `MuonOnlyWithCov`<br>`OnlyBCs`
`reducedAod_PbPbData_LHC15o.root` | `LHC15o` | `tableMaker` | `BarrelOnlyWithCent`<br>`OnlyBCs`
`reducedAod_PbPbData_LHC15o_Flow.root` | `LHC15o` | `tableMaker` | `FullWithCent`<br>`BarrelOnlyWithQvector`<br>`OnlyBCs`
`reducedAod_PbPbData_LHC15o_dileptonHadron.root` | `LHC15o` | `tableMaker` | `BarrelOnly`<br>`OnlyBCs`
`reducedAod_ppData_LHC222c.root` | `LHC222c` | `tableMaker` | `MuonOnlyWithCov`<br>`OnlyBCs`

Reduced DQ Dileptons skimmed data list For Dilepton Analysis (dilepton-track and dilepton-hadron) created with tableReader/dqEfficiency:

Data | Dataset | Used Workflow | Selected Processes (from tableMaker) |
--- | --- | --- | --- |
`dileptonAOD_ppMC_BC100.root` | `Bc100` | `dqEfficiency` | `MuonOnlyWithCov`<br>`OnlyBCs`
`dileptonAOD_PbPbData_LHC15o_dileptonHadron.root` | `LHC15o` | `tableReader` | `BarrelOnly`<br>`OnlyBCs`

## Pre-Made JSON configuration Files In Tutorials

Config JSON list created with Scripts.

Common JSON Configs:

Config | For | Description
--- | --- | --- |
`configAnalysis_LHC21i3b_MC.json` | `MCRun3` | Run dqEfficiency on LHC21i3b Simulation → reducedAod_ppMC_LHC21i3b.root
`configAnalysis_LHC21i3d2_MC.json` | `MCRun3` | Run dqEfficiency on LHC21i3d2 Simulation → reducedAod_ppMC_LHC21i3d2.root
`configAnalysis_LHC21i3f2_MC.json` | `MCRun3` | Run dqEfficiency on LHC21i3f2 Simulation → reducedAod_ppMC_LHC21i3f2.root
`ConfigAnalysis_LHC15o_Data.json` | `DataRun2` | Run tableReader on LHC15o Data without flow → reducedAod_PbPbData_LHC15o.root
`ConfigAnalysis_LHC15o_Flow_Data.json` | `DataRun2` | Run tableReader on LHC15o Data for Flow Analysis → reducedAod_PbPbData_LHC15o_Flow.root
`ConfigAnalysis_LHC22c_Data.json` | `DataRun3` | Run tableReader on LHC22c Data → reducedAod_PbPbData_LHC15o.root
`configTableMaker_LHC21i3b_MCRun3.json` | `MCRun3` | Run tableMakerMC on LHC21i3b Simulation → AO2D_ppMCRun3_LHC21i3b.root
`configTableMaker_LHC21i3d2_MCRun3.json` | `MCRun3` | Run tableMakerMC on LHC21i3d2 Simulation → AO2D_ppMCRun3_LHC21i3d2.root
`configTableMaker_LHC21i3f2_MCRun3.json` | `MCRun3` | Run tableMakerMC on LHC21i3f2 Simulation → AO2D_ppMCRun3_LHC21i3f2.root
`ConfigTableMaker_LHC15o_DataRun2.json` | `DataRun2` | Run tableMaker on LHC15o without Flow → AO2D_PbPbDataRun2_LHC15o.root
`ConfigTableMaker_LHC15o_Flow_DataRun2.json` | `DataRun2` | Run tableMaker on LHC15o For Flow Analysis → AO2D_PbPbDataRun2_LHC15o.root
`ConfigTableMaker_LHC22c_DataRun3.json` | `DataRun3` | Run tableMaker on LHC22c Data → AO2D_ppDataRun3_LHC22c.root
`configV0Selector_LHC15o_DataRun2.json` | `DataRun2` | Run v0Selector on LHC15o Data → AO2D_PbPbDataRun2_LHC15o.root

JSON Configs for Single Workflows:

Config | For | Description
--- | --- | --- |
`configFilterPP_fwdprompt_Run3.json` | `MCRun3` | Run filterPP on fwdprompt → AO2D_fwdprompt.root
`configFlow_LHC15o_DataRun2.json` | `DataRun2` | Run dqFlow on LHC15o Data  → AO2D_PbPbDataRun2_LHC15o.root
`configV0Selector_LHC15o_DataRun2.json` | `DataRun2` | Run v0Selector on LHC15o Data → AO2D_PbPbDataRun2_LHC15o.root

JSON Configs for dilepton-hadron and dilepton-track analysis:

Config | For | Description
--- | --- | --- |
`configTableMaker_Bc100_MCRun3.json` | `MCRun3` | Run tableMakerMC on Bc100 Simulation for prepare dilepton-track analysis → AO2D_Bc100.root
`configAnalysis_Bc100_MC.json` | `MCRun3` | Run dqEfficiency on Bc100 Simulation for prepare skimmed dileptons output → reducedAod_ppMC_Bc100.root
`configAnalysisDilepton_Bc100_MC.json` | `MCRun3` | Run dqEfficiency on Bc100 Simulation for dilepton analysis → dileptonAOD_ppMC_BC100.root
`configTableMaker_LHC15o_DileptonHadron_DataRun2.json` | `DataRun2` | Run tableMaker on LHC15o Data for prepare dilepton-hadron analysis → AO2D_PbPbDataRun2_LHC15o.root
`configAnalysis_LHC15o_dileptonHadron_Data.json` | `DataRun2` | Run tableReader on LHC15o Data for prepare skimmed dileptons output → reducedAod_PbPbData_LHC15o_dileptonHadron.root
`configAnalysisDilepton_LHC15o_dileptonHadron_Data.json` | `DataRun2` | Run tableReader on LHC15o Data for dilepton analysis → reducedAod_PbPbData_LHC15o_dileptonHadron.root

P.S. Root files are inputs for JSON configs

## MC Part

### Run tableMakerMC on LHC21i3d2 (jpsi to MuMu pp Run3Simulation)

Command To Run:

```ruby
python3 runTableMaker.py Configs/configTableMakerMCRun3.json -runMC --aod Datas/AO2D_ppMCRun3_LHC21i3d2.root --process MuonOnlyWithCov OnlyBCs --syst pp --cfgWithQA true --cfgMCsignals muFromJpsi Jpsi muon --cfgMuonCuts muonQualityCuts muonTightQualityCutsForTests --add_track_prop --debug debug --logFile
```

 ### Run dqEfficiency on MC (LHC21i3d2 pp Run3Simulation)

You need to produce reducedAod.root file with tableMakerMC in previous step.

Command To Run:

```ruby
python3 runDQEfficiency.py Configs/configAnalysisMC.json --aod reducedAod.root --analysis muonSelection eventSelection sameEventPairing --process JpsiToMuMu --cfgQA true --cfgMuonCuts muonQualityCuts muonTightQualityCutsForTests --cfgMuonMCSignals muFromJpsi --cfgBarrelMCGenSignals Jpsi --cfgBarrelMCRecSignals mumuFromJpsi dimuon --debug debug --logFile
```

### Run tablemakerMC on LHC21i3b (Prompt jpsi to dilectron pp Run3Simulation)

Command To Run:

```ruby
python3 runTableMaker.py Configs/configTableMakerMCRun3.json -runMC --aod Datas/AO2D_ppMCRun3_LHC21i3b.root --process OnlyBCs BarrelOnly --syst pp --cfgWithQA true --cfgBarrelTrackCuts jpsiO2MCdebugCuts --cfgMCsignals electronPrimary eFromJpsi Jpsi LMeeLF LMeeLFQ --debug debug --logFile
```

 ### Run dqEfficiency on MC (LHC21i3b pp Run3Simulation)

You need to produce reducedAod.root file with tableMakerMC in previous step.

Command To Run:

```ruby
python3 runDQEfficiency.py Configs/configAnalysisMC.json --aod reducedAod.root --analysis trackSelection eventSelection sameEventPairing --process JpsiToEE --cfgQA true --cfgBarrelMCGenSignals Jpsi --cfgBarrelMCRecSignals eeFromJpsi dielectron --cfgTrackCuts jpsiO2MCdebugCuts --cfgTrackMCSignals eFromJpsi --debug debug --logFile
```

### Run tablemakerMC on LHC21i3f2 (Non-Prompt jpsi to dilectron pp Run3Simulation)

Command To Run:

```ruby
python3 runTableMaker.py Configs/configTableMakerMCRun3.json -runMC --aod Datas/AO2D_ppMCRun3_LHC21i3f2.root --process OnlyBCs BarrelOnly --syst pp --cfgWithQA true --cfgBarrelTrackCuts jpsiO2MCdebugCuts --cfgMCsignals electronPrimary eFromJpsi eFromNonpromptJpsi eFromLMeeLF LMeeLF Jpsi everythingFromBeauty --debug debug --logFile
```

 ### Run dqEfficiency on LHC21i3f2 (LHC21i3f2 pp Run3Simulation)

You need to produce reducedAod.root file with tableMakerMC in previous step.

Command To Run:

```ruby
python3 runDQEfficiency.py Configs/configAnalysisMC.json --aod reducedAod.root --analysis trackSelection eventSelection sameEventPairing --process JpsiToEE --cfgQA true --cfgBarrelMCGenSignals Jpsi nonPromptJpsi --cfgBarrelMCRecSignals eeFromJpsi dielectron --cfgTrackCuts jpsiO2MCdebugCuts --cfgTrackMCSignals eFromJpsi eFromNonpromptJpsi --debug debug --logFile
```

## Data Part

### Run tableMaker on LHC15o (LHC15o PbPb Run2Data)

Command To Run:

```ruby
python3 runTableMaker.py Configs/configTableMakerDataRun2.json -runData --aod Datas/AO2D_PbPbDataRun2_LHC15o.root --process OnlyBCs BarrelOnlyWithCent --syst PbPb --cfgWithQA true --est Run2V0M --cfgBarrelTrackCuts jpsiPID1 jpsiPID2 --add_fdd_conv --debug debug --logFile
```

### Run tableReader on LHC15o (LHC15o PbPb Run2Data)

You need to produce reducedAod.root file with tableMaker in previous step.

Command To Run:

```ruby
python3 runTableReader.py Configs/configAnalysisData.json --aod reducedAod.root --analysis eventSelection trackSelection eventMixing sameEventPairing --process JpsiToEE --cfgQA true --cfgTrackCuts jpsiPID1 jpsiPID2 --debug debug --logFile
```

### Run tableMaker on LHC15o With Generic Flow Analysis (LHC15o PbPb Run2Data)

Command To Run:

```ruby
python3 runTableMaker.py Configs/configTableMakerDataRun2.json -runData --aod Datas/AO2D_PbPbDataRun2_LHC15o.root --process OnlyBCs FullWithCent BarrelOnlyWithQvector --syst PbPb --cfgWithQA true --est Run2V0M --cfgBarrelTrackCuts jpsiPID1 jpsiPID2 --add_fdd_conv --debug debug --logFile
```

### Run tableReader on LHC15o with Generic Flow Analysis (LHC15o PbPb Run2Data)

You need to produce reducedAod.root file with tableMaker in previous step.

Command To Run:

```ruby
python3 runTableReader.py Configs/configAnalysisData.json --aod reducedAod.root --analysis eventSelection trackSelection eventMixingVn sameEventPairing --process VnJpsiToEE --cfgQA true --cfgTrackCuts jpsiPID1 jpsiPID2 --debug debug --logFile
```

### Run dqFlow on LHC15o (LHC15o PbPb Run2Data)

Command To Run:

```ruby
python3 runDQFlow.py Configs/configFlowDataRun2.json --aod Datas/AO2D_PbPbDataRun2_LHC15o.root --syst PbPb --cfgWithQA true --est Run2V0M --FT0 Run2 --cfgBarrelTrackCuts jpsiPID1 jpsiPID2 --cfgMuonCuts muonQualityCuts muonTightQualityCutsForTests --isVertexZeq false --add_fdd_conv --debug debug --logFile
```
### Run v0Selector on LHC15o (LHC15o PbPb Run2Data)

Command To Run:

```ruby
python3 runV0selector.py Configs/configV0SelectorDataRun2.json --aod Datas/AO2D_PbPbDataRun2_LHC15o.root --add_fdd_conv --isVertexZeq false
```

### Run tableMaker on LHC22c (LHC22c pp Run3Data)

Command To Run:

```ruby
python3 runTableMaker.py Configs/configTableMakerDataRun3.json -runData --aod Datas/AO2D_ppDataRun3_LHC22c.root --process OnlyBCs MuonOnlyWithCov --syst pp --cfgWithQA true --cfgMuonsCuts muonQualityCuts --cfgMuonCuts muonQualityCuts muonTightQualityCutsForTests --add_track_prop --isVertexZeq false --debug debug --logFile
```

### Run tableReader on Data (LHC22c pp Run3Data)

You need to produce reducedAod.root file with tableMaker in previous step.

Command To Run:

```ruby
python3 runTableReader.py Configs/configAnalysisData.json --aod reducedAod.root --analysis eventSelection muonSelection sameEventPairing --process JpsiToMuMuVertexing --cfgQA true --cfgMuonCuts muonQualityCuts muonTightQualityCutsForTests --debug debug --logFile
```

### Run filterPP on fwdprompt(fwdprompt pp Run3Data)

Command To Run:

```ruby
python3 runFilterPP.py Configs/configFilterPPDataRun3.json --aod Datas/AO2D_fwdprompt.root --process barrelTrackSelection eventSelection muonSelection --syst pp --cfgBarrelTrackCuts jpsiO2MCdebugCuts jpsiPID2 --cfgBarrelSels jpsiO2MCdebugCuts:pairNoCut:1 jpsiPID2::1 --cfgMuonsCuts muonLowPt muonHighPt muonLowPt --cfgMuonSels muonLowPt::1 muonHighPt::1 muonLowPt:pairUpsilon:1 --isVertexZeq false --debug debug --logFile
```

## Special Part : Dilepton Analysis For Non-Standart Existing Workflows in DQ

This section includes analysis with non-standard workflows in DQ workflows. These analyzes are carried out in 3 stages:

1. DQ skimmed data is created with TableMaker/tableMakerMC (input: AO2D.root, output: AnalysisResults.root)

2. DQ skimmed extra dilepton tables are created with tableReader/dqEfficiency and with this way new DQ skimmed data with extra dilepton tables are created on dileptonAod.root, Normally reducedAod.root that does not contains dilepton tables (input : reducedAod.root, output: AnalysisResults.root and dileptonAod.root)

3. With tableReader/dqEfficiency, analysis is performed on DQ skimmed dilepton data created earlier (input: dileptonAod.root and output: AnalysisResults.root)

### MC : Dilepton Track Analysis (On Bc Simulation)

First Command To Run:

```ruby
python3 runTableMaker.py Configs/configTableMakerMCRun3.json -runMC --aod Datas/AO2D_Bc100.root --process MuonOnlyWithCov OnlyBCs --syst pp --cfgMCsignals Jpsi Bc anyBeautyHadron --cfgMuonCuts matchedGlobal --cfgMuonLowPt 0.0 --debug debug --logFile
```

Second Command To Run:

```ruby
python3 runDQEfficiency.py Configs/configAnalysisMC.json --aod reducedAod.root --analysis eventSelection muonSelection sameEventPairing --process JpsiToMuMuVertexing --cfgQA true --cfgMuonCuts matchedGlobal --cfgMuonMCSignals muon muFromJpsi muFromBc dimuon --cfgBarrelMCGenSignals Jpsi --cfgBarrelMCRecSignals mumuFromJpsi --cfgBarrelDileptonMCRecSignals mumuFromJpsiFromBc mumumuFromBc --cfgBarrelDileptonMCGenSignals Jpsi --debug debug --logFile
```
Third Command To Run:

```ruby
python3 runDQEfficiency.py Configs/configAnalysisMC.json --aod dileptonAOD.root --analysis eventSelection muonSelection dileptonTrackDimuonMuonSelection sameEventPairing --process JpsiToMuMuVertexing --cfgMuonCuts matchedGlobal --cfgMuonMCSignals muon muFromJpsi muFromBc dimuon --cfgBarrelMCGenSignals Jpsi --cfgBarrelMCRecSignals mumuFromJpsi --cfgBarrelDileptonMCRecSignals mumuFromJpsiFromBc mumumuFromBc --cfgBarrelDileptonMCGenSignals Jpsi --debug debug --logFile
```

### Data : Dilepton Hadron Analysis (On PbPb Data LHC15o)

First Command To Run:

```ruby
python3 runTableMaker.py Configs/configTableMakerDataRun2.json -runData --aod Datas/AO2D_PbPbDataRun2_LHC15o.root --process OnlyBCs BarrelOnly --syst PbPb --cfgWithQA true --est Run2V0M --cfgBarrelTrackCuts jpsiPID1 jpsiPID2 --add_fdd_conv --debug debug --logFile
```

Second Command To Run:

```ruby
python3 runTableReader.py Configs/configAnalysisData.json --aod reducedAod.root --analysis eventSelection trackSelection sameEventPairing --process JpsiToEE --cfgQA true --cfgTrackCuts jpsiPID1 jpsiPID2 --debug debug --logFile
```

Third Command To Run:

```ruby
python3 runTableReader.py Configs/configAnalysisData.json --aod dileptonAOD.root --analysis eventSelection trackSelection sameEventPairing dileptonHadron --process JpsiToEE --cfgQA true --cfgTrackCuts jpsiPID1 jpsiPID2 --debug debug --logFile
```

[← Go back to Instructions For Python Scripts](5_InstructionsForPythonScripts.md) | [↑ Go to the Table of Content ↑](../README.md) | [Continue to Design Notes →](7_DesignNotes.md)