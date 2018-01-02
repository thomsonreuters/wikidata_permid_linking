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
# - downloads entities with LEIs but not PermID from Wikidata (using the python helper)
# - extracts permids for leis from a provided bulk file
# - joins them, creating a CSV suitable for load to Wikidata using QuickStatements

if [ $# -lt 1 ]; then
	echo "Usage leis_bulk.sh <BulkOrganizationsNTriplesFileFromOpenPermID>"
	exit
fi

# extract only the LEI currency lines from the OpenPermID download, print raw (quoted)
# permid & lei code
gunzip -c $1 | sed -n 's|^<https://permid.org/1-\([0-9]*\)> <http://permid.org/ontology/organization/hasLEI> "\([A-Z0-9]*\)"^^<http://www.w3.org/2001/XMLSchema#string> .|"\1"	\2|p'  > temp_leis.tsv

# Get the currencies without a permid from wikidata
python map_by_lei.py > temp_wikidata.tsv

# Sort each file then pass to join. The $'\t' nonsense forces join to use a tab on
# output which we need for QuickStatements
join -1 2 -2 1 -o 2.2,2.3,1.1 -t $'\t'  <(sort -k 2  temp_leis.tsv) <(sort temp_wikidata.tsv) > joined.tsv
sort -k 1 -u joined.tsv > sorted.tsv
rm joined.tsv
rm temp_leis.tsv
rm temp_wikidata.tsv
