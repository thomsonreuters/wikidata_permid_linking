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
import locale
import codecs
import requests
import time
from SPARQLWrapper import SPARQLWrapper, JSON

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def search_by_company_name(access_token, name):
	headers = {'X-AG-Access-Token' : access_token}
	url = 'https://api.thomsonreuters.com/permid/search?q='+name+'&entitytype=organization'
	ret = None
	try:
		response = requests.get(url, headers=headers)
	except Exception as e:
		print ('Error in connect ' , e)
		return
	if response.status_code == 200:
		j_response = response.json()
		org_count = j_response['result']['organizations']['total']
		if org_count > 0:
			orgs =  j_response['result']['organizations']['entities']
			ret = orgs
	else:
		raise Exception(u"Invalid response from permid.org {0}".format(response))
	return ret

def permid_match_api(access_token, payload):
	headers = {'X-AG-Access-Token' : access_token,
		'x-openmatch-dataType':'Organization',
		'Content-Type':'text/plain; charset=UTF-8',
		'x-openmatch-numberOfMatchesPerRecord': '1'}
	url = 'https://api.thomsonreuters.com/permid/match'
	ret = None
	try:
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

# from https://stackoverflow.com/questions/4545661/unicodedecodeerror-when-redirecting-to-file
# Wrap sys.stdout into a StreamWriter to allow writing unicode.
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

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
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en,de". }
  ?item wdt:P159 ?headquarters_location.
}
LIMIT 50
}
ORDER BY ?itemLabel""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()
count = 0

str_list = []
str_list.append(u'LocalID,Name,Country,City,Website')
previous_org_code = ""

for result in results["results"]["bindings"]:
	url, sep, code = result["item"]["value"].rpartition('/')
	if previous_org_code == code:
		continue
	previous_org_code = code

	company_url = u""
	if result.has_key("url"):
		company_url = result["url"]["value"]
	str_list.append(u"{0},\"{1}\",\"{2}\",\"{3}\",{4}".format(code,
		result["itemLabel"]["value"],
		result["countryLabel"]["value"],
		result["headquarters_locationLabel"]["value"],
		company_url))
matches = permid_match_api(access_token,'\n'.join(str_list))
if matches is not None:
	for match in matches:
		if match["Match Level"] == "Excellent":
			url,sep, permID = match["Match OpenPermID"].rpartition('-')
			print(u"{0}\tP3347\t\"{1}\"\t{2}={3}"
				.format(match["Input_LocalID"],permID,match["Input_Name"],match["Match OrgName"]))
		else:
			eprint(u"No match for {0}, '{1}', trying search by name"
				.format(match["Input_Name"],match["Input_LocalID"]))
			found_orgs = search_by_company_name(access_token,match["Input_Name"])
			time.sleep(.5)
			if found_orgs is None:
				eprint(u"No search match for org {0}".format(match["Input_Name"]))
			else:
				for org in found_orgs:
					eprint(org)
					org_name = org['organizationName']
					uri, separator, permid = org['@id'].rpartition('-')
					print(u"{0}\tP3347\t\"{1}\"\t{2}\t{3}={4}"
					.format(match["Input_LocalID"],permid,count,match["Input_Name"],			org_name))
		count = count + 1
