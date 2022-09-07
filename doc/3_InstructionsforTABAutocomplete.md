# Instructions for TAB Autocomplete

@tableofcontents

Before proceeding to this stage, you should make sure that you activate the O2 environment with alienv, then install the argcomplete package with `pip install argcomplete` and `pip3 install argcomplete` in O2, and then source the autocomplete bash script with `source argcomplete.sh`

You can Complete this with a TAB key after each word and character you type in command line. Keep this thing in your mind.

If you have successfully installed this package and successfully sourced the script, follow these steps.

step 1: type python3 (If your symbolic link is python for python3, type python)

```ruby
python3
```

step 2: type the name of your script (eg runTableMaker.py)
```ruby
python3 runTableMaker.py
```

step 3: At this stage, since the JSON configuration files are in the Configs folder, enter the name of your JSON config file by completing it with TAB or listing the available options

for ex. if you type:

```ruby
python3 runTableMaker.py Configs
```

you will get this displayed options in your terminal:
```ruby
Configs/configAnalysisData.json                  Configs/configFlowDataRun3.json                  Configs/configtestFilterPPDataRun3.json          Configs/readerConfiguration_reducedEventMC.json
Configs/configAnalysisMC.json                    Configs/configTableMakerDataRun2.json            Configs/configtestFlowDataRun3.json              Configs/writerConfiguration_dileptonMC.json
Configs/configFilterPPDataRun2.json              Configs/configTableMakerDataRun3.json            Configs/configtestTableMakerDataRun3.json        Configs/writerConfiguration_dileptons.json
Configs/configFilterPPDataRun3.json                  Configs/configTableMakerMCRun2.json              Configs/readerConfiguration_dilepton.json        
Configs/configFlowDataRun2.json                  Configs/configTableMakerMCRun3.json              Configs/readerConfiguration_reducedEvent.json 
```

