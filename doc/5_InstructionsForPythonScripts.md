# Instructions For Python Scripts

@tableofcontents

# Instructions for DownloadLibs.py

## Download CutsLibrary, MCSignalLibrary, MixingLibrary From Github

VERY IMPORTANT P.S: Downloading DQ libraries from Github is unstable and has a lot of issues. So use `DownloadLibs.py` script locally if you are working at local machine. It is highly recommended to skip this part directly and go to `Get CutsLibrary, MCSignalLibrary, MixingLibrary From Local Machine` (You cannot use the Local option for LXPLUS, use this part if you are working in LXPLUS).

These libraries must be downloaded for validation and autocomplete. After the argscomplete package is installed and sourced, they will be downloaded automatically if you do an one time autocomplete operation with the TAB key and the name of the script in the terminal. If you cannot provide this, the `DownloadLibs.py` script in the NewAllWorkFlows folder can do it manually. To run this script, simply type the following on the command line.

P.S. Don't forget source your argcomplete Before the using this script. --> `source argcomplete.sh`

`python3 DownloadLibs.py`

For tag version based download (depends your production) e.g for nightly-20220619, just enter as 20220619:

`python3 DownloadLibs.py --version 20220619`

If the libraries are downloaded successfully you will get this message:

`[INFO] Libraries downloaded successfully!`

## Get CutsLibrary, MCSignalLibrary, MixingLibrary From Local Machine

These libraries must be downloaded for validation and autocomplete. Instead of downloading libraries from github, you can configure the DownloadLibs.py script to pull the DQ libraries locally from the alice software on the existing computer. This option will not work on LXPLUS. if you are working on a local machine always use this option.

P.S. Don't forget source your argcomplete Before the using this script. --> `source argcomplete.sh`

Ex. Usage for Working Locally:

`python3 DownloadLibs.py --local`

In this configuration, the location of alice software is defaulted to `/home/<user>/alice`. If your alice software folder has a different name or is in a different location, you can configure it with the --localPath parameter. Ex. Usage for different path

`python3 DownloadLibs.py --local --localPath alice-software`

So with this configuration, your alice software path is changed to `/home/<user>/alice-software`. Another ex.

`python3 DownloadLibs.py --version 20220619 --local --localPath Software/alice`

So with this configuration, your alice software path is changed to `/home/<user>/Sofware/alice`

If the DQ libraries are pulled from local alice software successfully you will get this message:

`[INFO] DQ Libraries pulled from local alice software successfully!`

We have many logger message for this interface. If you have a problem with configuration, you can find the solution very easily by following the logger messages here. This solution is completely stable

## Available configs in DownloadLibs.py Interface

Arg | Opt | Local/Online | nargs | ex. usage
--- | --- | --- | --- | --- | 
`-h` | No Param | `Online and Local` | 0 | `python3 DownloadLibs.py -h`
`--version` | all | `Online` | 1 |  `python3 DownloadLibs.py --version  20220619`
`--debug` |<p> `NOTSET`<br> `DEBUG`<br>`INFO`<br>`WARNING` <br> `ERROR` <br>`CRITICAL` <br> </p> |  `Online and Local` | 1 |  `python3 DownloadLibs.py --debug INFO`
`--local` | No Param |  `Local` | 1 |  `python3 DownloadLibs.py --local`
`--localPath` | all |  `Local` | 1 |  `python3 DownloadLibs.py --local --localPath alice-software`

* More Details for `DownloadLibs.py` interface parameters

Arg | Ref Type| Desc | Default | Real Type
--- | --- | --- | --- | --- |
`-h` | No Param | list all helper messages for configurable commands | | *
`--version` | Integer | Online: Your Production tag for O2Physics example: for nightly-20220619, just enter as 20220619 | master | str |
`--debug` | string | Online and Local: execute with debug options" | `INFO` | str.upper
`--local` | No Param |Local: Use Local Paths for getting DQ Libraries instead of online github download. If you are working LXPLUS, It will not working so don't configure with option | - | *
`--localPath` | String | Local: Configure your alice software folder name in your local home path. Default is alice. Example different configuration is --localpath alice-software --local --> home/user/alice-software | `alice` | str


# Instructions for runTableMaker.py

Add extrac tables and converters with:
1. **--add_mc_conv**: conversion from o2mcparticle to o2mcparticle_001
2. **--add_fdd_conv**: conversion o2fdd from o2fdd_001
   * If you get error like this, you should added it in your workflow 
   * `[ERROR] Exception caught: Couldn't get TTree "DF_2571958947001/O2fdd_001" from "YOURAOD.root". Please check https://aliceo2group.github.io/analysis-framework/docs/troubleshooting/treenotfound.html for more information.` 
