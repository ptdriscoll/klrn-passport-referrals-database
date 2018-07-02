# -*- coding: utf-8 -*-
"""
Created on Tue Jun 13 14:11:15 2017

@author: pdriscoll
"""

import sqlite3
import datetime
import os
import re
from graphs import pie_chart, timeline
import pandas as pd
from queries_views_episodes import run as episodes_run 

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

#stats include start and end dates 
#trends include start date BUT NOT end date     
start = '2018-06-25' 
end = '2018-07-02' 

#set query_type to either stats or trends
query_type = 'trends'

#if query_type is trends, set how many days to plot 
plot_days=8

#also get top show episodes (other queries run just top shows)   
run_episodes = True

root = '\\\\ALLEG\\General\\Public Relations\\ONLINE\\Passport\\STATS\\Referrals\\'


'''
other setup
'''

#query with dates and sort variables 
query_string = '''
    SELECT 
        LOWER(Videos.content_channel) AS channel,
        SUM(Pages.pageviews) AS pageviews,
        SUM(Pages.time_on_page) AS engagement,
        SUM(Pages.page_value) AS donations
    FROM Pages	
    INNER JOIN Referrers ON Pages.referrer_id = Referrers.id
    INNER JOIN Videos ON Referrers.video_id  = Videos.id  
    WHERE Pages.date_seconds_id >= strftime('%s', '{}')
    AND Pages.date_seconds_id  <= strftime('%s', '{}')
    GROUP BY channel 
    ORDER BY {} DESC;
    '''
    
#query for single content channel on single day 
query_string_day = '''
    SELECT 
        LOWER(Videos.content_channel) AS channel,
        SUM(Pages.pageviews) AS pageviews,
        SUM(Pages.time_on_page) AS engagement,
        SUM(Pages.page_value) AS donations
    FROM Pages	
    INNER JOIN Referrers ON Pages.referrer_id = Referrers.id
    INNER JOIN Videos ON Referrers.video_id = Videos.id  
    WHERE Pages.date_seconds_id = strftime('%s', '{}')
    AND channel = '{}'
    GROUP BY channel;
    '''    
    
#header for csv file, must match fields in query    
query_header = 'Content Channel, Pageviews, Time on Page, Donations, Dollars per View'
    
def capitalize(title):
    if title: 
        title = re.sub('(?:^| \W?)(\w)', lambda x: x.group(0).upper(), title)
    else: return title
    
    #make exception for NOVA
    title = title.replace('Nova', 'NOVA') 
    
    return title       

def get_stats(rows, root, count=10, print_stats=True):    
    cols = [] #to return for plot_daily
    print '\nViews\tEngage\tDonate\tValue\tTitle\n'
    for row in rows:        
        if count == 0: break 
        if not row[1]: break 
        if row[0]: 
            cols.append(row[0]) 
            title = capitalize(row[0])             
        print row[1], '\t', int(row[2]), '\t', int(row[3]), '\t', '{0:.2f}'.format(row[3]/float(row[1])), '\t', title
        count -= 1
    
    date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')  
    outputf = 'output/stats_{}.csv'.format(date)    
    text = '{}\n'.format(query_header)
    
    #save results
    if print_stats:
        with open(os.path.join(root, outputf), 'w') as f:
            for row in rows:
                if not row[1]: break
                if row[0]:
                    title = capitalize(row[0])
                    title = title.encode('utf-8') 
                else: title = ''    
                text +='{},{},{},{},{}\n'.format(title, row[1], int(row[2]), int(row[3]), '{0:.2f}'.format(row[3]/float(row[1])))
            f.write(text) 
        
    #plot results      
    inputf = os.path.join(root, outputf)    
    outputf = os.path.join(root, outputf.replace('csv', 'jpg'))
    title = 'Top Referral Channels'
    include_others = True
    
    if print_stats: 
        pie_chart(inputf, outputf, title, include_others) 

    #return list of shows and new outputf
    outputf = os.path.join(root, outputf.replace('stats_', 'trending_stats_'))
        
    return cols, outputf          

