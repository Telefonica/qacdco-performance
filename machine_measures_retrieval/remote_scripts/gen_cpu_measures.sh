#!/bin/bash

if [ $1 ]
then
	OUTPUT_FILE=$1
else
	echo "Please use $0 fileoutput.csv"
	exit 1
fi


# AHORA=$(date +%Y%m%d_%H%M)
OUTPUT_FILE=$1

sadf -d -P ALL > $OUTPUT_FILE
sed -i 's/\;/\,/g' $OUTPUT_FILE
sed -i 's/ UTC//g' $OUTPUT_FILE
