# Technical Informations

- [Technical Informations](#technical-informations)
  - [Helper Command Functionality](#helper-command-functionality)
  - [Debug and Logging Options for O2DQWorkflows and DownloadLibs.py](#debug-and-logging-options-for-o2dqworkflows-and-downloadlibspy)
  - [Some Things You Should Be Careful For Using and Development](#some-things-you-should-be-careful-for-using-and-development)
  - [Some Notes Before The Instructions](#some-notes-before-the-instructions)
  - [Interface Modes: JSON Overrider and JSON Additional](#interface-modes-json-overrider-and-json-additional)
  - [Project Architecture](#project-architecture)


## Helper Command Functionality

With the `python3 <scriptname> -h` command you will see a help message for all commands valid for the CLI. It is recommended to use this command at least once before using the interface. If you do not remember the arguments related to the interface, you can list all valid arguments and the values that these arguments can take with this command. For example, if you want to get a help message with the `python3 runTableMaker.py -h` command:

P.S The default values you see in the helper messages are the default values for the interface. The values you see None will directly take the default values from JSON


<details><summary>Example Helper Message:</summary>

```ruby
usage: runTableMaker.py [-h] [-runParallel] [--aod-memory-rate-limit AOD_MEMORY_RATE_LIMIT] [--writer WRITER] [--helpO2] [--add_mc_conv] [--add_fdd_conv] [--add_track_prop] [--add_weakdecay_ind]
                        [--debug {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}] [--logFile] [--override {true,false}] [--internal-dpl-aod-reader:time-limit]
                        [--internal-dpl-aod-reader:orbit-offset-enumeration] [--internal-dpl-aod-reader:orbit-multiplier-enumeration] [--internal-dpl-aod-reader:start-value-enumeration]
                        [--internal-dpl-aod-reader:end-value-enumeration] [--internal-dpl-aod-reader:step-value-enumeration] [--internal-dpl-aod-reader:aod-file] [--event-selection-task:syst]
                        [--event-selection-task:muonSelection] [--event-selection-task:customDeltaBC] [--event-selection-task:isMC] [--event-selection-task:processRun2]
                        [--event-selection-task:processRun3] [--track-selection:compatibilityIU] [--track-selection:isRun3] [--track-selection:itsMatching] [--track-selection:ptMin]
                        [--track-selection:ptMax] [--track-selection:etaMin] [--track-selection:etaMax] [--track-propagation:ccdb-url] [--track-propagation:lutPath]
                        [--track-propagation:geoPath] [--track-propagation:grpPath] [--track-propagation:mVtxPath] [--track-propagation:processStandard]
                        [--track-propagation:processCovariance] [--track-extension:compatibilityIU] [--track-extension:processRun2] [--track-extension:processRun3]
                        [--multiplicity-table:doVertexZeq] [--multiplicity-table:processRun2] [--multiplicity-table:processRun3] [--centrality-table:estRun2V0M]
                        [--centrality-table:estRun2SPDtks] [--centrality-table:estRun2SPDcls] [--centrality-table:estRun2CL0] [--centrality-table:estRun2CL1] [--centrality-table:estFV0A]
                        [--centrality-table:estFT0M] [--centrality-table:estFDDM] [--centrality-table:estNTPV] [--centrality-table:ccdburl] [--centrality-table:ccdbpath]
                        [--centrality-table:genname] [--centrality-table:processRun2] [--centrality-table:processRun3] [--v0-selector:d_bz_input] [--v0-selector:v0cospa]
                        [--v0-selector:v0max_mee] [--v0-selector:maxpsipair] [--v0-selector:dcav0dau] [--v0-selector:v0Rmin] [--v0-selector:v0Rmax] [--v0-selector:dcamin]
                        [--v0-selector:dcamax] [--v0-selector:mincrossedrows] [--v0-selector:maxchi2tpc] [--v0-selector:ccdb-url] [--v0-selector:lutPath] [--v0-selector:geoPath]
                        [--v0-selector:grpmagPath] [--track-pid-qa:dcamin] [--track-pid-qa:dcamax] [--track-pid-qa:mincrossedrows] [--track-pid-qa:maxchi2tpc] [--track-pid-qa:processQA]
                        [--v0-gamma-qa:processNM] [--tof-pid:param-file] [--tof-pid:param-sigma] [--tof-pid:ccdb-url] [--tof-pid:ccdbPath] [--tof-pid:ccdb-timestamp]
                        [--tof-pid:enableTimeDependentResponse] [--tof-pid:pid-el  ...]] [--tof-pid:pid-mu  ...]] [--tof-pid:pid-pi  ...]] [--tof-pid:pid-ka  ...]] [--tof-pid:pid-pr  ...]]
                        [--tof-pid:pid-de  ...]] [--tof-pid:pid-tr  ...]] [--tof-pid:pid-he  ...]] [--tof-pid:pid-al  ...]] [--tof-pid:processWSlice] [--tof-pid:processWoSlice]
                        [--tof-pid-full:param-file] [--tof-pid-full:param-sigma] [--tof-pid-full:ccdb-url] [--tof-pid-full:ccdbPath] [--tof-pid-full:ccdb-timestamp]
                        [--tof-pid-full:enableTimeDependentResponse] [--tof-pid-full:pid-el  ...]] [--tof-pid-full:pid-mu  ...]] [--tof-pid-full:pid-pi  ...]] [--tof-pid-full:pid-ka  ...]]
                        [--tof-pid-full:pid-pr  ...]] [--tof-pid-full:pid-de  ...]] [--tof-pid-full:pid-tr  ...]] [--tof-pid-full:pid-he  ...]] [--tof-pid-full:pid-al  ...]]
                        [--tof-pid-full:processWSlice] [--tof-pid-full:processWoSlice] [--tpc-pid-full:param-file] [--tpc-pid-full:ccdb-url] [--tpc-pid-full:ccdbPath]
                        [--tpc-pid-full:ccdb-timestamp] [--tpc-pid-full:useNetworkCorrection] [--tpc-pid-full:autofetchNetworks] [--tpc-pid-full:networkPathLocally]
                        [--tpc-pid-full:enableNetworkOptimizations] [--tpc-pid-full:networkPathCCDB] [--tpc-pid-full:pid-el  ...]] [--tpc-pid-full:pid-mu  ...]] [--tpc-pid-full:pid-pi  ...]]
                        [--tpc-pid-full:pid-ka  ...]] [--tpc-pid-full:pid-pr  ...]] [--tpc-pid-full:pid-de  ...]] [--tpc-pid-full:pid-tr  ...]] [--tpc-pid-full:pid-he  ...]]
                        [--tpc-pid-full:pid-al  ...]] [--dalitz-pairing:cfgEventCuts  ...]] [--dalitz-pairing:cfgDalitzTrackCuts  ...]] [--dalitz-pairing:cfgDalitzPairCuts  ...]]
                        [--dalitz-pairing:cfgAddTrackHistogram  ...]] [--dalitz-pairing:cfgQA] [--dalitz-pairing:cfgBarrelLowPIN] [--dalitz-pairing:cfgEtaCut]
                        [--dalitz-pairing:cfgTPCNSigElLow] [--dalitz-pairing:cfgTPCNSigElHigh] [--dalitz-pairing:processFullTracks] [--analysis-qvector:cfgEventCuts  ...]]
                        [--analysis-qvector:cfgBarrelTrackCuts  ...]] [--analysis-qvector:cfgMuonCuts  ...]] [--analysis-qvector:cfgQA] [--analysis-qvector:cfgCutPtMin]
                        [--analysis-qvector:cfgCutPtMax] [--analysis-qvector:cfgCutEtaMin] [--analysis-qvector:cfgCutEtaMax] [--analysis-qvector:cfgEtaLimitMin]
                        [--analysis-qvector:cfgEtaLimitMax] [--analysis-qvector:cfgNHarm] [--analysis-qvector:cfgNPow] [--analysis-qvector:cfgEfficiency] [--analysis-qvector:cfgAcceptance]
                        [--analysis-qvector:ccdb-url] [--analysis-qvector:ccdb-path] [--analysis-qvector:ccdb-no-later-than] [--analysis-qvector:processBarrelQvector]
                        [--d-q-barrel-track-selection-task:cfgBarrelTrackCuts  ...]] [--d-q-barrel-track-selection-task:cfgWithQA] [--d-q-barrel-track-selection-task:processSelection]
                        [--d-q-barrel-track-selection-task:processSelectionTiny] [--d-q-muons-selection:cfgMuonsCuts  ...]] [--d-q-muons-selection:cfgWithQA]
                        [--d-q-muons-selection:processSelection] [--d-q-event-selection-task:cfgEventCuts  ...]] [--d-q-event-selection-task:cfgWithQA]
                        [--d-q-event-selection-task:processEventSelection] [--d-q-filter-p-p-task:cfgBarrelSels  ...]] [--d-q-filter-p-p-task:cfgMuonSels  ...]]
                        [--d-q-filter-p-p-task:cfgWithQA] [--d-q-filter-p-p-task:processFilterPP] [--d-q-filter-p-p-task:processFilterPPTiny] [--table-maker:cfgEventCuts  ...]]
                        [--table-maker:cfgBarrelTrackCuts  ...]] [--table-maker:cfgMuonCuts  ...]] [--table-maker:cfgBarrelLowPt] [--table-maker:cfgMuonLowPt] [--table-maker:cfgMinTpcSignal]
                        [--table-maker:cfgMaxTpcSignal] [--table-maker:cfgQA] [--table-maker:cfgDetailedQA] [--table-maker:cfgAddEventHistogram  ...]]
                        [--table-maker:cfgAddTrackHistogram  ...]] [--table-maker:cfgAddMuonHistogram  ...]] [--table-maker:cfgIsRun2] [--table-maker:cfgIsAmbiguous] [--table-maker:ccdb-url]
                        [--table-maker:ccdb-path-tpc] [--table-maker:cfgTPCpostCalib] [--table-maker:processFull] [--table-maker:processFullWithCov] [--table-maker:processFullWithCent]
                        [--table-maker:processBarrelOnlyWithV0Bits] [--table-maker:processBarrelOnlyWithDalitzBits] [--table-maker:processBarrelOnlyWithEventFilter]
                        [--table-maker:processBarrelOnlyWithQvector] [--table-maker:processBarrelOnlyWithCent] [--table-maker:processBarrelOnlyWithCov] [--table-maker:processBarrelOnly]
                        [--table-maker:processMuonOnlyWithCent] [--table-maker:processMuonOnlyWithCov] [--table-maker:processMuonOnly] [--table-maker:processMuonOnlyWithQvector]
                        [--table-maker:processMuonOnlyWithFilter] [--table-maker:processAmbiguousMuonOnly] [--table-maker:processAmbiguousBarrelOnly] [--table-maker:processOnlyBCs]
                        Config.json

Arguments to pass

positional arguments:
  Config.json           config JSON file name (mandatory)

options:
  -h, --help            show this help message and exit
  -runParallel          Run parallel sessions (default: False)

Global workflow options:
  --aod-memory-rate-limit AOD_MEMORY_RATE_LIMIT
                        Rate limit AOD processing based on memory (default: None)
  --writer WRITER       Argument for producing extra reduced tables (default: None)
  --helpO2              Display help message on O2 (default: False)

Add to workflow O2 Converter task options:
  --add_mc_conv         Add the converter from mcparticle to mcparticle+001 (Adds your workflow o2-analysis-mc-converter task) (default: False)
  --add_fdd_conv        Add the fdd converter (Adds your workflow o2-analysis-fdd-converter task) (default: False)
  --add_track_prop      Add track propagation to the innermost layer (TPC or ITS) (Adds your workflow o2-analysis-track-propagation task) (default: False)
  --add_weakdecay_ind   Add Converts V0 and cascade version 000 to 001 (Adds your workflow o2-analysis-weak-decay-indices task) (default: False)

Helper Options:
  --debug {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        execute with debug options (default: INFO)
  --logFile             Enable logger for both file and CLI (default: False)
  --override {true,false}
                        If false JSON Overrider Interface If true JSON Additional Interface (default: true)

JSON configuration options:
  --internal-dpl-aod-reader:time-limit 
  --internal-dpl-aod-reader:orbit-offset-enumeration 
  --internal-dpl-aod-reader:orbit-multiplier-enumeration 
  --internal-dpl-aod-reader:start-value-enumeration 
  --internal-dpl-aod-reader:end-value-enumeration 
  --internal-dpl-aod-reader:step-value-enumeration 
  --internal-dpl-aod-reader:aod-file 
  --event-selection-task:syst 
  --event-selection-task:muonSelection 
  --event-selection-task:customDeltaBC 
  --event-selection-task:isMC 
  --event-selection-task:processRun2 
  --event-selection-task:processRun3 
  --track-selection:compatibilityIU 
  --track-selection:isRun3 
  --track-selection:itsMatching 
  --track-selection:ptMin 
  --track-selection:ptMax 
  --track-selection:etaMin 
  --track-selection:etaMax 
  --track-propagation:ccdb-url 
  --track-propagation:lutPath 
  --track-propagation:geoPath 
  --track-propagation:grpPath 
  --track-propagation:mVtxPath 
  --track-propagation:processStandard 
  --track-propagation:processCovariance 
  --track-extension:compatibilityIU 
  --track-extension:processRun2 
  --track-extension:processRun3 
  --multiplicity-table:doVertexZeq 
  --multiplicity-table:processRun2 
  --multiplicity-table:processRun3 
  --centrality-table:estRun2V0M 
  --centrality-table:estRun2SPDtks 
  --centrality-table:estRun2SPDcls 
  --centrality-table:estRun2CL0 
  --centrality-table:estRun2CL1 
  --centrality-table:estFV0A 
  --centrality-table:estFT0M 
  --centrality-table:estFDDM 
  --centrality-table:estNTPV 
  --centrality-table:ccdburl
```
</details>

You will receive a message that. also you can run helper messages in O2 framework with  `--helpO2` argument e.g:

```ruby
 python3 runTableMakerMC.py configs/configTableMakerMCRun3.json --helpO2
 ```

<details><summary>You will displayed</summary>

 ```ruby
 ALICE O2 DPL workflow driver (full help)

Executor options:
  -h [ --help ] [=arg(=short)]          print help: short, full, executor, or 
                                        processor name
  -q [ --quiet ]                        quiet operation
  -s [ --stop ]                         stop before device start
  --single-step                         start in single step mode
  -b [ --batch ]                        batch processing mode
  --no-batch                            force gui processing mode
  --no-cleanup                          do not cleanup the shm segment
  --hostname arg (=localhost)           hostname to deploy
  --resources arg                       resources allocated for the workflow
  -p [ --start-port ] arg (=22000)      start port to allocate
  --port-range arg (=1000)              ports in range
  -c [ --completion-policy ] arg (=quit)
                                        what to do when processing is finished:
                                        quit, wait
  --error-policy arg (=quit)            what to do when a device has an error: 
                                        quit, wait
  --min-failure-level arg (=fatal)      minimum message level which will be 
                                        considered as fatal and exit with 1
  -g [ --graphviz ]                     produce graphviz output
  --mermaid arg                         produce graph output in mermaid format 
                                        in file under specified name or on 
                                        stdout if argument is "-"
  -t [ --timeout ] arg (=0)             forced exit timeout (in seconds)
  -D [ --dds ] arg                      create DDS configuration
  -D [ --dds-workflow-suffix ] arg      suffix for DDS names
  --dump-workflow                       dump workflow as JSON
  --dump-workflow-file arg (=-)         file to which do the dump
  --run                                 run workflow merged so far. It implies 
                                        --batch. Use --no-batch to see the GUI
  --no-IPC                              disable IPC topology optimization
  --o2-control arg                      dump O2 Control workflow configuration 
                                        under the specified name
  --resources-monitoring arg (=0)       enable cpu/memory monitoring for 
                                        provided interval in seconds
  --resources-monitoring-dump-interval arg (=0)
                                        dump monitoring information to disk 
                                        every provided seconds

  --severity arg (=info)                severity level of the log
  -P [ --plugin ] arg                   FairMQ plugin list
  -S [ --plugin-search-path ] arg       FairMQ plugins search path
  --control-port arg                    Utility port to be used by O2 Control
  --rate arg                            rate for a data source device (Hz)
  --exit-transition-timeout arg         timeout before switching to READY state
  --expected-region-callbacks arg       region callbacks to expect before 
                                        starting
  --timeframes-rate-limit arg (=0)      how many timeframes can be in fly
  --shm-monitor arg                     whether to use the shared memory 
                                        monitor
  --channel-prefix arg                  prefix to use for multiplexing multiple
                                        workflows in the same session
  --bad-alloc-max-attempts arg (=1)     throw after n attempts to alloc shm
  --bad-alloc-attempt-interval arg (=50)
                                        interval between shm alloc attempts in 
                                        ms
  --io-threads arg (=1)                 number of FMQ io threads
  --shm-segment-size arg                size of the shared memory segment in 
                                        bytes
  --shm-mlock-segment arg (=false)      mlock shared memory segment
  --shm-mlock-segment-on-creation arg (=false)
                                        mlock shared memory segment once on 
                                        creation
  --shm-zero-segment arg (=false)       zero shared memory segment
  --shm-throw-bad-alloc arg (=true)     throw if insufficient shm memory
  --shm-segment-id arg (=0)             shm segment id
  --shm-allocation arg (=rbtree_best_fit)
                                        shm allocation method
  --shm-no-cleanup arg (=false)         no shm cleanup
  --shmid arg                           shmid
  --environment arg                     comma separated list of environment 
                                        variables to set for the device
  --stacktrace-on-signal arg (=simple)  dump stacktrace on specified signal(s) 
                                        (any of `all`, `segv`, `bus`, `ill`, 
                                        `abrt`, `fpe`, `sys`.)Use `simple` to 
                                        dump only the main thread in a reliable
                                        way
  --post-fork-command arg               post fork command to execute (e.g. 
                                        numactl {pid}
  --session arg                         unique label for the shared memory 
                                        session
  --network-interface arg               network interface to which to bind tpc 
                                        fmq ports without specified address
  --early-forward-policy arg (=never)   when to forward early the messages: 
                                        never, noraw, always
  --configuration arg                   configuration connection string
  --driver-client-backend arg           driver connection string
  --monitoring-backend arg              monitoring connection string
  --infologger-mode arg                 O2_INFOLOGGER_MODE override
  --infologger-severity arg             minimun FairLogger severity which goes 
                                        to info logger
  --dpl-tracing-flags arg               pipe separated list of events to trace
  --child-driver arg                    external driver to start childs with 
                                        (e.g. valgrind)


Global workflow options:
  --readers arg (=1)                    number of parallel readers to use
  --spawners arg (=1)                   number of parallel spawners to use
  --pipeline arg                        override default pipeline size
  --clone arg                           clone processors from a template
  --labels arg                          add labels to dataprocessors
  --workflow-suffix arg                 suffix to add to all dataprocessors
  --timeframes-rate-limit-ipcid arg (=-1)
                                        Suffix for IPC channel for 
                                        metrix-feedback, -1 = disable
  --aod-memory-rate-limit arg (=0)      Rate limit AOD processing based on 
                                        memory
  --aod-writer-json arg                 Name of the json configuration file
  --aod-writer-resdir arg               Name of the output directory
  --aod-writer-resfile arg              Default name of the output file
  --aod-writer-maxfilesize arg (=0)     Maximum size of an output file in 
                                        megabytes
  --aod-writer-resmode arg (=RECREATE)  Creation mode of the result files: NEW,
                                        CREATE, RECREATE, UPDATE
  --aod-writer-ntfmerge arg (=-1)       Number of time frames to merge into one
                                        file
  --aod-writer-keep arg                 Comma separated list of 
                                        ORIGIN/DESCRIPTION/SUBSPECIFICATION:tre
                                        ename:col1/col2/..:filename
  --fairmq-rate-logging arg (=0)        Rate logging for FairMQ channels
  --fairmq-recv-buffer-size arg (=4)    recvBufferSize option for FairMQ 
                                        channels
  --fairmq-send-buffer-size arg (=4)    sendBufferSize option for FairMQ 
                                        channels
  --fairmq-ipc-prefix arg (=@)          Prefix for FairMQ channels location
  --forwarding-policy arg (=dangling)   Which messages to forward. *dangling*: 
                                        dangling outputs, all: all messages, 
                                        none: no forwarding - it will complain 
                                        if you try to create dangling outputs
  --forwarding-destination arg (=drop)  Destination for forwarded messages. 
                                        drop: simply drop them, file: write to 
                                        file, fairmq: send to output proxy

Available data processors:
  --internal-dpl-clock arg              Option groups by process name: 
                                        --internal-dpl-clock "<processor 
                                        options>"
  --internal-dpl-aod-reader arg         Option groups by process name: 
                                        --internal-dpl-aod-reader "<processor 
                                        options>"
  --internal-dpl-injected-dummy-sink arg
                                        Option groups by process name: 
                                        --internal-dpl-injected-dummy-sink 
                                        "<processor options>"
  --analysis-event-selection arg        Option groups by process name: 
                                        --analysis-event-selection "<processor 
                                        options>"
  --analysis-muon-selection arg         Option groups by process name: 
                                        --analysis-muon-selection "<processor 
                                        options>"
  --analysis-track-selection arg        Option groups by process name: 
                                        --analysis-track-selection "<processor 
                                        options>"
  --analysis-same-event-pairing arg     Option groups by process name: 
                                        --analysis-same-event-pairing 
                                        "<processor options>"
  --analysis-event-mixing arg           Option groups by process name: 
                                        --analysis-event-mixing "<processor 
                                        options>"
  --internal-dpl-aod-writer arg         Option groups by process name: 
                                        --internal-dpl-aod-writer "<processor 
                                        options>"
  --analysis-dilepton-hadron arg        Option groups by process name: 
                                        --analysis-dilepton-hadron "<processor 
                                        options>"
  --internal-dpl-aod-global-analysis-file-sink arg
                                        Option groups by process name: 
                                        --internal-dpl-aod-global-analysis-file
                                        -sink "<processor options>"

Data processor options: internal-dpl-aod-reader:
  --aod-file arg                        Input AOD file
  --aod-reader-json arg                 json configuration file
  --aod-parent-access-level arg         Allow parent file access up to 
                                        specified level. Default: no (0)
  --aod-parent-base-path-replacement arg
                                        Replace base path of parent files. 
                                        Syntax: FROM;TO. E.g. 
                                        "alien:///path/in/alien;/local/path". 
                                        Enclose in "" on the command line.
  --time-limit arg (=0)                 Maximum run time limit in seconds
  --orbit-offset-enumeration arg (=0)   initial value for the orbit
  --orbit-multiplier-enumeration arg (=0)
                                        multiplier to get the orbit from the 
                                        counter
  --start-value-enumeration arg (=0)    initial value for the enumeration
  --end-value-enumeration arg (=-1)     final value for the enumeration
  --step-value-enumeration arg (=1)     step between one value and the other

Data processor options: analysis-event-selection:
  --cfgMixingVars arg                   Mixing configs separated by a comma, 
                                        default no mixing
  --cfgEventCuts arg (=eventStandard)   Event selection
  --cfgQA                               If true, fill QA histograms
  --cfgAddEventHistogram arg            Comma separated list of histograms
  --processSkimmed                      Run event selection on DQ skimmed 
                                        events
  --processDummy                        Dummy function

Data processor options: analysis-muon-selection:
  --cfgMuonCuts arg (=muonQualityCuts)  Comma separated list of muon cuts
  --cfgQA                               If true, fill QA histograms
  --cfgAddMuonHistogram arg             Comma separated list of histograms
  --processSkimmed                      Run muon selection on DQ skimmed muons
  --processDummy                        Dummy function

Data processor options: analysis-track-selection:
  --cfgTrackCuts arg (=jpsiPID1)        Comma separated list of barrel track 
                                        cuts
  --cfgQA                               If true, fill QA histograms
  --cfgAddTrackHistogram arg            Comma separated list of histograms
  --processSkimmed                      Run barrel track selection on DQ 
                                        skimmed tracks
  --processDummy                        Dummy function

Data processor options: analysis-same-event-pairing:
  --cfgTrackCuts arg                    Comma separated list of barrel track 
                                        cuts
  --cfgMuonCuts arg                     Comma separated list of muon cuts
  --ccdb-url arg (=http://ccdb-test.cern.ch:8080)
                                        url of the ccdb repository
  --ccdb-path arg (=Users/lm)           base path to the ccdb object
  --ccdb-no-later-than arg (=1671456802412)
                                        latest acceptable timestamp of creation
                                        for the object
  --cfgAddSEPHistogram arg              Comma separated list of histograms
  --processDecayToEESkimmed             Run electron-electron pairing, with 
                                        skimmed tracks
  --processDecayToMuMuSkimmed           Run muon-muon pairing, with skimmed 
                                        muons
  --processDecayToMuMuVertexingSkimmed  Run muon-muon pairing and vertexing, 
                                        with skimmed muons
  --processVnDecayToEESkimmed           Run electron-electron pairing, with 
                                        skimmed tracks for vn
  --processVnDecayToMuMuSkimmed         Run muon-muon pairing, with skimmed 
                                        tracks for vn
  --processElectronMuonSkimmed          Run electron-muon pairing, with skimmed
                                        tracks/muons
  --processAllSkimmed                   Run all types of pairing, with skimmed 
                                        tracks/muons
  --processDummy                        Dummy function, enabled only if none of
                                        the others are enabled

Data processor options: analysis-event-mixing:
  --cfgTrackCuts arg                    Comma separated list of barrel track 
                                        cuts
  --cfgMuonCuts arg                     Comma separated list of muon cuts
  --cfgMixingDepth arg (=100)           Number of Events stored for event 
                                        mixing
  --cfgAddEventMixingHistogram arg      Comma separated list of histograms
  --processBarrelSkimmed                Run barrel-barrel mixing on skimmed 
                                        tracks
  --processMuonSkimmed                  Run muon-muon mixing on skimmed muons
  --processBarrelMuonSkimmed            Run barrel-muon mixing on skimmed 
                                        tracks/muons
  --processBarrelVnSkimmed              Run barrel-barrel vn mixing on skimmed 
                                        tracks
  --processMuonVnSkimmed                Run muon-muon vn mixing on skimmed 
                                        tracks
  --processDummy                        Dummy function

Data processor options: analysis-dilepton-hadron:
  --cfgLeptonCuts arg                   Comma separated list of barrel track 
                                        cuts
  --cfgAddDileptonHadHistogram arg      Comma separated list of histograms
  --processSkimmed                      Run dilepton-hadron pairing, using 
                                        skimmed data
  --processDummy                        Dummy function
 ```
 
 </details>
 
You will see helper messages again. As long as this command is added in the parameters, the script will not run and will only show a help message.

## Debug and Logging Options for O2DQWorkflows and DownloadLibs.py

We have Debug options if you want to follow the flow in the Interface. For this, you can configure your script as `--debug` `<Level>` in the terminal. You can check which levels are valid and at which level to debug from the table. Also if you want to keep your LOG log in a file then the `--logFile` argument should be added to the workflow.

The LOG file will be created the same as the workflow name. For example, the file that will be created for tableMaker will be `tableMaker.log`. In addition, if you work with the debug option, the old LOG file will be automatically deleted first, so that there is no confusion in the log files and it does not override. Then a new LOG file will be created.

* You can See Debug Levels in the table:
  
Level | Numeric Value |
| --- | --- |
`NOTSET` | 0 |
`DEBUG` | 10 |
`INFO` | 20 |
`WARNING` | 30 |
`ERROR` | 40 |
`CRITICAL` | 50 |

You can see the debug messages of the numeric value you selected and the level above. If you want debug with `--debug` argument, you must select the Level you want to debug.

Example usage Logging for Both File and terminal:

```ruby 
  python3 runTableMaker.py configs/configTableMakerDataRun3.json --debug DEBUG --logFile --table-maker:processFull true --internal-dpl-aod-reader:aod-file Datas/AO2D.root --table-maker:cfgMuonCuts muonQualityCuts muonTightQualityCutsForTests --event-selection-task:syst pp --add_track_prop
```

Example usage for only logging to terminal:

```ruby 
  python3 runAnalysis.py configs/configAnalysisData.json --analysis-event-selection:processSkimmed true --analysis-track-selection:processSkimmed true --analysis-same-event-pairing:processDecayToEESkimmed true --analysis-track-selection:cfgTrackCuts jpsiO2MCdebugCuts --analysis-same-event-pairing:cfgTrackCuts jpsiO2MCdebugCuts --internal-dpl-aod-reader:aod-file Datas/reducedAod.root --debug debug --logFile
```

For example, when the file is logged, you should see a result like this when you open the relevant file.


<details><summary>Log Message:</summary>

```ruby 
[INFO] Only Select Configured as true
[INFO] INTERFACE MODE : JSON Overrider
[INFO]  - [internal-dpl-aod-reader] aod_file : Datas/AO2D_ppMCRun3_LHC21i3b.root
[INFO]  - [analysis-event-selection] processSkimmed : true
[INFO]  - [analysis-track-selection] cfgTrackCuts : jpsiO2MCdebugCuts
[INFO]  - [analysis-track-selection] processSkimmed : true
[INFO]  - [analysis-same-event-pairing] cfgTrackCuts : jpsiO2MCdebugCuts
[INFO]  - [analysis-same-event-pairing] processDecayToEESkimmed : true
[INFO] You provided single AO2D root file : Datas/AO2D_ppMCRun3_LHC21i3b.root
[INFO] Datas/AO2D_ppMCRun3_LHC21i3b.root has valid File Format and Path, File Found
[INFO] Command to run:
[INFO] o2-analysis-dq-table-reader --configuration json://tempConfigTableReader.json -b
[INFO] Args provided configurations List
[INFO] --cfgFileName : configs/configAnalysisData.json 
[INFO] --runParallel : False 
[INFO] --helpO2 : False 
[INFO] --add_mc_conv : False 
[INFO] --add_fdd_conv : False 
[INFO] --add_track_prop : False 
[INFO] --add_weakdecay_ind : False 
[INFO] --debug : DEBUG 
[INFO] --logFile : True 
[INFO] --override : true 
[INFO] --internal_dpl_aod_reader:aod_file : Datas/AO2D_ppMCRun3_LHC21i3b.root 
[INFO] --analysis_event_selection:processSkimmed : true 
[INFO] --analysis_track_selection:cfgTrackCuts : ['jpsiO2MCdebugCuts'] 
[INFO] --analysis_track_selection:processSkimmed : true 
[INFO] --analysis_same_event_pairing:cfgTrackCuts : ['jpsiO2MCdebugCuts'] 
[INFO] --analysis_same_event_pairing:processDecayToEESkimmed : true 
[INFO] Inserting inside for pycache remove: /home/batu/PythonInterfaceOOP/PythonInterfaceOOP
[INFO] pycaches removed succesfully
```
 </details>

## Some Things You Should Be Careful For Using and Development

* The runAnalysis, runTableMaker, and runEmEfficiency scripts have some selections for MC/Data or skimmed/not skimmed. By changing them to boolean from True or False, we make choices like Data or MC and skimmed or not skimmed. Keep this in mind.
* if your dataset is for run3, o2-analysis-trackextension will be automatically deleted from your workflow as if you define `--add_track_prop` argument for track-propagation. If the production of the data you want to analyze is new, you should add the o2-analysis-track-propagation task to your workflow with the `--add_track_prop` argument. You can found detalis from there [`Click Here`](https://aliceo2group.github.io/analysis-framework/docs/basics-usage/HelperTasks.html#track-selection)

## Some Notes Before The Instructions

* You don't need configure all the parameters in the Python interface. the parameter you did not configure will remain as the value in the JSON.
* Don't forget to configure your Config JSON file in interface for each workflow.
* Sometimes you may need to add extra tables and transformations to your workflow to resolve the errors you get. These are related to the data model and the production tag. It is stated in the steps that they will be used when errors are received. If you get an error about these add the relevant parameter to your workflow (you can look at troubleshoot tree not found section).

## Interface Modes: JSON Overrider and JSON Additional

The only select parameter gives you a choice depending on whether you want to keep your old configurations of the interface.

If `--override` is configured to true, you will run in JSON overrider interface mode (default value of this parameter is true).
only commands entered in the terminal for some parameters will preserved, while others are set to false.

If --override is false, you will run in JSON additional interface mode. the values ​​in your original JSON file will be preserved, values ​​entered from the terminal will be appended to the JSON. It would be much better to explain this through an example.

For example, let's say we're working on a tableMaker:

  ```ruby
    "table-maker": {
        "cfgEventCuts": "eventStandardNoINT7",
        "cfgBarrelTrackCuts": "jpsiO2MCdebugCuts2,jpsiO2MCdebugCuts3,jpsiO2MCdebugCuts,kaonPID",
        "cfgMuonCuts": "muonQualityCuts,muonTightQualityCutsForTests",
        "cfgBarrelLowPt": "0.5",
        "cfgMuonLowPt": "0.5",
        "cfgMinTpcSignal": "50",
        "cfgMaxTpcSignal": "200",
        "cfgNoQA": "false",
        "cfgDetailedQA": "true",
        "cfgIsRun2": "false",
        "processFull": "true",
        "processFullWithCov": "true",
        "processFullWithCent": "false",
        "processBarrelOnlyWithV0Bits": "false",
        "processBarrelOnlyWithEventFilter": "false",
        "processBarrelOnlyWithQvector" : "false",
        "processBarrelOnlyWithCent": "false",
        "processBarrelOnlyWithCov": "false",
        "processBarrelOnly": "false",
        "processMuonOnlyWithCent": "false",
        "processMuonOnlyWithCov": "false",
        "processMuonOnly": "false",
        "processMuonOnlyWithQvector": "false",
        "processMuonOnlyWithFilter": "false",
        "processOnlyBCs": "true"
    },
  ```

As seen here, the process functions for Full, FullWithCov, and OnlyBCs are true. Let's assume that we made the following configuration for the interface in the terminal:

```ruby
python3 runTableMaker.py configs/configTableMakerDataRun2.json --table-maker:processOnlyBCs true table-maker:processBarrelOnlyWithCent true --override true
```
P.S. Since override is true (you don't need to add it to your workflow when configuring `--override` to true, its default value is true I just added it to show, JSON Overrider Mode):

  ```ruby
    "table-maker": {
        "cfgEventCuts": "eventStandardNoINT7",
        "cfgBarrelTrackCuts": "jpsiO2MCdebugCuts2,jpsiO2MCdebugCuts3,jpsiO2MCdebugCuts,kaonPID",
        "cfgMuonCuts": "muonQualityCuts,muonTightQualityCutsForTests",
        "cfgBarrelLowPt": "0.5",
        "cfgMuonLowPt": "0.5",
        "cfgMinTpcSignal": "50",
        "cfgMaxTpcSignal": "200",
        "cfgNoQA": "false",
        "cfgDetailedQA": "true",
        "cfgIsRun2": "false",
        "processFull": "false",
        "processFullWithCov": "false",
        "processFullWithCent": "false",
        "processBarrelOnlyWithV0Bits": "false",
        "processBarrelOnlyWithEventFilter": "false",
        "processBarrelOnlyWithQvector" : "false",
        "processBarrelOnlyWithCent": "true",
        "processBarrelOnlyWithCov": "false",
        "processBarrelOnly": "false",
        "processMuonOnlyWithCent": "false",
        "processMuonOnlyWithCov": "false",
        "processMuonOnly": "false",
        "processMuonOnlyWithQvector": "false",
        "processMuonOnlyWithFilter": "false",
        "processOnlyBCs": "true"
    },
  ```

As you can see, only the OnlyBCs and BarrelOnlyWithCent process functions are set to true, while all other process functions in the tableMaker are set to false.

If we configured override to false (JSON Additional Mode):

```ruby
python3 runTableMaker.py configs/configTableMakerDataRun2.json --table-maker:processOnlyBCs true table-maker:processBarrelOnlyWithCent true --override false
```

Then our output would be:

  ```ruby
    "table-maker": {
        "cfgEventCuts": "eventStandardNoINT7",
        "cfgBarrelTrackCuts": "jpsiO2MCdebugCuts2,jpsiO2MCdebugCuts3,jpsiO2MCdebugCuts,kaonPID",
        "cfgMuonCuts": "muonQualityCuts,muonTightQualityCutsForTests",
        "cfgBarrelLowPt": "0.5",
        "cfgMuonLowPt": "0.5",
        "cfgMinTpcSignal": "50",
        "cfgMaxTpcSignal": "200",
        "cfgNoQA": "false",
        "cfgDetailedQA": "true",
        "cfgIsRun2": "false",
        "processFull": "true",
        "processFullWithCov": "true",
        "processFullWithCent": "false",
        "processBarrelOnlyWithV0Bits": "false",
        "processBarrelOnlyWithEventFilter": "false",
        "processBarrelOnlyWithQvector" : "false",
        "processBarrelOnlyWithCent": "true",
        "processBarrelOnlyWithCov": "false",
        "processBarrelOnly": "false",
        "processMuonOnlyWithCent": "false",
        "processMuonOnlyWithCov": "false",
        "processMuonOnly": "false",
        "processMuonOnlyWithQvector": "false",
        "processMuonOnlyWithFilter": "false",
        "processOnlyBCs": "true"
    },
  ```

As you can see, the old process values ​​Full and FullWithCov remained true, in addition, the BarrelOnlyWithCent process function was set to true. OnlyBCs was already true and remains true.

This is the case for the `--process`, `--pid` and `--est` parameters.

A similar situation applies to Analysis Cut configurations and MC Signal configurations. Suppose there is a configuration like this in it (for tableReader):

  ```ruby
    "analysis-track-selection": {
        "cfgTrackCuts": "jpsiO2MCdebugCuts2",
        "cfgTrackMCSignals": "eFromJpsi,eFromLMeeLF",
        "cfgQA": "true",
        "processSkimmed": "true",
        "processDummy": "false"
    },
  ```

Here we will configure the track cuts:

```ruby
python3 runAnalysis.py configs/configAnalysisData.json --analysis-track-selection:cfgTrackCuts jpsiPID1 jpsiPID2
```

The JSON is in overrider mode as the default is override true and the equivalent of this configuration is:

  ```ruby
    "analysis-track-selection": {
        "cfgTrackCuts": "jpsiPID1,jpsiPID2",
        "cfgTrackMCSignals": "eFromJpsi,eFromLMeeLF",
        "cfgQA": "true",
        "processSkimmed": "true",
        "processDummy": "false"
    },
  ```

As we can see, the old cut values ​​were deleted, the new cut values ​​were taken from the CLI.

If override is False:

```ruby
python3 runAnalysis.py configs/configAnalysisData.json --analysis-track-selection:cfgTrackCuts jpsiPID1 jpsiPID2 --override false
```

Then the JSON is in additional mode and the equivalent of this configuration is:

  ```ruby
    "analysis-track-selection": {
        "cfgTrackCuts": "jpsiO2MCdebugCuts2,jpsiPID1,jpsiPID2",
        "cfgTrackMCSignals": "eFromJpsi,eFromLMeeLF",
        "cfgQA": "true",
        "processSkimmed": "true",
        "processDummy": "false"
    },
  ```

As we can see, our old track cut value has been preserved and extra new ones have been added.

This is the same for all analysis cuts, MC Signals, barrel and muon sels in filterPP and mixing vars.

This is the main reason why Interface works in these two modes. If you already have a JSON configuration file prepared for a specific data for analysis, it makes sense to use JSON additional mode if you just want to add some values. Because you will want to preserve the old values.

If you are going to do an analysis from zero and you will prepare your JSON configuration file accordingly, or if you want to completely change your analysis values, then it makes sense to use JSON overrider mode. Because the default JSON files must be manipulated in accordance with the analysis (like configAnalysisData.json) or you choose this mode to change the complete analysis values



## Project Architecture

TODO explain this

[← Go back to Instructions For Instructions for TAB Autocomplete](3_InstructionsforTABAutocomplete.md) | [↑ Go to the Table of Content ↑](../README.md) | [Continue to Instructions For Python Scripts →](5_InstructionsForPythonScripts.md)