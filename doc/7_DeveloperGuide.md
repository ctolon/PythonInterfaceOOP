
# Introduction to Modifying

This chapter will explain to you how to integrate these updates when there are new updates to common dependencies, configuration or process functions in O2-DQ Framework or in Common framework.

## Developer Tools

Tools used to add new configurable or new process functions in JSONs and more are defined as functions in the `configSetter.py` script in the extramodules folder (You can found more information in doc strings).

If you need a modification, you only need to modify the functions in the main tools. Helper tools are utility functions and you don't need to modify them. These are standard.

**Main Tools:**

* **SetArgsToArgumentParser** → An interface creator class that parses the JSON configuration file and creates the arguments for the CLI, defining possible autocompletes and defining hard coded arguments.
* **setConverters** → This function that allows to include converter tasks given to the CLI into the workflow

**Helper Tools:**

* **dispArgs** → Prints each argument provided by the CLI to the screen for monitoring
* dispInterfaceMode →  Prints the mode in which the interface will work.
* **dispO2HelpMessage** → Utility function to run `--help full` command in O2 with `--helpO2` argument in python scripts
* **debugSettings** → Utility function to log terminal or file (or both)
* **generateDescriptors** → Utility function that creates a descriptor json file for generating reduced tables
* **tableProducerSkimming/tableProducerAnalysis** → They are helper functions for the generatorDescriptor utility function that saves the tables defined in the DQ data model to a hashmap data structure and then writes it to the descriptor json file.
* **setProcessDummy** → if a task contains a processDummy function, processDummy must be true if no other process functions are true, and processDummy must be false if at least one process function is true. This is the auxiliary function that automatically manages the situation.
* **setParallelismOnSkimming** → It is a helper function that allows to run tableMaker and tableReader or tableMakerMC and dqEfficiency workflows at the same time.
* **commonDepsToRun** → It is the utility function used to set the dependencies required in the workflow.
* **setSwitch** → It is a utility function that automates the process functions according to the JSON interface mode.
* **setConfigs** → It is the utility function that allows to assign the argument parameter pairs provided by the CLI to the configurations in the json config file.

### How to modify O2-DQ task dependencies

Two strategies are used to manage O2 dependencies in Python scripts:

1-) Keeping the dependencies for common, barrel and muon in a separate list, then running the dependencies required according to the workflow with the naming rules (this strategy is used in the runTableMaker.py script)
2-) Collect all dependencies in one list and run them directly

In the first strategy, it is added to the list where it is defined according to the dependency type. For example, the dependencies defined for tableMaker are as follows:

```python 
commonDeps = ["o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table"]
barrelDeps = ["o2-analysis-trackselection", "o2-analysis-trackextension", "o2-analysis-pid-tof-base", "o2-analysis-pid-tof", "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta", "o2-analysis-pid-tpc-full"]
muonDeps = ["o2-analysis-fwdtrackextension"]
```

Relevant dependencies can be added here if necessary, first the common DepsToRun function calls all dependencies:

```python 
# Check which dependencies need to be run
depsToRun = commonDepsToRun(commonDeps)
```

Then the barrel and/or muon dependencies are invoked depending on whether the process function in the tableMaker contains the barrel or muon substring:

```python 
    # LOOK AT HERE
    for processFunc in specificDeps.keys():
        if processFunc not in config[taskNameInConfig].keys():
            continue
        if config[taskNameInConfig][processFunc] == "true":
            if "processFull" in processFunc or "processBarrel" in processFunc or "processAmbiguousBarrel" in processFunc:
                for dep in barrelDeps:
                    depsToRun[dep] = 1
            if "processFull" in processFunc or "processMuon" in processFunc or "processAmbiguousMuon" in processFunc:
                for dep in muonDeps:
                    depsToRun[dep] = 1

            # THIS WILL EXPLAIN LATER
            for dep in specificDeps[processFunc]:
                depsToRun[dep] = 1
```

Then the command to be executed in O2 is given as a string. Related dependencies for this string | is added by separating with:

```python
commandToRun = f"{taskNameInCommandLine} --configuration json://{updatedConfigFileName} --severity error --shm-segment-size 12000000000 --aod-writer-json {writerConfigFileName} -b"

    for dep in depsToRun.keys():
        commandToRun += " | " + dep + " --configuration json://" + updatedConfigFileName + " -b"
        logging.debug("%s added your workflow", dep)
```

