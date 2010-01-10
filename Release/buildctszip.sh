#!/bin/bash
SPEC_VERSION=1.4
CTS_REVISION=0.9.0
RELEASE_DATE=20100110

cd ..
find . -type f -print | grep -v ".svn" | zip COLLADA-${SPEC_VERSION}-CTS-${CTS_REVISION}-${RELEASE_DATE}.zip -@
