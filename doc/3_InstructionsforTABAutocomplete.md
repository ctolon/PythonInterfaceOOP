# Instructions for TAB Autocomplete

@tableofcontents

Before proceeding to this stage, you should make sure that you activate the O2 environment with alienv, then install the argcomplete package with `pip install argcomplete` and `pip3 install argcomplete` in O2, and then source the autocomplete bash script with `source argcomplete.sh`

You can Complete this with a TAB key after each word and character you type in command line. Keep this thing in your mind.

If you have successfully installed this package and successfully sourced the script, follow these steps.

**Step 1**: Type python3 (If your symbolic link is python for python3, type python)

```ruby
python3
```

**Step 2**: Type the name of your script (e.g runTableMaker.py)
```ruby
python3 runTableMaker.py
```

**Step 3**: At this stage, since the JSON configuration files are in the Configs folder, enter the name of your JSON config file by completing it with TAB or listing the available options

for ex. if you type:

```ruby
python3 runTableMaker.py configs
```

you will get this displayed options in your terminal:
```ruby
configs/configAnalysisData.json                  configs/configFlowDataRun3.json                  configs/configtestFilterPPDataRun3.json          configs/readerConfiguration_reducedEventMC.json
configs/configAnalysisMC.json                    configs/configTableMakerDataRun2.json            configs/configtestFlowDataRun3.json              configs/writerConfiguration_dileptonMC.json
configs/configFilterPPDataRun2.json              configs/configTableMakerDataRun3.json            configs/configtestTableMakerDataRun3.json        configs/writerConfiguration_dileptons.json
configs/configFilterPPDataRun3.json                  configs/configTableMakerMCRun2.json              configs/readerConfiguration_dilepton.json        
configs/configFlowDataRun2.json                  configs/configTableMakerMCRun3.json              configs/readerConfiguration_reducedEvent.json 
```

