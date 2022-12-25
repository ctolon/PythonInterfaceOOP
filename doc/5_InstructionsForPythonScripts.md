# Instructions For Python Scripts

- [Instructions For Python Scripts](#instructions-for-python-scripts)
- [Instructions for DownloadLibs.py](#instructions-for-downloadlibspy)
  - [Download CutsLibrary, MCSignalLibrary, MixingLibrary From Github](#download-cutslibrary-mcsignallibrary-mixinglibrary-from-github)
  - [Get CutsLibrary, MCSignalLibrary, MixingLibrary From Local Machine](#get-cutslibrary-mcsignallibrary-mixinglibrary-from-local-machine)
  - [Available configs in DownloadLibs.py Interface](#available-configs-in-downloadlibspy-interface)
  - [Hardcoded Arguments](#hardcoded-arguments)
- [Instructions for runTableMaker](#instructions-for-runtablemaker)
- [Instructions for runAnalysis.py](#instructions-for-runanalysispy)
- [Instructions for runFilterPP.py](#instructions-for-runfilterpppy)
- [Instructions for runDQFlow.py](#instructions-for-rundqflowpy)
- [Working with Histogram configurables and other configurables](#working-with-histogram-configurables-and-other-configurables)


# Instructions for DownloadLibs.py

## Download CutsLibrary, MCSignalLibrary, MixingLibrary From Github

**VERY IMPORTANT P.S**: You cannot use the Local option for LXPLUS, use this part if you are working in LXPLUS.

DQ Libraries (CutsLibrary.h, MCSignalLibrary.h, MixingLibrary.h, HistogramsLibrary.h) must be downloaded for auto-completion. After the argcomplete package is installed and sourced, they will be downloaded automatically if you do an one time autocomplete operation with the TAB key and the name of the script in the terminal. If you cannot provide this, the `DownloadLibs.py` script in the PythonInterfaceOOP folder can do it manually. To run this script, simply type the following on the command line.

**P.S.** Don't forget source your argcomplete Before the using this script. --> `source argcomplete.sh`

`python3 DownloadLibs.py`

For tag version based download (depends your production) e.g for nightly-20220619, just enter as 20220619:

`python3 DownloadLibs.py --version 20220619`

If the libraries are downloaded successfully you will get this message:

`[INFO] Libraries downloaded successfully!`

## Get CutsLibrary, MCSignalLibrary, MixingLibrary From Local Machine

These libraries must be downloaded for validation and autocomplete. Instead of downloading libraries from github, you can configure the DownloadLibs.py script to pull the DQ libraries locally from the alice software on the existing computer. This option will not work on LXPLUS. if you are working on a local machine always use this option.

**P.S.** Don't forget source your argcomplete Before the using this script. --> `source argcomplete.sh`

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


<details><summary>All Configs:</summary>

Arg | Opt | Local/Online | nargs | ex. usage
--- | --- | --- | --- | --- | 
`-h` | No Param | `Online and Local` | 0 | `python3 DownloadLibs.py -h`
`--version` | all | `Online` | 1 |  `python3 DownloadLibs.py --version  20220619`
`--debug` |<p> `NOTSET`<br> `DEBUG`<br>`INFO`<br>`WARNING` <br> `ERROR` <br>`CRITICAL` <br> </p> |  `Online and Local` | 1 |  `python3 DownloadLibs.py --debug INFO`
`--local` | No Param |  `Local` | 1 |  `python3 DownloadLibs.py --local`
`--localPath` | all |  `Local` | 1 |  `python3 DownloadLibs.py --local --localPath alice-software`
</details>


<details><summary>More Details for DownloadLibs.py interface parameters</summary>

Arg | Ref Type| Desc | Default | Real Type
--- | --- | --- | --- | --- |
`-h` | No Param | list all helper messages for configurable commands | | *
`--version` | Integer | Online: Your Production tag for O2Physics example: for nightly-20220619, just enter as 20220619 | master | str |
`--debug` | string | Online and Local: execute with debug options" | `INFO` | str.upper
`--local` | No Param |Local: Use Local Paths for getting DQ Libraries instead of online github download. If you are working LXPLUS, It will not working so don't configure with option | - | *
`--localPath` | String | Local: Configure your alice software folder name in your local home path. Default is alice. Example different configuration is --localpath alice-software --local --> home/user/alice-software | `alice` | str
</details>


## Hardcoded Arguments

These are helper hardcoded arguments for every run python scripts that do not directly manage configurations in json configuration files.


<details><summary>List of hard coded arguments:</summary>

```ruby
positional arguments:
  Config.json           config JSON file name (mandatory)

options:
  -h, --help            show this help message and exit
  -runParallel          Run parallel in session (default: False)

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
  --add_col_conv        Add the converter from collision to collision+001 (default: False)

Helper Options:
  --debug {NOTSET,DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        execute with debug options (default: INFO)
  --logFile             Enable logger for both file and CLI (default: False)
  --override {true,false}
                        If true JSON Overrider Interface If false JSON Additional Interface (default: true)
```
</details>



# Instructions for runTableMaker

* Minimum Required Parameter List:
  * The runOverMC variable, which is just below the main function in the script, must be False for tableMaker and True for tableMakerMC
  * `python3`
  * `runTableMaker.py`
  * JSON Config File
    * Example usage: configs/configTableMakerDataRun3.json 

Examples:
- Run TableMaker on Data run3 With Minimum Commands for Barrel Only (in script, runOverMC must be False)
  ```ruby
  python3 runTableMaker.py configs/configTableMakerDataRun3.json --table-maker:processBarrelOnly true
  ```
- Run TableMaker on MC run3 with Minimum Commands for Barrel Only (in script, runOverMC must be True)
  ```ruby
  python3 runTableMaker.py configs/configTableMakerMCRun3.json --table-maker-m-c:processBarrelOnly true
  ```
- Run TableMaker on Data run2 With Minimum Commands for Barrel Only (in script, runOverMC must be False)
  ```ruby
  python3 runTableMaker.py configs/configTableMakerDataRun2.json --table-maker:processBarrelOnly true
  ```
- Run TableMaker on MC run2 with Minimum Commands for Barrel Only (in script, runOverMC must be True)
  ```ruby
  python3 runTableMaker.py configs/configTableMakerMCRun2.json --table-maker-m-c:processBarrelOnly true
  ```

In case of multiple configs example(**runOverMC have to be True** for run with **tableMakerMC**):

  ```ruby
python3 runTableMaker.py configs/configTableMakerMCRun3.json --table-maker-m-c:processMuonOnlyWithCov true --table-maker-m-c:processOnlyBCs true --table-maker-m-c:cfgMCsignals muFromJpsi Jpsi muFromPsi2S Psi2S --overrider true --internal-dpl-aod-reader:aod-file Datas/AO2D.root --table-maker-m-c:cfgMuonCuts muonQualityCuts muonTightQualityCutsForTests --event-selection-task:syst pp --overrider true --add_track_prop
  ```
# Instructions for runAnalysis.py
* The runOverMC variable, which is just below the main function in the script, must be False for tableReader and True for dqEfficiency
* Minimum Required Parameter List:
  * `python3`
  * `runAnalysis.py`
  * JSON Config File
    * Example For Most common usages: configs/configAnalysisData.json or configs/configAnalysisMC.json

Examples:
- Run tableReader on Data run3 With Minimum Commands (in script, runOverMC must be False)
  ```ruby
  python3 runAnalysis.py configs/configAnalysisData.json
  ```
- Run dqEfficiency on MC run3 With Minimum Commands (in script, runOverMC must be True)
  ```ruby
  python3 runAnalysis.py configs/configAnalysisMC.json
  ```

In case of multiple configs example (**runOverMC have to be False** for run with **tableReader**):

  ```ruby
  python3 runAnalysis.py configs/configAnalysisData.json --analysis-event-selection:processSkimmed true --analysis-track-selection:processSkimmed true --analysis-same-event-pairing:processDecayToEESkimmed true --analysis-track-selection:cfgTrackCuts jpsiO2MCdebugCuts --analysis-same-event-pairing:cfgTrackCuts jpsiO2MCdebugCuts --internal-dpl-aod-reader:aod-file Datas/reducedAod.root --debug debug --logFile
  ```
# Instructions for runFilterPP.py

* Minimum Required Parameter List:
  * `python3`
  * `runFilterPP.py`
  * JSON Config File
    * Example For usage: configs/configFilterPPDataRun3.json 

Examples:
- Run filterPP on Data run3 With Minimum Commands
  ```ruby
  python3 runFilterPP.py configs/configFilterPPDataRun3.json
  ```

- Run filterPP on Data run2 With Minimum Commands
  ```ruby
  python3 runFilterPP.py configs/configFilterPPDataRun2.json
  ```

In case of multiple configs example
  ```ruby
python3 runFilterPP.py configs/configFilterPPDataRun3.json --internal-dpl-aod-reader:aod-file Datas/AO2D.root  --event-selection-task:syst pp --d-q-event-selection-task:processEventSelection true --d-q-barrel-track-selection-task:processSelection true --d-q-muons-selection:processSelection true --d-q-filter-p-p-task:cfgBarrelSels jpsiO2MCdebugCuts2::1 --d-q-event-selection-task:cfgEventCuts eventStandardNoINT7 --d-q-barrel-track-selection-task:cfgBarrelTrackCuts jpsiO2MCdebugCuts2 jpsiO2MCdebugCuts2 --d-q-filter-p-p-task:cfgWithQA true
  ```

# Instructions for runDQFlow.py

* Minimum Required Parameter List:
  * `python3`
  * `runDQFlow.py`
  * JSON Config File
    * Example For usage: configs/configFlowDataRun3.json

Examples:
- Run filterPP on Data run3 With Minimum Commands
  ```ruby
  python3 runDQFlow.py configs/configFlowDataRun3.json
  ```

- Run filterPP on Data run2 With Minimum Commands
  ```ruby
  python3 runDQFlow.py configs/configFlowDataRun2.json
  ```

In case of multiple configs example
  ```ruby
python3 runDQFlow.py configs/configFlowDataRun3.json --internal-dpl-aod-reader:aod-file Datas/AO2D.root --event-selection-task:syst PbPb --analysis-qvector:cfgBarrelTrackCuts jpsiPID1 --analysis-qvector:cfgMuonCuts muonQualityCuts --analysis-qvector:cfgWithQA true --analysis-qvector:cfgCutPtMin 1 --analysis-qvector:cfgCutPtMax 15 
  ```

TODO v0selector interface instructions will be added.
TODO EMefficiency interface instructions will be added.
TODO dalitzSelection interface instructions will be added.

# Working with Histogram configurables and other configurables

ONGOING...

[← Go back to Instructions For Techincal Informations](4_TechincalInformations.md) | [↑ Go to the Table of Content ↑](../README.md) | [Continue to Tutorials →](6_Tutorials.md)