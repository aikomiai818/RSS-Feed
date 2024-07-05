import requests
from bs4 import BeautifulSoup
import re


def get_cover(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.content, 'html.parser')
    cover_photo = soup.find('meta', property='og:image')
    if cover_photo:
        return cover_photo['content']
    return None


def parse_udemy(url):
    if 'discudemy.com' not in url:
        return url
    
    last_part = url.split('/')[-1]
    converted_url = f"https://www.discudemy.com/go/{last_part}#google_vignette"
    
    response = requests.get(converted_url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    all_links = soup.find_all('a', href=True)
    
    udemy_links = [link['href'] for link in all_links if 'udemy.com' in link['href'] and 'discudemy.com' not in link['href']]
    
    if udemy_links:
        return udemy_links[0]
    
    return url