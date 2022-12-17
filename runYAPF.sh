#!/usr/bin/env bash

# Script for reformatted like Clang in C++ (YAPF)
yapf -e .style.yapf -p -vv *.py extramodules/*.py -i