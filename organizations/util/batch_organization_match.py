#bulk matching script 2018-01-16
#-Last updated by Dan Meisner - daniel.meisner@thomsonreuters.com
#Utilizes the PermID.org Matching API to break a large file (up tp 5M records) into manageable chunks,
#call the api, and reassemble the aggregate results to an output CSV

import requests
import pandas as pd
import json
import numpy as np
	
def batch_organization_match(access_token, input_df, batch_size=1000, retry_attempts=0, batch_override=None):
	"""Utilize the PermID.org Matching API with large sets of Organization records.
	Args:
		access_token: your API token for PermID.org
		input_df: Dataframe containing records to be matched with headers: ['LocalID','Standard Identifier','Name','Country','Street','City','PostalCode','State','Website']
		batch_size: Target batch size sent to API.  Default == 1000
		retry_attempts: Number of attempts to retry failed batches.  Default = 0
		batch_override: Used with recursive calls of this function to retry failed batches.  You probably shouldn't use this.
	
	Returns:
		DataFrame containing aggregated match output
		
	Raises:
		TypeError
	"""

	#make sure that input_df is a valid DataFrame
	if not type(input_df) is pd.DataFrame:
		raise TypeError("input_df must be a valid pandas DataFrame")
	
	#build request headers
	headers = {'X-AG-Access-Token' : access_token,
			   'x-openmatch-dataType' : 'Organization'}

	#prep failed batches list
	failed = []

	out = pd.DataFrame()
	
	#build batch list or use batch_override
	if batch_override is None:
		batches = range(0,int(np.ceil(len(input_df.index)/batch_size + 1)))
	else:
		batches =  batch_override
	
	#send batches to match API
	for i in batches:  
		start, end = i*batch_size, (i+1)*batch_size
		if end > len(input_df.index): 
			end = len(input_df.index)
		input_df[start:end].to_csv('tmp.csv', index=False)
		files = {'file': open('tmp.csv')}
		p = requests.post('https://api.thomsonreuters.com/permid/match/file', headers=headers, files=files)
		
		#get df from response
		try:
			df = pd.read_json(json.dumps(p.json(strict=False)['outputContentResponse']).replace("\\r", ""))
			out = out.append(df)
		except:
			print p.content
			failed.append(i)
		print(i)
	
	#handle failed batches
	if retry_attempts > 0 and len(failed) > 0:
		print "retrying failed batches"
		out.append(batch_organization_match(access_token, input_df, batch_size, retry_attempts - 1, batch_override = failed))
		return out
	elif len(failed) > 0:
		print "Maximum  retry attempts reached.  Some batches did not complete successfully"
		return out
	else:
		return out