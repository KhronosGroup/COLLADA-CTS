#!/bin/bash
SPEC_VERSION=1.4
CTS_REVISION=1.0.1
RELEASE_DATE=20110220

cd ..
cp Release/config_adopters.txt config.txt
rm -rf TestProcedures
rm -rf PackagedResults
find . -type f -print | grep -v ".svn" | zip COLLADA-${SPEC_VERSION}-CTS-ADOPTER-${CTS_REVISION}-${RELEASE_DATE}.zip -@
