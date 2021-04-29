# -*- coding: utf-8 -*-

import sqlite3
import urllib2
from bs4 import BeautifulSoup
from urlparse import urlparse
import time
from db_backup import database_backup

import scrapers 
from scrapers_selenium import iframe_partnerPlayer_id


def get_video_id(referrer):
    if ('pbs.org/video/' in referrer 
        or 'video.klrn.org/video/' in referrer 
        or 'player.pbs.org/widget/' in referrer
        or 'player.pbs.org/stationplayer/' in referrer
        or 'player.pbs.org/portalplayer/' in referrer): 
        parts = urlparse(referrer).path.split('/')   
        for part in reversed(parts):
            if part: return part    
    return None  

def scrape_page(url, video_id):
    #make sure video_id can be converted to an integer
    if video_id: 
        video_id = video_id if video_id.isdigit() else None
    else: video_id = None 
    
    #fix a borken url
    if url.startswith('pbsvideo://'): url = url.replace('pbsvideo://', 'http://')
    
    #connect to page
    try:
        conn = urllib2.urlopen(url)
        html = conn.read()    
    except:
        return None, video_id
        
    soup = BeautifulSoup(html, 'lxml')
    
    title = soup.title
    if title and title.string: title = ' '.join(title.string.split())        
    if video_id: return title, video_id    
    
    #if no video_id, loop through imported scrapers to look for it 
    for key, val in scrapers.__dict__.iteritems():
        if video_id: break
        if callable(val):            
            video_id = val(soup)   
            
            #again, make sure video_id can be converted to an integer
            if video_id: 
                video_id = video_id if video_id.isdigit() else None
    
    conn.close()    
       
    #if still no video_id, try to get it through embedded iframe using selenium
    if not video_id: video_id = iframe_partnerPlayer_id(url)  
        
    return title, video_id  
  
def get_title_videoID(url):    
    video_id = get_video_id(url)
    return scrape_page(url, video_id)

#connect to database
def db_conn():
    conn = sqlite3.connect('database/db.sqlite')
    cur = conn.cursor()
    
    #############################################
    #FOR TESTING ONLY
    #cur.execute('''
    #    UPDATE Referrers
    #    SET video_id = NULL,
    #        title = NULL,
    #        page_scraped = 0
    #    ''')
    
    #ALSO FOR TESTING ONLY     
    #cur.execute('DROP TABLE IF EXISTS Videos') 
    #############################################

    cur.execute('''
        CREATE TABLE IF NOT EXISTS Videos
        (
        id INTEGER PRIMARY KEY,	
        title TEXT,	
        content_channel TEXT,	
        description TEXT,
        image TEXT,
        page_scraped INTEGER
        ) 
    ''')
     
    return conn, cur   

#insert row to Videos
def db_insert(conn, cur, id):
    cur.execute('''
    INSERT OR IGNORE INTO Videos 
    (id, title, content_channel, description, image, page_scraped) 
    VALUES (?, ?, ?, ?, ?, ?)''', 
    (id, None, None, None, None, 0))
    
    conn.commit()

def print_data(id, referrer, video_id, title, page_scraped):
    print ''
    print 'VIDEO ID', video_id 
    print 'ID:', id
    print 'REFERRER:', referrer
    print 'TITLE:', title
    print 'PAGE SCRAPED:', page_scraped
    print ''
    
#update Referrers 
def db_update(conn, cur, row):

    #prep data
    id = row[0]
    referrer = row[1]
    title, video_id = get_title_videoID(referrer)
    if video_id: video_id = int(video_id) if video_id.isdigit() else None
    page_scraped = row[4] + 1    

    cur.execute('''
        UPDATE Referrers
        SET video_id = ?,
            title = ?,
            page_scraped = ?
        wHERE id = ?           
    ''',
    (video_id, title, page_scraped, id))    

    conn.commit()
    print_data(id, referrer, video_id, title, page_scraped) 
    return video_id

def run():
    #connect to database
    conn, cur = db_conn()
    
    #get Referrers rows to be updated, make updates, and insert video_ids into Videos      
    rows = cur.execute('''SELECT * FROM Referrers 
                          WHERE page_scraped < 3 
                          AND video_id IS NULL''').fetchall()
    count = 0 
    count_video_ids = 0     
    for row in rows:    
        count += 1
        #if count > 3: break 
        print '\nITEM', count, 'OUT OF', len(rows)
        video_id = db_update(conn, cur, row)
        if video_id: 
            db_insert(conn, cur, video_id)
            count_video_ids += 1
        time.sleep(2)
    
    print '\nDONE'
    print '\n', count_video_ids, 'VIDEO IDS OUT OF', len(rows), 'ITEMS'
    conn.close()   
    database_backup('database/db.sqlite', 'database/archive/', step='REFERRERS')

run()




