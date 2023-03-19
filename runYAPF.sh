#!/usr/bin/env bash

# Script for reformatted like Clang in C++ (YAPF)
yapf -e .style.yapf -p -vv *.py PythonInterfaceOOP/*.py PythonInterfaceOOP/extramodules/*.py -i