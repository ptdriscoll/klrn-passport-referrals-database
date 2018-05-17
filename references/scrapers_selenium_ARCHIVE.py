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
        iframe.video-player__iframe
    '''

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 5)
        wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selectors)))
        driver.switch_to.frame(driver.find_element_by_css_selector(css_selectors)) 
        #driver.implicitly_wait(3)
        html = driver.page_source
        
    except:
        print 'NO CONNECTION BY SELENIUM OR NO PARTNERPLAYER'
        driver.close()
        driver.quit()
        return None
        
    video_id_search = re.search(r'id="video_([0-9]+)"', html)
    if video_id_search: 
        driver.close()
        driver.quit()        
        return video_id_search.group(1)
        
    #not all pages make video available on first load, so refresh and try again    
    else: 
        try:
            driver.refresh() 
            wait = WebDriverWait(driver, 5)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, css_selectors)))
            driver.switch_to.frame(driver.find_element_by_css_selector(css_selectors)) 
            html = driver.page_source
            
        except:
            print 'COULD NOT RECONNECT WITH SELENIUM OR GET PARTNERPLAYER'
            driver.close()
            driver.quit()
            return None
    
    #and try regex search one more time
    video_id_search = re.search(r'id="video_([0-9]+)"', html)
    if video_id_search: 
        driver.close()
        driver.quit()        
        return video_id_search.group(1)    
    
    driver.close()
    driver.quit()    
    return None