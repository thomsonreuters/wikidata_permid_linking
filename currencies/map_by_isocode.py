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

# This will need:
# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

from SPARQLWrapper import SPARQLWrapper, JSON
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setQuery("""SELECT ?item ?name ?iso_code WHERE {
  ?item wdt:P31 wd:Q8142.
  ?item rdfs:label ?name.
  ?item wdt:P498 ?iso_code
  MINUS {?item wdt:P3347 ?permID}
  FILTER (lang(?name) = 'en')

}""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    uri = result['item']['value']
    url, sep, code = uri.rpartition('/')
    iso_code = result['iso_code']['value']
    print("{0}\t{1}\tP3347".format(iso_code, code))


