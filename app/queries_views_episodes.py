# -*- coding: utf-8 -*-
"""
Created on Mon Apr 30 14:11:15 2010

@author: pdriscoll
"""

import sqlite3
import datetime
import os
import re


#set default coding to utf8 and fix where output is directed 
#https://stackoverflow.com/questions/25494182/print-not-showing-in-ipython-notebook-python
import sys
stdout = sys.stdout
reload(sys)  
sys.setdefaultencoding('utf8')
sys.stdout = stdout


'''
settings
'''

#stats DO NOT include end date     
start = '2018-04-23' 
end = '2018-04-30'

root = '\\\\ALLEG\\General\\Public Relations\\ONLINE\\Passport\\STATS\\Referrals\\'


'''
other setup
'''

#query with dates and sort variables 
query_string = '''
    SELECT 
      LOWER(Videos.content_channel),
      LOWER(Videos.title),
      SUM(Pages.pageviews) AS total_views,
      SUM(Pages.page_value) AS donations
    FROM Pages	
    INNER JOIN Referrers ON Pages.referrer_id = Referrers.id
    INNER JOIN Videos ON Referrers.video_id = Videos.id  
    WHERE Pages.date_seconds_id >= strftime('%s', '{}')
    AND Pages.date_seconds_id < strftime('%s', '{}')
    GROUP BY Videos.content_channel, Videos.title 
    ORDER BY {} DESC;
    '''
    
#header for csv file, must match fields in query    
query_header = 'Show,Episode,Referrals,Donations'
    
def capitalize(title):
    if title: 
        title = re.sub('(?:^| \W?)(\w)', lambda x: x.group(0).upper(), title)
    else: return title
    
    #make exception for NOVA
    title = title.replace('Nova', 'NOVA') 
    
    return title       

def get_stats(rows, root, start, end, count=10, print_stats=True):    
    text = '{}\n'.format(query_header)
    if print_stats: 
        print '\n\nTop Episodes from ' + start + ' to just before ' + end + '\n\nRefs\tUSD\tEpisode\n'    
    for row in rows:  
        if row[0] == None or row[1] == None: continue    
        show = capitalize(row[0])   
        episode = '"' + capitalize(row[1]).replace('"', '""') + '"'
        referrals = int(row[2])
        donations = '$' + str(int(row[3])) if int(row[3] > 0) else '0' 
        text += '{},{},{},{}\n'.format(show, episode, referrals, donations)          
        if print_stats and count > 0: print referrals, '\t', donations, '\t', show + '  ##  ' + episode
        count -= 1
    
    date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  
    outputf = 'output/episodes_{}.csv'.format(date)   
    
    #save results
    with open(os.path.join(root, outputf), 'w') as f:
        f.write(text) 

#connect to database
def db_conn():
    conn = sqlite3.connect('database/db.sqlite')
    cur = conn.cursor()   
    return conn, cur

def run(start, end, root, sort='total_views'):
    #connect to database
    conn, cur = db_conn()
    
    #run query  
    query = query_string.format(start, end, sort)
    rows = cur.execute(query).fetchall()
    get_stats(rows, root, start, end)

    conn.close()  

'''
run
'''

#stats DO NOT include end date 
if __name__ == '__main__':    
    run(start=start, end=end, root=root)