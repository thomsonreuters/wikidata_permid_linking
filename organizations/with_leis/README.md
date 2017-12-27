## Using the script

This script is designed to work with [Quick Statements](https://tools.wmflabs.org/wikidata-todo/quick_statements.php). 

To use, run from the command line 
```shell
python get_companies_with_leis.py <Your PermID.org API key> 
```

The script will download 20 companies with LEIs but without PermIDs from WikiData. For each company, it will then attempt to 
search permid.org for the matching company. If a unique match is found, the resulting match is output as tab separated values. 
For example:
```
Q1446709	P3347	"4296590069"	2	V22E9B3P7BX1W5NNT053	Crown Equipment Corp
```

The first three columns can then be cut/paste into Quick Statements (note that copy/paste from console will likely drop the tab
characters that Quick Statements requires)

The other three columns are for quality control:
- index of found company
- LEI
- Company Name (from permid.org)

O and multi matches are output to std err so you can redirect the script output to a file if you wish

