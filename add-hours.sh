#!/bin/bash
# Script that adds time. Eg: 2h 30m 1h 15m.
# Letters "h" and "m" are optional: if time > 8 assumes minutes, else hours.


TOTAL_TIME_IN_MINUTES=0

for var in "$@"
do
    RAW_VALUE=$( echo "$var" |sed 's/.$//' )
    if [[ "$var" == *m ]]
    then
        TOTAL_TIME_IN_MINUTES=$((TOTAL_TIME_IN_MINUTES + RAW_VALUE))
    elif [[ "$var" == *h ]]
    then
        TOTAL_TIME_IN_MINUTES=$((TOTAL_TIME_IN_MINUTES + (RAW_VALUE * 60)))
    elif [[ "$var" -le 8 ]]
    then # Assumes its a time in hours
        TOTAL_TIME_IN_MINUTES=$((TOTAL_TIME_IN_MINUTES + (var * 60)))
    elif [[ "$var" -gt 8 ]] && [[ "$var" -lt 60 ]]
    then # Assumes its a time in minutes
        TOTAL_TIME_IN_MINUTES=$((TOTAL_TIME_IN_MINUTES + var))
    else
        echo "Unexpected format: ""$var"
    fi
done

if [[ "$TOTAL_TIME_IN_MINUTES" -ge 60 ]]
then
    MINUTES=$((TOTAL_TIME_IN_MINUTES%60))
    HOURS=$((TOTAL_TIME_IN_MINUTES/60))

    echo "Total: ""$HOURS""h ""$MINUTES""m"
else
    echo "Total: ""$TOTAL_TIME_IN_MINUTES""m"
fi
