## Using the script

This script is designed to work with [Quick Statements](https://tools.wmflabs.org/wikidata-todo/quick_statements.php). 

To use, run from the command line 
```shell
python match.py <Your PermID.org API key> 
```

The script will download 20 companies including website (if available), name, country and city without a PermID. 
These are then passed to the permid.org matching service. For each record returned, if the match is 'excellent' 
then a Quick Statements compatible statement is output to stdout. Non matches are output to stderr

For example:
```
Q2283	P3347	"4295907168"	Microsoft Corp
```

The first three columns can then be cut/paste into Quick Statements (note that copy/paste from console will likely drop the tab
characters that Quick Statements requires)

The remaining column (name) is for quality control.

O and multi matches are output to std err so you can redirect the script output to a file if you wish

