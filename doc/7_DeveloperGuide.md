
# Introduction to Modifying

This chapter will explain to you how to integrate these updates when there are new updates to common dependencies, configuration or process functions in O2.

## Developer Tools

Tools used to add new configurable or new process functions in JSONs and more are defined as functions in the `configSetter.py` script in the extramodules folder (You can found more information in doc strings).

Main Tools:

* setConfig:
* setSelection:
* setSwitch
* setProcessDummy

Helper Tools:
* setPrefixSuffix
* setFalseHasDeps
* setConverters
* mandatoryArgChecker
* depsChecker
* oneToMultiDepsChecker

TODO Ongoing


## Naming Conventions

* Folders: All lowercase
* Class: Upper camelcase
* Function: Lower camelcase
* Variables: Lower camelcase
* Constants: Screaming camelcase
* O2 converter arguments: Snake case

### setConfig

This function allows you to assign the argument parameter in CLI directly to JSON when the argument you give in CLI and the argument name in JSON are the same. This is common to all interfaces. This function must be defined in a for loop iterating over JSONs in run python scripts. This function must be defined in the for loop that iterates over JSONs in run python scripts. If you use the same naming conventions you can define it in a constant in this template:

setConfig(config, task, cfg, allArgs, cliMode)

// TODO explain args

Application:

To explain this simply, let's say, for example, our JSON configuration is:

    "analysis-dilepton-track": {
        "cfgLeptonCuts": "",
        "cfgFillCandidateTable": "false",
        "cfgBarrelMCRecSignals": "mumuFromJpsiFromBc,mumumuFromBc",
        "cfgBarrelMCGenSignals": "Jpsi",
        "processDimuonMuonSkimmed": "false",
        "processDielectronKaonSkimmed": "false",
        "processDummy": "true"
    },

Suppose the following are given as arguments to the CLI:

--cfgLeptonCuts muonQualityCuts --cfgFillCandidateTable true

then the naming of cfgEventCuts and cfgFillCandidateTable CLI arguments is exactly the same as the configuration arguments in JSON, so it provides configuration directly and its output is as follows:

    "analysis-dilepton-track": {
        "cfgLeptonCuts": "muonQualityCuts",
        "cfgFillCandidateTable": "true",
        "cfgBarrelMCRecSignals": "mumuFromJpsiFromBc,mumumuFromBc",
        "cfgBarrelMCGenSignals": "Jpsi",
        "processDimuonMuonSkimmed": "false",
        "processDielectronKaonSkimmed": "false",
        "processDummy": "true"
    },

// TODO explain interface modes

### setSelection


This function creates dictionary structures in python similar to the configuration json files, allowing the user-specified previously specified arguments to be true if given as CLI arguments, then directly as specified in the dictionary structure.

Application:

For example, let's say we have a JSON file like this:


     "analysis-event-selection": {
         "cfgMixingVars": "Vtx3",
         "cfgEventCuts": "eventStandardNoINT7",
         "cfgQA": "true",
         "cfgAddEventHistogram": "trigger,cent,muon",
         "processSkimmed": "false",
         "processDummy": "true"
     },
     "analysis-track-selection": {
         "cfgTrackCuts": "jpsiO2MCdebugCuts",
         "cfgDalitzCutId": "32",
         "cfgQA": "true",
         "cfgAddTrackHistogram": "dca,its,tpcpid,tofpid,postcalib_electron,postcalib_pion,postcalib_proton",
         "processSkimmed": "false",
         "processDummy": "true"
     },
     "analysis-prefilter-selection": {
         "cfgDalitzTrackCutsId": "",
         "cfgDalitzPairCuts": "",
         "cfgAddTrackPairHistogram": "",
         "cfgQA": "true",
         "processBarrelSkimmed": "false",
         "processDummy": "true"
     },
     "analysis-muon-selection": {
         "cfgMuonCuts": "muonQualityCuts",
         "cfgQA": "true",
         "cfgAddMuonHistogram": "muon",
         "processSkimmed": "true",
         "processDummy": "false"
     },
     "analysis-event-mixing": {
         "cfgTrackCuts": "jpsiO2MCdebugCuts",
         "cfgMuonCuts": "muonQualityCuts",
         "cfgAddEventMixingHistogram": "barrel,vertexing,flow",
         "cfgMixingDepth": "1",
         "processBarrelSkimmed": "false",
         "processMuonSkimmed": "false",
         "processBarrelMuonSkimmed": "false",
         "processBarrelVnSkimmed": "false",
         "processMuonVnSkimmed": "false",
         "processDummy": "true"
     },
     "analysis-same-event-pairing": {
         "cfgTrackCuts": "jpsiO2MCdebugCuts",
         "cfgMuonCuts": "muonQualityCuts",
         "cfgAddSEPHistogram": "barrel,vertexing,flow",
         "ccdb-url": "http:\/\/ccdb-test.cern.ch:8080",
         "ccdb-path": "Users\/lm",
         "ccdb-no-later-than": "1638360910432",
         "processDecayToEESkimmed": "true",
         "processDecayToEEPrefilterSkimmed": "false",
         "processDecayToMuMuSkimmed": "true",
         "processDecayToMuMuVertexingSkimmed": "false",
         "processVnDecayToEESkimmed": "false",
         "processVnDecayToMuMuSkimmed": "false",
         "processElectronMuonSkimmed": "false",
         "processAllSkimmed": "false",
         "processDummy": "false"
     },
     "analysis-dilepton-hadron": {
         "cfgLeptonCuts": "jpsiPID1",
         "cfgAddDileptonHadHistogram": "dilepton-hadron-correlation",
         "processSkimmed": "false",
         "processDummy": "true"
     },


