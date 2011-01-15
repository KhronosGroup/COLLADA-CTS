#!/bin/bash
SPEC_VERSION=1.4
CTS_REVISION=1.0.0
RELEASE_DATE=20100625

cd ..
rm -rf TestProcedures
rm -rf PackagedResults
find . -type f -print | grep -v ".svn" | grep -v "Feeling" | grep -v "FViewer" | grep -v "Coherency" | zip COLLADA-${SPEC_VERSION}-CTS-IMPLEMENTER-${CTS_REVISION}-${RELEASE_DATE}.zip -@
