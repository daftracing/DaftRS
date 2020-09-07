#!/bin/bash

for f in "G1F7-14C368-AA" "G1F7-14C366-AL" "G1F7-14C367-AL" "HP57-14C366-AG" "HP57-14C367-AG"; do
	if [ ! -f "$f.vbf" ] ; then
	    curl 'https://www.fordtechservice.dealerconnection.com/vdirs/wds/PCMReprogram/DSFM_DownloadFile.asp' --data-raw "filename=$f" --output $f.zip >/dev/null
	    unzip $f.zip
	    rm $f.zip
	fi
done

bspatch ./G1F7-14C366-AL.vbf ./G1F7-14C366-AL-DAFT-T5.vbf ./G1F7-14C366-AL-DAFT-T5.vbf.diff
bspatch ./G1F7-14C366-AL.vbf ./G1F7-14C366-AL-DAFT-T11.vbf ./G1F7-14C366-AL-DAFT-T11.vbf.diff
bspatch ./G1F7-14C366-AL.vbf ./G1F7-14C366-AL-DAFT-T13.vbf ./G1F7-14C366-AL-DAFT-T13.vbf.diff
bspatch ./G1F7-14C366-AL.vbf ./G1F7-14C366-AL-DAFT-T14.vbf ./G1F7-14C366-AL-DAFT-T14.vbf.diff
bspatch ./G1F7-14C366-AL.vbf ./G1F7-14C366-AL-DAFT-T15.vbf ./G1F7-14C366-AL-DAFT-T15.vbf.diff
bspatch ./G1F7-14C366-AL.vbf ./G1F7-14C366-AL-DAFT-T16.vbf ./G1F7-14C366-AL-DAFT-T16.vbf.diff
bspatch ./G1F7-14C366-AL.vbf ./G1F7-14C366-AL-DAFT-T18.vbf ./G1F7-14C366-AL-DAFT-T18.vbf.diff
bspatch ./G1F7-14C366-AL.vbf ./G1F7-14C366-AL-DAFT-X1.vbf ./G1F7-14C366-AL-DAFT-X1.vbf.diff

bspatch ./G1F7-14C367-AL.vbf ./G1F7-14C367-AL-DAFT-DS1.vbf ./G1F7-14C367-AL-DAFT-DS1.vbf.diff
bspatch ./G1F7-14C367-AL.vbf ./G1F7-14C367-AL-DAFT-DS3.vbf ./G1F7-14C367-AL-DAFT-DS3.vbf.diff

bspatch ./HP57-14C366-AG.vbf ./HP57-14C366-AG-DAFT-T1.vbf ./HP57-14C366-AG-DAFT-T1.vbf.diff
