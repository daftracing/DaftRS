#!/bin/bash

for f in "G1F7-14C368-AA" "G1F7-14C366-AL" "G1F7-14C367-AL"; do
	curl 'https://www.fordtechservice.dealerconnection.com/vdirs/wds/PCMReprogram/DSFM_DownloadFile.asp' --data-raw "filename=$f" --output $f.zip >/dev/null
	unzip $f.zip
	rm $f.zip
done

bspatch ./G1F7-14C366-AL.vbf ./G1F7-14C366-AL-DAFT-T5.vbf ./G1F7-14C366-AL-DAFT-T5.vbf.diff
bspatch ./G1F7-14C366-AL.vbf ./G1F7-14C366-AL-DAFT-T11.vbf ./G1F7-14C366-AL-DAFT-T11.vbf.diff