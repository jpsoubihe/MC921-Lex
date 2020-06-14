#!/bin/bash
for file in gabarito/*.uc
do
	echo "Running $file"
	python3 uc.py $file -no-opt
	echo
	echo "-------------------"
	echo
done
