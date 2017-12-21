#pip install sparqlwrapper
#https://rdflib.github.io/sparqlwrapper/

from SPARQLWrapper import SPARQLWrapper, JSON
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
sparql.setQuery("""SELECT ?item ?name ?iso_code WHERE {
  ?item wdt:P31 wd:Q8142.
  ?item rdfs:label ?name.
  ?item wdt:P498 ?iso_code
  FILTER (lang(?name) = 'en')

}""")
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

for result in results["results"]["bindings"]:
    uri = result['item']['value']
    iso_code = result['iso_code']['value']
    print("{0},{1}".format(iso_code, uri))


