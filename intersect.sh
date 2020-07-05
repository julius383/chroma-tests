#!/usr/bin/env bash

# $1 name of dump

# find all fingerprints in this dump
awk -F',' '{ print $1 }' "$1" > fpid.txt

if [[ ! -e "mbid.2019.csv" ]];then
  awk -F',' '{ print $2 }' "mbid.2019.csv" > mbid.txt
fi

cat fpid.txt mbid.txt | sort -n | uniq -d > uniq.txt

sqlite3 -header -csv work/csv_database.db < aggregate.sql > data.csv

awk -F ',' '{ if (FNR == 1) { printf("id,%s\n", $0) } else { printf("%d,%s\n", FNR - 1, $0)} }' data.csv > reordered-data.csv

sort -t, -k2,2 -n -u reordered-data.csv | sponge reordered-data.csv

psql -d audionerve -c <<-EOF
\copy public."Song" (id,"acousticId","musicbrainzId","fingerprint") FROM 
'/home/kajm/code/Python/Miscellaneous/chroma-tests/test-data.csv' DELIMITER ',' CSV HEADER;
EOF
