import datetime
import sqlite3
import analytics
from db_backup import database_backup


#create list of dates to run through analytics api call
def get_dates(last_date):
    start = datetime.datetime.utcfromtimestamp(last_date).toordinal() + 1
    end = datetime.date.today().toordinal()
    
    #############################################
    #FOR TESTING ONLY
    #start = datetime.date.today().toordinal() - 5
    #end = datetime.date.today().toordinal() -3    
    #############################################    
    
    dates = [datetime.date.fromordinal(x) for x in range(start, end+1)] 
    
    print '\nDATES TO CHECK:\n\n', dates    
    #return []    
    
    return  dates

#call google analytics api v4, and parse response  
def get_data(date):        
    #api call
    response = analytics.run(date.strftime('%Y-%m-%d'))
    
    #save json for review
    #with open('response.json', 'w') as f:
    #    f.write(json.dumps(response, indent=2))
    
    #parse response
    data = analytics.parse_response(response)        
    
    return data

#for checking parsed response data
def check_data(date, data):
    row_count = 0 
    for row in data:
        print '\n\n', 'ROW_COUNT: ', row_count
        print date, '\n'
        for key, value in row.iteritems():
            print key, ': ', value
        row_count += 1

#checker for safe float conversions        
def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

#oonvert python datetime.date(2017, 5, 11) object to unix seconds integer
def datetime_to_seconds(date): 
    unix = datetime.date(1970, 1, 1)
    return int((date - unix).total_seconds())

#connect to database
def db_conn():
    conn = sqlite3.connect('database/db.sqlite')
    conn.execute('PRAGMA foreign_keys = ON')
    cur = conn.cursor()
    
    #############################################
    #FOR TESTING ONLY
    #cur.execute('DROP TABLE IF EXISTS Pages')
    #cur.execute('DROP TABLE IF EXISTS Dates')    
    #cur.execute('DROP TABLE IF EXISTS Referrers')
    #############################################
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Pages
        (
        id INTEGER PRIMARY KEY,
        page TEXT,
        date_seconds_id INTEGER, 
        referrer_id INTEGER,
        pageviews INTEGER,
        unique_pageviews INTEGER, 
        time_on_page REAL, 
        bounces INTEGER,
        entrances INTEGER, 
        exits INTEGER, 
        page_value REAL,
        FOREIGN KEY(date_seconds_id) REFERENCES Dates(seconds_id) 
        FOREIGN KEY(referrer_id) REFERENCES Referrers(id) 
        )
    ''')  
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Dates
        (
        seconds_id INTEGER PRIMARY KEY,
        date TEXT,
        temp INTEGER
        )    
    ''')
     
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Referrers
        (
        id INTEGER PRIMARY KEY,
        referrer TEXT NOT NULL UNIQUE,
        video_id INTEGER, 
        title TEXT,
        page_scraped INTEGER
        )  
    ''')     

    #default starting date, which is a date in utc seconds
    #this is set to day before KLRN Passport started
    last_date = datetime_to_seconds(datetime.date(2016, 4, 3))     

    #get most recent id and date from database where temp is false
    cur.execute('SELECT MAX(seconds_id), date, seconds_id FROM Dates WHERE temp=0')
    
    try:
        row = cur.fetchone()
        print '\n\nMOST RECENT ID:', row[0]
        print 'MOST RECENT DATE:', row[1]
        
        if row[0] is not None: 
            last_date = row[2]
            
    except:
        print 'NO DATA:', row   
     
    return conn, cur, last_date    

#insert row to database
def db_insert(conn, cur, date, row):
    
    #prep data        
    page = row['pagePath'] if len(row['pagePath']) > 1 else None
    page_url_clean = page.replace('referrer=pbsvideo://video.pbs.org/', 'referrer=http://video.pbs.org/')
    referrer = page_url_clean.split('referrer=')[1] if 'referrer=' in page_url_clean else None
    date_seconds = datetime_to_seconds(date)
    temp = 0 if date.toordinal() < datetime.date.today().toordinal() - 1 else 1
    pageviews = int(row['pageviews']) if row['pageviews'].isdigit() else None
    unique_pageviews = int(row['uniquePageviews']) if row['uniquePageviews'].isdigit() else None
    time_on_page = float(row['timeOnPage']) if is_float(row['timeOnPage']) else None
    bounces  = int(row['bounces']) if row['bounces'].isdigit() else None
    entrances  = int(row['entrances']) if row['entrances'].isdigit() else None
    exits = int(row['exits']) if row['exits'].isdigit() else None
    page_value  = float(row['pageValue']) if is_float(row['pageValue']) else None    
  
    #first add data to Referrers table to get foreign key reference for Pages table 
    cur.execute('''
        INSERT OR IGNORE INTO Referrers 
        (referrer, video_id, title, page_scraped) 
        VALUES (?, ?, ?, ?)''', 
        (referrer, None, None, 0))    
  
    #commit to Referrers table
    conn.commit()
    
    #now get referrer_id as foreign key for Pages table
    cur.execute('SELECT id FROM Referrers WHERE referrer=?', (referrer,))
    referrer_id = cur.fetchone()[0]
    
    #add date info to Dates table, replace rows where temp previously was true     
    cur.execute('''
        INSERT OR REPLACE INTO Dates 
        (seconds_id, date, temp) 
        VALUES (?, ?, ?)''', 
        (date_seconds, date, temp))    
    
    #add row, or replace all data (where temp previously was true all should be replaced)    
    cur.execute('''
        INSERT OR REPLACE INTO Pages 
        (page, date_seconds_id, referrer_id, pageviews, unique_pageviews, time_on_page, bounces, entrances, exits, page_value) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
        (page, date_seconds, referrer_id, pageviews, unique_pageviews, time_on_page, bounces, entrances, exits, page_value))     
   
    conn.commit()
        
def run():
    #connect to database
    conn, cur, last_date = db_conn()
    
    #create list of dates to update
    dates = get_dates(last_date)
    
    #make api calls to get analytics data for each date in list
    print ''
    for date in dates:           
        data = get_data(date)
        #check_data(date, data)  
        
        for row in data:
            db_insert(conn, cur, date, row)
            
        print 'FINISHED:', date.strftime('%Y-%m-%d')    
    
    print '\nDONE'
    conn.close()      
    database_backup('database/db.sqlite', 'database/archive/', step='PAGES')
    
run()    