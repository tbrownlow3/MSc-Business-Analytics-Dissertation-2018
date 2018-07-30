#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 07:38:24 2018

@author: Taylor
"""


import scrapy
import time
from selenium import webdriver
from scrapy.selector import Selector

class MediumSpider(scrapy.Spider):
    name = "recs"
    
    start_urls = ["https://medium.com/@geoffruddock/has-recommended"]
    #start_urls = 
    def __init__(self):
        self.driver = webdriver.Chrome()
        
    def scroll_until_loaded(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
            time.sleep(1.5)

        # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
            time.sleep(5)
            
    def parse(self,response):
        self.driver.get(response.url)
        self.scroll_until_loaded()
        page = Selector(text = self.driver.page_source.encode('utf-8'))
        #titles = []
#        links = []
#        for art in page.css("div.dg div.j"):
#            title = art.css("div.j.dh.di.dj.dk.dl div a div section.dt.du h1::text").extract_first()
#            link = art.css("section.c.d.e.f.g.h.i div div.dc.ac div.j.dh.di.dj.dk.dl div a::attr(href)").extract_first()
#            print(link)
#            titles.append(title)
#            links.append(link)
        titles = self.driver.find_elements_by_xpath("//div[contains(@class,'dh')]//h1[@class]")
        links = []
        for a in page.css("div[class*='dh']"):
            link = a.css("div+a::attr(href)").extract_first()
            links.append(link)
        #print("what'd we got")
        #print(titles)
        print(len(titles))
        print(links)
        print(len(links))
        yield {'links':links
                
                }
            