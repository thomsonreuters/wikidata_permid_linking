## Using the script

This script is designed to work with [Quick Statements](https://tools.wmflabs.org/wikidata-todo/quick_statements.php). To use, download the currencies file from permid.org and then run the convert shell script
```shell
./convert.sh OpenPermID-bulk-currency-20171217_070420.ntriples 
```

The script will download all currencies without PermIDs from wikidata, join them via ISO three digit currency code and put the resulting data in a file named `joined.tsv`.

This file is formatted so you can then directly cut and paste into Quick Statements. 

I ran the script and processed 209 currencies on December 27th 2017. So this will only need running again after some new currencies have been inserted into Wikidata (Open PermID currently has 267 so there's a few missing from WikiData)