In the second strategy all the dependency are added to a single list, then they are all added to the similarly generated commandToRun string. For ex. for runFilterPP:

```python
# All dependencies
commonDeps = ["o2-analysis-timestamp", "o2-analysis-event-selection", "o2-analysis-multiplicity-table", "o2-analysis-trackselection", "o2-analysis-trackextension", "o2-analysis-pid-tof-base", "o2-analysis-pid-tof", "o2-analysis-pid-tof-full", "o2-analysis-pid-tof-beta", "o2-analysis-pid-tpc-full", "o2-analysis-fwdtrackextension"]

# Check which dependencies need to be run
depsToRun = commonDepsToRun(commonDeps)

commandToRun = f"{taskNameInCommandLine} --configuration json://{updatedConfigFileName} --severity error --shm-segment-size 12000000000 -b"
    for dep in depsToRun.keys():
        commandToRun += " | " + dep + " --configuration json://" + updatedConfigFileName + " -b"
        logging.debug("%s added your workflow", dep)
```

If two or more DQ workflows or common dependencies are wanted to be pipelined and run at the same time, then specific dependency trees can be created with hashmap like O2 dependencies can be added, and they can be run depending on the process functions. for e.g in runTableMaker.py:

```python
specificDeps = {
    "processFull": [],
    "processFullTiny": [],
    "processFullWithCov": [],
    "processFullWithCent": ["o2-analysis-centrality-table"],
    "processBarrelOnly": [],
    "processBarrelOnlyWithCov": [],
    "processBarrelOnlyWithV0Bits": ["o2-analysis-dq-v0-selector"],
    "processBarrelOnlyWithDalitzBits": ["o2-analysis-dq-dalitz-selection"],
    "processBarrelOnlyWithEventFilter": ["o2-analysis-dq-filter-pp"],
    "processBarrelOnlyWithQvector": ["o2-analysis-centrality-table", "o2-analysis-dq-flow"],
    "processBarrelOnlyWithCent": ["o2-analysis-centrality-table"],
    "processMuonOnly": [],
    "processMuonOnlyWithCov": [],
    "processMuonOnlyWithCent": ["o2-analysis-centrality-table"],
    "processMuonOnlyWithQvector": ["o2-analysis-centrality-table", "o2-analysis-dq-flow"],
    "processMuonOnlyWithFilter": ["o2-analysis-dq-filter-pp"],
    "processAmbiguousMuonOnly": [],
    "processAmbiguousBarrelOnly": []
    # "processFullWithCentWithV0Bits": ["o2-analysis-centrality-table","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
    # "processFullWithEventFilterWithV0Bits": ["o2-analysis-dq-filter-pp","o2-analysis-dq-v0-selector", "o2-analysis-weak-decay-indices"],
    }
```

As can be seen, O2 dependency dependencies according to the process function (for example, if the processBarrelOnlyWithCent function is true, it also includes the o2-analysis-centrality-table dependency in the workflow) or other DQ workflows (for example, if the processBarrelOnlyWithEventFilter function is true o2-analysis-dq-filter- pp is included in the workflow and run simultaneously with the table-maker) can be included in the pipeline by process function

we manage this with hashmaps as mentioned before (this code block was given above when explaining O2 dependencies):

```python
    for processFunc in specificDeps.keys():
        if processFunc not in config[taskNameInConfig].keys():
            continue
        if config[taskNameInConfig][processFunc] == "true":
            if "processFull" in processFunc or "processBarrel" in processFunc or "processAmbiguousBarrel" in processFunc:
                for dep in barrelDeps:
                    depsToRun[dep] = 1
            if "processFull" in processFunc or "processMuon" in processFunc or "processAmbiguousMuon" in processFunc:
                for dep in muonDeps:
                    depsToRun[dep] = 1

            # LOOK AT HERE
            for dep in specificDeps[processFunc]:
                depsToRun[dep] = 1
```

Starting from here, you can add dependency trees and specific dependencies according to each process function, and you can directly add common, barrel or muon dependencies to the lists.


### How to modify or add new reduced tables

