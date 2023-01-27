import pandas as pd
import os
from simple_salesforce import Salesforce


def query_to_pandas(query):
    """
    This function takes in a 'query' from POH salesforce
    as input and returns a pandas dataframe as output.
    """
    results = sf.query_all(query)
    if results['records']:
        results = pd.DataFrame(
            results['records'], columns=results['records'][0].keys()).drop('attributes', axis=1)
        return results
    else:
        return pd.DataFrame()


# get credentials from github actions secrets
USERNAME = os.environ['SF_USERNAME']
PASSWORD = os.environ['SF_PASSWORD']
SECURITY_TOKEN = os.environ['SF_SECURITY_TOKEN']

# authenticate via salesforce
sf = Salesforce(username=USERNAME, password=PASSWORD,
                security_token=SECURITY_TOKEN)


# countries to get data from:
countries_included = ['United Kingdom']


dfs = []
for i,country in enumerate(countries_included):
  events_query = """
    SELECT Id, ActivityDate, AccountId, Contact__c, Contact_S2S_Levels__c, OwnerId, Owner__c
    FROM Event
    WHERE Account.Country__c = {} 
    AND  Account.Account_Record_Type_Name__c = 'Practice'
    AND Account.AccountStatus__c != 'Invalid'
    AND ActivityDate >= 2022-12-01 
    AND RecordTypeId = '0121t0000005w41AAA'
    """.format(f"'{country}'")
  df = query_to_pandas(events_query)
  if df.shape[0] != 0:
    dfs.append(df)
    print(f" Finished with country: {country}")
  else:
    print(f"Country: {country} has no data.")
    
events = pd.concat(dfs)
events = events.rename(columns={"Contact__c":"ContactId","Contact_S2S_Levels__c":"S2S"})
print(f"Max date found: {events.ActivityDate.max()}")
events.to_csv("events.csv")