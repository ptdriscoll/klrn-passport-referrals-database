import sys
import re

sys.path.insert(0, 'c:/python27/lib/site-packages')
from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#firefox_path = 'C:/Program Files (x86)/Mozilla Firefox/firefox.exe %s'
chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'

def iframe_partnerPlayer_id(url):
    #driver = webdriver.Firefox(executable_path = 'bin/geckodriver.exe')
    driver = webdriver.Chrome('bin/chromedriver.exe')
    
    css_selectors = '''
        #partnerPlayer,
        iframe.video-player__iframe,
        #mount-jwplayer
    ''' 
    
    re_searches = [
        r'id="video_([0-9]+)"',
        r'\s+"contentID":\s+(\d+),'
    ]
    
    for attempt in xrange(2):
        try:
            if attempt == 0: driver.get(url)
            else: driver.refresh() 
            wait = WebDriverWait(driver, 5)
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, css_selectors))) 
            html = driver.page_source
            
            #if html was grabbed, try to get video id    
            for re_search in re_searches:
                video_id_search = re.search(re_search, html)
                if video_id_search: 
                    driver.close()
                    driver.quit()        
                    return video_id_search.group(1) 
            
            continue #refresh browser and try one more time
           
        except Exception as e:            
            print '\nERROR TYPE:', type(e).__name__

            #not all pages make video available on first load, so try again with refresh 
            if attempt == 0: 
                print 'NO INITIAL CONNECTION BY SELENIUM OR NO PARTNERPLAYER, SO REFRESHING'
                continue 
                
            #that's it, forget about it            
            else:
                print 'COULD NOT CONNECT WITH SELENIUM OR GET PARTNERPLAYER AFTER REFRESH'
                driver.close()
                driver.quit()
                return None      
   
    driver.close()
    driver.quit()    
    return None