def get_trending(cur, root, end):
    #get date formats to compare past three days to three days before that
    format_s ='%Y-%m-%d'
    
    if end: first_day = datetime.datetime.strptime(end, '%Y-%m-%d').toordinal() 
    else: first_day = datetime.date.today().toordinal() 
    
    day_before = datetime.date.fromordinal(first_day-1).strftime(format_s)    
    three_days_ago = datetime.date.fromordinal(first_day-3).strftime(format_s) 
    four_days_ago = datetime.date.fromordinal(first_day-4).strftime(format_s) 
    six_days_ago = datetime.date.fromordinal(first_day-6).strftime(format_s)  

    track = {}
    query = query_string.format(three_days_ago, day_before, 'pageviews')
    rows = cur.execute(query).fetchall()
    for row in rows:        
        if row[0] > 1: 
            track[row[0]] = [row[1], 0]
    
    results = []
    query = query_string.format(six_days_ago, four_days_ago, 'pageviews')    
    rows = cur.execute(query).fetchall()   
    
    for row in rows:
        if row[0] in track:            
            if track[row[0]][0] >= row[1]: 
                track[row[0]][1] = row[1]
    
    results = []
    for k,v in track.iteritems():
        if v[0] > v[1]: 
            difference = v[0] - v[1] 
            results.append([k, v[0], v[1], difference])
    
    if len(results) == 0:
        print '\nNO TRENDING RESULTS'
        return
        
    results = sorted(results, key=lambda x: x[3], reverse=True) 
    date = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')    
    outputf = 'output/trending_{}.csv'.format(date)
    text = 'Content Channel,Views Last 3 Days,Views Last 4-6 Days,Differnece\n'
    
    #save results    
    with open(os.path.join(root, outputf), 'w') as f:
        count = 0
        print '\nOut 3\tOut 6\tDiff\tTitle\n'
        for row in results:
            count += 1
            title = capitalize(row[0])
            if count < 10:
                print str(row[1]),'\t',str(row[2]),'\t',str(row[3]),'\t',title
            title = title.encode('utf-8')
            text += '{},{},{},{}\n'.format(title, row[1], row[2], row[3]) 
        f.write(text) 
   
    #return a list of shows and new outputf
    shows = [] 
    for row in results:
        shows.append(row[0])
        
    outputf = os.path.join(root, outputf.replace('csv', 'jpg'))
        
    return shows, outputf    
        
#get daily results and plot as timeline        
def plot_daily(shows, outputf, cur, root, end, number_shows=5, number_days=7, title='Trending'):
    count = 0
    daily = {} #object to build df with
    cols = [] #trim shows and preserve order to use as df columns 
    
    if end: first_day = datetime.datetime.strptime(end, '%Y-%m-%d').toordinal() 
    else: first_day = datetime.date.today().toordinal()     

    for show in shows:
        count += 1
        if count > number_shows: break
        
        #print ''
        days = [] #store day labels for df index
        views = [] #store pageviews over six days  
        show = show.replace("'", "''") #add sql escape for single quote  
        for i in range(number_days, 0, -1):   
            day = datetime.date.fromordinal(first_day-i)
            days.append(day.strftime('%a'))
            query = query_string_day.format(day.strftime('%Y-%m-%d'), show) 
            #print 'CHECK',show
            row_day = cur.execute(query).fetchone()
            if row_day is None: views.append(0)                
            else: views.append(row_day[1])           
        
        daily[capitalize(show)] = views
        cols.append(capitalize(show))        

    df = pd.DataFrame(daily, index=days)  
    df = df[cols]  
    timeline(inputf=df, outputf=outputf, title_text=title+' Passport Referrals')    

#connect to database
def db_conn():
    conn = sqlite3.connect('database/db.sqlite')
    cur = conn.cursor()   
    return conn, cur

def run(start, end, root, query_type='stats', sort='pageviews', plot_days=7):
    #connect to database
    conn, cur = db_conn()
    
    #run query  
    if query_type == 'trends': 
        
        #get trending
        shows, outputf = get_trending(cur, root, end) 
        plot_daily(shows, outputf, cur, root, end, number_days=plot_days)
        
        #get most viewed
        query = query_string.format(start, end, sort)
        rows = cur.execute(query).fetchall()
        shows, outputf = get_stats(rows, root, print_stats=False)
        if len(shows) > 0:
            plot_daily(shows, outputf, cur, root, end, title='Top', number_days=plot_days)
        else: print 'NO TOP SHOWS IN DATE RANGE'
        
    else: 
        query = query_string.format(start, end, sort)
        rows = cur.execute(query).fetchall()
        get_stats(rows, root)

    conn.close()  


'''
run
'''

#stats include start and end dates 
#trends include start date BUT NOT end date 
#set query_type to either stats or trends    
run(start=start, 
    end=end, 
    root=root,
    query_type=query_type,
    plot_days=plot_days
   )

if run_episodes:
    episodes_run(start=start, end=end, root=root)