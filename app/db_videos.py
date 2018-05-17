import sqlite3
import urllib2
from bs4 import BeautifulSoup
import time
from db_backup import database_backup, delete_old_backups


def scrape_page(video_id):
    url = 'https://video.klrn.org/video/%s/' % video_id
    
    try:
        conn = urllib2.urlopen(url)
        html = conn.read()   
    except:
        return None, None, None, None
        
    soup = BeautifulSoup(html, 'lxml')
    
    #get text from three elements, or return None when not available 
    title = soup.find('h1', class_='video-player__title')
    if title and title.string: title = ' '.join(title.string.split())
    
    content_channel = soup.select('p.over-title a')
    if content_channel and content_channel[0]: 
        content_channel = content_channel[0].text.strip() 
    else: content_channel = None    

    description = soup.select('p.video-player__details__description')
    if description and description[0]:
        description = description[0].text.strip()  
    else: description = None

    image = soup.select('div.modal-body__info img')
    if image and image[0]: 
        image = image[0]['src'].strip() 
    else: image = None    
 
    return title, content_channel, description, image

#connect to database
def db_conn():
    conn = sqlite3.connect('database/db.sqlite')
    cur = conn.cursor()
    
    #############################################
    #FOR TESTING ONLY
    #cur.execute('''
    #    UPDATE Videos
    #    SET title = NULL,
    #        content_channel = NULL,
    #        description = NULL,
    #        image = NULL,
    #        page_scraped = 0
    #    ''')
    #############################################    
    
    return conn, cur  
 
#update Videos 
def db_update(conn, cur, row):    
    print 'row[0]:', row[0] 
    title, content_channel, description, image = scrape_page(row[0])
    id = row[0]
    page_scraped = row[5] + 1
    print_data(id, title, content_channel, description, image, page_scraped)
    
    cur.execute('''
        UPDATE Videos
        SET title = ?,
            content_channel = ?,
            description = ?,
            image = ?,
            page_scraped = ?
        wHERE id = ?           
    ''',
    (title, content_channel, description, image, page_scraped, id))
   
    conn.commit()
    return title

def print_data(id, title, content_channel, description, image, page_scraped):
    print ''
    print 'ID:', id
    print 'TITLE:', title
    print 'CONTENT CHANNEL:', content_channel
    print 'DESCRIPTION:', description 
    print 'IMAGE:', image
    print 'PAGE SCRAPED:', page_scraped
    print ''

def run():
    #connect to database
    conn, cur = db_conn()
    
    #get Videos rows to be updated and make updates       
    rows = cur.execute('''SELECT * FROM Videos 
                          WHERE page_scraped < 3 
                          AND (title IS NULL OR content_channel IS NULL)''').fetchall()
    count = 0 
    count_titles = 0 
    for row in rows:    
        count += 1
        #if count > 3: break
        print '\nITEM', count, 'OUT OF', str(len(rows)) + ': with ID', row[0]
        title = db_update(conn, cur, row)
        if title: count_titles += 1
        time.sleep(2)
    
    print '\nDONE'
    print '\n', count_titles, 'TITLES OUT OF', len(rows), 'ITEMS'
    conn.close()  
    database_backup('database/db.sqlite', 'database/archive/', step='FULL')
    delete_old_backups('database/archive/')

run()  