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


def ExpandDeepTDirs(tf, to_map):
    """
    A deep-mapping function for one TDirectory
    """
    
    tpath = None # dummy param
    names = sorted(to_map.keys())
    # print("names = ",names)
    for n in names:
        # print("n =", n)
        if len(to_map[n]) != 1:
            continue
        if tpath == None:
            tpath_ = n
        else:
            tpath_ = tpath + "/" + n
        
        tobject = to_map[n][0]
        if type(tobject) is ROOT.TDirectoryFile:
            m = Map(tf, tobject, tpath_)
            #print(m)
            to_map[n].append(m)
            # print("TO MAP = ", to_map[n])
            return to_map[n] #


def MappingTFile(filename):
    """
    Get TTree names from one Data Frame
    """
    if filename.endswith("txt") or filename.endswith("text"):
        with open(filename) as f:
            for line in f:
                line = line.strip()
                if line.endswith(".root"):
                    logging.info("Converter manager will use this file from text list : %s", line)
                    filename = line
                    break
    
    f = ROOT.TFile(filename)
    m = Map(f, f)
    # print("MAP = ",m)
    # print("FİLE = ",f)
    return ExpandDeepTDirs(f, m)


def getTTrees(aod: str):
    """ Get TTrees from one DF

    Args:
        aod (CLI Argument): CLI Argument for AO2D.root File 

    Returns:
        list: list of all ttres names in provided AO2D.root File
    """
    textAodList = aod.startswith("@")
    endsWithTxt = aod.endswith("txt") or aod.endswith("text")
    ttreeList = []
    
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
    for i in tFile:
        if isinstance(i, dict):
            for key in i.keys():
                ttreeList.append(key)
    return ttreeList