then you can complete your JSON config file (for example assuming you export configTableMakerMCRun3.json to configure tablemaker for mc run 3

```ruby
python3 runTableMaker.py Configs/configTableMakerMCRun3.json
```

P.S You can Complete this with a TAB key after each word and character you type in command line.

step 4: now when you type -- and press TAB key all parameter options in interface will be listed

```ruby
python3 runTableMaker.py Configs/configTableMakerMCRun3.json --
```

if you type like this and press TAB you will see all the parameters in the interface in your terminal like this:
```ruby
--add_fdd_conv           --cfgBarrelSels          --cfgMinTpcSignal        --cfgPairCuts            --dcamin                 --isCovariance           --mincrossedrows         --syst
--add_mc_conv            --cfgBarrelTrackCuts     --cfgMuonCuts            --cfgWithQA              --dcav0dau               --isFilterPPTiny         --muonSelection          --tof-expreso
--add_track_prop         --cfgDetailedQA          --cfgMuonLowPt           --customDeltaBC          --debug                  --isProcessEvTime        --onlySelect             --v0cospa
--aod                    --cfgEventCuts           --cfgMuonsCuts           --cutLister              --est                    --logFile                --pid                    --v0Rmax
--autoDummy              --cfgMaxTpcSignal        --cfgMuonSels            --d_bz                   --help                   --maxchi2tpc             --process                --v0Rmin
--cfgBarrelLowPt         --cfgMCsignals           --cfgNoQA                --dcamax                 --isBarrelSelectionTiny  --MCSignalsLister        --run 
```

VERY IMPORTANT STEP AND P.S: When configuring the runTableMaker.py script, the -runData and -runMC parameters are used when configuring the tablemaker for MC or Data. Since these parameters start with a single minus, do not forget to configure the TableMaker script only at the first time, by pressing the tab and configuring it (other interfaces do not have a parameter that starts with a single minus)

```ruby
python3 runTableMaker.py Configs/configTableMakerMCRun3.json -
```

Then you will see -runData and -runMC in your parameters:

```ruby
--add_fdd_conv           --cfgBarrelTrackCuts     --cfgMuonLowPt           --cutLister              -h                       --maxchi2tpc             --run                    --v0Rmin
--add_mc_conv            --cfgDetailedQA          --cfgMuonsCuts           --d_bz                   --help                   --MCSignalsLister        -runData                 
--add_track_prop         --cfgEventCuts           --cfgMuonSels            --dcamax                 --isBarrelSelectionTiny  --mincrossedrows         -runMC                   
--aod                    --cfgMaxTpcSignal        --cfgNoQA                --dcamin                 --isCovariance           --muonSelection          --syst                   
--autoDummy              --cfgMCsignals           --cfgPairCuts            --dcav0dau               --isFilterPPTiny         --onlySelect             --tof-expreso            
--cfgBarrelLowPt         --cfgMinTpcSignal        --cfgWithQA              --debug                  --isProcessEvTime        --pid                    --v0cospa                
--cfgBarrelSels          --cfgMuonCuts            --customDeltaBC          --est                    --logFile                --process                --v0Rmax  
```

step 5: After entering one of these parameters (eg --cfgBarrelTrackCuts for runTableMaker.py) leave a space and press tab again. As a result you will see each value this parameter can take.

```ruby
python3 runTableMaker.py Configs/configTableMakerMCRun3.json -runMC --cfgBarrelTrackCuts
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

step 6: after configuring the config, type space and -- again to see other parameters again and see other parameters and use autocomplete with TAB as you type

```ruby
python3 runTableMaker.py Configs/configTableMakerMCRun3.json -runMC --cfgBarrelTrackCuts --
```

```ruby
--add_fdd_conv           --cfgBarrelSels          --cfgMinTpcSignal        --cfgPairCuts            --dcamin                 --isCovariance           --mincrossedrows         --syst
--add_mc_conv            --cfgBarrelTrackCuts     --cfgMuonCuts            --cfgWithQA              --dcav0dau               --isFilterPPTiny         --muonSelection          --tof-expreso
--add_track_prop         --cfgDetailedQA          --cfgMuonLowPt           --customDeltaBC          --debug                  --isProcessEvTime        --onlySelect             --v0cospa
--aod                    --cfgEventCuts           --cfgMuonsCuts           --cutLister              --est                    --logFile                --pid                    --v0Rmax
--autoDummy              --cfgMaxTpcSignal        --cfgMuonSels            --d_bz                   --help                   --maxchi2tpc             --process                --v0Rmin
--cfgBarrelLowPt         --cfgMCsignals           --cfgNoQA                --dcamax                 --isBarrelSelectionTiny  --MCSignalsLister        --run 
```

After that you can similarly continue configuring your parameters with autocompletion.

VERY IMPORTANT P.S: Not every parameter in the interface has a value to configure. Some are configured as metavariable, meaning they are itself a value parameter. To explain this situation in detail, for example, `--cfgWithQA` parameter in tablemaker has to take one of two values as true or false, while `--add_track_prop` or `-runMC` is a parameter value directly and remains false when it is not added to the command line, they do not take a value. They are configured as true only when you type them on the command line.

Example:

```ruby
python3 runTableMaker.py Configs/configTableMakerMCRun3.json -runMC --add_track_prop
```

```ruby
python3 runTableMaker.py Configs/configTableMakerMCRun3.json --cfgBarrelTrackCuts jpsiPID1 --cfgWithQA true
```

list of metavar parameters:

* `--add_track_prop`
* `--add_fdd_conv`
* `--add_mc_conv`
* `-runMC` (This parameter is only for tableMakerMC)
* `-runData` (This parameter is only for tableMaker)
* `--logFile`
* `--MCSignalsLister` (this parameter only for tableMakerMC and dqEfficiency interface)
* `--cutLister`
* `--mixingLister` (this parameter only for tableReader interface)

[← Go back to Prerequisites](2_Prerequisites.md) | [↑ Go to the Table of Content ↑](../README.md) | [Continue to Techincal Informations →](4_TechincalInformations.md)