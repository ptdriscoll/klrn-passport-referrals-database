#! python
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 16:44:16 2017

@author: pdriscoll
"""

import numpy as np
import pandas as pd
import random
import argparse
from Tkinter import *
import datetime
import urllib2
from bs4 import BeautifulSoup
import re
from urlparse import urlparse
import scrapers 
from scrapers_selenium import iframe_partnerPlayer_id


#Python regex tester
#https://regex101.com/


#see if id is in url (ids are now replaced by slugs)
def get_video_id(referrer):
    if 'pbs.org/video/' in referrer or 'video.klrn.org/video/' in referrer:
        parts = urlparse(referrer).path.split('/')   
        for part in reversed(parts):
            if part: return part    
    return None  


def referrers_scrape_page(url, video_id):
    #make sure video_id can be converted to an integer
    if video_id: 
        video_id = video_id if video_id.isdigit() else None
    else: video_id = None    
    
    #fix a borken url
    if url.startswith('pbsvideo://'): url = url.replace('pbsvideo://', 'http://') 
    #print url
    
    #connect to page    
    try:
        conn = urllib2.urlopen(url)
        html = conn.read()    
    except urllib2.HTTPError, e:
        print '\nNO REFERRAL CONNECTION\n'
        print e.code
        print e.read()
        return None, video_id
        
    soup = BeautifulSoup(html, 'lxml')
    
    title = soup.title
    if title and title.string: title = ' '.join(title.string.split())        
    if video_id: return title, video_id    
    
    #if no video_id, loop through imported scrapers to look for it 
    for key, val in scrapers.__dict__.iteritems():
        if video_id: break
        if callable(val): #and key == 'partnerPlayer_id_embed':            
            print '\nCALLING:', key
            print 'URL:', url
            video_id = val(soup)   
            
            #again, make sure video_id can be converted to an integer
            if video_id: 
                video_id = video_id if video_id.isdigit() else None
    
    conn.close()    
       
    #if still no video_id, try to get it through embedded iframe using selenium
    if not video_id: video_id = iframe_partnerPlayer_id(url)  
        
    return title, video_id  


#get video title, description, etc. from video page in COVE     
def video_scrape_page(video_id):
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


'''
RUN
'''

print ''

url = 'http://www.pbs.org/wgbh/nova/earth/killer-floods.html'
url = 'https://www.pbs.org/wgbh/masterpiece/episodes/victoria-s2-e1/'
#url = 'http://player.pbs.org/partnerplayer/1swkRFEIA0865nS-Y-bjEQ==/?w=680&amp;h=430.2397&amp;chapterbar=true&amp;endscreen=false&amp;topbar=true&amp;wmode=transparent'
#3006473602

#print '\n', get_video_id(url)  
#print referrers_scrape_page(url, '')
#print video_scrape_page('2365392760')


#try to get id just through selenium
print iframe_partnerPlayer_id(url)