Tables in the O2-DQ framework data model are integrated into the python script with list and hashmap. The tables variable is a hashmap structure that contains all the tables that we can produce with table-maker or table-maker-mc in the O2-DQ framework The dependencies of each table are divided according to the process functions and whether they are general or not. Common tables are always generated, barrel tables are generated if at least one process function starting with processBarrel is true in table-maker or table-maker-mc, muon tables are generated if at least one process function starting with processMuon is true. they are assigned in a list structure called commonTables, barrelTables and muonTables variables to keep table names. If the process function needs to generate a special table (for example, processBarrelOnlyWithCov generates the extra necessary covariance tables for the track barrel) these are specified under the variable specificTables with the hashmap:

```python
    # yapf: disable
    # Definition of all the tables we may write
    tables = {
        "ReducedEvents": {"table": "AOD/REDUCEDEVENT/0"},
        "ReducedEventsExtended": {"table": "AOD/REEXTENDED/0"},
        "ReducedEventsVtxCov": {"table": "AOD/REVTXCOV/0"},
        "ReducedEventsQvector": {"table": "AOD/REQVECTOR/0"},
        "ReducedMCEventLabels": {"table": "AOD/REMCCOLLBL/0"},
        "ReducedMCEvents": {"table": "AOD/REDUCEDMCEVENT/0"},
        "ReducedTracks": {"table": "AOD/REDUCEDTRACK/0"},
        "ReducedTracksBarrel": {"table": "AOD/RTBARREL/0"},
        "ReducedTracksBarrelCov": {"table": "AOD/RTBARRELCOV/0"},
        "ReducedTracksBarrelPID": {"table": "AOD/RTBARRELPID/0"},
        "ReducedTracksBarrelLabels": {"table": "AOD/RTBARRELLABELS/0"},
        "ReducedMCTracks": {"table": "AOD/REDUCEDMCTRACK/0"},
        "ReducedMuons": {"table": "AOD/RTMUON/0"},
        "ReducedMuonsExtra": {"table": "AOD/RTMUONEXTRA/0"},
        "ReducedMuonsCov": {"table": "AOD/RTMUONCOV/0"},
        "ReducedMuonsLabels": {"table": "AOD/RTMUONSLABELS/0"},
        "AmbiguousTracksMid": {"table": "AOD/AMBIGUOUSTRACK/0"},
        "AmbiguousTracksFwd": {"table": "AOD/AMBIGUOUSFWDTR/0"},
        "DalitzBits": {"table": "AOD/DALITZBITS/0"},
        #"ReducedV0s": {"table": "AOD/REDUCEDV0/0"}, # NOTE V0 Bits cannot save to reduced tables
        #"V0Bits": {"table": "AOD/V0BITS/0"}
        }
    # yapf: enable
    # Tables to be written, per process function
    commonTables = ["ReducedEvents", "ReducedEventsExtended", "ReducedEventsVtxCov"]
    barrelCommonTables = ["ReducedTracks", "ReducedTracksBarrel", "ReducedTracksBarrelPID"]
    muonCommonTables = ["ReducedMuons", "ReducedMuonsExtra"]
    specificTables = {
        "processFull": [],
        "processFullTiny": [],
        "processFullWithCov": ["ReducedTracksBarrelCov", "ReducedMuonsCov"],
        "processFullWithCent": [],
        "processBarrelOnly": [],
        "processBarrelOnlyWithCov": ["ReducedTracksBarrelCov"],
        "processBarrelOnlyWithV0Bits": [],
        "processBarrelOnlyWithDalitzBits": ["DalitzBits"],
        "processBarrelOnlyWithQvector": ["ReducedEventsQvector"],
        "processBarrelOnlyWithEventFilter": [],
        "processBarrelOnlyWithCent": [],
        "processMuonOnly": [],
        "processMuonOnlyWithCov": ["ReducedMuonsCov"],
        "processMuonOnlyWithCent": [],
        "processMuonOnlyWithQvector": ["ReducedEventsQvector"],
        "processMuonOnlyWithFilter": [],
        "processAmbiguousMuonOnly": ["AmbiguousTracksFwd"],
        "processAmbiguousBarrelOnly": ["AmbiguousTracksMid"]
        }
```
if a table has been added to the DQ data model and you want to modify it to scripts, always first! You should add this table to the tables variable. If this table is linked to a process function, then you must define it against the relevant process function in the hashmap list in the specificTables variable. If it is a more general table (common, barrel or muon) then you can add it directly to the lists.

finally after adding them to python scripts, Finally, after adding them to the python scripts, you should add the tables you added in the reader json files (readerConfiguration_reducedEvent.json for Data, readerConfiguration_reducedEventMC.json for MC).

