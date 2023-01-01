#!/bin/bash

if [ "$#" -lt 3 ]
then
	echo "3 arguments are required: path/to/file.enc path/to/private.pem path/to/destination"
	echo "Script stopped."
	exit 1;
fi

ENCRYPTED_FILE="$1"
DECRYPTED_FILENAME=$( echo "$ENCRYPTED_FILE" | sed "s;.*/;;" | sed "s/\.enc$//")
ENCRYPTED_KEY=$( echo "$1" | sed "s/\.enc$/.key.enc/" )
PRIVATE_KEY="$2"
DESTINATION_FOLDER=$( echo "$3" | sed "s;/$;;" )"/"
DECRYPTED_KEY="./key.bin"


if [ ! -f "$ENCRYPTED_KEY" ]
then
	echo "A key file is missing. It's expected to exist as ""$ENCRYPTED_KEY"
	echo "Script stopped."
	exit 1
fi


OUTPUT_FILE=$( echo "$1" | sed 's/.enc//' )

openssl rsautl -decrypt -inkey "$PRIVATE_KEY" -in "$ENCRYPTED_KEY" -out key.bin

openssl enc -d -aes-256-cbc -pbkdf2 -iter 100000 \
	-in "$ENCRYPTED_FILE" -out "$DESTINATION_FOLDER""$DECRYPTED_FILENAME" \
	-pass file:"$DECRYPTED_KEY"

rm "$DECRYPTED_KEY"

echo "File decrypted at:"
echo " ""$DESTINATION_FOLDER""$DECRYPTED_FILENAME"
