#!/bin/bash
for file in gabarito/*.uc
do
	echo "Running $file"
	python3 uc.py $file -opt
	echo
	echo "-------------------"
	echo
done