### How to add new CLI arguments

If a new configurable or processFunction has been added to O2 DQ framework then if you just add it to the corresponding task in JSON configuration files, the argument will be generated automatically by the python scripts. For example, assuming we want to add a new configurable cfgNewCuts variable to the analysis-same-event pairing task (tableReader) in the configAnalysisData.json file. Before:

```python
    "analysis-same-event-pairing": {
        "cfgTrackCuts": "jpsiO2MCdebugCuts",
        "cfgMuonCuts": "muonQualityCuts",
        "cfgAddSEPHistogram": "barrel,vertexing,flow",
        "ccdb-url": "http:\/\/alice-ccdb.cern.ch",
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
```

After:

```python
    "analysis-same-event-pairing": {
        "cfgNewCuts": ""
        "cfgTrackCuts": "jpsiO2MCdebugCuts",
        "cfgMuonCuts": "muonQualityCuts",
        "cfgAddSEPHistogram": "barrel,vertexing,flow",
        "ccdb-url": "http:\/\/alice-ccdb.cern.ch",
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
```

Adding it like this will suffice. So you will be able to access this command as:

```ruby
--analysis-same-event-pairing:cfgNewCuts
```
if you want to add a global argument, they are hardcoded in SetArgsToArgumentParser class in the configSetter.py script. You can add here directly and you can define business logic in run scripts:

```python
# We can define hard coded global arguments
self.parser.add_argument("cfgFileName", metavar = "Config.json", default = "config.json", help = "config JSON file name (mandatory)")
self.parser.add_argument("-runParallel", help = "Run parallel in session", action = "store_true", default = False)

# GLOBAL OPTIONS
groupGlobal = self.parser.add_argument_group(title = f"Global workflow options")
groupGlobal.add_argument("--aod-memory-rate-limit", help = "Rate limit AOD processing based on memory", action = "store", type = str)
groupGlobal.add_argument("--writer", help = "Argument for producing extra reduced tables", action = "store", type = str).completer = ChoicesCompleter(booleanSelections)
groupGlobal.add_argument("--helpO2", help = "Display help message on O2", action = "store_true", default = False)

# Converter Task Options
groupO2Converters = self.parser.add_argument_group(title = f"Add to workflow O2 Converter task options")
groupO2Converters.add_argument("--add_mc_conv", help = "Add the converter from mcparticle to mcparticle+001 (Adds your workflow o2-analysis-mc-converter task)", action = "store_true",)
groupO2Converters.add_argument("--add_fdd_conv", help = "Add the fdd converter (Adds your workflow o2-analysis-fdd-converter task)", action = "store_true",)
groupO2Converters.add_argument("--add_track_prop", help = "Add track propagation to the innermost layer (TPC or ITS) (Adds your workflow o2-analysis-track-propagation task)", action = "store_true",)
groupO2Converters.add_argument("--add_weakdecay_ind", help = "Add Converts V0 and cascade version 000 to 001 (Adds your workflow o2-analysis-weak-decay-indices task)", action = "store_true",)
groupO2Converters.add_argument("--add_col_conv", help = "Add the converter from collision to collision+001", action = "store_true")

# Helper Options
groupHelper = self.parser.add_argument_group(title = f"Helper Options")
groupHelper.add_argument("--debug", help = "execute with debug options", action = "store", type = str.upper, default = "INFO", choices = debugLevelSelectionsList,).completer = ChoicesCompleterList(debugLevelSelectionsList)
groupHelper.add_argument("--logFile", help = "Enable logger for both file and CLI", action = "store_true")
groupHelper.add_argument("--override", help = "If true JSON Overrider Interface If false JSON Additional Interface", action = "store", default = "true", type = str.lower, choices = booleanSelections,).completer = ChoicesCompleter(booleanSelections)
```

for ex. For example, `--debug` and `--logFile` arguments are global, and the scripts for logging settings are specifically defined:

```python
# Debug Settings
debugSettings(args.debug, args.logFile, fileName = "v0selector.log")
```


### How to define new autocompletions

Autocompletions are defined for a configurable or process function in python scripts. These are defined in the SetArgsToArgumentParser class in the configSetter.py script in the extramodules folder. Two types of autocompletion are currently available:

1-) Autocompletions by parsing DQ header files and assigning analysis cuts, MC signals, histogram groups or event mixing variables to a variable.

