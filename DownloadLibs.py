#!/usr/bin/env python3
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


import urllib.request
from urllib.request import Request, urlopen
import os
import sys
import json
from ast import parse
import argparse
import re
import ssl
import logging
import logging.config
import shutil

"""
argcomplete - Bash tab completion for argparse
Documentation https://kislyuk.github.io/argcomplete/
Instalation Steps
pip install argcomplete
sudo activate-global-python-argcomplete
Only Works On Local not in O2
Activate libraries in below and activate #argcomplete.autocomplete(parser) line
"""
import argcomplete  
from argcomplete.completers import ChoicesCompleter



# This script provides download to DQ libraries from O2Physics-DQ Manually with/without Production tag or get DQ libraries from alice-software in local machine

# header for github download
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
}

parser = argparse.ArgumentParser(description="Arguments to pass")
parser.add_argument("--version", help="Online: Your Production tag for O2Physics example: for nightly-20220619, just enter as 20220619", action="store", type=str.lower)
parser.add_argument("--debug", help="Online and Local: execute with debug options", action="store", choices=["NOTSET","DEBUG","INFO","WARNING","ERROR","CRITICAL"], default="DEBUG" , type=str.upper)
parser.add_argument("--local", help="Local: Use Local Paths for getting DQ Libraries instead of online github download. If you are working LXPLUS, It will not working so don't configure with option", action="store_true")
parser.add_argument("--localPath", help="Local: Configure your alice software folder name in your local home path (prefix: home/<user>). Default is home/<user>/alice. Example different configuration is --localpath alice-software --local --> home/<user>/alice-software", action="store", type=str)

argcomplete.autocomplete(parser)
extrargs = parser.parse_args()

MY_PATH = os.path.abspath(os.getcwd())
HOME_PATH = os.environ["HOME"]

ALICE_SOFTWARE_PATH = os.environ["HOME"] + "/alice"

localPathCutsLibrary = ALICE_SOFTWARE_PATH + "/O2Physics/PWGDQ/Core/CutsLibrary.h"
localPathMCSignalsLibrary = ALICE_SOFTWARE_PATH + "/O2Physics/PWGDQ/Core/MCSignalLibrary.h"
localPathEventMixing = ALICE_SOFTWARE_PATH + "/O2Physics/PWGDQ/Core/MixingLibrary.h"

URL_CUTS_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/CutsLibrary.h?raw=true"
URL_MCSIGNALS_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/MCSignalLibrary.h?raw=true"
URL_MIXING_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/MixingLibrary.h?raw=true"

isLibsExist = True

if extrargs.version != None:
    prefix_version = "nightly-"
    extrargs.version = prefix_version + extrargs.version
    
if extrargs.debug:
    DEBUG_SELECTION = extrargs.debug
    numeric_level = getattr(logging, DEBUG_SELECTION.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % DEBUG_SELECTION)
    logging.basicConfig(format="[%(levelname)s] %(message)s", level=DEBUG_SELECTION)

if extrargs.version and extrargs.local == False:
    logging.info("DQ libs will downloaded from github. Your Version For Downloading DQ Libs From Github : %s", extrargs.version)
    
    URL_CUTS_LIBRARY = "https://raw.githubusercontent.com/AliceO2Group/O2Physics/" + extrargs.version + "/PWGDQ/Core/CutsLibrary.h"
    URL_MCSIGNALS_LIBRARY = "https://raw.githubusercontent.com/AliceO2Group/O2Physics/" + extrargs.version + "/PWGDQ/Core/MCSignalLibrary.h"
    URL_MIXING_LIBRARY = "https://raw.githubusercontent.com/AliceO2Group/O2Physics/" + extrargs.version + "/PWGDQ/Core/MixingLibrary.h"
    
if extrargs.local and extrargs.version:
    logging.warning("Your provided configuration for getting DQ libs in locally. You don't need to configure your github nightly version. It's for Online Downloading")
    logging.warning("%s nightly version will not used in interface. Local working on going",extrargs.version)
    
if extrargs.localPath and extrargs.local:
    ALICE_SOFTWARE_PATH = os.environ["HOME"] + "/" + extrargs.localPath
    logging.info("Alice software Local Path is Changed. New Local Path is %s", ALICE_SOFTWARE_PATH)
    if os.path.isdir(ALICE_SOFTWARE_PATH) == True:
        logging.info("Alice software found at %s local Path change is true", ALICE_SOFTWARE_PATH)
    else:
        logging.error("Alice software not found in path!!! Fatal Error. Check your Alice software path configuration")
        sys.exit()
    
    
if extrargs.localPath and extrargs.local == False:
    logging.error("Misconfiguration. You forget to add --local option interface for working localy. You need add this parameter to workflow")
    logging.info("Example usage: python3 DownloadLibs.py --local --localPath alice")
    sys.exit()

    
