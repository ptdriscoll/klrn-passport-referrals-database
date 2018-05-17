#adapted from
#https://developers.google.com/analytics/devguides/reporting/core/v4/quickstart/installed-py

import argparse
from apiclient.discovery import build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from auth.settings import view_id 

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = ('https://analyticsreporting.googleapis.com/$discovery/rest')
CLIENT_SECRETS_PATH = 'auth/client_secrets.json' # path to client_secrets.json file.
VIEW_ID = view_id


def initialize_analyticsreporting():
  """Initializes the analyticsreporting service object.

  Returns:
    analytics an authorized analyticsreporting service object.
  """
  # Parse command-line arguments.
  parser = argparse.ArgumentParser(
      formatter_class=argparse.RawDescriptionHelpFormatter,
      parents=[tools.argparser])
  flags = parser.parse_args([])

  # Set up a Flow object to be used if we need to authenticate.
  flow = client.flow_from_clientsecrets(
      CLIENT_SECRETS_PATH, scope=SCOPES,
      message=tools.message_if_missing(CLIENT_SECRETS_PATH))

  # Prepare credentials, and authorize HTTP object with them.
  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to a file.
  storage = file.Storage('auth/analyticsreporting.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = tools.run_flow(flow, storage, flags)
  http = credentials.authorize(http=httplib2.Http())

  # Build the service object.
  analytics = build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)

  return analytics

def get_report(analytics, day):
  # Use the Analytics Service Object to query the Analytics Reporting API V4.
  return analytics.reports().batchGet(
      body={
        'reportRequests': [{
          'viewId': VIEW_ID,
          'dateRanges': [
            {'startDate': day, 'endDate': day}
          ],
          'metrics': [
            {'expression': 'ga:pageviews'},
            {'expression': 'ga:uniquePageviews'},
            {'expression': 'ga:timeOnPage'},
            {'expression': 'ga:bounces'},
            {'expression': 'ga:entrances'},
            {'expression': 'ga:exits'},
            {'expression': 'ga:pageValue'},
          ],
          'dimensions': [{'name': 'ga:pagePath'}],
          'dimensionFilterClauses': [{
            'filters': [{
                'dimensionName': 'ga:pagePath',
                'operator': 'REGEXP',
                'expressions': ['[\?&]referrer=']
            }]
          }],
          'orderBys': [
            {'fieldName': 'ga:pageviews', 'sortOrder': 'DESCENDING'}
          ]              
        }]
      }
  ).execute()

def parse_response(response):
  """Parses and prints the Analytics Reporting API V4 response"""
  data = []
      
  for report in response.get('reports', []):
    columnHeader = report.get('columnHeader', {})
    dimensionHeaders = columnHeader.get('dimensions', [])
    metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
    rows = report.get('data', {}).get('rows', [])
    
    row_count = 0 
    for row in rows:
      #print '\n\n', 'ROW_COUNT: ', row_count, '\n'
      data.append({})    

      dimensions = row.get('dimensions', [])
      dateRangeValues = row.get('metrics', [])

      for header, dimension in zip(dimensionHeaders, dimensions):
        #print header + ': ' + dimension
        data[row_count][header[3:]] = dimension
        
      for i, values in enumerate(dateRangeValues):
        #print 'Date range (' + str(i) + ')'
        for metricHeader, value in zip(metricHeaders, values.get('values')):
          #print metricHeader.get('name') + ': ' + value
          data[row_count][metricHeader.get('name')[3:]] = value
          
      row_count += 1 
      
  return data    

def run(day=None):
  #if day == None: day = '2017-04-23'  
  analytics = initialize_analyticsreporting()
  response = get_report(analytics, day)
  #parse_response(response)
  return response

if __name__ == '__main__':
  run()