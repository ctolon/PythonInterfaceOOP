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
import argparse
import ssl
import logging
import logging.config
import shutil
import argcomplete
import pathlib

# This script provides download to DQ libraries from O2Physics-DQ Manually with/without Production tag or get DQ libraries from alice-software in local machine


def main():
    
    # header for github download
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36"
        }
    
    parser = argparse.ArgumentParser(description = "Arguments to pass")
    parser.add_argument("--version", help = "Online: Your Production tag for O2Physics example: for nightly-20220619, just enter as 20220619", action = "store", type = str.lower,)
    parser.add_argument("--debug", help = "Online and Local: execute with debug options", action = "store", choices = ["NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], default = "DEBUG", type = str.upper,)
    parser.add_argument("--local", help = "Local: Use Local Paths for getting DQ Libraries instead of online github download. If you are working LXPLUS, It will not working so don't configure with option", action = "store_true",)
    parser.add_argument("--localPath", help = "Local: Configure your alice software folder name in your local home path (prefix: home/<user>). Default is home/<user>/alice. Example different configuration is --localpath alice-software --local --> home/<user>/alice-software", action = "store", type = str)
    
    argcomplete.autocomplete(parser)
    extrargs = parser.parse_args()
    
    MY_PATH = os.path.abspath(os.getcwd())
    TEMP_LIB_PATH = '/templibs/'
    HOME_PATH = os.environ["HOME"]
    
    ALICE_SOFTWARE_PATH = HOME_PATH + "/alice"
    
    localPathCutsLibrary = ALICE_SOFTWARE_PATH + "/O2Physics/PWGDQ/Core/CutsLibrary.cxx"
    localPathMCSignalsLibrary = ALICE_SOFTWARE_PATH + "/O2Physics/PWGDQ/Core/MCSignalLibrary.cxx"
    localPathEventMixing = ALICE_SOFTWARE_PATH + "/O2Physics/PWGDQ/Core/MixingLibrary.cxx"
    localPathHistogramsLibrary = ALICE_SOFTWARE_PATH + "/O2Physics/PWGDQ/Core/HistogramsLibrary.cxx"
    
    URL_CUTS_LIBRARY = ("https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/CutsLibrary.cxx?raw=true")
    URL_MCSIGNALS_LIBRARY = ("https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/MCSignalLibrary.cxx?raw=true")
    URL_MIXING_LIBRARY = ("https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/MixingLibrary.cxx?raw=true")
    URL_HISTOGRAMS_LIBRARY = "https://github.com/AliceO2Group/O2Physics/blob/master/PWGDQ/Core/HistogramsLibrary.cxx?raw=true"
    
    isLibsExist = True
    
    if extrargs.version is not None:
        prefix_version = "nightly-"
        extrargs.version = prefix_version + extrargs.version
    
    if extrargs.debug:
        DEBUG_SELECTION = extrargs.debug
        numeric_level = getattr(logging, DEBUG_SELECTION.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError("Invalid log level: %s" % DEBUG_SELECTION)
        logging.basicConfig(format = "[%(levelname)s] %(message)s", level = DEBUG_SELECTION)
    
    # Create templibs directory if not exist
    if not os.path.isdir("templibs"):
        logging.info("templibs directory is missing. it will be created...")
        path = pathlib.Path(__file__).parent.resolve()
        pathWithFile = os.path.join(path, "templibs")
        try:
            os.mkdir(pathWithFile)
            logging.info(f"templibs directory created successfully: {pathWithFile}")
        except OSError as error:
            raise OSError(error)
    
    if extrargs.version and extrargs.local is False:
        logging.info("DQ libs will downloaded from github. Your Version For Downloading DQ Libs From Github : %s", extrargs.version,)
        
        URL_CUTS_LIBRARY = ("https://github.com/AliceO2Group/O2Physics/blob/" + extrargs.version + "/PWGDQ/Core/CutsLibrary.cxx?raw=true")
        URL_MCSIGNALS_LIBRARY = ("https://github.com/AliceO2Group/O2Physics/blob/" + extrargs.version + "/PWGDQ/Core/MCSignalLibrary.cxx?raw=true")
        URL_MIXING_LIBRARY = ("https://github.com/AliceO2Group/O2Physics/blob/" + extrargs.version + "/PWGDQ/Core/MixingLibrary.cxx?raw=true")
        URL_HISTOGRAMS_LIBRARY = ("https://github.com/AliceO2Group/O2Physics/blob/" + extrargs.version + "/PWGDQ/Core/HistogramsLibrary.cxx?raw=true")
    
    if extrargs.local and extrargs.version:
        logging.warning("Your provided configuration for getting DQ libs in locally. You don't need to configure your github nightly version. It's for Online Downloading")
        logging.warning("%s nightly version will not used in interface. Local working on going", extrargs.version)
    
    if extrargs.localPath and extrargs.local:
        ALICE_SOFTWARE_PATH = os.environ["HOME"] + "/" + extrargs.localPath
        logging.info("Alice software Local Path is Changed. New Local Path is %s", ALICE_SOFTWARE_PATH)
        if os.path.isdir(ALICE_SOFTWARE_PATH) is True:
            logging.info("Alice software found at %s local Path change is true", ALICE_SOFTWARE_PATH)
        else:
            logging.error("Alice software not found in path!!! Fatal Error. Check your Alice software path configuration")
            sys.exit()
    
    if extrargs.localPath and extrargs.local is False:
        logging.error("Misconfiguration. You forget to add --local option interface for working localy. You need add this parameter to workflow")
        logging.info("Example usage: python3 DownloadLibs.py --local --localPath alice")
        sys.exit()
    
    if extrargs.local:
        if extrargs.localPath is None:
            logging.info("Default Path will used for Alice Software. Default Path : %s", ALICE_SOFTWARE_PATH)
            if os.path.isdir(ALICE_SOFTWARE_PATH) is True:
                logging.info("Default Path: %s is Valid", ALICE_SOFTWARE_PATH)
            elif os.path.isdir(ALICE_SOFTWARE_PATH) is False:
                logging.error("Default Path: %s is invalid!! Fatal Error. Check your Alice software path configuration", ALICE_SOFTWARE_PATH,)
                sys.exit()
        
        logging.info("DQ libs will be getting from local folders. You alice software path : %s", ALICE_SOFTWARE_PATH,)
        
        localPathCutsLibrary = ALICE_SOFTWARE_PATH + "/O2Physics/PWGDQ/Core/CutsLibrary.cxx"
        localPathMCSignalsLibrary = ALICE_SOFTWARE_PATH + "/O2Physics/PWGDQ/Core/MCSignalLibrary.cxx"
        localPathEventMixing = ALICE_SOFTWARE_PATH + "/O2Physics/PWGDQ/Core/MixingLibrary.cxx"
        localPathHistogramsLibrary = ALICE_SOFTWARE_PATH + "/O2Physics/PWGDQ/Core/HistogramsLibrary.cxx"
        
        logging.info("Local CutsLibrary.cxx Path: %s ", localPathCutsLibrary)
        logging.info("Local MCSignalsLibrary.cxx Path: %s ", localPathMCSignalsLibrary)
        logging.info("Local MixingLibrary.cxx Path: %s ", localPathEventMixing)
        logging.info("Local HistogramsLibrary.cxx Path: %s ", localPathHistogramsLibrary)
        try:
            with open(MY_PATH + TEMP_LIB_PATH + "tempCutsLibrary.cxx", "wb") as f:
                shutil.copyfile(localPathCutsLibrary, MY_PATH + TEMP_LIB_PATH + "tempCutsLibrary.cxx")
                if os.path.isfile("templibs/tempCutsLibrary.cxx") is True:
                    logging.info("tempCutsLibrary.cxx created at %s", MY_PATH + TEMP_LIB_PATH)
                else:
                    logging.error("tempCutsLibrary.cxx not created at %s Fatal Error", MY_PATH + TEMP_LIB_PATH)
                    sys.exit()
        except FileNotFoundError:
            logging.error("%s not found in your provided alice-software path!!! Check your alice software path", localPathCutsLibrary,)
            sys.exit()
        
        try:
            with open(MY_PATH + TEMP_LIB_PATH + "tempMCSignalsLibrary.cxx", "wb") as f:
                shutil.copyfile(localPathMCSignalsLibrary, MY_PATH + TEMP_LIB_PATH + "tempMCSignalsLibrary.cxx")
                if os.path.isfile("templibs/tempMCSignalsLibrary.cxx") is True:
                    logging.info("tempMCSignalsLibrary.cxx created at %s", MY_PATH)
                else:
                    logging.error("tempMCSignalsLibrary.cxx not created at %s Fatal Error", MY_PATH + TEMP_LIB_PATH)
                    sys.exit()
        except FileNotFoundError:
            logging.error("%s not found in your provided alice-software path!!! Check your alice software path", localPathMCSignalsLibrary,)
            sys.exit()
        
        try:
            with open(MY_PATH + TEMP_LIB_PATH + "tempMixingLibrary.cxx", "wb") as f:
                shutil.copyfile(localPathEventMixing, MY_PATH + TEMP_LIB_PATH + "tempMixingLibrary.cxx")
                if os.path.isfile("templibs/tempMixingLibrary.cxx") is True:
                    logging.info("tempMixingLibrary.cxx created at %s", MY_PATH + TEMP_LIB_PATH)
                else:
                    logging.error("tempMixingLibrary.cxx not created at %s Fatal Error", MY_PATH + TEMP_LIB_PATH)
                    sys.exit()
        except FileNotFoundError:
            logging.error("%s not found in your provided alice-software path!!! Check your alice software path", localPathEventMixing,)
            sys.exit()
        
        try:
            with open(MY_PATH + TEMP_LIB_PATH + "tempHistogramsLibrary.cxx", "wb") as f:
                shutil.copyfile(localPathHistogramsLibrary, MY_PATH + TEMP_LIB_PATH + "tempHistogramsLibrary.cxx")
                if os.path.isfile("templibs/tempHistogramsLibrary.cxx") is True:
                    logging.info("tempHistogramsLibrary.cxx created at %s", MY_PATH + TEMP_LIB_PATH)
                else:
                    logging.error("tempHistogramsLibrary.cxx not created at %s Fatal Error", MY_PATH + TEMP_LIB_PATH)
                    sys.exit()
        except FileNotFoundError:
            logging.error("%s not found in your provided alice-software path!!! Check your alice software path", localPathHistogramsLibrary,)
            sys.exit()
        
        logging.info("DQ Libraries pulled from local alice software successfully!")
        sys.exit()
    
    if extrargs.local is False:
        if (os.path.isfile("tempCutsLibrary.cxx") and os.path.isfile("tempMCSignalsLibrary.cxx") and os.path.isfile("tempMixingLibrary.cxx") and os.path.isfile("tempHistogramsLibrary.cxx")) is False:
            logging.info("Some Libs are Missing. All DQ libs will download")
            logging.info("Github CutsLibrary.cxx Path: %s ", URL_CUTS_LIBRARY)
            logging.info("Github MCSignalsLibrary.cxx Path: %s ", URL_MCSIGNALS_LIBRARY)
            logging.info("Github MixingLibrary.cxx Path: %s ", URL_MIXING_LIBRARY)
            logging.info("Github HistogramsLibrary.cxx Path: %s ", URL_HISTOGRAMS_LIBRARY)
            isLibsExist = False
            if extrargs.debug:
                try:
                    context = ssl._create_unverified_context() # prevent ssl problems
                except urllib.error.HTTPError as error:
                    logging.error(error)
            else:
                # Dummy SSL Adder
                context = ssl._create_unverified_context() # prevent ssl problems
            
            # HTTP Request
            requestCutsLibrary = Request(URL_CUTS_LIBRARY, headers = headers)
            requestMCSignalsLibrary = Request(URL_MCSIGNALS_LIBRARY, headers = headers)
            requestMixingLibrary = Request(URL_MIXING_LIBRARY, headers = headers)
            requestHistogramsLibrary = Request(URL_HISTOGRAMS_LIBRARY, headers = headers)
            
            # Get Files With Http Requests
            htmlCutsLibrary = urlopen(requestCutsLibrary, context = context).read()
            htmlMCSignalsLibrary = urlopen(requestMCSignalsLibrary, context = context).read()
            htmlMixingLibrary = urlopen(requestMixingLibrary, context = context).read()
            htmlHistogramsLibrary = urlopen(requestHistogramsLibrary, context = context).read()
            
            with open("templibs/tempCutsLibrary.cxx", "wb") as f:
                f.write(htmlCutsLibrary)
                logging.info("tempCutsLibrary.cxx downloaded successfully from github")
            with open("templibs/tempMCSignalsLibrary.cxx", "wb") as f:
                f.write(htmlMCSignalsLibrary)
                logging.info("tempMCSignalsLibrary.cxx downloaded successfully from github")
            with open("templibs/tempMixingLibrary.cxx", "wb") as f:
                f.write(htmlMixingLibrary)
                logging.info("tempMixingLibrary.cxx downloaded successfully from github")
            with open("templibs/tempHistogramsLibrary.cxx", "wb") as f:
                f.write(htmlHistogramsLibrary)
                logging.info("tempHistogramsLibrary.cxx downloaded successfully from github")
        
        if isLibsExist:
            logging.info("DQ Libraries have been downloaded before. If you want to update, delete they manually and run this script again.")
            sys.exit()
        else:
            logging.info("DQ Libraries downloaded from github successfully!")


if __name__ == '__main__':
    sys.exit(main())