if extrargs.local:
    if extrargs.localPath == None:
        if os.path.isdir(ALICE_SOFTWARE_PATH) == True:
            logging.info("Default Path will used for Alice Software. Default Path : %s and Valid", ALICE_SOFTWARE_PATH)
        
        
    logging.info("DQ libs will be getting from local folders. You alice software path : %s", ALICE_SOFTWARE_PATH)
    
    localPathCutsLibrary = ALICE_SOFTWARE_PATH + "/O2Physics/PWGDQ/Core/CutsLibrary.h"
    localPathMCSignalsLibrary = ALICE_SOFTWARE_PATH + "/O2Physics/PWGDQ/Core/MCSignalLibrary.h"
    localPathEventMixing = ALICE_SOFTWARE_PATH + "/O2Physics/PWGDQ/Core/MixingLibrary.h"
    
    logging.info("Local CutsLibrary.h Path: %s ",localPathCutsLibrary)
    logging.info("Local MCSignalsLibrary.h Path: %s ",localPathMCSignalsLibrary)
    logging.info("Local MixingLibrary.h Path: %s ",localPathEventMixing)
    
    with open("tempCutsLibrary.h", "wb") as f:
        shutil.copyfile(localPathCutsLibrary, MY_PATH + "/tempCutsLibrary.h")
        if os.path.isfile("tempCutsLibrary.h") == True:
            logging.info("tempCutsLibrary.h created at %s",MY_PATH)
        else:
            logging.info("tempCutsLibrary.h not created at %s Fatal Error", MY_PATH)
            sys.exit()
            
    with open("tempMCSignalsLibrary.h", "wb") as f:
        shutil.copyfile(localPathMCSignalsLibrary, MY_PATH + "/tempMCSignalsLibrary.h") 
        if os.path.isfile("tempMCSignalsLibrary.h") == True:
            logging.info("tempMCSignalsLibrary.h created at %s", MY_PATH)
        else:
            logging.info("tempMCSignalsLibrary.h not created at %s Fatal Error", MY_PATH)
            sys.exit()
            
    with open("tempMixingLibrary.h", "wb") as f:
        shutil.copyfile(localPathEventMixing, MY_PATH + "/tempMixingLibrary.h")
        if os.path.isfile("tempMixingLibrary.h") == True :
            logging.info("tempMixingLibrary.h created at %s", MY_PATH)
        else:
            logging.error("tempMixingLibrary.h not created at %s Fatal Error", MY_PATH)
            sys.exit()
            
    logging.info("DQ Libraries pulled from local alice software successfully!")
    sys.exit()
 
 
if extrargs.local == False:    
    if (os.path.isfile("tempCutsLibrary.h") == False) or (os.path.isfile("tempMCSignalsLibrary.h") == False) or (os.path.isfile("tempMixingLibrary.h")) == False:
        logging.info("Some Libs are Missing. All DQ libs will download")
        logging.info("Github CutsLibrary.h Path: %s ",URL_CUTS_LIBRARY)
        logging.info("Github MCSignalsLibrary.h Path: %s ",URL_MCSIGNALS_LIBRARY)
        logging.info("Github MixingLibrary.h Path: %s ",URL_MIXING_LIBRARY)
        isLibsExist = False
        if extrargs.debug:
            try:
                context = ssl._create_unverified_context()  # prevent ssl problems
                request = urllib.request.urlopen(URL_CUTS_LIBRARY, context=context)
                request = urllib.request.urlopen(URL_MCSIGNALS_LIBRARY, context=context)
                request = urllib.request.urlopen(URL_MIXING_LIBRARY, context=context)
            except urllib.error.HTTPError as error:
                logging.error(error)
        else:
            # Dummy SSL Adder
            context = ssl._create_unverified_context()  # prevent ssl problems
            request = urllib.request.urlopen(URL_CUTS_LIBRARY, context=context)
        
        # HTTP Request
        requestCutsLibrary = Request(URL_CUTS_LIBRARY, headers=headers)
        requestMCSignalsLibrary = Request(URL_MCSIGNALS_LIBRARY, headers=headers)
        requestMixingLibrary  = Request(URL_MIXING_LIBRARY , headers=headers)
        
        # Get Files With Http Requests
        htmlCutsLibrary = urlopen(requestCutsLibrary, context=context).read()
        htmlMCSignalsLibrary = urlopen(requestMCSignalsLibrary, context=context).read()
        htmlMixingLibrary = urlopen(requestMixingLibrary, context=context).read()
        
        with open("tempCutsLibrary.h", "wb") as f:
            f.write(htmlCutsLibrary)
            logging.info("tempCutsLibrary.h downloaded successfully from github")
        with open("tempMCSignalsLibrary.h", "wb") as f:
            f.write(htmlMCSignalsLibrary)
            logging.info("tempMCSignalsLibrary.h downloaded successfully from github")
        with open("tempMixingLibrary.h", "wb") as f:
            f.write(htmlMixingLibrary)
            logging.info("tempMixingLibrary.h downloaded successfully from github")

    if isLibsExist:
        logging.info("DQ Libraries have been downloaded before. If you want to update, delete they manually and run this script again.")
        sys.exit()    
    else:
        logging.info("DQ Libraries downloaded from github successfully!")
sys.exit()