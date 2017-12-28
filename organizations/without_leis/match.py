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

def permid_match_api(access_token, payload):
	headers = {'X-AG-Access-Token' : access_token,
		'x-openmatch-dataType':'Organization',
		'Content-Type':'text/plain; charset=UTF-8',
		'x-openmatch-numberOfMatchesPerRecord': '1'}
	url = 'https://api.thomsonreuters.com/permid/match'
	ret = None
	try:
		#eprint('request')
		eprint(payload.encode('utf-8'))
		response = requests.post(url, data=payload.encode('utf-8'), headers=headers)
	except Exception  as e:
		eprint (u'Error in connect ' , e)
		return
	if response.status_code == 200:
		j_response = response.json()
		ret = j_response["outputContentResponse"]
	else:
		raise Exception("Invalid response from permid.org {0}".format(response))
	return ret


if len(sys.argv) < 2:
	print ('Get companies without LEIs from wikidata, match to orgs on permid.org')
	print ('Using the concordance API on permid.org')
	print ('Results are rendered in tab separated format, with PermIDs and WikiData')
	print ('subjects formatted for copy/paste into QuickStatements')
	print ()
	print ('Usage: python match.py <permid_token> > <tsv_to_save>')
	sys.exit(1)

access_token = sys.argv[1]
# Query wikidata for orgs that don't have permid or lei.
# Use an outer sort to handle orgs that have multiple headquarters
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setQuery("""SELECT ?item ?itemLabel ?country ?countryLabel ?url ?headquarters_location ?headquarters_locationLabel WHERE {
SELECT ?item ?itemLabel ?country ?countryLabel ?url ?headquarters_location ?headquarters_locationLabel WHERE {
  ?item wdt:P31 wd:Q4830453.
  MINUS { ?item wdt:P3347 ?permID. }
  OPTIONAL { ?item wdt:p856 ?url. }
  ?item wdt:P17 ?country.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
  ?item wdt:P159 ?headquarters_location.
}
LIMIT 20
}
ORDER BY ?item""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()
count = 0
str_list = []
str_list.append(u'LocalID,Name,Country,City,Website')
previous_org_code = ""
# for each lei, search permid.org by LEI for the organization
for result in results["results"]["bindings"]:
	url, sep, code = result["item"]["value"].rpartition('/')
	if previous_org_code == code:
		continue
	previous_org_code = code

	company_url = u""
	if result.has_key("url"):
		company_url = result["url"]["value"]

	str_list.append(u"{0},{1},\"{2}\",\"{3}\",{4}".format(code,
		result["itemLabel"]["value"],
		result["countryLabel"]["value"],
		result["headquarters_locationLabel"]["value"],
		company_url))
matches = permid_match_api(access_token,'\n'.join(str_list))
if matches is not None:
	for match in matches:
		if match["Match Level"] == "Excellent":
			url,sep, permID = match["Match OpenPermID"].rpartition('-')
			print(u"{0}\tP3347\t\"{1}\"\t{2}"
				.format(match["Input_LocalID"],permID,match["Match OrgName"]))
		else:
			eprint(u"No match for {0}, {1}"
				.format(match["Input_Name"],match["Input_LocalID"]))