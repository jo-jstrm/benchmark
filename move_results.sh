#!/bin/bash

FOLDER_NUMBER=$1

mkdir /home/jjestram/git/benchmark/"run_$FOLDER_NUMBER"
mv /home/jjestram/rime_logs/*.log /home/jjestram/git/benchmark/"run_$FOLDER_NUMBER"
