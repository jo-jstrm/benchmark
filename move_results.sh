#!/bin/bash

FOLDER_NUMBER=$1

mkdir ~/jjestram/"run_$FOLDER_NUMBER"
mv ~/rime_logs/*.log ~/git/benchmark/"run_$FOLDER_NUMBER"