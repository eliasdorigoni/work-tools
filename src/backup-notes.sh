#!/bin/bash
# Usage: ./backup-notes source-directory destination-directory
# Both paths must not end with slash

sourceDir="$1"
destinationFile="$2""/""$(date '+%Y-%m-%d_%H-%M-%S')"".zip"

cd "$sourceDir"

zip --quiet --recurse-paths "$destinationFile" .

cd - > /dev/null

# To see the zip contents: unzip -vl {filename}
# Crontab:
# 0  9 * * 1-5 ~/some-path/backup-notes.sh source dest >> ~/some-path/crontab.backup-notes.log 2>&1
# 3 30 13 * * 1-5 ...
# 4 45 17 * * 1-5 ...