2-) Hard codded selections (such as true-false for process functions or QA options, or -1, 0 or 1 selections for autocompletion e.g. in pid or est configurations etc.).

Configuration strings (such as analysis cuts) obtained by parsing DQ libraries are retrieved by instantiating the DQLibGetter class in the dqLibGetter.py script in the extramodules folder:

```python
# Dependency injection
dqLibGetter = DQLibGetter()

# Get All Configurables for DQ Framework from DQ header files
allAnalysisCuts = dqLibGetter.allAnalysisCuts
allMCSignals = dqLibGetter.allMCSignals
allSels = dqLibGetter.allSels
allMixing = dqLibGetter.allMixing

# Get all histogram groups for DQ Framework from histogram library
# NOTE Now we use only all histos for backward comp.
allHistos = dqLibGetter.allHistos
# allEventHistos = dqLibGetter.allEventHistos
# allTrackHistos = dqLibGetter.allTrackHistos
# allMCTruthHistos = dqLibGetter.allMCTruthHistos
# allPairHistos = dqLibGetter.allPairHistos
# allDileptonHistos = dqLibGetter.allDileptonHistos
```

Hard coded selections are defined in lists by the user:

```python
# Predefined lists for autocompletion
booleanSelections = ["true", "false"]
itsMatchingSelections = ["0", "1", "2", "3"]
binarySelection = ["0", "1"]
tripletSelection = ["-1", "0", "1"]
collisionSystemSelections = ["PbPb", "pp", "pPb", "Pbp", "XeXe"]
eventMuonSelections = ["0", "1", "2"]
debugLevelSelectionsList = ["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
```


Autocompletion property is assigned to later configurations according to naming conventions. For example, since all analysis cuts in the entire DQ framework contain the "Cuts" substring:

```python
# AUTOCOMPLETION CONDITION
containsCuts = "Cuts" in configurable

# ASSIGN AUTOCOMPLETION
if containsCuts:
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allAnalysisCuts)
```

Definition has been made. Thus, an autocompletion is made for each configuration that contains Cuts in the JSON config file. Every configuration that satisfies this condition, ie configurables containing Cuts, analysis segments parsed from the DQ library, is assigned to the argument as autocompletion.

These are all currently defined autocompletion conditions and when you add a configuration that satisfies these conditions to JSON, autocompletion will be automatically assigned to the relevant parameter (You can examine autocompletion conditions from SetArgsToArgumentParser class):


```python
# Define some autocompletion rules for match-case (for O2-DQ Framework)
containsCuts = "Cuts" in configurable
containsSignals = configurable.endswith("Signals") or configurable.endswith("signals")
containsHistogram = "Histogram" in configurable
containsSels = configurable.endswith("BarrelSels") or configurable.endswith("MuonSels")
containsMixingVars = "MixingVars" in configurable
containsQA = configurable.startswith("cfg") and "QA" in configurable
containsAmbiguous = configurable == "cfgIsAmbiguous"
containsFillCandidateTable = configurable == "cfgFillCandidateTable"
containsFlatTables = configurable == "cfgFlatTables"
containsTPCpostCalib = configurable == "cfgTPCpostCalib"
containsProcess = configurable.startswith("process")
```

These autocompletion conditions are assigned to the parser arguments with if conditions. If you are going to add a new autocompletion, you must first define the condition as above, then integrate it into the following if conditions(You can examine if conditions from SetArgsToArgumentParser class):


```python
# We may define posible all autocompletions as semi hard-coded with substring search (according to naming conventions)
# DQ Framework
if containsCuts:
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allAnalysisCuts)
elif containsSignals:
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allMCSignals)
elif containsHistogram:
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allHistos)
elif containsSels:
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allSels)
elif containsMixingVars:
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allMixing)
elif containsQA:
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
elif containsAmbiguous:
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
elif containsFillCandidateTable:
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
elif containsFlatTables:
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
elif containsTPCpostCalib:
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
elif configurable == "processDummy": # NOTE we don't need configure processDummy since we have dummy automizer
    continue

# Common Framework
elif containsProcess: # NOTE This is an global definition in O2 Analysis framework, all process functions startswith "process"
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
elif configurable == "syst":
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str, metavar = "\b").completer = ChoicesCompleter(collisionSystemSelections)
elif configurable == "doVertexZeq":
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str, metavar = "\b").completer = ChoicesCompleter(binarySelection)
elif configurable.startswith("pid-") or configurable.startswith("est"):
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(tripletSelection)
elif configurable == "muonSelection":
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str, metavar = "\b").completer = ChoicesCompleter(eventMuonSelections)
elif configurable == "itsMatching":
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str, metavar = "\b").completer = ChoicesCompleter(itsMatchingSelections)
elif configurable == "compatibilityIU":
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
else:
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str, metavar = "\b") # Has no autocompletion

argcomplete.autocomplete(self.parser, always_complete_options = False)
self.parser.parse_args()
```

