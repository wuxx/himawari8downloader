#!/bin/bash

#convert png to video

dirname=$1

if [ ${#dirname} -eq 0 ]; then
    echo "$0 dirname"
    exit 1
fi

files=$(ls ${dirname}/)

echo $files
i=0

for file in $files
do
    echo $i
    i=$(($i+1));
    cp ${dirname}/${file} ${dirname}/a$i.png
done

ffmpeg -framerate 12 -i ${dirname}/a%d.png -codec copy ${dirname}.mkv

rm ${dirname}/a*.png
tar -zcvf ${dirname}.tar.gz ${dirname}/*
#ffmpeg -f image2 -framerate 12 -i 20170821/a%d.png test.gif
