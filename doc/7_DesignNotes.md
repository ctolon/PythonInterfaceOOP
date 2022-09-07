# Design Notes

@tableofcontents

## TODO List For Python Workflows
* `Finished` We need more meaningful explanations for argument explanations (helping comments).
* `Open` The values that JSON values can take for transaction management should be classified and filtered with
choices and data types.
* `Finished` Also some JSON values are bound together (eg. if cfgRun2 is false, isRun3 variable should be true
automatically) so some error handling and automation should be done for transaction management.
* `Finished` Some configurations for MC may not be available for data configurations (eg. cfgMCsignals or vice versa, also
valid for Run2 Run3 options). Therefore, when we configure this variable for data, it does not throw an error or
make any changes. For this, the python script should be configured.
* `Open` Python CLI only works by overriding values, so some of the unattached configurations should be integrated
into the TableMaker JSONs (Config MCRun2,MCRun3,DataRun2,Data Run3) in the O2DQWorkflows
repository as default or null values.
* `Finished` Some Tasks arguments need to be refactored.
* `Finished` For faster development, the auto completion feature should be implemented for arguments with the tab like
bash (Already Integrated for local).
* `Finished` After the developments are finished, the user manual should be prepared.
* `Open` For new feature tests, the ability to append new key-value pairs to JSONs should be implemented.
* `Closed` JSON databases can be refactored in a more meaningful way. Now key-value pairs are equal (After Setting Naming conventions).
* `Closed` A transaction management should be written to search whether the entered aod file is in the location.
* `Closed` If a configuration entered is not in JSON, a warning message should be written with a logger for this.
* `Open` Transaction management, which checks whether the parameters are entered only once, should be written, for example -process BarrelOnly BarrelOnly should throw an error or a warning message should be checked by checking that the parameters are entered as value more than once with a warning.


## Feedbacks, Suggestions and User Acceptance Test List

Date |  User | Type | Desc 
--- | --- | --- | --- |
`Aug 11, 2022` | `luca Micheletti` | `Suggestion` | Preparing a tutorial script for scripts. 
`Aug 15, 2022` | `Anastasia Merzlaya` | `User Acceptance Test` | ran the scripts successfully. Passed user acceptance tests. (only DQEfficiency) 
`Aug 19, 2022` | `Liuyao Zhang` | `User Acceptance Test` | He had trouble with the argcomplete package on his macOS-based system. We solved this problem together in the same day and it ran all the scripts without any problem. Passed user acceptance tests. Updated argcomplete package installation instructions for macOS. (argcomplete package)
`Aug 22, 2022` | `Liuyao Zhang` | `User Acceptance Test` | Reports a problem about aod checker functionality in interface. It fixed. (interface functionality)
`Aug 23, 2022` | `Liuyao Zhang` | `User Acceptance Test` | Reports a bug for SEP Process functionality, It fixed. (for tableReader and dqEfficiency)
`Aug 23, 2022` | `Liuyao Zhang` | `User Acceptance Test` | Reports a bug dilepton analysis for pp (for LHC22c). DileptonAOD.root ttres are created blank. It's not fixed now. (only for pp datas)
`Aug 30, 2022` | `Liuyao Zhang` | `User Acceptance Test` | He reports, o2-analysis-trackextension is not valid option for run3, details added in code, so we have transacation management for this issue, it fixed now.

If you have problem about running the scripts or you have some suggestions for interface, contact me at: `cevat.batuhan.tolon@cern.ch` or you can send a message on mattermost `@ctolon`. I will try to fix your problem ASAP.

## Updates

