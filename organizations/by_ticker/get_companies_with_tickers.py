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

def search_permid_for_ticker(access_token, ric):
	headers = {'X-AG-Access-Token' : access_token}
	url = 'https://api.thomsonreuters.com/permid/search?q=ric:'+ric+'&entitytype=organization'
	ret = None
	try:
		response = requests.get(url, headers=headers)
	except Exception  as e:
		print ('Error in connect ' , e)
		return
	if response.status_code == 200:
		j_response = response.json()
		org_count = j_response['result']['organizations']['total']
		if org_count > 0:
			orgs =  j_response['result']['organizations']['entities']
			ret = orgs 
		else:
			eprint(u"Found {0} orgs on permid for ric {1}".format(org_count, ric))
	else:
		raise Exception(u"Invalid response from permid.org {0}".format(response))
	return ret

def wikidata_exchange_for_ric(ric_terminator):
	if ric_terminator == 'N': #NYSE
		return 'Q13677'
	elif ric_terminator == 'O': #LSE
		return 'Q171240'
	elif ric_terminator == 'V': #Canadian Venture Exchange
		return 'Q7671764'
	elif ric_terminator == 'MI': #Milan Stock Exchange
		return 'Q936563'
	elif ric_terminator == 'T': #Tokyo Stock Exchange
		return 'Q217475'
	else:
		eprint('Exchange '+ric_terminator+' not found')
	


if len(sys.argv) < 3:
	print ('Get companies with tickers from wikidata, match to orgs on permid.org')
	print ('Results are rendered in tab separated format, with PermIDs and WikiData')
	print ('subjects formatted for copy/paste into QuickStatements')
	print ()
	print ('Usage: python get_companies_with_tickers.py <permid_token> <exchange_code> > <tsv_to_save>')
	sys.exit(1)


access_token = sys.argv[1]
exchange_code = sys.argv[2]
# from https://stackoverflow.com/questions/4545661/unicodedecodeerror-when-redirecting-to-file
# Wrap sys.stdout into a StreamWriter to allow writing unicode.
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout) 
# Query wikidata for orgs that have an lei
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
query = """SELECT ?item ?itemLabel ?statement ?ticker WHERE {
	?item p:P414 ?statement.
	?statement pq:P249 ?ticker. 
	?statement ps:P414 wd:"""+wikidata_exchange_for_ric(exchange_code)+""" .
	SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" . } 
	MINUS { ?item wdt:P3347 ?PermID. } 
	} 
	LIMIT 40"""
eprint(query)
sparql.setQuery(query)

sparql.setReturnFormat(JSON)
results = sparql.query().convert()
count = 0
# for each ticker, search permid.org by tickerfor the organization
for result in results["results"]["bindings"]:
	ticker = result["ticker"]["value"]
	wikidata_uri = result["item"]["value"]
	wikidata_company = result["itemLabel"]["value"]
	ric = ticker+'.'+exchange_code
	found_orgs = search_permid_for_ticker(access_token,ric)
	if found_orgs is None:
		eprint(u"No match for org {0}, ric {1}".format(wikidata_uri,ric))
	else:
		for org in found_orgs:
			org_name = org['organizationName']
			uri, separator, permid = org['@id'].rpartition('-')
			url, sep, code = wikidata_uri.rpartition('/')
			print(u"{0}\tP3347\t\"{1}\"\t{2}\t{3}\t{4}={5}".format(code, permid, count, ric, wikidata_company, org_name))
	count = count + 1
	time.sleep(1)


