#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 18:48:08 2018

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
    name = "articlebot"
    
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
        
    def get_links(self):
        df = pd.read_csv('timeline_9.csv',names = ['User','Order','link'])
        links = df['link']
        users = df['User']
        orders = df['Order']
        return links,users,orders
        
        
    def c_score(self,text):
        nlp= spacy.load('en')
        doc = nlp(text)
        sentences = [sent for sent in doc.sents]
        words = 0
        for sentence in sentences:
            words+= len([token for token in sentence])
        num_sent = len(sentences)
        sent_len = float(words/num_sent)
        sylls = textstatistics().syllable_count(text)
        ASPW = float(sylls)/float(words)
        syls_p_wd = legacy_round(ASPW,1)
        FRE = 206.835 - float(1.015 * sent_len)- float(84.6 * syls_p_wd)
        score = legacy_round(FRE,2)
        return words, score
        
    def get_author(self,link):
        self.driver.get(link)
        page = Selector(text = self.driver.page_source.encode('utf-8'))
        try:
            followinga =(page.css("a[href*='following']::text").extract_first())
            print(followinga)
        except:
            followinga = 0
        try:
            followersa = (page.css("a[href*='followers']::text").extract_first())
            print(followersa)
        except:
            followersa = 0
#        claps = []
#        all_ =page.css("div[class*='dk']")
#        for a in all_:
#            claps.append(a.css("div[class*='av']").extract_first())
#        art_count = len(all_)
#        claps_per_a = np.mean(claps)
        self.driver.back()
        return followinga, followersa
    
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
        time.sleep(3)
        self.login()
        links,users,orders = self.get_links()
        print(len(links))
        yes = 0
        no = 0
        for i in range(len(links)):
            try:
                link = links[i]
                user = users[i]
                order = orders[i]
                yield scrapy.Request(link, callback = self.parse_article, meta = {'link_a':link,'user':user,'order':order})
                yes +=1
            except Exception as e:
                print(e)
                no+=1
            
        
        
        
    def parse_article(self,response): #Scrapes the article for title, author, tags, and fans
        print("parsing article")
        self.driver.get(response.url)
        time.sleep(5)
        page = Selector(text = self.driver.page_source.encode('utf-8'))
        title = page.css("div.postArticle-content div.section-content div.section-inner h1::text").extract_first()
        author = page.css("header.container div.col div.uiScale div.u-flex1 a::text").extract_first()
        try:
            star = self.driver.find_element_by_xpath["//span[@class = 'svgIcon svgIcon--star svgIcon--15px']"]
            featured = 1
        except:
            featured = 0
            pass
        total_words = 0
        complexity = []
        for par in page.css("div.section-content"):
            graph = par.css("p::text").extract_first()
            if type(graph) is str:
                word_count,complex_ = self.c_score(graph)
                total_words +=word_count
                complexity.append(complex_)
            else:
                print("nothing returned")
        complex_score = np.mean(complexity)
        figures = len(page.css("div.section-content div.progressiveMedia"))
        for x in page.css("div.section-content div.progressiveMedia"):
            print(x.css("img::attr(src)").extract_first())
        but = self.driver.find_element_by_xpath("//button[@data-action='show-recommends']").text
        date = self.driver.find_element_by_xpath("//time").text
        #print("author")
        #print(author)
        tags = []
        for tag in page.css("div.container div.row div.col div.u-paddingBottom10 ul.tags li"):
            tagg = tag.css("a::text").extract()
            tags.append(tagg)
        self.scroll_until_loaded()
        try:
            comm_button = self.driver.find_element_by_xpath("//button[@data-action = 'show-other-responses']")
            print("found more responses")
            comm_button.click()
            time.sleep(3)
            page = Selector(text= self.driver.page_source.encode('utf-8'))
        except Exception as e:
            print(e)
        sentiments = []
        for comment in page.css("div.responsesStream div.postArticle"):
            text = comment.css("p::text").extract_first()
            print(text)
            if type(text)==str:
                sentiments.append(TextBlob(text).sentiment.polarity)
        com_count= len(sentiments)
        avg_sent = np.mean(sentiments)
        refs= []
        for ref in page.css("div.section-inner p"):
            add = ref.css("a::attr(href)").extract_first()
            if type(add) is str:
                refs.append(add)
        try:
            aut_link = page.css("header.container div.uiScale div.u-flex1 a::attr(href)").extract_first()
            followinga, followersa = self.get_author(aut_link)
        except:
            followinga = 0
            followersa = 0
        try: 
            file = open("again_9.csv","a")
            tag_str = ','.join(str(e)for e in tags)
            row = [response.meta['user'],response.meta['order'],title,author,followinga,followersa,tag_str,response.meta['link_a'],date,figures, but,total_words,avg_sent,com_count,complex_score,featured,refs]
            filewriter = csv.writer(file)
            filewriter.writerow(row)
            print("saved")
        except Exception as e:
            print("Problem w/ yield")
            print(e)        