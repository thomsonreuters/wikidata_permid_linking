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

exchange_mappings = {'BX':'Q1003245', #Bucharest Stock Exchange
'CO':'Q1019983', #OMX Nordic Exchange Copenhagen A/S
'ST':'Q1019992', #OMX Nordic Exchange Stockholm AB - cash
'BR':'Q1146518', #Euronext Brussels
'NG':'Q1188840', #Nagoya Stock Exchange
'BK':'Q1330208', #The Stock Exchange of Thailand
'N':'Q13677', #New York Stock Exchange
'ZA':'Q140388', #Zagreb Stock Exchange
'IS':'Q1407995', #BORSA ISTANBUL
'I':'Q144458', #The Irish Stock Exchange
'TA':'Q1507974', #Tel Aviv Stock Exchange
'F':'Q151139', #Frankfurt Stock Exchange
'SI':'Q1515558', #Singapore Exchange Securities Trading Ltd
'GH':'Q1521374', #Ghana Stock Exchange
'PS':'Q1526647', #Philippine Stock Exchange, Inc
'JK':'Q1661737', #Indonesia Stock Exchange (formerly Jakarta SE)
'L':'Q171240', #London Stock Exchange
'T':'Q217475', #Tokyo Stock Exchange
'LM':'Q2380045', #Bolsa de Valores de Lima S.A.
'PA':'Q2385849', #Euronext Paris
'PAp':'Q2385849', #Euronext Paris
'LS':'Q2415561', #Euronext Lisbon
'MM':'Q2632892', #Moscow Interbank Currency Exchange (MICEX)
'CY':'Q2888321', #Cyprus Stock Exchange
'KL':'Q43335', #Bursa Malaysia
'KQ':'Q491503', #Korea Exchange - KOSDAQ
'KS':'Q495372', #Korea Exchange - KSE
'HE':'Q581755', #OMX Nordic Exchange Helsinki Oy
'WA':'Q59551', #Warsaw Stock Exchange
'NZ':'Q627019', #New Zealand Stock Exchange
'J':'Q627514', #Johannesburg Stock Exchange
'NS':'Q638740', #National Stock Exchange of India Limited
'S':'Q661834', #SIX Swiss Exchange
'SH':'Q739514', #Shanghai Stock Exchange
'BV':'Q74603', #Bratislava Stock Exchange
'LU':'Q74662', #Luxembourg Stock Exchange
'AT':'Q755341', #Athens Stock Exchange
'SA':'Q796297', #BM&F Bovespa SA Bolsa de Valores Mercadorias e Futuros
'TO':'Q818723', #The Toronto Stock Exchange
'OQ':'Q82059', #NASDAQ Stock Exchange Global Market
'AS':'Q842108', #Euronext Amsterdam
'BU':'Q851259', #Budapest Stock Exchange
'MX':'Q891559', #Bolsa Mexicana de Valores S.A. de C.V.
'BA':'Q891560', #Bolsa de Comercio de Buenos Aires
'SN':'Q891561', #Bolsa de Comercio de Santiago
'OL':'Q909158' #Oslo Stock Exchange
}

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def search_permid_for_ticker(access_token, code, by_ric):
	headers = {'X-AG-Access-Token' : access_token}
	if by_ric:
		url = 'https://api.thomsonreuters.com/permid/search?q=ric:'+code+'&entitytype=organization'
	else:
		url = 'https://api.thomsonreuters.com/permid/search?q=ticker:'+code+'&entitytype=organization'

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
			eprint(u"Found {0} orgs on permid for code {1}".format(org_count, code))
	else:
		raise Exception(u"Invalid response from permid.org {0}".format(response))
	return ret

def wikidata_exchange_for_ric(ric_terminator):
	if ric_terminator in exchange_mappings:
		return exchange_mappings[ric_terminator]
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
	found_orgs = search_permid_for_ticker(access_token,ric, True)
	if found_orgs is None:
		eprint(u"No match for org {0}, ric '{1}', trying by ticker".format(wikidata_uri,ric))
		found_orgs = search_permid_for_ticker(access_token,ticker, False)
	if found_orgs is None:
		eprint(u"No match for org {0}, ticker '{1}'".format(wikidata_uri,ticker))
	else:
		for org in found_orgs:
			org_name = org['organizationName']
			uri, separator, permid = org['@id'].rpartition('-')
			url, sep, code = wikidata_uri.rpartition('/')
			print(u"{0}\tP3347\t\"{1}\"\t{2}\t{3}\t{4}={5}".format(code, permid, count, ric, wikidata_company, org_name))
	count = count + 1
	time.sleep(1)


