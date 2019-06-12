#!/bin/bash

# Generate bundles of css and js files for bazardelux pages


if [ $(which uglifycss) == '' ]; then
    echo "yui-compressor is not installed! (do 'sudo npm install uglifycss -g')"
    exit 1
fi

if [ $(which uglifyjs) == '' ]; then
    echo "yui-compressor is not installed! (do 'sudo npm install uglify-js -g')"
    exit 1
fi

for BUNDLE in $(ls bundle.*); do

    NAME=$(echo $BUNDLE | cut -d '.' -f 2)
    TYPE=$(echo $BUNDLE | cut -d '.' -f 3)
    MD5=$(cat $BUNDLE | md5sum | cut -c1-6)
    BUNDLE_FILE=$NAME-$MD5.$TYPE
    BUNDLE_FILE_MIN=$NAME-$MD5.min.$TYPE

    echo "=> Generating $BUNDLE_FILE"
    touch $BUNDLE_FILE
    echo '' > $BUNDLE_FILE
    for F in $(cat $BUNDLE); do
        cat ../$F >> $BUNDLE_FILE
    done

    if [ $TYPE == 'css' ]; then
        uglifycss $BUNDLE_FILE > $BUNDLE_FILE_MIN
    elif [ $TYPE == 'js' ]; then
        uglifyjs $BUNDLE_FILE > $BUNDLE_FILE_MIN
    fi
done