* `Jul 20, 2022` Developed pythonCLI version 1 for tablemaker in its simplest form, not integrated into main task.
* `Jul 21, 2022` Fixed some important bugs.
* `Jul 22, 2022` The repository has been refactored. The CLI written for TableMaker was integrated into the task, main python scripts were prepared for TableReader, DQEfficiency, and their CLIs were developed and integrated (Faulty versions).
* `Jul 23, 2022` CLI for TableMaker for automations and transaction management has been heavily refactored and some automations imported.
* `Jul 24, 2022` In the CLI written for tableMaker, some options were refactored and automated. Version 2 released with minimal testing.
* `Jul 25, 2022` A lot of tests have been done for the CLI written for tableMaker and the necessary refactor and automation tests have been done. CLI development for TableMaker is fully completed and Integrated to python script. Writing User Manual Documentation in progress.
* `Jul 26, 2022` Readme completed for `runTableMaker.py` and TableReader DQEfficiency workflows CLI based v1 released. processEvTime transaction management refactoring, for pp collisionsi centrality-table o2 task and JSON configs deleting automatized. New checker for Run/MC added.
* `Jul 27, 2022` Fixed a bug for filterpp tiny selection in Tablemaker, AOD File Checker added to TableMaker, readme updated (instructions added), New Critical Transaction Managements Added, For TableMaker process Function, Workflow Decision Tree Added   
* `Jul 28, 2022` Workflows with CLI for TableReader and DQEfficiency Completed. Demo versions and Old Version Deleted. JSON path's for single workflows updated. Mixing Library added for Skimmed processes, runtime errors fixed, writer configs added to CLI, CommandToRun Fixed in TableReader in DQEfficiency, MC Rec Gen Signals fixed for dileptons in DQEfficiency, only-select automation parameter will implemnt for TableReader and DQEfficiency, installation guide for argcomplate added, Instructions and avaiable commands added readme for TableMaker DQ Efficiency
* `Jul 29, 2022` All Tests passed for workflows and development is completed. Only some parts need refactoring for clean code and readme will updated.
* `Aug 09, 2022` JSON Databases removed as suggested. We have compiled time solutions regarding to O2Physics (based on regex exp. and some string operations). TableMaker and DQEfficiency Workflows refactored for user friendliness. All things are discussed with Ionut.
* `Aug 10, 2022` path fix for writer configs. Transcation management added for Same Event Pairing and readme guide updated.
* `Aug 11, 2022` provide a native solution for libraries with urllib, cut and mcsignal lister added, helper messages has beauty format, for filter pp task, sels are fixed. readme update, added new script for internet based solution: `DownloadLibs.py`. Some parameter value names has refactored in DQ Efficiency, fix for dileptonTrack Selection DQ Efficiency task, fix for Same event pairing automation logger message (when you try give an process function in DQEfficiency or TableReader if you forget give a parameter value in e.g --analysis eventSelection --process JpsiToMuMu sameEventPairing value automaticaly added to analysis workflow like this (Logger Message: `"[WARNING] You forget to add sameEventPairing option to analysis for Workflow. It Automatically added by CLI."`) --> --analysis eventSelection sameEventPairing we provide this way with automation)
* `Aug 12, 2022` runFilterPP.py Interface refactored and released. `--cfgMuonsCuts` parameter added tablemaker and filterpp workflow (it's different from `--cfgMuonCuts`). listToString method impl to barrel and muon sels. Readme update for instructions and available configs in FilterPP python script.
* `Aug 13, 2022` In FilterPP, processEvTime and Tiny Options added to JSON files and python scripts, we need trans. manag for them, processDummy option added for run 3 Data in tablemaker, dummy automizer activated for dq muons selection. Protection Added to all scripts for alienv load. Transaction management protection added for cfgMuonSels and cfgBarrelSels in filterPP Task (TableMaker and FilterPP python scripts) also logger message and fix instructions added, forget to assign value to parameters transcation management carried to top of code, String to List method update, nargs fix for Sels in filter pp
* `Aug 14, 2022` `o2-analysis-mc-converter` `o2-analysis-fdd-converter` and `o2-analysis-track-propagation` task adders added to all Workflows as parameters. taskNameInConfig in dqflow is fixed. DQ Flow JSON configs fixed. `o2-analysis-track-propagation` dep removed and `o2-analysis-trackextension` added in DQ Flow as deps.
* `Aug 15, 2022` version based downloaded functionality added to DownloadLibs.py and fixed download functionality to DQ libs for all python scripts, unused comment lines deleted, metavar deleted from process function in filterpp for help messages, in filterepp `o2-analysis-trackextension` analysis task added as dep and removed `o2-analysis-track-propagation` as dep, because in before we add parameters for adding this additional tasks. filterpp tiny process selection fixed for transcation management, writer configs for dilepton analysis will bu updated, test configs added for local test, they will be removed. we should discussed some common tasks configs should deleted from json for using default params in DPL config. readme update for dqflow and others. SSL certificates added for download DQ libs due to github validation
* `Aug 17-18, 2022`  Logger Functionality implemented to O2DQWorkflows and DownloadLibs.py Some minimal fixes provided. Fix info message for centrality Table Transcation for pp. readme updated. Pretty print formatted implemented to O2DQWorkflows for helper messages (cut lister, MC signal lister and event mixing variables) lister. Interface updated for DownloadLibs.py script to get DQ libraries from local machine. All relevant Instructions have been added to the readme  
* `Aug 19-20, 2022` Temp DQ libs added to O2DQWorkflows for working LXPLUS and test. Because If you configure the DownloadLibs.py script locally, there is no problem when pulling libraries on the local machine and while it is completely stable, it has been added temporarily for some user acceptance tests because the libraries cannot be pulled locally in LXPLUS and it is not stable to download DQ libraries from github. argcomplete integrated to DownloadLibs.py, comment lines updated for functions, for important values, sub help messages added, default value viewer added to help messages, Interface predefined selections carried to top for readability, readme updated and helper message usage added to readme.
* `Aug 21, 2022` Choicer Completer Method integrated for pretty print display for auto completions, always_complete_options setted false for pretty print display with TAB, New ChoicesCompleterList Class Integrated to All Workflows for Getting choices nargs *, helper message updates in very detailed, all argparser groups has subgroups now, task adder help messages updated, some naming conventions setted for variables and code quality improved, not needed comments lines deleted for code quality, minimal fix for dqflow. Readme updated and Instructions for autocomplete added to readme, metavar explanations added to readme.
* `Aug 22, 2022` Helper Messages Updated. One minimal display bug added to readme. New interface development is ongoing with new JSON Configs.based on nightly-2022_08_23
* `Aug 23, 2022` AOD File checker fixed, Same Event Pairing process functionality fixed, centrality table fixed in new interface, new automated things provided.
* `Aug 24-26, 2022` All bugs are fixed. All functionalities provided, all scripts are tested by different users. Interface development is completed.
* `Aug 26-29, 2022` Writer Config json files updated for reduced dileptons in dq skimmed data, dqFlow task integrated to tableReader and tableMaker, transaction management added for eventMixing Selections in tableReader, reader json creator functionality integrated to tableMaker, vertexZeq options manualy coverted to 0 for run 3 options otherwise process will crash, v0Selector added in pythonized workflows, Now interface has two mode : Overrider and additional, tutorials added to readme 
* `Aug 30, 2022`  o2-analysis-trackextension is not valid option for run3, details added in code, so we have transacation management for this issue, it fixed now (this issue reported by Liuyao Zhang).

[← Go back to Instructions For Tutorials](6_Tutorials.md) | [↑ Go to the Table of Content ↑](../README.md)