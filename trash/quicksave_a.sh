#!/bin/bash
# Copyright 2017 Aleksander Gajewski <adiog@brainfuck.pl>
#   created:  pon, 27 mar 2017, 21:07:34
#   modified: pon, 27 mar 2017, 21:07:58

# BASH_CLEANUP {{{
BASH_CLEANUP_FILE=`mktemp`
trap BASH_CLEANUP EXIT

function BASH_CLEANUP() {
  BASH_CLEANUP_FILE_REV=`mktemp`
  tac $BASH_CLEANUP_FILE > $BASH_CLEANUP_FILE_REV
  . $BASH_CLEANUP_FILE_REV
  rm $BASH_CLEANUP_FILE $BASH_CLEANUP_FILE_REV
}

function BASH_FINALLY() {
  echo "$*" >> $BASH_CLEANUP_FILE
}

function BASH_MKTEMP() {
  BASH_TMP=`mktemp`
  echo "rm $BASH_TMP" >> $BASH_CLEANUP_FILE
  echo $BASH_TMP
}

function BASH_MKTEMP_DIR() {
  BASH_TMP=`mktemp -d`
  echo "rm -fr $BASH_TMP" >> $BASH_CLEANUP_FILE
  echo $BASH_TMP
}
# }}}

cd $(basedir $0)
/io.quicksave.bootstrap/client/quicksave_a.py

