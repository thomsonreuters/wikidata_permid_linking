## Using this script

Some wikidata entries have a ticker attached to them. Since permid.org has a much wider coverage for tickers, just searching 
for the ticker will result in multiple matches.

However, if we can quantify which exchange the ticker is on, we can convert the ticker to a [Reuters Instrument Code](https://en.wikipedia.org/wiki/Reuters_Instrument_Code) and search for that which _should be_ unique.

This script queries for 40 organizations at a time from Wikidata that have no permid but do have a ticker. 

The script takes two command line parameters:
- PermID.org API key
- Exchange to search. This is the code following the period in a RIC (for instance 'N' is NYSE). 

The code will be converted to the appropriate WikiData entry for the exchange (for instance, NYSE = Q13677)

This script is designed to work with [Quick Statements](https://tools.wmflabs.org/wikidata-todo/quick_statements.php).

To use, run from the command line. You might want to redirect std out to a file:
```shell
python get_companies_with_tickers.py <Your API key> N > mapped.tsv
```

Each match is written to std out, the misses are written to stderr:
 
```
Q871700	P3347	"4295905139"	33	UAL.N	United Continental Holdings=United Continental Holdings Inc
```

The first three columns can then be cut/paste into Quick Statements (note that copy/paste from console will likely drop the tab
characters that Quick Statements requires)

The other three columns are for quality control:
- index of found company
- RIC 
- Company Name (from both sources)

O and multi matches are output to std err so you can redirect the script output to a file if you wish

