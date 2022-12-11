#!/bin/bash

if [ "$#" -lt 2 ]
then
    echo "Usage: ./backup-notes.sh source-directory destination-directory"
    exit 1
fi

SOURCE_DIR=$( echo "$1" | sed "s;/+$;;" )
DESTINATION_FILE=$( echo "$2" | sed "s;/+$;;" )"/""$(date '+%Y-%m-%d_%H-%M-%S')"".zip"

cd "$SOURCE_DIR"

zip --quiet --recurse-paths "$DESTINATION_FILE" .

cd - > /dev/null

# To see the zip contents: unzip -vl {filename}

# Crontab:
# 0  9 * * 1-5 ~/some-path/backup-notes.sh source dest >> ~/some-path/crontab.backup-notes.log 2>&1
# 3 30 13 * * 1-5 ...
# 4 45 17 * * 1-5 ...
