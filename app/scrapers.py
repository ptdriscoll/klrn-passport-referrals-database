import re


def partnerPlayer_id(soup):
    video = soup.find('iframe', id='partnerPlayer') 
    if video and video.has_attr('src') and '/widget/partnerplayer/' in video['src']:
        video_url_half = video['src'].split('/widget/partnerplayer/')[1]
        video_id_string = re.search(r'^[0-9]+', video_url_half).group()            
        return video_id_string  
        
def partnerPlayer_id_embed(soup):
    body = soup.find('body').text
    video_id_string = re.search(r"'<iframe id=\"partnerPlayer\"\s.*src=\".*/(\d+).*>'", body) 
    if video_id_string and video_id_string.group(1):
        print video_id_string.group(1)
        return video_id_string.group(1) 
    return None          
        
def portalPlayer(soup):
    head = soup.find('head').text
    video_id_string = re.search(r"\n\s+id:\s+'(\d+)',", head)  
    if video_id_string and video_id_string.group(1):
        print video_id_string.group(1)
        return video_id_string.group(1) 
    return None  

def viralplayer(soup):
    iframes = soup.findAll('iframe') 
    for iframe in iframes:
        if iframe.has_attr('src') and 'pbs.org/viralplayer/' in iframe['src']:
            video_url_half = iframe['src'].split('/viralplayer/')[1]
            video_id_string = re.search(r'^[0-9]+', video_url_half).group()
            return video_id_string     
    
def nature(soup):
    video = soup.find('iframe', class_='partnerPlayer') 
    if video and video.has_attr('src') and '/widget/partnerplayer/' in video['src']:
        video_url_half = video['src'].split('/widget/partnerplayer/')[1]
        video_id_string = re.search(r'^[0-9]+', video_url_half).group()            
        return video_id_string           

def masterpiece(soup):
    video = soup.find('div', class_='thumb-container')
    if video and video.has_attr('data-embed-code') and '/widget/partnerplayer/' in video['data-embed-code']:
        iframe = video['data-embed-code']
        video_url_half = iframe.split('/widget/partnerplayer/')[1]
        video_id_string = re.search(r'^[0-9]+', video_url_half).group()            
        return video_id_string   

def american_experience(soup):
    video = soup.select('a.watch-link.js-cove-link')
    if video and video[0] and video[0].has_attr('data-coveid'):
        video_id_string = video[0]['data-coveid']            
        return video_id_string          

def nova(soup):
    video = soup.select('div.full-program.bip')
    if video and video[0] and video[0].has_attr('data-coveid'):
        video_id_string = video[0]['data-coveid']            
        return video_id_string    

def antiques_roadshow(soup):
    video = soup.select('.article-lede-video .js-load-video')
    if video and video[0] and video[0].has_attr('data-cove-id'):
        video_id_string = video[0]['data-cove-id']   
        return video_id_string   

def great_civilizations(soup):
    video = soup.select('.video01 .play-video')
    if video and video[0] and video[0].has_attr('data-video-id'):
        video_id_string = video[0]['data-video-id']   
        return video_id_string   

def wnet(soup):
    video = soup.find('iframe', id='player_embed_tag') 
    if video and video.has_attr('src') and '/widget/partnerplayer/' in video['src']:
        video_url_half = video['src'].split('/widget/partnerplayer/')[1]
        video_id_string = re.search(r'^[0-9]+', video_url_half).group()            
        return video_id_string 

def wgbh(soup):
    video = soup.select('div.col-left-with-ad.hero')
    if video and video[0] and video[0].has_attr('data-coveid'):
        video_id_string = video[0]['data-coveid']            
        return video_id_string  

def wgbh_2(soup):
    video = soup.select('.stacks-embed.embed-left-ad-right.grid')
    if video and video[0] and video[0].has_attr('data-service-id'):
        video_id_string = video[0]['data-service-id']            
        return video_id_string  

def wgbh_3(soup):
    video = soup.find('iframe', id='coveplayer') 
    if video and video.has_attr('src') and '/widget/partnerplayer/' in video['src']:
        video_url_half = video['src'].split('/widget/partnerplayer/')[1]
        video_id_string = re.search(r'^[0-9]+', video_url_half).group()            
        return video_id_string