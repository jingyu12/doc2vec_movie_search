# -*- coding: utf-8 -*-
"""
Created on Sat Mar 17 23:46:07 2018

@author: jingyu
"""
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.keys import Keys

import os
import pandas as pd
import numpy as np


os.chdir('D:/UNIST/17-2학기 자료/IM/')

# naver crawling with chrome 
driver=webdriver.Chrome()

# naver login
driver.get('http://www.naver.com')

driver.find_element_by_xpath("//*[@id='id']").send_keys('your_id') # put your naver ID
elem = driver.find_element_by_xpath("//*[@id='pw']").send_keys('your_pw!') # put your naver PW

driver.find_element_by_xpath("//*[@id='frmNIDLogin']/fieldset/span/input").click()


# make veterinarian list
user_id_list=['xedziihn']
user_id=user_id_list[0]

# find out page number
driver.get('http://kin.naver.com/userinfo/answerList.nhn?userId=%s&' %user_id)
all_answer_count=driver.find_element_by_xpath("//*[@id='au_main_profile_box']/div[2]/div[3]/dl/dd[2]/strong")
all_answer_count=int(all_answer_count.text.replace(",", ""))


page_num=int(all_answer_count)//20
page_num_plus=int(all_answer_count)%20
print(page_num)
print(page_num_plus) 

##################
# scraping data
##################    
question_list=[]
q_time_list=[]

answer_list=[]
synop_list=[]
q_gen_list=[]


driver.get('http://kin.naver.com/userinfo/answerList.nhn?userId={0}&page={1}'.format(user_id,1))

for k in range(99,101): 
    driver.get('http://kin.naver.com/userinfo/answerList.nhn?userId={0}&page={1}'.format(user_id,k))    
    for i in range(1,21):
        elem=driver.find_element_by_xpath("//*[@id='au_board_list']/tr["+str(i)+"]/td[1]/a")
        
        # for deleted page
        try:
            elem.click()         
            if driver.switch_to_alert():
                driver.switch_to_alert().accept()
                i=i+1
                elem=driver.find_element_by_xpath("//*[@id='au_board_list']/tr["+str(i)+"]/td[1]/a")
                elem.click()
        except NoAlertPresentException as e:
            pass
        
        # extract time
        q_time=driver.find_element_by_xpath("//*[@id='qna_detail_question']/div[1]/div[1]/div[2]/dl/dd[4]")
        q_gen=driver.find_element_by_xpath("//*[@id='au_location']/li[4]/a[1]")
        
        # extract question        
        try:
            question=driver.find_element_by_xpath("//*[@id='contents_layer_0']/div[1]/div")    
        except NoSuchElementException:
            question=driver.find_element_by_xpath("//*[@id='contents_layer_0']/div[1]")
            
        # extract answer        
        j=1
        while j<10:
            try:
                answer=driver.find_element_by_xpath("//*[@id='contents_layer_"+str(j)+"']/div[1]/div")
                break
            except NoSuchElementException:
                try:
                    j=j+1
                    answer=driver.find_element_by_xpath("//*[@id='contents_layer_"+str(j)+"']/div[1]/div")
                    break
                except NoSuchElementException:
                    pass
        
        # link to movie page
        j=1
        try:
            elem=driver.find_element_by_xpath("//*[@id='contents_layer_"+str(j)+"']/div[1]/div/div/div/dl/dt/a")
            elem.click()
            
        # for no synopsis movie        
            try:       
                driver.switch_to_window(driver.window_handles[1])
                synop=driver.find_element_by_xpath("//*[@id='content']/div[1]/div[4]/div[1]/div/div[1]/p")  
                synop_list.append(synop.text)
                    
            except NoSuchElementException:
                synop_list.append('There is no synopsis')
            
            driver.close() #closes new ta
            driver.switch_to_window(driver.window_handles[0])#change to old tab

        # append the results
            question_list.append(question.text)
            q_time_list.append(q_time.text)
            answer_list.append(answer.text)
            q_gen_list.append(q_gen.text)                
                
        except NoSuchElementException:
            pass
        
        driver.get('http://kin.naver.com/userinfo/answerList.nhn?userId={0}&page={1}'.format(user_id,k))                

     
driver.quit()

len(q_gen_list)
len(q_time_list)
len(question_list)
len(answer_list)
len(synop_list)

# make question, answer to Dataframe 
df2=pd.DataFrame({"q_gen":q_gen_list,"time":q_time_list, "question":question_list,
                 "answer":answer_list,'synopsis':synop_list})
    

pd.DataFrame.to_csv(df2,'sample.csv')