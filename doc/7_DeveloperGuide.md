
# Introduction to Modifying

This chapter will explain to you how to integrate these updates when there are new updates to common dependencies, configuration or process functions in O2.

## Developer Tools

Tools used to add new configurable or new process functions in JSONs and more are defined as functions in the `configSetter.py` script in the extramodules folder (You can found more information in doc strings).

Main Tools:

* setConfigs
* SetArgsToArgumentParser:
* setSwitch
* setProcessDummy

Helper Tools:
* setConverters
* mandatoryArgChecker
* depsChecker
* oneToMultiDepsChecker

TODO Ongoing

## Naming Conventions

* Folders: All lowercase
* Class: Upper camelcase
* Function: Lower camelcase
* Variables: Lower camelcase
* Constants: Screaming camelcase
* O2 converter arguments: Snake case

[← Go back to Instructions For Tutorials](6_Tutorials.md) | [↑ Go to the Table of Content ↑](../README.md) [Continue to TroubleshootingTreeNotFound →](8_TroubleshootingTreeNotFound.md)