The dictionary structure we define is as follows (we need to define it right at the beginning of the run python script):

     analysisSelectionDeps = {
         "trackSelection": {"analysis-track-selection": "processSkimmed"},
         "prefilterSelection": {"analysis-prefilter-selection": "processBarrelSkimmed"},
         "eventSelection": {"analysis-event-selection": "processSkimmed"},
         "muonSelection": {"analysis-muon-selection": "processSkimmed"},
         "dileptonHadron": {"analysis-dilepton-hadron": "processSkimmed"}
         }


Here keys are argument parameters that we will provide to the CLI, value is analysis task name, process function pair.

Now we need to specify an argument name. For example, let's say our argument is --analysis. First we need to define this argument in interface argument class python scripts (examples are available in dqtasks folders):

groupAnalysisSelections.add_argument("--analysis", help = "Skimmed process selections for Data Analysis", action = "store", nargs = "*", type = str, metavar = "ANALYSIS", choices = analysisSelectionsList,).completer = ChoicesCompleterList(analysisSelectionsList)

After defining it this way, inside the run python script:

setSelection(config, analysisSelectionDeps, args.analysis, cliMode)

We can define as. Here, the first argument config is our JSON configuration file input, the second argument is the python dictionary we defined, the third argument is our interface argument parameters (we accessed it with namespace), and the last one is the one we specifically defined the interface mode. This function must be declared on JSON just before iteration starts with a for loop.

After these operations, Suppose the following are given as arguments to the CLI:

--analysis eventSelection trackSelection

and so the argument parameters assign to JSON according to the python dictionaries we created earlier and the result will be ((processSkimmed functions defined in the dictionary for analysis-track-selection vs analysis-event-selection are set to true with argument parameters)):


     "analysis-event-selection": {
         "cfgMixingVars": "Vtx3",
         "cfgEventCuts": "eventStandardNoINT7",
         "cfgQA": "true",
         "cfgAddEventHistogram": "trigger,cent,muon",
         "processSkimmed": "true",
         "processDummy": "false"
     },
     "analysis-track-selection": {
         "cfgTrackCuts": "jpsiO2MCdebugCuts",
         "cfgDalitzCutId": "32",
         "cfgQA": "true",
         "cfgAddTrackHistogram": "dca,its,tpcpid,tofpid,postcalib_electron,postcalib_pion,postcalib_proton",
         "processSkimmed": "true",
         "processDummy": "false"
     },
     "analysis-prefilter-selection": {
         "cfgDalitzTrackCutsId": "",
         "cfgDalitzPairCuts": "",
         "cfgAddTrackPairHistogram": "",
         "cfgQA": "true",
         "processBarrelSkimmed": "false",
         "processDummy": "true"
     },
     "analysis-muon-selection": {
         "cfgMuonCuts": "muonQualityCuts",
         "cfgQA": "true",
         "cfgAddMuonHistogram": "muon",
         "processSkimmed": "true",
         "processDummy": "false"
     },
     "analysis-event-mixing": {
         "cfgTrackCuts": "jpsiO2MCdebugCuts",
         "cfgMuonCuts": "muonQualityCuts",
         "cfgAddEventMixingHistogram": "barrel,vertexing,flow",
         "cfgMixingDepth": "1",
         "processBarrelSkimmed": "false",
         "processMuonSkimmed": "false",
         "processBarrelMuonSkimmed": "false",
         "processBarrelVnSkimmed": "false",
         "processMuonVnSkimmed": "false",
         "processDummy": "true"
     },
     "analysis-same-event-pairing": {
         "cfgTrackCuts": "jpsiO2MCdebugCuts",
         "cfgMuonCuts": "muonQualityCuts",
         "cfgAddSEPHistogram": "barrel,vertexing,flow",
         "ccdb-url": "http:\/\/ccdb-test.cern.ch:8080",
         "ccdb-path": "Users\/lm",
         "ccdb-no-later-than": "1638360910432",
         "processDecayToEESkimmed": "true",
         "processDecayToEEPrefilterSkimmed": "false",
         "processDecayToMuMuSkimmed": "true",
         "processDecayToMuMuVertexingSkimmed": "false",
         "processVnDecayToEESkimmed": "false",
         "processVnDecayToMuMuSkimmed": "false",
         "processElectronMuonSkimmed": "false",
         "processAllSkimmed": "false",
         "processDummy": "false"
     },
     "analysis-dilepton-hadron": {
         "cfgLeptonCuts": "jpsiPID1",
         "cfgAddDileptonHadHistogram": "dilepton-hadron-correlation",
         "processSkimmed": "false",
         "processDummy": "true"
     },


NOTE: If you have noticed, although our --analysis argument only sets the processSkimmed function to true, the processDummy functions are also set to false in the relevant analysis tasks. This is because we have a separate dummy automizer function written for python scripts and you should use it for every configuration with processDummy. Otherwise your workflow will explode. In the other topic, the dummy automizer function will be explained.

### setProcessDummy


### setSwitch



// TODO explain interface modes
        

[← Go back to Instructions For Tutorials](6_Tutorials.md) | [↑ Go to the Table of Content ↑](../README.md) [Continue to TroubleshootingTreeNotFound →](8_TroubleshootingTreeNotFound.md)