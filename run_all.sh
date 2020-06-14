#!/bin/bash
for file in gabarito/*.uc
do
	echo "Running $file"
	python3 uc.py $file -no-opt
	echo "File ran successfully"
	echo ""
done
