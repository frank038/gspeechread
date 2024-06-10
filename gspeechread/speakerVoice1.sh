#!/bin/bash

sleep 1
# piper could be a better program instead of espeak
echo "$1" | espeak-ng -v en

