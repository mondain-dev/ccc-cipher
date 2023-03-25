#!/usr/bin/env bash

enc=$1
if [ -z "$enc" ]; then
 echo 'No file name is provided.'
else
  tput smcup
  if [ -f "$enc" ]; then
    mv $enc ${enc}.old
    base32 -d ${enc}.old > ${enc}.old.bin
    read -sp 'Enter password: ' PASS
    echo
    { printf '%s\n' "$PASS" | openssl enc -aes-256-ctr -pbkdf2 -d          -kfile /dev/stdin -in ${enc}.old.bin ; cat ; } |
    { printf '%s\n' "$PASS" | openssl enc -aes-256-ctr -pbkdf2 -salt -kfile /dev/stdin -in /dev/fd/3 -out ${enc}.bin ; } 3<&0
    unset PASS
    base32 $enc.bin > $enc
    rm ${enc}.old.bin $enc.bin
  else
    openssl enc -aes-256-ctr -pbkdf2 -salt | base32 > $enc
  fi
  tput rmcup
  python "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"/Base32CJK.py -i $enc -o $(echo ${enc%.enc} | sed 's/.txt$//').CJK.txt
fi
