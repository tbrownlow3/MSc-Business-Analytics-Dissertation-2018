#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 13 21:03:48 2018

@author: Taylor
"""

import scrapy
import time
from selenium import webdriver
from scrapy.selector import Selector
import csv


class MediumSpider(scrapy.Spider):
    name = "fans"
    
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
            
    def click_button(self):
        button = self.driver.find_element_by_xpath("//button[@data-action='show-recommends']")
        self.driver.execute_script("arguments[0].scrollIntoView();",button)
       # print("scrolled")
        self.driver.execute_script("window.scrollBy(0,-200);")
        button.click()
        #launches new window
            
    
    def parse(self,response):
        self.driver.get(response.url)
        self.login()
        link = "https://towardsdatascience.com/5-dataviz-blogs-to-follow-d30dbd90e52c?source=---------8---------------------"
        yield scrapy.Request(link, callback = self.parse_recs)
        
    def parse_recs(self,response):
        self.driver.get(response.url)
        self.click_button()
        time.sleep(3)
        counter = 0
        page = Selector(text = self.driver.page_source.encode('utf-8'))
        sent = self.driver.find_element_by_xpath("//h3[@class='overlay-title']").text
        print(sent)
        ppl_count = int(sent.split("from ")[1].split(" people")[0])
        print(ppl_count)
        while True:
            try:
                last_counter = counter
                loadmorebutton = self.driver.find_element_by_xpath("//button[@data-action='show-more-recommends']")
                loadmorebutton.click()
                time.sleep(5)
                page = Selector(text = self.driver.page_source.encode('utf-8'))
                counter = len(page.css("ul.list li"))
                print(counter)
                if counter==ppl_count or counter==last_counter:
                    break
                else:
                    print("AGAIN")
                    self.driver.execute_script("window.scrollBy(0,document.body.scrollHeight);")
                    time.sleep(3)
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
                link = link +'/has-recommended'
                people.append(per)
                ppl_links.append(link)
                file = open("recs_9.csv","a")
                row = [per,ppl_count,link]
                filewriter = csv.writer(file)
                filewriter.writerow(row)

            except:
                print("Didn't get to recomended")
                pass
        
        
        