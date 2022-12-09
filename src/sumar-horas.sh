#!/bin/bash
# This script can sum time with a specific format, like "1h 45m" and such.

TOTAL_TIME_IN_MINUTES=0

for var in "$@"
do
    RAW_VALUE=$( echo "$var" |sed 's/.$//' )
    if [[ "$var" == *m ]]
    then
        TOTAL_TIME_IN_MINUTES=$(($TOTAL_TIME_IN_MINUTES+$RAW_VALUE))
    elif [[ "$var" == *h ]]
    then
        TOTAL_TIME_IN_MINUTES=$(($TOTAL_TIME_IN_MINUTES+($RAW_VALUE*60)))
    else
        echo "Unexpected format: ""$var"
    fi
done

if [[ "$TOTAL_TIME_IN_MINUTES" -ge 60 ]]
then
    MINUTES=$(($TOTAL_TIME_IN_MINUTES%60))
    HOURS=$(($TOTAL_TIME_IN_MINUTES/60))

    echo "Total: ""$HOURS""h ""$MINUTES""m"
else
    echo "Total: ""$TOTAL_TIME_IN_MINUTES""m"
fi