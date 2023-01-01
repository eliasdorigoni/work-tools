#!/bin/bash
# Generates a key pair. Accepts an optional argument as destination.

DESTINATION_PATH="./"

if [ $1 ]
then
    DESTINATION_PATH=$( echo "$1" | sed "s;/$;;" )"/"
fi

PRIVATE_KEY_FILE="$DESTINATION_PATH""privatekey.pem"
PUBLIC_KEY_FILE="$DESTINATION_PATH""publickey.pub"

if [ -f "$PRIVATE_KEY_FILE" ]
then
    ORIGINAL_PRIVATE_KEY_FILE="$PRIVATE_KEY_FILE"
    ORIGINAL_PUBLIC_KEY_FILE="$PUBLIC_KEY_FILE"
    COUNT=0
    while [ -f "$PRIVATE_KEY_FILE" ];
    do
        PRIVATE_KEY_FILE="$ORIGINAL_PRIVATE_KEY_FILE"".""$COUNT"
        PUBLIC_KEY_FILE="$ORIGINAL_PUBLIC_KEY_FILE"".""$COUNT"
        COUNT=$(($COUNT+1))
    done
fi

openssl genrsa -out "$PRIVATE_KEY_FILE" 2048
openssl rsa -in "$PRIVATE_KEY_FILE" -outform pem -pubout -out "$PUBLIC_KEY_FILE"

echo "Keys generated at:"
echo " -> ""$PRIVATE_KEY_FILE"
echo " -> ""$PUBLIC_KEY_FILE"

if [ -z "$1" ]
then
    echo "Note: the first parameter is the path, otherwise is set to . (dot)"
fi