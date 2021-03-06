#!./env/bin/python3

import time
import json
import sys
import requests
from blacklist import blacklist
from selenium import webdriver

def test_link(link):
    r = requests.head(link)
    headers = r.headers
    if 'content-type' not in headers.keys() or "audio" not in headers['content-type']:
        return False
    return r.status_code == 200

def link_matches(link, query):
    matches = 0
    print("testing match for : "+link)
    for word in query.split(" "):
        if word.lower() in link.split("/")[len(link.split("/")) - 1].lower().replace("%20", " "):
            matches += 1
    if matches > (len(query.split(" ")) / 2) and matches > 0:
        if test_link(link):
            print(link)
            return True
    return False

def is_blacklisted(url):
    print(url)
    for domain in blacklist:
        if domain in url:
            return True
    return False

def get_google_results(search, query, page=0):
    output = []
    urls = []
    driver = webdriver.PhantomJS()
    driver.get('http://www.google.com/')
    driver.implicitly_wait(10)
    search_box = driver.find_element_by_class_name("lst")
    search_box.send_keys(search)
    button = driver.find_element_by_name("btnG")
    button.click()
    driver.implicitly_wait(10)
    start = page * 10
    driver.get(driver.current_url+"&start=%i" %start)
    driver.implicitly_wait(10)
    links = driver.find_elements_by_xpath("//*[@href]")
    for link in links:
        if "http://www.google.fr/url?q=" in link.get_attribute('href') and "webcache.googleusercontent.com" not in link.get_attribute('href'):
            urls.append(link.get_attribute('href'))
    for url in urls:
        if not is_blacklisted(url):
            driver.get(url)
            driver.implicitly_wait(10)
            mp3_links = driver.find_elements_by_xpath("//a[contains(@href, '.mp3')] [1]")
            for mp3_link in mp3_links:
                print("mp3 link found : "+mp3_link.get_attribute('href'))
                if link_matches(mp3_link.get_attribute('href'), query):
                    return mp3_link.get_attribute('href')
    return json.dumps(output, ensure_ascii=False).encode('utf-8').decode('utf-8')

if __name__ == "__main__":
    get_google_results("github lupin012345", 1)
