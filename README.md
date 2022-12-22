# User Python Based Interface for O2-DQ Framework

\tableofcontents

[![doxygen](https://img.shields.io/badge/doxygen-documentation-blue.svg)](https://dquserinterfaceoop.github.io/docs/html/)

This project includes python based user interface development for PWG-DQ Workflows based on nightly-20222212. You can follow the instructions and you can find tutorials in table of contents at the end of the page (For prerequisites, Installation guide for argcomplete and Some Informations good to know).

## Contact
Ionut Cristian Arsene (Owner of [`O2DQWorkflows`](https://github.com/iarsene/O2DQworkflows))

* Contact: iarsene@cern.ch / i.c.arsene@fys.uio.no 

Cevat Batuhan Tolon (Author Of Interface)

* Contact: cevat.batuhan.tolon@cern.ch

If you are having problems with scripts, you can first ask your questions on mattermost directly to @ctolon account or via e-mail at cevat.batuhan.tolon@cern.ch.


## Important

Since the interface is constantly updated for stability, it is recommended to update it with `git pull --rebase` command

## Standard Run Template

We have standard run template for each run workflow python scripts.

Template:

`python3 <script.py> <config.json> --task-name:<configurable|processFunc> parameter ...`

* `script.py` e.g:
  * runAnalysis.py 
  * runTableMaker.py

* `config.json` e.g:
  * configTableMakerDataRun3.json
  * configAnalysisMC.json

Note: You should provide config.json with full path! Like that: (configs/configAnalysisMC.json) 

* `--task-name:<configurable|processFunc> parameter` e.g:
  * --table-maker:processBarrelOnly true 
  * --analysis-same-event-pairing:cfgTrackCuts jpsiPID1 jpsiPID2
  * --analysis-event-selection:processSkimmed true --analysis-track-selection:cfgTrackCuts jpsiPID1 jpsiPID2


Switcher Variables (in boolean type): `runOverMC` and `runOverSkimmed` (you can found runOverMC variable under the main() functions in runTableMaker.py and runAnalysis.py scripts, runOverSkimmed in runEMEfficiency.py script).

Variable in script | Workflow Script | Value | Selected Task | Taskname in config
--- | --- | --- | --- | --- | 
runOverMC | runTableMaker.py | `False` | tableMaker.cxx | table-maker
runOverMC | runTableMaker.py | `True` | tableMakerMC.cxx | table-maker-m-c
runOverMC | runAnalysis.py | `False` | tableReader.cxx | analysis-event-selection (For Real Data Analysis)
runOverMC | runAnalysis.py | `True` | dqEfficiency.cxx | analysis-event-selection (For MC Analysis)
runOverSkimmed | runEMEfficiency.py | `False` | emEfficiency.cxx | analysis-event-selection (It will run with not skimmed data)
runOverSkimmed | runEMEfficiency.py | `True` | emEfficiency.cxx | analysis-event-selection (It will run with skimmed data)

**IMPORTANT NOTE:** It creates interface arguments by parsing the json before executing the script with dependency injection, so it is very important that you configure it correctly! 

e.g. for run tableMaker.cxx with runTableMaker.py script (runOverMC is have to be False in script):

```ruby
  python3 runTableMaker.py configs/configTableMakerDataRun3.json --internal-dpl-aod-reader:aod-file Datas/AO2D_ppDataRun3_LHC22c.root --table-maker:processMuonOnlyWithCov true --table-maker:processBarrelOnlyWithCov true --event-selection-task:syst pp --table-maker:cfgQA true --table-maker:cfgMuonCuts muonQualityCuts muonTightQualityCutsForTests --table-maker:cfgBarrelTrackCuts jpsiPID1 jpsiPID2 jpsiO2MCdebugCuts --add_track_prop --logFile
```

## Which things are changed?

* Some Scripts have been merged:
* The runTableMaker.py and runTableMakerMC.py scripts have been merged into the runTableMaker.py script.
  * **IMPORTANT**: You need Switch runOverMC variable to True in the script if you want work on tableMakerMC for MC else it will run for tableMaker for Data
* The runTableReader.py and runDQEfficiency.py scripts have been merged into the runAnalysis.py script.
  * **IMPORTANT**: You need Switch runOverMC variable to True in the script if you want work on dqEfficiency for MC else it will run for tableMaker for Data
* the runEMEfficiency.py an runEMEfficiencyNotSkimmed.py scripts have been merged into the the runEMEfficiency.py script.
  * **IMPORTANT**: You need Switch runOverSkimmed variable to True in the script if you want work on skimmed EM efficiency else it will run for not Skimmed EM efficiency

* The argument parameter template has changed, now for each task, arguments in the form of doublets separated by separate colons are given, and then parameters are given (Template: `python3 <script.py> >config.json> --taskname:<configurable|processFunction> <parameters>`).
  * OLD TEMPLATE e.g: `python3 runTableMaker.py configs/configTableMakerDataRun3.json --table-maker:processBarrelOnly true --table-maker:cfgBarrelTrackCuts jpsiPID1 jpsiPID2 `
  * NEW TEMPLATE e.g: `python3 runTableMaker.py configs/configTableMakerDataRun3.json --table-maker:processBarrelOnly true --table-maker:cfgBarrelTrackCuts jpsiPID1 jpsiPID2 `

* Now interface arguments are not hard coded but dynamically generated by parsing JSON files. That's why interface scripts were deleted.

* Since the arguments are configured according to the tasks, it is necessary to configure some configurations separately for each task. For example, when configuring cfgTrackCuts, in the old version of interface all cfgTrackCuts configs in JSON config files were configured, now they are configured for each task separately (important to keep in your mind!).


## Modifying the scripts

You can refer to this chapter to modify scripts:

[Developer Guide](doc/7_DeveloperGuide.md)

## For Newcomers (NOT INTEGRATED YET!)

If you don't know much about these python scripts or if you want to understand the structure of the scripts line by line, there are explanation documentation for each script, line by line or code blocks (Since utility functions are not explained in depth in this section, you can read and examine these functions directly from the doc strings of python scripts, or you can get short explanations from the developer guide section)

- [runTableMaker Line-by-Line Explanation](doc/workflowscripts/1_runTableMaker.md)

## Table Of Contents
- [Python Scripts And JSON Configs](doc/1_ScriptsAndConfigs.md)
  - [Main Python Scripts](doc/1_ScriptsAndConfigs.md#main-python-scripts)
  - [Config Files](doc/1_ScriptsAndConfigs.md#config-files)
  - [Extra Modules](doc/1_ScriptsAndConfigs.md#extra-modules)
- [Prerequisites!!!](doc/2_Prerequisites.md)
  - [Cloning repository](doc/2_Prerequisites.md#cloning-repository)
  - [argcomplete - Bash tab completion for argparse](doc/2_Prerequisites.md#argcomplete---bash-tab-completion-for-argparse)
  - [Instalation Guide For argcomplete](doc/2_Prerequisites.md#instalation-guide-for-argcomplete)
    - [Prerequisites Before Installation argcomplete Package For Linux Based Systems and LXPLUS](doc/2_Prerequisites.md#prerequisites-before-installation-argcomplete-package-for-linux-based-systems-and-lxplus)
    - [Local Instalation (Not Need For O2)](doc/2_Prerequisites.md#local-instalation-not-need-for-o2)
    - [O2 Installation](doc/2_Prerequisites.md#o2-installation)
    - [Prerequisites Before Installation argcomplete Package For MacOS Based Systems](doc/2_Prerequisites.md#prerequisites-before-installation-argcomplete-package-for-macos-based-systems)
    - [Local Instalation (Not Need For O2)](doc/2_Prerequisites.md#local-instalation-not-need-for-o2-1)
    - [O2 Installation](doc/2_Prerequisites.md#o2-installation-1)
- [Instructions for TAB Autocomplete](doc/3_InstructionsforTABAutocomplete.md)
  - [Possible Autocompletions](doc/3_InstructionsforTABAutocomplete.md#possible-autocompletions) 
- [Technical Informations](doc/4_TechincalInformations.md)
  - [Helper Command Functionality](doc/4_TechincalInformations.md#helper-command-functionality)
  - [Some Things You Should Be Careful For Using and Development](doc/4_TechincalInformations.md#some-things-you-should-be-careful-for-using-and-development)
  - [Some Notes Before The Instructions](doc/4_TechincalInformations.md#some-notes-before-the-instructions)
  - [Interface Modes: JSON Overrider and JSON Additional](doc/4_TechincalInformations.md#interface-modes-json-overrider-and-json-additional)
- [Instructions for Python Scripts](doc/5_InstructionsForPythonScripts.md)
  - [Download CutsLibrary, MCSignalLibrary, MixingLibrary From Github](doc/5_InstructionsForPythonScripts.md#download-cutslibrary-mcsignallibrary-mixinglibrary-from-github)
  - [Get CutsLibrary, MCSignalLibrary, MixingLibrary From Local Machine](doc/5_InstructionsForPythonScripts.md#get-cutslibrary-mcsignallibrary-mixinglibrary-from-local-machine)
  - [Available configs in DownloadLibs.py Interface](doc/5_InstructionsForPythonScripts.md#available-configs-in-downloadlibspy-interface)
  - [Hardcoded Arguments](doc/5_InstructionsForPythonScripts.md#hardcoded-arguments)
- [Instructions for runTableMaker](doc/5_InstructionsForPythonScripts.md#instructions-for-runtablemaker)
- [Instructions for runAnalysis.py](doc/5_InstructionsForPythonScripts.md#instructions-for-runanalysispy)
- [Instructions for runFilterPP.py](doc/5_InstructionsForPythonScripts.md#instructions-for-runfilterpppy)
- [Instructions for runDQFlow.py](doc/5_InstructionsForPythonScripts.md#instructions-for-rundqflowpy)
- [Tutorial Part](doc/6_Tutorials.md)
  - [Download Datas For Tutorials](doc/6_Tutorials.md#download-datas-for-tutorials)
    - [Workflows In Tutorials](doc/6_Tutorials.md#workflows-in-tutorials)
    - [Skimmed Datas In Tutorials](doc/6_Tutorials.md#skimmed-datas-in-tutorials)
    - [Pre-Made JSON configuration Files In Tutorials](doc/6_Tutorials.md#pre-made-json-configuration-files-in-tutorials)
  - [MC Part](doc/6_Tutorials.md#mc-part)
    - [Run tableMakerMC on LHC21i3d2 (jpsi to MuMu pp Run3Simulation)](doc/6_Tutorials.md#run-tablemakermc-on-lhc21i3d2-jpsi-to-mumu-pp-run3simulation)
    - [Run dqEfficiency on MC (LHC21i3d2 pp Run3Simulation)](doc/6_Tutorials.md#run-dqefficiency-on-mc-lhc21i3d2-pp-run3simulation)
    - [Run tablemakerMC on LHC21i3b (Prompt jpsi to dielectron pp Run3Simulation)](doc/6_Tutorials.md#run-tablemakermc-on-lhc21i3b-prompt-jpsi-to-dielectron-pp-run3simulation)
    - [Run dqEfficiency on MC (LHC21i3b pp Run3Simulation)](doc/6_Tutorials.md#run-dqefficiency-on-mc-lhc21i3b-pp-run3simulation)
    - [Run tablemakerMC on LHC21i3f2 (Non-Prompt jpsi to dielectron pp Run3Simulation)](doc/6_Tutorials.md#run-tablemakermc-on-lhc21i3f2-non-prompt-jpsi-to-dielectron-pp-run3simulation)
    - [Run dqEfficiency on LHC21i3f2 (LHC21i3f2 pp Run3Simulation)](doc/6_Tutorials.md#run-dqefficiency-on-lhc21i3f2-lhc21i3f2-pp-run3simulation)
  - [Data Part](doc/6_Tutorials.md#data-part)
    - [Run tableMaker on LHC15o (LHC15o PbPb Run2Data)](doc/6_Tutorials.md#run-tablemaker-on-lhc15o-lhc15o-pbpb-run2data)
    - [Run tableReader on LHC15o (LHC15o PbPb Run2Data)](doc/6_Tutorials.md#run-tablereader-on-lhc15o-lhc15o-pbpb-run2data)
    - [Run tableMaker on LHC15o With Generic Flow Analysis (LHC15o PbPb Run2Data)](doc/6_Tutorials.md#run-tablemaker-on-lhc15o-with-generic-flow-analysis-lhc15o-pbpb-run2data)
    - [Run tableReader on LHC15o with Generic Flow Analysis (LHC15o PbPb Run2Data)](doc/6_Tutorials.md#run-tablereader-on-lhc15o-with-generic-flow-analysis-lhc15o-pbpb-run2data)
    - [Run dqFlow on LHC15o (LHC15o PbPb Run2Data)](doc/6_Tutorials.md#run-dqflow-on-lhc15o-lhc15o-pbpb-run2data)
    - [Run v0Selector on LHC15o (LHC15o PbPb Run2Data)](doc/6_Tutorials.md#run-v0selector-on-lhc15o-lhc15o-pbpb-run2data)
    - [Run tableMaker on LHC22c (LHC22c pp Run3Data)](doc/6_Tutorials.md#run-tablemaker-on-lhc22c-lhc22c-pp-run3data)
    - [Run tableReader on Data (LHC22c pp Run3Data)](doc/6_Tutorials.md#run-tablereader-on-data-lhc22c-pp-run3data)
    - [Run filterPP on fwdprompt(fwdprompt pp Run3Data)](doc/6_Tutorials.md#run-filterpp-on-fwdpromptfrom-hands-on-session-ii)
  - [Special Part : Dilepton Analysis For Non-Standart Existing Workflows in DQ](doc/6_Tutorials.md#special-part--dilepton-analysis-for-non-standart-existing-workflows-in-dq)
    - [MC : Dilepton Track Analysis (On Bc Simulation)](doc/6_Tutorials.md#mc--dilepton-track-analysis-on-bc-simulation)
    - [Data : Dilepton Hadron Analysis (On PbPb Data LHC15o)](doc/6_Tutorials.md#data--dilepton-hadron-analysis-on-pbpb-data-lhc15o)
  - [Special Part : run tableMaker and tableReader at the same time](doc/6_Tutorials.md#special-part--run-tablemaker-and-tablereader-at-the-same-time)
- [Developer Guide](doc/7_DeveloperGuide.md)
  - [Developer Tools](doc/7_DeveloperGuide.md#developer-tools)
    - [How to modify O2-DQ task dependencies](doc/7_DeveloperGuide.md#how-to-modify-o2-dq-task-dependencies)
    - [How to modify or add new reduced tables](doc/7_DeveloperGuide.md#how-to-modify-or-add-new-reduced-tables)
    - [How to add new CLI arguments](doc/7_DeveloperGuide.md#how-to-add-new-cli-arguments)
    - [How to define new autocompletions](doc/7_DeveloperGuide.md#how-to-define-new-autocompletions)
    - [How to add new O2 converter tasks](doc/7_DeveloperGuide.md#how-to-add-new-o2-converter-tasks)
  - [Naming Conventions](doc/7_DeveloperGuide.md#naming-conventions)
- [Troubleshooting: Tree Not Found](doc/8_TroubleshootingTreeNotFound.md)
  - [Converters](doc/8_TroubleshootingTreeNotFound.md#converters-special-additional-tasks-for-workflows)
  - [add_track_prop](doc/8_TroubleshootingTreeNotFound.md#addtrackprop)