#!/usr/bin/env bash

encCJK=$1
if [ -z "$encCJK" ]; then
 echo 'No file name is provided.'
else
  if [ -f "$encCJK" ]; then
    DIR_SCRIPT=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
    python "$DIR_SCRIPT"/Base64_CJK.py -i $encCJK -d | openssl enc -aes-256-ctr -a -A -d
  fi | less
fi
