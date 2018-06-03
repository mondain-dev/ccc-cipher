#!/usr/bin/env bash

enc=$1
if [ -z "$enc" ]; then
 echo 'No file name is provided.'
else
  tput smcup
  if [ -f "$enc" ]; then
    mv $enc ${enc}.old
    read -sp 'Enter password: ' PASS
    echo
    { printf '%s\n' "$PASS" | openssl enc -aes-256-ctr -a -d    -kfile /dev/stdin -in ${enc}.old ; cat ; } |
    { printf '%s\n' "$PASS" | openssl enc -aes-256-ctr -a -salt -kfile /dev/stdin -in /dev/fd/3 -out $enc ; } 3<&0
    unset PASS
  else
    openssl enc -aes-256-ctr -a -salt -out $enc
  fi
  tput rmcup
  python "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"/Base64_CJK.py -i $enc -o $(echo ${enc%.enc} | sed 's/.txt$//').CJK.txt
fi
