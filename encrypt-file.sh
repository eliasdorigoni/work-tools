#!/bin/bash

if [ "$#" -lt 3 ]
then
	echo "3 arguments are required: path/to/file.ext path/to/publickey.pub path/to/destination"
	echo "Script stopped."
	exit 1;
fi

SOURCE_FILE="$1"
PUBLIC_KEY_FILE="$2"
DESTINATION_FOLDER=$( echo "$3" | sed "s;/$;;" )"/"

SOURCE_FILENAME=$( echo "$SOURCE_FILE" | sed "s;.*/;;" )
ENCRYPTED_FILE="$DESTINATION_FOLDER""$SOURCE_FILENAME"".enc"

GENERATED_KEY="./key"
ENCRYPTED_KEY="$DESTINATION_FOLDER""$SOURCE_FILENAME"".key.enc"

# Generate a random key
openssl rand -base64 32 > "$GENERATED_KEY"

# Encrypt the main file
openssl enc -aes-256-cbc -pbkdf2 -iter 100000 \
	-salt -in "$SOURCE_FILE" -pass file:"$GENERATED_KEY" -out "$ENCRYPTED_FILE"
	
# Encrypt the key
openssl rsautl -encrypt -inkey "$PUBLIC_KEY_FILE" -pubin -in "$GENERATED_KEY" \
	-out "$ENCRYPTED_KEY"

# Delete the unencrypted key
rm "$GENERATED_KEY"

echo "Files created as:"
echo " ""$ENCRYPTED_FILE"
echo " ""$ENCRYPTED_KEY"
echo "Remember to save both files for proper decryption."