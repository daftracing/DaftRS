#!/bin/bash

for f in "G1F7-14C368-AA" "G1F7-14C366-AL" "G1F7-14C367-AL"; do
	if [ ! -f "$f.vbf" ] ; then
	    curl 'https://www.fordtechservice.dealerconnection.com/vdirs/wds/PCMReprogram/DSFM_DownloadFile.asp' --data-raw "filename=$f" --output $f.zip >/dev/null
	    unzip $f.zip
	    rm $f.zip
	fi
done

bspatch ./G1F7-14C366-AL.vbf ./G1F7-14C366-AL-DAFT-T5.vbf ./G1F7-14C366-AL-DAFT-T5.vbf.diff
bspatch ./G1F7-14C366-AL.vbf ./G1F7-14C366-AL-DAFT-T11.vbf ./G1F7-14C366-AL-DAFT-T11.vbf.diff
bspatch ./G1F7-14C366-AL.vbf ./G1F7-14C366-AL-DAFT-T13.vbf ./G1F7-14C366-AL-DAFT-T13.vbf.diff
bspatch ./G1F7-14C367-AL.vbf ./G1F7-14C367-AL-DAFT-DS1.vbf ./G1F7-14C367-AL-DAFT-DS1.vbf.diff
bspatch ./G1F7-14C367-AL.vbf ./G1F7-14C367-AL-DAFT-DS3.vbf ./G1F7-14C367-AL-DAFT-DS3.vbf.diff
