#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 21:50:00 2018

@author: Taylor
"""

import scrapy
import time
from selenium import webdriver
from scrapy.selector import Selector
import csv
from textblob import TextBlob
import numpy as np
from textstat.textstat import textstatistics, easy_word_set, legacy_round
import spacy
import pandas as pd

class MediumSpider(scrapy.Spider):
    name = "timeline"
    
    start_urls = ["https://medium.com/tag/data"]
    
    def __init__(self):
        self.driver = webdriver.Chrome()
        
        
    def login(self):
        try:
            goaway = self.driver.find_element_by_xpath("//button[@title='I agree.']")
            goaway.click()
        except:
            pass
        time.sleep(3)
        loginbutton = self.driver.find_element_by_xpath("//a[@data-action='sign-in-prompt']")
        loginbutton.click()
        email_login = self.driver.find_element_by_xpath("//button[@data-action='twitter-auth']")
        email_login.click()
        time.sleep(5)
        email_input = self.driver.find_element_by_xpath("//input[@id='username_or_email']")
        email_input.send_keys('tbrownlow3@gmail.com')
        password = self.driver.find_element_by_xpath("//input[@type='password']")
        password.send_keys('Timtp-3*')
        cont= self.driver.find_element_by_xpath("//input[@type='submit']")
        cont.click()
        time.sleep(5)
        
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

        
    def get_links(self):
        df = pd.read_csv("recs_9.csv",names= ['User','Count','link'])
        links=df['link']
        people = df['User']
        return links,people
        
    def parse(self,response):
        self.driver.get(response.url)
        time.sleep(3)
        self.login()
        links,people = self.get_links()
        print(len(links))
        for i in range(len(links)):
            link = links[i]
            person = people[i]
            yield scrapy.Request(link,callback = self.parse_timeline,meta={'people':person})
            
    def parse_timeline(self,response):
        self.driver.get(response.url)
        person = response.meta['people']
        self.scroll_until_loaded()
        page = Selector(text = self.driver.page_source.encode('utf-8'))
        try:
            following =(page.css("a[href*='following']::text").extract_first())
            print(following)
        except:
            following = 0
        try:
            followers = (page.css("a[href*='followers']::text").extract_first())
            print(followers)
        except:
            followers = 0
        order = 0
        links = []
        #counter = 0
        for a in page.css("div[class*='d']"):
            try:
                link = a.css("div+a::attr(href)").extract_first()
                link_ = "https://www.medium.com"+link
                if link_ not in links:
                    links.append(link_)
                    order +=1
                    file = open("timeline_9.csv","a")
                    row = [person,order,link_]
                    filewriter = csv.writer(file)
                    filewriter.writerow(row)
                else:
                    pass
            except Exception as e:
                print(e)
        
        