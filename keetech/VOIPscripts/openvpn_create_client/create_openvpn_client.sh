#!/bin/bash

OPENVPN_RSA_DIR=/etc/openvpn/easy-rsa/
OPENVPN_KEYS="$OPENVPN_RSA_DIR"keys
OUTPUT_FOLDER=/root
BASE_FILE=voip_elastix.conf.base

confirm () {
    # call with a prompt string or use a default
    read -r -p "${1:-Are you sure? [y/N]} " response
    case $response in
        [yY][eE][sS]|[yY]) 
            true
            ;;
        *)
            false
            ;;
    esac
}

echo "The base name used is: '$1'"
if [[ -z "${1// }" ]]; then
	echo "Cannot use empty string as base name, exiting..."
	exit 0
fi

confirm || exit 0

CN=$1
if [ -f $OPENVPN_KEYS/$CN.crt ]
	then echo "Error: certificate with the CN $CN alread exists!"
		echo "    $OPENVPN_KEYS/$CN.crt"
	exit
fi

cd $OPENVPN_RSA_DIR

#echo `pwd`
source ./vars > /dev/null
./build-key --batch $CN

cd $OPENVPN_KEYS

cp $CN.crt $OUTPUT_FOLDER
cp $CN.key $OUTPUT_FOLDER
cp ca.crt $OUTPUT_FOLDER

cd $OUTPUT_FOLDER

CN_CONF="$CN".conf 

cp $BASE_FILE $CN_CONF

echo '<ca>' >> $CN_CONF && cat ca.crt >> $CN_CONF && echo -e '</ca>\n' >> $CN_CONF
echo '<cert>' >> $CN_CONF && cat "$CN".crt >> $CN_CONF && echo -e '</cert>\n' >> $CN_CONF
echo '<key>' >> $CN_CONF && cat "$CN".key >> $CN_CONF && echo -e '</key>\n' >> $CN_CONF

# END

rm -f $CN.crt
rm -f $CN.key
rm -f ca.crt

echo ""
echo "####################################################################################"
echo "COMPLETE! Copy the file '$OUTPUT_FOLDER/$CN_CONF' to the client and configure!"
echo "####################################################################################"

