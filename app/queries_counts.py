import sqlite3
import datetime
import os


'''
settings
'''

#stats include start and end dates
start = '2016-04-01'    
#start = '2017-10-01'
end = '2019-06-01'

#query by day, week or month
query_type = 'month'

root = '//alleg/General/Public Relations/ONLINE/Passport/STATS/Referrals/'   


'''
other setup
'''

#query with dates and sort variables 
query_string = '''
    SELECT 
        strftime('{}', Dates.date) AS dates,
        SUM(Pages.pageviews) AS pageviews,
        SUM(Pages.page_value) AS donations
    FROM Pages	
    LEFT JOIN Dates ON Dates.seconds_id = Pages.date_seconds_id 
    WHERE Pages.date_seconds_id >= strftime('%s', '{}')
    AND Pages.date_seconds_id  <= strftime('%s', '{}')
    GROUP BY dates 
    ORDER BY dates;
    '''
    
#header for csv file, must match fields in query    
query_header = 'Date, Pageviews, Donations, Dollars per View'
    
def parse(rows, root, count=0):
    if count == 0: count = 10
    #print '\nDate\t\tViews\tDonate\tValue\n'
    for row in rows:        
        #if count == 0: break 
        #print row[0], '\t', row[1], '\t', int(row[2]), '\t' , '{0:.2f}'.format(row[2]/float(row[1]))
        count -= 1
    
    date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')    
    outputf = 'output/counts_{}.csv'.format(date)    
    text = '{}\n'.format(query_header)
    
    with open(os.path.join(root, outputf), 'w') as f:
        for row in rows:
            if not row[1]: break
            text +='{},{},{},{}\n'.format(row[0], row[1], int(row[2]), '{0:.2f}'.format(row[2]/float(row[1])))
        encoded_text = text.encode('utf-8')        
        f.write(encoded_text)

#connect to database
def db_conn():
    conn = sqlite3.connect('database/db.sqlite')
    cur = conn.cursor()   
    return conn, cur 
    
def run(start, end, root, query_type='month'):
    date_formats = {
    'day': '%Y-%m-%d',
    'week': '%Y-%W',
    'month': '%Y-%m'
    }
    
    #connect to database
    conn, cur = db_conn()
    
    print date_formats[query_type]
    print start
    print end
    
    #run query  
    query = query_string.format(date_formats[query_type], start, end)
    rows = cur.execute(query).fetchall()
    parse(rows, root)

    conn.close()

    
'''
run
'''

#stats include start and end dates
#query by day, week or month
run(start = start, 
    end = end, 
    root = root,
    query_type = query_type
   )