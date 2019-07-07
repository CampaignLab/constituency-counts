for dir in ./*; do
    cat $dir/*.csv >> $dir.csv;
    done
