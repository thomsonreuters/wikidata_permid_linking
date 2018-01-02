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

#pip install sparqlwrapper
#https://rdflib.github.io/sparqlwrapper/

from __future__ import print_function


import sys
import requests
import time
from SPARQLWrapper import SPARQLWrapper, JSON

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def search_permid_for_lei(access_token, lei):
	headers = {'X-AG-Access-Token' : access_token}
	url = 'https://api.thomsonreuters.com/permid/search?q='+lei
	ret = None
	try:
		response = requests.get(url, headers=headers)
	except Exception  as e:
		print ('Error in connect ' , e)
		return
	if response.status_code == 200:
		j_response = response.json()
		org_count = j_response['result']['organizations']['total']
		if org_count == 1:
			org =  j_response['result']['organizations']['entities'][0]
			ret = org
		else:
			eprint("Found {0} orgs on permid for lei {1}".format(org_count, lei))
	else:
		raise Exception("Invalid response from permid.org {0}".format(response))
	return ret


if len(sys.argv) < 2:
	print ('Get companies with LEIs from wikidata, match to orgs on permid.org')
	print ('Results are rendered in tab separated format, with PermIDs and WikiData')
	print ('subjects formatted for copy/paste into QuickStatements')
	print ('Reads a list of LEIs to exclude (e.g. no hits from permid.org) from stdin')
	print ('use an empty file to ignore this')
	print ()
	print ('Usage: python get_companies_with_leis.py <permid_token> <<ignore_leis> > <tsv_to_save>')
	sys.exit(1)


exclude_leis = []
for line in sys.stdin:
	exclude_leis.append('"'+line.strip()+'"')

access_token = sys.argv[1]
# Query wikidata for orgs that have an lei
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setQuery("""SELECT  ?item ?Legal_Entity_ID WHERE {
  ?item wdt:P31 wd:Q4830453.
  ?item wdt:P1278 ?Legal_Entity_ID.
  MINUS {?item wdt:P3347 ?permID}.
  FILTER (?Legal_Entity_ID NOT IN ("""+",".join(exclude_leis)
  +"""))}
  LIMIT 40
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()
count = 0
# for each lei, search permid.org by LEI for the organization
for result in results["results"]["bindings"]:
	lei = result["Legal_Entity_ID"]["value"]
	wikidata_uri = result["item"]["value"]
	found_org = search_permid_for_lei(access_token,lei)
	if found_org is None:
		eprint("No single match for org {0}, lei {1}".format(wikidata_uri,lei))
	else:
		org_name = found_org['organizationName']
		uri, separator, permid = found_org['@id'].rpartition('-')
		url, sep, code = wikidata_uri.rpartition('/')
		print("{0}\tP3347\t\"{1}\"\t{2}\t{3}\t{4}".format(code,permid, count,lei,org_name,))
	count = count + 1
	time.sleep(1)


