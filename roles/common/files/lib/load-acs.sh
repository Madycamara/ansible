#!/bin/bash

ACSBIN=/usr/local/lib/acs

for i in `ls $ACSBIN/acs-*.sh`; do
	. $i
done
