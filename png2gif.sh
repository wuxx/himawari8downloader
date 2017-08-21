#!/bin/bash

dirname=$1

files=$(ls *.png)

i=0

for file in $files
do
    ls $file
    echo $i
    i=$(($i+1));
    cp $file a$i.png
done

#ffmpeg -f image2 -framerate 12 -i 20170821/a%d.png test.gif
