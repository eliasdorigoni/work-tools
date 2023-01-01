#!/bin/bash

TMP_FOLDER="./tmp-"$( openssl rand -hex 6 )
TMP_KEYS_FOLDER="$TMP_FOLDER""/keys"
TMP_SOURCE_FOLDER="$TMP_FOLDER""/source"
TMP_ENCRYPTED_FOLDER="$TMP_FOLDER""/encrypted"
TMP_DECRYPTED_FOLDER="$TMP_FOLDER""/decrypted"

echo "Testing at folder: ""$TMP_FOLDER"

mkdir -p "$TMP_KEYS_FOLDER"
mkdir -p "$TMP_SOURCE_FOLDER"
mkdir -p "$TMP_ENCRYPTED_FOLDER"
mkdir -p "$TMP_DECRYPTED_FOLDER"

echo $( openssl rand -hex 32 ) > "$TMP_SOURCE_FOLDER""/random.txt"
./generate-keys.sh "$TMP_KEYS_FOLDER"

./encrypt-file.sh "$TMP_SOURCE_FOLDER""/random.txt" "$TMP_KEYS_FOLDER""/publickey.pub" "$TMP_ENCRYPTED_FOLDER"

./decrypt-file.sh "$TMP_ENCRYPTED_FOLDER""/random.txt.enc" "$TMP_KEYS_FOLDER""/privatekey.pem" "$TMP_DECRYPTED_FOLDER"

echo ""
echo "Now running the test. Source and decrypted file must be identical"
echo ">>>>>>>>>>>>>>>>>>>>>>>>"
diff --report-identical-files "$TMP_SOURCE_FOLDER""/random.txt" "$TMP_DECRYPTED_FOLDER""/random.txt"
echo ">>>>>>>>>>>>>>>>>>>>>>>>"
echo ""
echo "Do you want to delete the test files? [y/n] [default y]"
read keep_files

if [[ "$keep_files" = "y" || -z "$keep_files" ]]
then
	rm -rf "$TMP_FOLDER"
	echo "Test files deleted."
else
	echo "Test files exist at ""$TMP_FOLDER""."
fi