3. **--add_track_prop**: conversion from o2track to o2track_iu ([link](https://aliceo2group.github.io/analysis-framework/docs/helperTasks/trackPropagation.html))
   * If you get error like this, you should added it in your workflow 
   * `[ERROR] Exception caught: Couldn't get TTree "DF_2660520692001/O2track" from "Datas/AO2D.root". Please check https:/aliceo2group.github.io/analysis-framework/docs/troubleshooting/treenotfoundhtml for more information.` 

* Minimum Required Parameter List:
  * `python3`
  * `runTableMaker.py`
  * JSON Config File
    * Example usage: Configs/configTableMakerDataRun3.json 
  *  `-run<MC|Data>` 
     *  Usage (only select one value): `-runMC` or `-runData`
  *  `--process <Value>` 
     *  Usage examples (can take several value) : `--process MuonsOnly` or `--process BarrelOnly MuonOnly BarrelOnlyWithEventFilter`

Examples(in NewAllWorkFlows):
- Run TableMaker on Data run3 With Minimum Commands for Barrel Only (with automation)
  ```ruby
  python3 runTableMaker.py Configs/configTableMakerDataRun3.json -runData --process BarrelOnly
  ```
- Run TableMaker on MC run3 with Minimum Commands for Barrel Only (with automation)
  ```ruby
  python3 runTableMaker.py Configs/configTableMakerMCRun3.json -runMC --process BarrelOnly
  ```
- Run TableMaker on Data run2 With Minimum Commands for Barrel Only (with automation)
  ```ruby
  python3 runTableMaker.py Configs/configTableMakerDataRun2.json -runData --process BarrelOnly
  ```
- Run TableMaker on MC run2 with Minimum Commands for Barrel Only (with automation)
  ```ruby
  python3 runTableMaker.py Configs/configTableMakerMCRun2.json -runMC --process BarrelOnly
  ```

In case of multiple configs example
  ```ruby
python3 runTableMaker.py Configs/configTableMakerMCRun3.json -runMC --process MuonOnlyWithCov OnlyBCs --cfgMCsignals muFromJpsi Jpsi muFromPsi2S Psi2S --onlySelect true --aod Datas/AO2D.root --cfgMuonCuts muonQualityCuts muonTightQualityCutsForTests --syst pp --onlySelect true --add_track_prop
  ```

## Available configs in runTableMaker Interface

* For `runTableMaker.py` Selections

Arg | Opt | Task | nargs |
--- | --- | --- | --- |
`-h` | No Param | all | 0 |
`--aod` | all | `internal-dpl-aod-reader` | 1 |
`--aod-memory-rate-limit` | all | `internal-dpl-aod-reader` | 1 |
`--onlySelect` | `true`<br> `false`<br>  | Special Option | 1 |
`--autoDummy` | `true`<br> `false`<br>  | Special Option | 1 |
`--process` | `Full` <br> `FullTiny`<br>  `FullWithCov`<br>  `FullWithCent`<br>  `BarrelOnlyWithV0Bits`<br>  `BarrelOnlyWithEventFilter`<br> `BarrelOnlyWithQvector` <br>  `BarrelOnlyWithCent`<br>  `BarrelOnlyWithCov`<br>  `BarrelOnly`<br>  `MuonOnlyWithCent`<br>  `MuonOnlyWithCov`<br>  `MuonOnly`<br>  `MuonOnlyWithFilter`<br> `MuonOnlyWithQvector` <br>  `OnlyBCs`<br>  | `table-maker` | * |
`--run` | `2`<br> `3`<br> | Special Option | 1 |
`-runData` | No Param | `event-selection-task`<br> Special Option | 0 |
`-runMC` |  No Param | `event-selection-task`<br> Special Option | 0 |
`--add_mc_conv` | No Param  | `o2-analysis-mc-converter`<br> Special Option | 0 |
`--add_fdd_conv` | No Param | `o2-analysis-fdd-converter`<br> Special Option | 0 |
`--add_track_prop` | No Param | `o2-analysis-track-propagation`<br> Special Option | 0 |
`--syst` | `pp`<br> `PbPb`<br> `pPb`<br> `Pbp`<br> `XeXe`<br> | `event-selection-task` | 1 |
`--muonSelection` | `0`<br> `1`<br> `2` | `event-selection-task` | 1 |
`--CustomDeltaBC` | all | `event-selection-task` | 1 |
`--isVertexZeq` | `true`<br> `false`<br>  | `multiplicity-table` | 1 |
`--isCovariance` | `true`<br> `false`<br> | `track-propagation` | 1 |
`--isWSlice` | `true`<br> `false`<br> | `tof-pid-full tof-pid` | 1 |
`--enableTimeDependentResponse` | `true`<br> `false`<br> | `tof-pid-full tof-pid` | 1 |
`--FT0` | `FT0`<br> `NOFT0`<br>`OnlyFT0`<br> `Run2` | `tof-event-time` | 1 |
`--tof-expreso` | all | `tof-pid-beta` | 1 |
`--isBarrelSelectionTiny` | `true`<br> `false`<br> | `d-q-barrel-track-selection-task` | 1 |
`--est` | `Run2V0M`<br> `Run2SPDtks`<br> `Run2SPDcls`<br> `Run2CL0`<br> `Run2CL1`<br> `FV0A`<br> `FT0M`<br> `FDDM`<br> `NTPV`<br>| `centrality-table` | * |
`--cfgWithQA` | `true`<br> `false`<br> | `d-q-barrel-track-selection-task`<br> `d-q-event-selection-task`<br> `d-q-event-selection-task`<br> `d-q-filter-p-p-task`<br>`analysis-qvector`  | 1 |
`--d_bz` | all | `v0-selector` | 1 |
`--v0cospa` | all | `v0-selector` | 1 |
`--dcav0dau` | all | `v0-selector` | 1 |
`--v0Rmin` | all | `v0-selector` | 1 |
`--v0Rmax` | all | `v0-selector` | 1 |
`--dcamin` | all | `v0-selector` | 1 |
`--dcamax` | all | `v0-selector` |  1|
`--mincrossedrows` | all | `v0-selector` | 1 |
`--maxchi2tpc` | all | `v0-selector` | 1 |
`--cfgCutPtMin` | all  | `analysis-qvector`<br>  | 1 |
`--cfgCutPtMax ` | all  | `analysis-qvector`<br> | 1 |
`--cfgCutEta ` | all  | `analysis-qvector` | 1 |
`--cfgEtaLimit` | all  | `analysis-qvector`<br>  | 1 |
`--cfgNPow` | all  | `analysis-qvector`<br> | 1 |
`--cfgEfficiency` | all  | `analysis-qvector` | 1 |
`--cfgAcceptance` | all  | `analysis-qvector`<br>  | 1 |
`--pid` | `el`<br> `mu`<br> `pi`<br> `ka`<br> `pr`<br> `de`<br> `tr`<br> `he`<br> `al`<br> | `tof-pid tpc-pid` | * |
`--isFilterPPTiny` | `true`<br>  `false`<br> | `d-q-filter-p-p-task` | 1 |
`--cfgBarrelSels` | `namespacedCuts` | `d-q-filter-p-p-task` | * |
`--cfgMuonSels` | `namespacedCuts` | `d-q-filter-p-p-task` | * |
`--cfgEventCuts` | `allCuts` | `table-maker` | * |
`--cfgBarrelTrackCuts` | `allCuts` | `table-maker` | * |
`--cfgMuonCuts` | `allCuts` | `table-maker` | * |
`--cfgMuonsCuts` | `allCuts` | `d-q-muons-selection` | * |
`--cfgBarrelLowPt` | all | `table-maker` | 1 |
`--cfgMuonLowPt` | all | `table-maker` | 1 |
`--cfgNoQA` | `true`<br> `false`<br> | `table-maker` | 1 |
`--cfgDetailedQA` | `true`<br> `false`<br> | `table-maker` | 1 |
`--cfgMinTpcSignal` | all | `table-maker` | 1 |
`--cfgMaxTpcSignal` | all | `table-maker` | 1 |
`--cfgMCsignals` | `allSignals` | `table-maker` | * |
`--cutLister` | No Param | `allCuts` | 0 |
`--MCSignalsLister` | No Param | `allSignals` | 0 |
`--debug` | `NOTSET`<br> `DEBUG`<br>`INFO`<br>`WARNING` <br> `ERROR` <br>`CRITICAL` <br>  | all  | 1 |
`--logFile` | No Param | special option  | 0 |

* Details parameters for `runTableMaker.py`

Arg | Ref Type| Desc | Default | Real Type
--- | --- | --- | --- | --- |
`-h` | No Param | list all helper messages for configurable command |  | *
`--aod` | String | Add your aod file with path  |  | str |
`--aod-memory-rate-limit` | String | Rate limit AOD processing based on memory |  |  str
`--onlySelect` | Boolean | An Automate parameter for keep options for only selection in process, pid and centrality table (true is highly recomended for automation) | `false` | str.lower |
`--autoDummy` | Boolean | Dummy automize parameter (if your selection true, it automatically activate dummy process and viceversa) | `true` | str.lower |
`--process` | String | process selection for skimmed data model in tablemaker |  | str |
`--run` | Integer | Data run option for ALICE 2/3 |  | str
`-runData` | no Param |  Data Selection instead of MC |   | str
`-runMC` |  No Param | MC Selection instead of data |  | -
`--add_mc_conv` | No Param  | Conversion from o2mcparticle to o2mcparticle_001< |  | -
`--add_fdd_conv` | No Param | Conversion o2fdd from o2fdd_001 |  | -
`--add_track_prop` | No Param | Conversion from o2track to o2track_iu  |  | -
`--syst` | String | Collision system selection |  | str
`--muonSelection` | Integer | 0 - barrel, 1 - muon selection with pileup cuts, 2 - muon selection without pileup cuts |  | str
`--CustomDeltaBC` | all |custom BC delta for FIT-collision matching |  | str
`--isVertexZeq` | Boolean  | if true: do vertex Z eq mult table |  | str.lower
`--isCovariance` | Boolean | If false, Process without covariance, If true Process with covariance related to `track-propagation` |  | str.lower
`--isWSlice` | Boolean | Process with track slices|  | str.lower
`--enableTimeDependentResponse` | Boolean | Flag to use the collision timestamp to fetch the PID Response |  | str.lower
`--FT0` | Boolean | FT0: Process with FT0, NoFT0: Process without FT0, OnlyFT0: Process only with FT0, Run2: Process with Run2 data |  | str.lower
`--tof-expreso` | Float | Expected resolution for the computation of the expected beta |  | str
`--isBarrelSelectionTiny` | Boolean | Run barrel track selection instead of normal(process func. for barrel selection must be true) |  | str.lower
`--est` | String | Produces centrality percentiles parameters | | str
`--cfgWithQA` | Boolean | If true, fill QA histograms |  | str.lower
`--d_bz` | Float | bz field |  | str
`--v0cospa` | Float | v0cospa |  | str
`--dcav0dau` | Float | DCA V0 Daughters |  | str
`--v0Rmin` | Float | V0min |  | str
`--v0Rmax` | Float | V0max|  | str
`--dcamin` | Float | dcamin  |  | str
`--dcamax` | Float | dcamax |  | str
`--mincrossedrows` | Float | Min crossed rows  |  | str
`--maxchi2tpc` | Float | max chi2/NclsTPC  |  | str
`--cfgCutPtMin` | Float | Minimal pT for tracks |  | str
`--cfgCutPtMax ` | Float | Maximal pT for tracks  |  | str
`--cfgCutEta ` | Float | Eta range for tracksselection  |  | str
`--cfgEtaLimit` | Float | Eta gap separation, only if using subEvents |  | str
`--cfgNPow` | Integer | Power of weights for Q vector  |  | str
`--cfgEfficiency` | String | CCDB path to efficiency object  |  | str
`--cfgAcceptance` | String | CCDB path to acceptance object  |  | str
`--pid` | String | Produce PID information for the particle mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1) |  | str.lower
`--isFilterPPTiny` | Boolean | Run filter tiny task instead of normal (processFilterPP must be true) |  | str.lower
`--cfgBarrelSels` | String | Configure Barrel Selection track-cut:pair-cut:n,track-cut:pair-cut:n,... example jpsiO2MCdebugCuts2::1|  | str
`--cfgMuonSels` | String | Configure Muon Selection muon-cut:[pair-cut]:n example muonQualityCuts:pairNoCut:1|  | str
`--cfgEventCuts` | String | Space separated list of event cuts |  | str
`--cfgBarrelTrackCuts` | String | Space separated list of barrel track cuts |  | str
`--cfgMuonCuts` | String | Space separated list of muon cuts in tablemaker and analysis-qvector  |  | str
`--cfgMuonsCuts` | String | Space separated list of ADDITIONAL muon track cuts  |  | str
`--cfgBarrelLowPt` | Float | Specify the lowest pt cut for electrons; used in a Partition expression to improve CPU efficiency (GeV) |  | str
`--cfgMuonLowPt` | Float | Specify the lowest pt cut for muons; used in a Partition expression to improve CPU efficiency  (GeV) |  | str
`--cfgNoQA` | Boolean | If true, no QA histograms |  | str.lower
`--cfgDetailedQA` | Boolean | If true, include more QA histograms (BeforeCuts classes and more) |  | str.lower
`--cfgMinTpcSignal` | Integer| TPC Min Signal Selection |  | str
`--cfgMaxTpcSignal` | Integer | TPC Max Signal Selection |  | str
`--cfgMCsignals` | String | Space separated list of MC signals |  | str
`--cutLister` | No Param | Lists All of the valid Analysis Cuts from CutsLibrary.h from O2Physics-DQ  |  | -
`--MCSignalsLister` | No Param | Lists All of the valid MCSignals from MCSignalLibrary.h from O2Physics-DQ |  | -
`--debug` | String | execute with debug options  | - | str.upper |
`--logFile` | No Param | Enable logger for both file and CLI  | - | - |



# Instructions for runTableReader.py

* Minimum Required Parameter List:
  * `python3`
  * `runTableReader.py`
  * JSON Config File
    * Example For Most common usage: Configs/configAnalysisData.json  

Examples(in NewAllWorkFlows):
- Run TableReader on Data run3 With Minimum Commands
  ```ruby
  python3 runTableReader.py Configs/configAnalysisData.json
  ```

In case of multiple configs example
  ```ruby
  python3 runTableReader.py Configs/configAnalysisData.json --analysis eventSelection trackSelection eventMixing sameEventPairing --process JpsiToEE --cfgTrackCuts jpsiO2MCdebugCuts --aod reducedAod.root --debug debug --logFile
  ```


## Available configs in runTableReader Interface

Arg | Opt | Task | nargs |
--- | --- | --- | --- |
`-h` | No Param | all | 0 |
`--aod` | all | `internal-dpl-aod-reader` | 1 |
`--autoDummy` | `true`<br> `false`<br>  | Special Option | 1 |
`--reader` | all | Special Option | 1 |
`--writer` | all | Special Option | 1 |
`--analysis` | `eventSelection`<br>`trackSelection`<br>`muonSelection`<br>`eventMixing`<br>`eventMixingVn`<br> `sameEventPairing`<br> `dileptonHadron`  | `analysis-event-selection`<br>`analysis-track-selection`<br>`analysis-muon-selection`<br>`analysis-event-mixing`<br>`analysis-same-event-pairing`<br>`analysis-dilepton-hadron`  | * |
`--mixing` | `Barrel`<br>`Muon`<br>`BarrelMuon`<br>`BarrelVn`<br>`MuonVn` | `analysis-same-event-pairing` | * |
`--process` | `JpsiToEE`<br>`JpsiToMuMu`<br>`JpsiToMuMuVertexing`<br>`VnJpsiToEE`<br>`VnJpsiToMuMu`<br>`ElectronMuon`<br> `All`  | `analysis-same-event-pairing` | * |
`--syst` | `pp`<br> `PbPb`<br> `pPb`<br> `Pbp`<br> `XeXe`<br> | `event-selection-task` | 1 |
`--cfgQA` |`true` <br> `false`  | `analysis-event-selection`<br> `analysis-track-selection`<br> `analysis-muon-selection`  | 1 |
`--cfgMixingVars` | `allMixingVars`  | `analysis-event-selection`<br> | * |
`--cfgEventCuts` | `allCuts`  | `analysis-event-selection`<br>  | * |
`--cfgTrackCuts` | `allCuts` | `analysis-track-selection`<br> | * |
`--cfgMuonCuts` | `allCuts` | `analysis-muon-selection` | * |
`--cfgLeptonCuts` | `true`<br> `false`<br> | `analysis-dilepton-hadron` | * |
`--cutLister` | No Param | `allCuts` | 0 |
`--mixingLister` | No Param | `allMixing` | 0 |
`--debug` | `NOTSET`<br> `DEBUG`<br>`INFO`<br>`WARNING` <br> `ERROR` <br>`CRITICAL` <br>  | all  | 1 |
`--logFile` | No Param | special option  | 0 |

* Details parameters for `runTableReader.py`

Arg | Ref Type| Desc | Default | Real Type
--- | --- | --- | --- | --- |
`-h` | No Param | list all helper messages for configurable command |  | *
`--aod` | String | Add your AOD File with path | - | str
`--autoDummy` | Boolean | Dummy automize parameter (if process skimmed false, it automatically activate dummy process and viceversa) | `true` | str.lower
`--reader` | String | Add your AOD Reader JSON with path | `Configs/readerConfiguration_reducedEvent.json` | str
`--writer` | String | Add your AOD Writer JSON with path | `Configs/writerConfiguration_dileptons.json` | str
`--analysis` | String | Skimmed process selections for analysis | - | str
`--mixing` | String | Skimmed process selections for Event Mixing manually | - | str
`--process` | String | Skimmed process Selections for Same Event Pairing  | - | str |
`--isMixingEvent` | String | Event Mixing Activate or Disable Option | - | str.lower |
`--cfgQA` | Boolean | If true, fill QA histograms | - | str
`--cfgMixingVars` | String | Mixing configs separated by a space | - | str
`--cfgEventCuts` |  String | Space separated list of event cuts | - | str
`--cfgTrackCuts` | String | Space separated list of barrel track cuts | - | str
`--cfgMuonCuts` | String | Space separated list of muon cuts | - | str
`--cfgLeptonCuts` | String | Space separated list of barrel track cuts | - | str
`--cutLister` | No Param | Lists All of the valid Analysis Cuts from CutsLibrary.h from O2Physics-DQ  |  | -
`--mixingLister` | No Param | Lists All of the valid event mixing selections from MixingLibrary.h from O2Physics-DQ |  | -
`--debug` | String | execute with debug options  | - | str.upper |
`--logFile` | No Param | Enable logger for both file and CLI  | - | - |
# Instructions for runDQEfficiency.py
* Minimum Required Parameter List:
  * `python3`
  * `runDQEfficiency.py`
  * JSON Config File
    * Example For Most common usage: Configs/configAnalysisMC.json  

Examples(in NewAllWorkFlows):
- Run DQEfficiency on Data run3 With Minimum Commands
  ```ruby
  python3 runDQEfficiency.py Configs/configAnalysisMC.json
  ```

In case of multiple configs example
  ```ruby
python3 runDQEfficiency.py Configs/configAnalysisMC.json --analysis muonSelection eventSelection sameEventPairing --aod reducedAod.root --cfgMuonCuts muonQualityCuts muonTightQualityCutsForTests --cfgMuonMCSignals muFromJpsi muFromPsi2S --cfgBarrelMCGenSignals Jpsi Psi2S --cfgBarrelMCRecSignals mumuFromJpsi mumuFromPsi2S dimuon --process JpsiToMuMu --cfgQA true


  ```

## Available configs in runDQEfficiency Interface

* For `runDQEfficiency.py` Selections

Arg | Opt | Task | nargs |
--- | --- | --- | --- |
`-h` | No Param | all | 0 |
`--aod` | all | `internal-dpl-aod-reader` | 1 |
`--autoDummy` | `true`<br> `false`<br>  | Special Option | 1 |
`--reader` | all | Special Option | 1 |
`--writer` | all | Special Option | 1 |
`--analysis` | `eventSelection`<br>`trackSelection`<br>`muonSelection`<br>`sameEventPairing`<br>`dileptonTrackDimuonMuonSelection`<br> `dileptonTrackDielectronKaonSelection`<br> | `analysis-event-selection`<br>`analysis-track-selection`<br>`analysis-muon-selection`<br>`analysis-same-event-pairing`<br>`analysis-dilepton-track` | * |
`--process` | `JpsiToEE`<br>`JpsiToMuMu`<br>`JpsiToMuMuVertexing`<br>| `analysis-same-event-pairing` | * |
`--cfgQA` |`true` <br> `false`  | `analysis-event-selection`<br> `analysis-track-selection`<br> `analysis-muon-selection` | 1 |
`--cfgEventCuts` | `allCuts` | `analysis-event-selection`<br>  | * |
`--cfgTrackCuts` | `allCuts` | `analysis-track-selection`<br> | * |
`--cfgTrackMCSignals` | `allMCSignals` | `analysis-track-selection` | * |
`--cfgMuonCuts` | `allCuts` | `analysis-muon-selection` | * |
`--cfgMuonMCSignals` | `allMCSignals` | `analysis-muon-selection` | * |
`--cfgBarrelMCRecSignals` | `allMCSignals` | `analysis-same-event-pairing` | * |
`--cfgBarrelMCGenSignals` | `allMCSignals` | `analysis-same-event-pairing` | * |
`--cfgFlatTables` | `true` <br> `false` | `analysis-same-event-pairing` | 1 | 
`--cfgLeptonCuts` | `allCuts` | `analysis-dilepton-track` | * | 
`--cfgFillCandidateTable` | `true` <br> `false` | `analysis-dilepton-track` | 1 | 
`--cfgBarrelDileptonMCRecSignals` | `allMCSignals` | `analysis-dilepton-track` | * |
`--cfgBarrelDileptonMCGenSignals` | `allMCSignals` | `analysis-dilepton-track` | * |
`--cutLister` | No Param | `allCuts` | 0 |
`--MCSignalsLister` | No Param | `allSignals` |  0 |
`--debug` | `NOTSET`<br> `DEBUG`<br>`INFO`<br>`WARNING` <br> `ERROR` <br>`CRITICAL` <br>  | all  | 1 |
`--logFile` | No Param | special option  | 0 |

* Details parameters for `runDQEfficiency.py`

Arg | Ref Type| Desc | Default | Real Type
--- | --- | --- | --- | --- |
`-h` | No Param | list all helper messages for configurable command |  | *
`--aod` | String | Add your AOD File with path | - | str
`--autoDummy` | Boolean | Dummy automize parameter (if process skimmed false, it automatically activate dummy process and viceversa) | `true` | str.lower
`--reader` | String | Add your AOD Reader JSON with path | `Configs/readerConfiguration_reducedEventMC.json` | str
`--writer` | String | Add your AOD Writer JSON with path | `Configs/writerConfiguration_dileptonMC.json` | str
`--analysis` | String | Skimmed process selections for analysis | - | str
`--process` | String | Skimmed process selections for Same Event Pairing | - | str
`--cfgQA` | Boolean | If true, fill QA histograms | - | str
`--cfgEventCuts` |  String | Space separated list of event cuts | - | str
`--cfgTrackCuts` | String | Space separated list of barrel track cuts | - | str
`--cfgTrackMCSignals` | String | Space separated list of MC signals | - | str
`--cfgMuonCuts` | String | Space separated list of muon cuts | - | str
`--cfgMuonMCSignals` | String | Space separated list of MC signals | - | str
`--cfgBarrelMCRecSignals` | String | Space separated list of MC signals (reconstructed) | - | str
`--cfgBarrelMCGenSignals` | String | Space separated list of MC signals (generated) | - | str
`--cfgBarrelDileptonMCRecSignals` | String | Space separated list of MC signals (reconstructed) cuts | - | str
`--cfgBarrelDileptonMCGenSignals` | String | Space separated list of MC signals (generated)cuts | - | str
`--cutLister` | No Param | Lists All of the valid Analysis Cuts from CutsLibrary.h from O2Physics-DQ  |  | -
`--MCSignalsLister` | No Param | Lists All of the valid MCSignals from MCSignalLibrary.h from O2Physics-DQ |  | -
`--debug` | String | execute with debug options  | - | str.upper |
`--logFile` | No Param | Enable logger for both file and CLI  | - | - |

# Instructions for runFilterPP.py

Add extrac tables and converters with:
1. **--add_mc_conv**: conversion from o2mcparticle to o2mcparticle_001
2. **--add_fdd_conv**: conversion o2fdd from o2fdd_001
   * If you get error like this, you should added it in your workflow 
   * `[ERROR] Exception caught: Couldn't get TTree "DF_2571958947001/O2fdd_001" from "YOURAOD.root". Please check https://aliceo2group.github.io/analysis-framework/docs/troubleshooting/treenotfound.html for more information.` 
3. **--add_track_prop**: conversion from o2track to o2track_iu ([link](https://aliceo2group.github.io/analysis-framework/docs/helperTasks/trackPropagation.html))
   * If you get error like this, you should added it in your workflow 
   * `[ERROR] Exception caught: Couldn't get TTree "DF_2660520692001/O2track" from "Datas/AO2D.root". Please check https:/aliceo2group.github.io/analysis-framework/docs/troubleshooting/treenotfoundhtml for more information.`

* Minimum Required Parameter List:
  * `python3`
  * `runFilterPP.py`
  * JSON Config File
    * Example For usage: Configs/configFilterPPDataRun3.json 

Examples(in NewAllWorkFlows):
- Run filterPP on Data run3 With Minimum Commands
  ```ruby
  python3 runFilterPP.py Configs/configFilterPPDataRun3.json
  ```

- Run filterPP on Data run2 With Minimum Commands
  ```ruby
  python3 runFilterPP.py Configs/configFilterPPDataRun2.json
  ```

In case of multiple configs example
  ```ruby
python3 runFilterPP.py Configs/configFilterPPDataRun3.json --aod AO2D.root --syst pp --process barrelTrackSelection eventSelection --cfgBarrelSels jpsiO2MCdebugCuts2::1 --cfgEventCuts eventStandardNoINT7 --cfgBarrelTrackCuts jpsiO2MCdebugCuts2 jpsiO2MCdebugCuts2 --cfgWithQA true
  ```

## Available configs in runFilterPP Interface

* For `runFilterPP.py` Selections

Arg | Opt | Task | nargs |
--- | --- | --- | --- |
`-h` | No Param | all | 0 |
`--aod` | all | `internal-dpl-aod-reader` | 1 |
`--autoDummy` | `true`<br> `false`<br>  | Special Option | 1 |
`--process` | `barrelTrackSelection`<br>`eventSelection`<br>`muonSelection`<br>`barrelTrackSelectionTiny`<br>`filterPPSelectionTiny`| `d-q-barrel-track-selection`<br>`d-q-event-selection-task`<br>`d-q-muons-selection`| * |
`--add_mc_conv` | No Param  | `o2-analysis-mc-converter`<br> Special Option | 0 |
`--add_fdd_conv` | No Param | `o2-analysis-fdd-converter`<br> Special Option | 0 |
`--add_track_prop` | No Param | `o2-analysis-track-propagation`<br> Special Option | 0 |
`--syst` | `pp`<br> `PbPb`<br> `pPb`<br> `Pbp`<br> `XeXe`<br> | `event-selection-task` | 1 |
`--muonSelection` | `0`<br> `1`<br> `2` | `event-selection-task` | 1 |
`--CustomDeltaBC` | all | `event-selection-task` | 1 |
`--isVertexZeq` | `true`<br> `false`<br>  | `multiplicity-table` | 1 |
`--pid` | `el`<br> `mu`<br> `pi`<br> `ka`<br> `pr`<br> `de`<br> `tr`<br> `he`<br> `al`<br> | `tof-pid tpc-pid` | * |
`--isWSlice` | `true`<br> `false`<br> | `tof-pid-full tof-pid` | 1 |
`--enableTimeDependentResponse` | `true`<br> `false`<br> | `tof-pid-full tof-pid` | 1 |
`--tof-expreso` | all | `tof-pid-beta` | 1 |
`--FT0` | `FT0`<br> `NOFT0`<br>`OnlyFT0`<br> `Run2` | `tof-event-time` | 1 |
`--cfgWithQA` |`true` <br> `false`  | dq task selection<br> | 1 |
`--cfgEventCuts` | `allCuts` | `d-q-event-selection-task`<br>  | * |
`--cfgBarrelTrackCuts` | `allCuts` | `d-q-barrel-track-selection`<br> | * |
`--cfgBarrelSels` | `namespacedCuts` | `d-q-filter-p-p-task` | * |
`--cfgMuonSels` | `namespacedCuts` | `d-q-filter-p-p-task` | * |
`--cfgMuonsCuts` | `allCuts` | `d-q-muons-selection` | * |
`--cutLister` | No Param | `allCuts` | 0 |
`--debug` | `NOTSET`<br> `DEBUG`<br>`INFO`<br>`WARNING` <br> `ERROR` <br>`CRITICAL` <br>  | all  | 1 |
`--logFile` | No Param | special option  | 0 |


* Details parameters for `runFilterPP.py`

Arg | Ref Type| Desc | Default | Real Type
--- | --- | --- | --- | --- |
`-h` | No Param | list all helper messages for configurable command |  | *
`--aod` | String | Add your aod file with path  |  | str |
`--autoDummy` | Boolean | Dummy automize parameter (if process skimmed false, it automatically activate dummy process and viceversa) | `true` | str.lower
`--process` | `barrelTrackSelection`<br>`eventSelection`<br>`muonSelection`<br>`barrelTrackSelectionTiny`<br>`filterPPSelectionTiny`| dq task selection| * | str
`--add_mc_conv` | No Param  | Conversion from o2mcparticle to o2mcparticle_001< |  | -
`--add_fdd_conv` | No Param | Conversion o2fdd from o2fdd_001 |  | -
`--add_track_prop` | No Param | Conversion from o2track to o2track_iu  |  | -
`--syst` | String | Collision system selection |  | str
`--muonSelection` | Integer | 0 - barrel, 1 - muon selection with pileup cuts, 2 - muon selection without pileup cuts |  | str
`--CustomDeltaBC` | all |custom BC delta for FIT-collision matching |  | str
`--isVertexZeq` | Boolean  | if true: do vertex Z eq mult table |  | str.lower
`--pid` | String | Produce PID information for the particle mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1) |  | str.lower
`--isWSlice` | Boolean | Process with track slices|  | str.lower
`--enableTimeDependentResponse` | Boolean | Flag to use the collision timestamp to fetch the PID Response |  | str.lower
`--tof-expreso` | Float | Expected resolution for the computation of the expected beta |  | str
`--FT0` | Boolean | FT0: Process with FT0, NoFT0: Process without FT0, OnlyFT0: Process only with FT0, Run2: Process with Run2 data |  | str.lower
`--cfgWithQA` | Boolean | If true, fill QA histograms |  | str.lower
`--cfgEventCuts` | String | Space separated list of event cuts |  | str
`--cfgBarrelTrackCuts` | String | Space separated list of barrel track cuts |  | str
`--cfgBarrelSels` | String | Configure Barrel Selection track-cut:pair-cut:n,track-cut:pair-cut:n,... example jpsiO2MCdebugCuts2::1|  | str
`--cfgMuonSels` | String | Configure Muon Selection muon-cut:[pair-cut]:n example muonQualityCuts:pairNoCut:1|  | str
`--cfgMuonsCuts` | String | Space separated list of ADDITIONAL muon track cuts  |  | str
`--cutLister` | No Param | Lists All of the valid Analysis Cuts from CutsLibrary.h from O2Physics-DQ  |  | -
`--debug` | String | execute with debug options  | - | str.upper |
`--logFile` | No Param | Enable logger for both file and CLI  | - | - |


# Instructions for runDQFlow.py

* Minimum Required Parameter List:
  * `python3`
  * `runDQFlow.py`
  * JSON Config File
    * Example For usage: Configs/configFlowDataRun3.json

Examples(in NewAllWorkFlows):
- Run filterPP on Data run3 With Minimum Commands
  ```ruby
  python3 runDQFlow.py Configs/configFlowDataRun3.json
  ```

- Run filterPP on Data run2 With Minimum Commands
  ```ruby
  python3 runDQFlow.py Configs/configFlowDataRun2.json
  ```

In case of multiple configs example
  ```ruby
python3 runDQFlow.py Configs/configFilterPPDataRun3.json --aod AO2D.root --syst pp --cfgTrackCuts jpsiPID1 --cfgMuonCuts muonQualityCuts --cfgWithQA true --cfgCutPtMin 1 --cfgCutPtMax 15 
  ```

## Available configs in runDQFlow Interface

Add extrac tables and converters with:
1. **--add_mc_conv**: conversion from o2mcparticle to o2mcparticle_001
2. **--add_fdd_conv**: conversion o2fdd from o2fdd_001
   * If you get error like this, you should added it in your workflow 
   * `[ERROR] Exception caught: Couldn't get TTree "DF_2571958947001/O2fdd_001" from "YOURAOD.root". Please check https://aliceo2group.github.io/analysis-framework/docs/troubleshooting/treenotfound.html for more information.` 
3. **--add_track_prop**: conversion from o2track to o2track_iu ([link](https://aliceo2group.github.io/analysis-framework/docs/helperTasks/trackPropagation.html))
   * If you get error like this, you should added it in your workflow 
   * `[ERROR] Exception caught: Couldn't get TTree "DF_2660520692001/O2track" from "Datas/AO2D.root". Please check https:/aliceo2group.github.io/analysis-framework/docs/troubleshooting/treenotfoundhtml for more information.`

* For `runDQFlow.py` Selections

Arg | Opt | Task | nargs |
--- | --- | --- | --- |
`-h` | No Param | all | 0 |
`--aod` | all | `internal-dpl-aod-reader` | 1 |
`--add_mc_conv` | No Param  | `o2-analysis-mc-converter`<br> Special Option | 0 |
`--add_fdd_conv` | No Param | `o2-analysis-fdd-converter`<br> Special Option | 0 |
`--add_track_prop` | No Param | `o2-analysis-track-propagation`<br> Special Option | 0 |
`--syst` | `pp`<br> `PbPb`<br> `pPb`<br> `Pbp`<br> `XeXe`<br> | `event-selection-task` | 1 |
`--muonSelection` | `0`<br> `1`<br> `2` | `event-selection-task` | 1 |
`--CustomDeltaBC` | all | `event-selection-task` | 1 |
`--pid` | `el`<br> `mu`<br> `pi`<br> `ka`<br> `pr`<br> `de`<br> `tr`<br> `he`<br> `al`<br> | `tof-pid tpc-pid` | * |
`--est` | `Run2V0M`<br> `Run2SPDtks`<br> `Run2SPDcls`<br> `Run2CL0`<br> `Run2CL1`<br> `FV0A`<br> `FT0M`<br> `FDDM`<br> `NTPV`<br>| `centrality-table` | *
`--isVertexZeq` | `true`<br> `false`<br>  | `multiplicity-table` | 1 |
`--isWSlice` | `true`<br> `false`<br> | `tof-pid-full tof-pid` | 1 |
`--enableTimeDependentResponse` | `true`<br> `false`<br> | `tof-pid-full tof-pid` | 1 |
`--tof-expreso` | all | `tof-pid-beta` | 1 |
`--FT0` | `FT0`<br> `NOFT0`<br>`OnlyFT0`<br> `Run2` | `tof-event-time` | 1 |
`--cfgWithQA` |`true` <br> `false`  | `analysis-qvector`<br> | 1 |
`--cfgEventCuts` | `allCuts` | `analysis-qvector`<br>  | * |
`--cfgTrackCuts` | `allCuts` | `analysis-qvector`<br> | * |
`--cfgMuonCuts` | `allCuts` | `analysis-qvector` | * |
`--cfgCutPtMin` | all  | `analysis-qvector`<br>  | 1 |
`--cfgCutPtMax ` | all  | `analysis-qvector`<br> | 1 |
`--cfgCutEta ` | all  | `analysis-qvector` | 1 |
`--cfgEtaLimit` | all  | `analysis-qvector`<br>  | 1 |
`--cfgNPow` | all  | `analysis-qvector`<br> | 1 |
`--cfgEfficiency` | all  | `analysis-qvector` | 1 |
`--cfgAcceptance` | all  | `analysis-qvector`<br>  | 1 |
`--cutLister` | No Param | all  |  |
`--debug` | `NOTSET`<br> `DEBUG`<br>`INFO`<br>`WARNING` <br> `ERROR` <br>`CRITICAL` <br>  | all  | 1 |
`--logFile` | No Param | special option  | 0 |



* Details parameters for `runDQFlow.py`

Arg | Ref Type| Desc | Default | Real Type
--- | --- | --- | --- | --- |
`-h` | No Param | list all helper messages for configurable command |  | *
`--aod` | String | Add your aod file with path  |  | str |
`--add_mc_conv` | No Param  | Conversion from o2mcparticle to o2mcparticle_001< |  | -
`--add_fdd_conv` | No Param | Conversion o2fdd from o2fdd_001 |  | -
`--add_track_prop` | No Param | Conversion from o2track to o2track_iu  |  | -
`--syst` | String | Collision system selection |  | str
`--muonSelection` | Integer | 0 - barrel, 1 - muon selection with pileup cuts, 2 - muon selection without pileup cuts |  | str
`--CustomDeltaBC` | all |custom BC delta for FIT-collision matching |  | str
`--isVertexZeq` | Boolean  | if true: do vertex Z eq mult table |  | str.lower
`--isWSlice` | Boolean | Process with track slices|  | str.lower
`--enableTimeDependentResponse` | Boolean | Flag to use the collision timestamp to fetch the PID Response |  | str.lower
`--est` | String | Produces centrality percentiles parameters | | str
`--pid` | String | Produce PID information for the particle mass hypothesis, overrides the automatic setup: the corresponding table can be set off (0) or on (1) |  | str.lower
`--tof-expreso` | Float | Expected resolution for the computation of the expected beta |  | str
`--FT0` | Boolean | FT0: Process with FT0, NoFT0: Process without FT0, OnlyFT0: Process only with FT0, Run2: Process with Run2 data |  | str.lower
`--cfgWithQA` | Boolean | If true, fill QA histograms |  | str.lower
`--cfgEventCuts` | String | Space separated list of event cuts |  | str
`--cfgTrackCuts` | String | Space separated list of barrel track cuts |  | str
`--cfgMuonCuts` | String | Space separated list of muon cuts |  | str
`--cfgCutPtMin` | Float | Minimal pT for tracks |  | str
`--cfgCutPtMax ` | Float | Maximal pT for tracks  |  | str
`--cfgCutEta ` | Float | Eta range for tracksselection  |  | str
`--cfgEtaLimit` | Float | Eta gap separation, only if using subEvents |  | str
`--cfgNPow` | Integer | Power of weights for Q vector  |  | str
`--cfgEfficiency` | String | CCDB path to efficiency object  |  | str
`--cfgAcceptance` | String | CCDB path to acceptance object  |  | str
`--cutLister` | No Param | Lists All of the valid Analysis Cuts from CutsLibrary.h from O2Physics-DQ  |  | - -
`--debug` | String | execute with debug options  | - | str.upper |
`--logFile` | No Param | Enable logger for both file and CLI  | - | - |

[← Go back to Instructions For Techincal Informations](4_TechincalInformations.md) | [↑ Go to the Table of Content ↑](../README.md) | [Continue to Tutorials →](6_Tutorials.md)