then you can complete your JSON config file (for example assuming you export configTableMakerMCRun3.json to configure tablemaker for mc run 3

```ruby
python3 runTableMaker.py configs/configTableMakerDataRun3.json
```

**P.S** You can Complete this with a TAB key after each word and character you type in command line.

**Step 4**: Now when you type -- and press TAB key all parameter options in interface will be listed

```ruby
python3 runTableMaker.py configs/configTableMakerDataRun3.json --
```

if you type like this and press TAB you will see all the parameters in the interface in your terminal like this:
```ruby
--add_fdd_conv                                          --internal-dpl-aod-reader:aod-file                      --tof-pid:param-sigma
--add_mc_conv                                           --internal-dpl-aod-reader:end-value-enumeration         --tof-pid:pid-al
--add_track_prop                                        --internal-dpl-aod-reader:orbit-multiplier-enumeration  --tof-pid:pid-de
--add_weakdecay_ind                                     --internal-dpl-aod-reader:orbit-offset-enumeration      --tof-pid:pid-el
--analysis-qvector:ccdb-no-later-than                   --internal-dpl-aod-reader:start-value-enumeration       --tof-pid:pid-he
--analysis-qvector:ccdb-path                            --internal-dpl-aod-reader:step-value-enumeration        --tof-pid:pid-ka
--analysis-qvector:ccdb-url                             --internal-dpl-aod-reader:time-limit                    --tof-pid:pid-mu
--analysis-qvector:cfgAcceptance                        --logFile                                               --tof-pid:pid-pi
--analysis-qvector:cfgBarrelTrackCuts                   --multiplicity-table:doVertexZeq                        --tof-pid:pid-pr
--analysis-qvector:cfgCutEta                            --multiplicity-table:processRun2                        --tof-pid:pid-tr
--analysis-qvector:cfgCutPtMax                          --multiplicity-table:processRun3                        --tof-pid:processWoSlice
--analysis-qvector:cfgCutPtMin                          --overrider                                             --tof-pid:processWSlice
--analysis-qvector:cfgEfficiency                        --table-maker:ccdb-path-tpc                             --tpc-pid-full:autofetchNetworks
--analysis-qvector:cfgEtaLimit                          --table-maker:ccdb-url                                  --tpc-pid-full:ccdbPath
--analysis-qvector:cfgEventCuts                         --table-maker:cfgAddEventHistogram                      --tpc-pid-full:ccdb-timestamp
etc.
```

**Step 5**: After entering one of these parameters (e.g --table-maker:cfgBarrelTrackCuts for runTableMaker.py) leave a space and press tab again. As a result you will see each value this parameter can take.

```ruby
python3 runTableMaker.py configs/configTableMakerMCRun3.json --table-maker:cfgBarrelTrackCuts 
```


If you leave a space after cfgBarrelTrackCuts and press TAB:

```ruby
electronPID1                         eventStandard                        jpsiPIDshift                         matchedGlobal                        PIDCalib
electronPID1randomized               eventStandardNoINT7                  jpsiPIDworseRes                      mchTrack                             pidcalib_ele
electronPID1shiftDown                highPtHadron                         jpsiStandardKine                     muonHighPt                           PIDStandardKine
electronPID1shiftUp                  int7vtxZ5                            kaonPID                              muonLowPt                            singleDCA
electronPID2                         jpsiBenchmarkCuts                    kaonPIDnsigma                        muonQualityCuts                      standardPrimaryTrack
electronPID2randomized               jpsiKineAndQuality                   lmee_GlobalTrack                     muonTightQualityCutsForTests         TightGlobalTrack
electronPIDnsigma                    jpsiO2MCdebugCuts                    lmee_GlobalTrackRun3                 NoPID                                TightGlobalTrackRun3
electronPIDnsigmaLoose               jpsiO2MCdebugCuts2                   lmee_GlobalTrackRun3_lowPt           pairDCA                              TightTPCTrackRun3
electronPIDnsigmaOpen                jpsiO2MCdebugCuts3                   lmee_GlobalTrackRun3_TPC_ePID_lowPt  pairJpsi                             tof_electron
electronPIDnsigmaRandomized          jpsiPID1                             lmeeLowBKine                         pairJpsiLowPt1                       tof_electron_loose
electronPIDshift                     jpsiPID1Randomized                   lmeePID_TOFrec                       pairJpsiLowPt2                       tpc_electron
electronPIDworseRes                  jpsiPID1shiftDown                    lmeePID_TPChadrej                    pairMassLow                          tpc_kaon_rejection
electronStandardQuality              jpsiPID1shiftUp                      lmeePID_TPChadrejTOFrec              pairNoCut                            tpc_pion_band_rejection
electronStandardQualityBenchmark     jpsiPID2                             lmeePID_TPChadrejTOFrecRun3          pairPsi2S                            tpc_pion_rejection
electronStandardQualityForO2MCdebug  jpsiPID2Randomized                   lmeeStandardKine                     pairPtLow1                           tpc_pion_rejection_highp
eventDimuonStandard                  jpsiPIDnsigma                        lmee_TPCTrackRun3_lowPt              pairPtLow2                           tpc_proton_rejection
eventMuonStandard                    jpsiPIDnsigmaRandomized              matchedFwd                           pairUpsilon
```

**Step 6**: After configuring the argument - parameter pair, type space and -- again to see other parameters again and see other parameters and use autocomplete with TAB as you type

```ruby
python3 runTableMaker.py configs/configTableMakerMCRun3.json --table-maker:cfgBarrelTrackCuts jpsiPID1 jpsiPID2 --
```

```ruby
--add_fdd_conv                                          --internal-dpl-aod-reader:aod-file                      --tof-pid:param-sigma
--add_mc_conv                                           --internal-dpl-aod-reader:end-value-enumeration         --tof-pid:pid-al
--add_track_prop                                        --internal-dpl-aod-reader:orbit-multiplier-enumeration  --tof-pid:pid-de
--add_weakdecay_ind                                     --internal-dpl-aod-reader:orbit-offset-enumeration      --tof-pid:pid-el
--analysis-qvector:ccdb-no-later-than                   --internal-dpl-aod-reader:start-value-enumeration       --tof-pid:pid-he
--analysis-qvector:ccdb-path                            --internal-dpl-aod-reader:step-value-enumeration        --tof-pid:pid-ka
--analysis-qvector:ccdb-url                             --internal-dpl-aod-reader:time-limit                    --tof-pid:pid-mu
--analysis-qvector:cfgAcceptance                        --logFile                                               --tof-pid:pid-pi
--analysis-qvector:cfgBarrelTrackCuts                   --multiplicity-table:doVertexZeq                        --tof-pid:pid-pr
--analysis-qvector:cfgCutEta                            --multiplicity-table:processRun2                        --tof-pid:pid-tr
--analysis-qvector:cfgCutPtMax                          --multiplicity-table:processRun3                        --tof-pid:processWoSlice
--analysis-qvector:cfgCutPtMin                          --overrider                                             --tof-pid:processWSlice
--analysis-qvector:cfgEfficiency                        --table-maker:ccdb-path-tpc                             --tpc-pid-full:autofetchNetworks
--analysis-qvector:cfgEtaLimit                          --table-maker:ccdb-url                                  --tpc-pid-full:ccdbPath
--analysis-qvector:cfgEventCuts                         --table-maker:cfgAddEventHistogram                      --tpc-pid-full:ccdb-timestamp
etc.
```

After that you can similarly continue configuring your parameters with autocompletion.

**VERY IMPORTANT P.S**: Not every argument in the interface has a parameter to configure. Some are configured as metavariable, meaning they are itself a value parameter. To explain this situation in detail, for example, `--table-maker:cfgBarrelTrackCuts` argument in tablemaker has to take one of two values as true or false, while e.g `--add_track_prop` is a parameter value directly and remains false when it is not added to the command line, they do not take a value. They are configured as True only when you type them on the command line.

Example:

```ruby
python3 runTableMaker.py configs/configTableMakerDataRun3.json --add_track_prop
```

```ruby
python3 runTableMaker.py configs/configTableMakerDataRun3.json --table-maker:cfgBarrelTrackCuts jpsiPID1 --table-maker:cfgWithQA true
```

list of some metavar parameters:

* `--add_track_prop`
* `--add_fdd_conv`
* `--add_mc_conv`
* `--add_weak_decay_ind`
* `--logFile`


## Possible Autocompletions

In Python scripts, argument autocompletes are defined as built-in-method in the argcomplete package and CLI arguments do not need extra care for the arguments as the json files are created by parsing the json files before the script is executed, with the argcomplete package all arguments will be listed after typing -- and pressing TAB.

The auto-completions for the parameters taken by the arguments are implemented with the sub string search technique according to the naming rules. For example, if a configuration starts with "process", then the parameters it can take are defined as "true" or "false" (for e.g. **process**BarrelOnly). Again, in the O2-DQ Framework, for each configuration containing the "Cuts" sub string, all the cut string names in the CutsLibrary.h file are recommended and printed on the screen when the TAB key is pressed with autocompletion (for e.g cfgBarrelTrack**Cuts**).

Below you can see all the autocompletions for O2-DQ Framework currently available:

Naming Convention | Autocompletion | Type
--- | --- | --- | --- | --- |
`Cuts` in configuration name | All possible analysis cut definitions from [CutsLibrary.h](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/CutsLibrary.h) | Flexible
Configuration name endswith `signals` or `Signals` | All possible MC Signal definitions from [MCSignalLibrary.h](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/MCSignalLibrary.h) | Flexible 
`Histogram` in configuration name |  All possible histogram definitions from [HistogramLibrary.h](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/HistogramsLibrary.h) | Flexbile
Configuration name endswith `Sels` | All possible event trigger types from [CutsLibrary.h](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/CutsLibrary.h) | Flexible
`MixingVars` in configuration name | All possible mixing variables from [MixingLibrary.h](https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/MixingLibrary.h) | Flexible 
Configuration name startswith `cfg` and `QA` in configuration name | `true` or `false` | Flexible
Configuration name equals to `cfgIsAmbiguous` | `true` or `false` | Hardcoded
Configuration name equals to `cfgFillCandidateTable` | `true` or `false` | Hardcoded
Configuration name equals to `cfgFlatTables` | `true` or `false` | Hardcoded
Configuration name equals to `cfgTPCpostCalib` | `true` or `false` | Hardcoded
Configuration name starts with `process` | `true` or `false` | Flexible

If you want to know more autocompletion or for defining new autocompletions, you can visit [Developer guide](7_DeveloperGuide.md#how-to-define-new-autocompletions)

[← Go back to Prerequisites](2_Prerequisites.md) | [↑ Go to the Table of Content ↑](../README.md) | [Continue to Techincal Informations →](4_TechincalInformations.md)