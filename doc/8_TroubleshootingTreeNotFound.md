IMPORTANT!!! Converters are no longer part of the interface, because functionality that adds them automatically is provided

# Converters (Special Additional Tasks For Workflows)

@tableofcontents

If you get an error about ttree not found, the following converter may fix the error you get:

1. **--add_mc_conv**: conversion from o2mcparticle to o2mcparticle_001
   * If you get error like this, you should added it in your workflow 
   * `[ERROR] Exception caught: Couldn't get TTree "DF_2660520692001/O2mcparticle" from "Datas/AO2D.root". Please check https:/aliceo2group.github.io/analysis-framework/docs/troubleshooting/treenotfoundhtml for more information.`
2. **--add_fdd_conv**: conversion o2fdd from o2fdd_001
   * If you get error like this, you should added it in your workflow 
   * `[ERROR] Exception caught: Couldn't get TTree "DF_2571958947001/O2fdd_001" from "YOURAOD.root". Please check https://aliceo2group.github.io/analysis-framework/docs/troubleshooting/treenotfound.html for more information.` 
3. **--add_track_prop**: conversion from o2track to o2track_iu ([link](https://aliceo2group.github.io/analysis-framework/docs/basics-usage/HelperTasks.html#track-propagation))
   * If you get error like this, you should added it in your workflow 
   * `[ERROR] Exception caught: Couldn't get TTree "DF_2660520692001/O2track" from "Datas/AO2D.root". Please check https:/aliceo2group.github.io/analysis-framework/docs/troubleshooting/treenotfoundhtml for more information.`
4. **--add_weakdecay_ind**: Converts V0 and cascade version 000 to 001
   * If you get error like this, you should added it in your workflow 
   * `[ERROR] Exception caught: Couldn't get TTree "DF_2660520692001/O2v0_001" from "Datas/AO2D.root". Please check https:/aliceo2group.github.io/analysis-framework/docs/troubleshooting/treenotfoundhtml for more information.`

## --add_track_prop

Details: [click here](https://aliceo2group.github.io/analysis-framework/docs/basics-usage/HelperTasks.html#track-propagation) (here you can find details on what this task does)

From Doc:

The Run 3 AO2D stores the tracks at the point of innermost update. For a track with ITS this is the innermost (or second innermost) ITS layer. For a track without ITS, this is the TPC inner wall or for loopers in the TPC even a radius beyond that. In the AO2D.root the trees are therefore called O2tracks_IU and O2tracksCov_IU (IU = innermost update). The corresponding O2 data model tables are TracksIU and TracksCovIU, respectively. If your task needs tracks at the collision vertex it will fail because it looks for O2tracks and O2tracksCov.

In order to propagate the tracks to the collision vertex, include the task o2-analysis-track-propagation into your workflow. This task produces the tables Tracks and TracksCov (in order to get the latter, please enable processCovariance through the json configuration).

[ERROR] Exception caught: Couldn't get TTree "DF_2660520692001/O2track" from "Datas/AO2D.root". Please check https:/aliceo2group.github.io/analysis-framework/docs/troubleshooting/treenotfoundhtml for more information.

o2-analysis-track-propagation task should be included in the workflow in the latest data productions (for run 3) on Grid. We do not include this automatically in the python script. Because this task is incompatible with old data productions and it causes workflows to crash for old data productions. For Run 2 datas and MCs, we use o2-analysis-trackextension task for creating trackDCA tables. So when you working on run 2 Data or MC, you must not add track-propagation task in your workflow with `--add_track_prop` argument. If you don't add o2-analysis-track-propagation task with `add_track_prop` argument, workflow automatically will use o2-analysis-trackextension task for producing trackDCA tables.





