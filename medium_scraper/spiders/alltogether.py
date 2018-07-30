#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 15:46:36 2018

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

class MediumSpider(scrapy.Spider):
    name = "finalbot"
    
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
            

    def parse(self,response):
        #Parses original homepage w/ data science tag
        self.driver.get(response.url)
        self.login()
        self.scroll_until_loaded()
        ordera = 0
        page = Selector(text = self.driver.page_source.encode('utf-8'))
        SET_SELECTOR = "div.postArticle"
        for med in page.css(SET_SELECTOR):
            # Sends article url to next scraper
            ordera+=1
            link = med.css('div.postArticle-readMore a::attr(href)').extract_first()
            print(link)
            file = open("landing.csv","a")
            row = [link,ordera]
            filewriter = csv.writer(file)
            filewriter.writerow(row)
            yield scrapy.Request(med.css('div.postArticle-readMore a::attr(href)').extract_first(),
                    callback = self.parse_fans,meta = {'article_link':link,'ordera':ordera})
             
        
    def click_button(self):

        button = self.driver.find_element_by_xpath("//button[@data-action='show-recommends']")
        self.driver.execute_script("arguments[0].scrollIntoView();",button)
       # print("scrolled")
        self.driver.execute_script("window.scrollBy(0,-200);")
        button.click()
        #launches new window
        
    def parse_fans(self, response): 
        self.driver.get(response.url)
        self.scroll_until_loaded()
        print(response.meta['article_link'])
        time.sleep(3)
        self.click_button()
        time.sleep(3)
        counter2 = 0
        page = Selector(text = self.driver.page_source.encode('utf-8'))
        sent = self.driver.find_element_by_xpath("//h3[@class='overlay-title']").text
        print(sent)
        ppl_count = int(sent.split("from ")[1].split(" people")[0])
        print(ppl_count)
        while True:
            try:
                last_counter = counter2
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                loadmorebutton = self.driver.find_element_by_xpath("//button[@data-action='show-more-recommends']")
                #print('found button')
                #self.driver.execute_script("arguments[0].scrollIntoView();",loadmorebutton)
                loadmorebutton.click()
                time.sleep(5)
                height = self.driver.execute_script("return document.body.scrollHeight")
                page = Selector(text = self.driver.page_source.encode('utf-8'))
                counter2 = len(page.css("ul.list li"))
                print(counter2)
                if counter2==ppl_count or counter2==last_counter:
                    break
                else:
                    print("AGAIN")
                    self.driver.execute_script("window.scrollBy(0,document.body.scrollHeight);")
            except Exception as e:
                print(e)
                break        
        new_page = Selector(text= self.driver.page_source.encode('utf-8'))
        people = []
        ppl_links = []
        for person in new_page.css("div.overlay div.overlay-dialog div.overlay-content ul.list li.list-item div.u-flex1"):
            try:
                per = person.css("a::text").extract_first()
                link = person.css("a::attr(href)").extract_first()
                people.append(per)
                ppl_links.append(link+"/has-recommended")
                file = open("homepage.csv","a")
                row = [per,response.meta['article_link'],response.meta['ordera'],ppl_count]
                filewriter = csv.writer(file)
                filewriter.writerow(row)
                yield scrapy.Request(link+"/has-recommended", callback = self.parse_recs, meta = {'people':per,'article_link':response.meta['article_link'],'ordera':response.meta['ordera']})
            except:
                print("Didn't get to recomended")
                pass


    
    def parse_recs(self,response): #parse each fan's other likes
        self.driver.get(response.url)
        person = response.meta['people']
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
        links = []
        order = 0
        for a in page.css("div[class*='d']"):
            try:
                print("try loop")
                print(a)
                link = a.css("div+a::attr(href)").extract_first()
                link_ = "https://www.medium.com"+link
                links.append(link_)
                print('link')
                print(link_)
                order +=1
                print("parsing recs")
                file = open("recs.csv","a")
                row = [person,response.meta['article_link'],response.meta['ordera'],link_]
                filewriter = csv.writer(file)
                filewriter.writerow(row)
                yield scrapy.Request(link_, callback = self.parse_article, meta = {'article_link':response.meta['article_link'],'ordera':response.meta[
                        'ordera'],'people':person, 'order' : order,'following':following,'followers':followers})
            except Exception as e:
                print("EXCEPTION")
                print(e)
                pass
            
            
            
    def parse_article(self,response): #Scrapes the article for title, author, tags, and fans
        print("parsing article")
        person = response.meta['people']
        #print(person)
        order = response.meta['order']
        print(order)
        self.driver.get(response.url)
        time.sleep(5)
        #self.login()
        page = Selector(text = self.driver.page_source.encode('utf-8'))
        title = page.css("div.postArticle-content div.section-content div.section-inner h1::text").extract_first()
        #print("Title:")
        #print(title)
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
        #print('tags')
        #print(tags)
        com_count= len(sentiments)
        avg_sent = np.mean(sentiments)
        #get links
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
            file = open("articles.csv","a")
            tag_str = ','.join(str(e)for e in tags)
            row = [person,response.meta['followers'],response.meta['following'],str(order),title,author,followinga,followersa,tag_str,response.meta['article_link'],response.meta['ordera'],date,figures, but,total_words,avg_sent,com_count,complex_score,featured,refs]
            filewriter = csv.writer(file)
            filewriter.writerow(row)
            print("saved")
            print("Article #:"+str(order))
        except Exception as e:
            print("Problem w/ yield")
            print(e)