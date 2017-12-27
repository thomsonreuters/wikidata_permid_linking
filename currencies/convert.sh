#!/bin/bash
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.	 You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.	See the License for the
# specific language governing permissions and limitations
# under the License.

# This script, tested on Mac but should run on any modern Unix:
# - downloads currencies from Wikidata (using the python helper)
# - extracts permids for iso currency codes from a provided bulk file
# - joins them, creating a CSV suitable for load to Wikidata using QuickStatements

if [ $# -lt 1 ]; then
	echo "Usage convert.sh <BulkCurrencyNTriplesFileFromOpenPermID>"
	exit
fi

# extract only the ISO currency lines from the OpenPermID download, print raw (quoted)
# permid & iso code
sed -n 's|^<https://permid.org/1-\([0-9]*\)> <http://permid.org/ontology/currency/iso4217> "\([A-Z]*\)"^^<http://www.w3.org/2001/XMLSchema#string> .|"\1"	\2|p' <$1 > temp_permids.tsv

# Get the currencies without a permid from wikidata
python map_by_isocode.py > temp_wikidata.tsv

# Sort each file then pass to join. The $'\t' nonsense forces join to use a tab on
# output which we need for QuickStatements
join -1 2 -2 1 -o 2.2,2.3,1.1 -t $'\t'  <(sort -k 2  temp_permids.tsv) <(sort temp_wikidata.tsv) > joined.tsv

rm temp_permids.tsv
rm temp_wikidata.tsv
