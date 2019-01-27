:;#!/bin/bash
:;PATH=$PATH:~/.local/share/Sonar/sonar-scanner/bin
coverage run tests/runner.py 
coverage xml -i 
sonar-scanner
