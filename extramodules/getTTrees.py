#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
# -*- coding: utf-8 -*-

# Copyright 2019-2020 CERN and copyright holders of ALICE O2.
# See https://alice-o2.web.cern.ch/copyright for details of the copyright holders.
# All rights not expressly granted are reserved.
#
# This software is distributed under the terms of the GNU General Public
# License v3 (GPL Version 3), copied verbatim in the file "COPYING".
#
# In applying this license CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

# \Author: ionut.cristian.arsene@cern.ch
# \Interface:  cevat.batuhan.tolon@cern.ch

import ROOT
import logging

# TODO resolve the perfomance issue or prepare seperate string
# NOT MAINTAINED YET


class GetOutOfLoop(Exception):
    pass


def Map(tf, browsable_to, tpath = None):
    """
    Maps objets as dict[obj_name][0] using a TFile (tf) and TObject to browse.
    """
    m = {}
    for k in browsable_to.GetListOfKeys():
        n = k.GetName()
        if tpath == None:
            m[n] = [tf.Get(n)]
        else:
            m[n] = [tf.Get(tpath + "/" + n)]
    return m


def ExpandDeepTDirs(tf, to_map, tpath = None):
    """
    A recursive deep-mapping function that expands into TDirectory(ies)
    """
    names = sorted(to_map.keys())
    for n in names:
        if len(to_map[n]) != 1:
            continue
        if tpath == None:
            tpath_ = n
        else:
            tpath_ = tpath + "/" + n
        
        tobject = to_map[n][0]
        if type(tobject) is ROOT.TDirectoryFile:
            m = Map(tf, tobject, tpath_)
            to_map[n].append(m)
            ExpandDeepTDirs(tf, m, tpath_)


def MappingTFile(filename, deep_maps = None):
    """
    Maps an input file as TFile into a dictionary(ies) of objects and names.
    Structure: dict[name][0] == object, dict[name][1] == deeper dict.
    """
    if deep_maps == None:
        deep_maps = {}
    if not type(deep_maps) is dict:
        return deep_maps
    
    f = ROOT.TFile(filename)
    m = Map(f, f)
    ExpandDeepTDirs(f, m)
    
    deep_maps[filename] = [f]
    deep_maps[filename].append(m)
    
    return deep_maps


def getTTrees(aod: str):
    """TODO: add desc

    Args:
        aod (CLI Argument): CLI Argument for AO2D.root File 

    Returns:
        list: list of all ttres names in provided AO2D.root File
    """
    textAodList = aod.startswith("@")
    endsWithTxt = aod.endswith("txt") or aod.endswith("text")
    oneTimeLoop = False # For looping DF Folders only one time when founded for optimizing performance
    
    # Management for text aod list files
    if textAodList and endsWithTxt:
        aod = aod.replace("@", "")
        with open(aod) as f:
            for line in f:
                if line.endswith(".root"):
                    # print(line)
                    aod = line # get one AO2D.root file from text
                    break
    
    tFile = (MappingTFile(aod)) # Input as aod
    ttreeList = []
    
    try:
        for v in tFile.values():
            if oneTimeLoop == True:
                raise GetOutOfLoop
            print("Level 1", v, end = '\n') # k: AOD file name v: All objects
            for i in v:
                if oneTimeLoop == True:
                    raise GetOutOfLoop
                print(v)
                if isinstance(i, dict):
                    if oneTimeLoop == True:
                        raise GetOutOfLoop
                    #print(i.keys()) # all DF Folder names
                    for k2, v2 in i.items():
                        if oneTimeLoop == True:
                            raise GetOutOfLoop
                        elif k2.startswith("DF"):
                            # print(k2) # get one DF Folder name
                            for j in v2:
                                if oneTimeLoop == True:
                                    raise GetOutOfLoop
                                #print(j) # get dict for ttres : obj
                                if isinstance(j, dict):
                                    oneTimeLoop = True
                                    ttreeList = j.keys()
                                    raise GetOutOfLoop
                            
                            #raise GetOutOfLoop
                        #raise GetOutOfLoop
                    #raise GetOutOfLoop
                #raise GetOutOfLoop
    except GetOutOfLoop:
        print("ÇIKTI")
        return ttreeList