To avoid confusion here the autocomplete conditions are splitted for the DQ framework and the code for the common framework. Conditions in common framework are full hardcoded, conditions in DQ framework are semi hardcoded.

Another important point is that if the argument takes more than one parameter, `nargs = "*"` should be given as a parameter to the parser argument and the ChoicesCompleterList function should be used. If the argument can take a single parameter, then nargs should not be given as a parameter and the ChoicesCompleter function should be used. For ex.

```python
if containsCuts: # YOU CAN DEFINE MORE THAN ONE CUTS AS PARAMETER
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", nargs = "*", type = str, metavar = "\b").completer = ChoicesCompleterList(allAnalysisCuts)

elif containsProcess: # YOU CAN ONLY DEFINE ONE PARAMETER AS true OR false for process Functions
    groupJsonParser.add_argument("--" + arg, help = "", action = "store", type = str.lower, metavar = "\b").completer = ChoicesCompleter(booleanSelections)
```

### How to add new O2 converter tasks

The arguments required to include converter tasks in the workflow are defined as hardcoded in the SetArgsToArgumentParser class in the configSetter.py script in the extramodules folder:

```python
# Converter Task Options
groupO2Converters = self.parser.add_argument_group(title = f"Add to workflow O2 Converter task options")
groupO2Converters.add_argument("--add_mc_conv", help = "Add the converter from mcparticle to mcparticle+001 (Adds your workflow o2-analysis-mc-converter task)", action = "store_true",)
groupO2Converters.add_argument("--add_fdd_conv", help = "Add the fdd converter (Adds your workflow o2-analysis-fdd-converter task)", action = "store_true",)
groupO2Converters.add_argument("--add_track_prop", help = "Add track propagation to the innermost layer (TPC or ITS) (Adds your workflow o2-analysis-track-propagation task)", action = "store_true",)
groupO2Converters.add_argument("--add_weakdecay_ind", help = "Add Converts V0 and cascade version 000 to 001 (Adds your workflow o2-analysis-weak-decay-indices task)", action = "store_true",)
groupO2Converters.add_argument("--add_col_conv", help = "Add the converter from collision to collision+001", action = "store_true")
(booleanSelections)
# YOU CAN ADD NEW O2 CONVERTER TASK HERE
```

here you can add the new argument similarly. Then, to set these arguments, a hashmap in the form of argument - o2-analysis-|taskname| was created in the setConverter function in the configSetter.py script. It will be enough to add the converter task argument you just added here.

```python
def setConverters(allArgs: dict, updatedConfigFileName: str, commandToRun: str) -> str:
    specificTasks = {
        "add_mc_conv": "o2-analysis-mc-converter",
        "add_fdd_conv": "o2-analysis-fdd-converter",
        "add_track_prop": "o2-analysis-track-propagation",
        "add_weakdecay_ind": "o2-analysis-weak-decay-indices",
        "add_col_conv": "o2-analysis-collision-converter"
        # Add Your O2 converter task key-value pair to here
        }
    
    for cliArg, cliValue in allArgs.items():
        for converterArg, taskName in specificTasks.items():
            if converterArg == cliArg and cliValue is True:
                logging.debug(taskName + " added your workflow")
                commandToRun += (" | " + taskName + " --configuration json://" + updatedConfigFileName + " -b")
    return commandToRun
```


## Naming Conventions

* Folders: All lowercase
* Class: Upper camelcase
* Function: Lower camelcase
* Variables: Lower camelcase
* Constants: Screaming camelcase
* O2 converter arguments: Snake case

[← Go back to Instructions For Tutorials](6_Tutorials.md) | [↑ Go to the Table of Content ↑](../README.md) [Continue to TroubleshootingTreeNotFound →](8_TroubleshootingTreeNotFound.md)