#!/usr/bin/env bash

encCJK=$1
if [ -z "$encCJK" ]; then
 echo 'No file name is provided.'
else
  if [ -f "$encCJK" ]; then
    DIR_SCRIPT=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
    python "$DIR_SCRIPT"/Base32CJK.py -i $encCJK -d | base32 -d | openssl enc -pbkdf2 -aes-256-ctr -A -d
  fi | less
fi
