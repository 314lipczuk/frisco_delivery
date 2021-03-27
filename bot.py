from seleniumwire import webdriver
from pytz import timezone
import selenium
import sys
import time
import requests
import brotli
import json
import datetime
import re
##TODO
##Make it actually work

class friscoBot():
    f = open('.pb.txt', 'r')
    crds = f.read()
    f.close()
    crds = crds.split(":",1)
    email = crds[0]
    passw = crds[1]
    van_Request = None
    dayfocused = None

    def log(self, mes):
        f=open('log.txt','a')
        f.write('\n'+mes)
        f.close()

    def login(self):
        driver = webdriver.Chrome()
        driver.get("https://www.frisco.pl/login")
        time.sleep(3)
        #driver.find_element_by_xpath('i//*[@id="header"]/div[1]/div/div[3]/div/button[1]').click()
        #time.sleep(3)
        driver.find_element_by_id("email").send_keys(self.email)
        driver.find_element_by_id("password").send_keys(self.passw)
        driver.find_element_by_class_name("button").click()
        time.sleep(2)
        return driver

    def generateVanRequest(self, driver):
        if driver.find_elements_by_class_name('ps-active-y') == []:
            driver.find_element_by_class_name('header-delivery').click()
            time.sleep(3)
        try:
            days = driver.find_elements_by_class_name('day')
            for d in days:
                d.click()
        except:
            print('Some error in calling van via ui')
            pass
        time.sleep(0.5)
        nr = 1
        req = None
        while req is None:
            print('inside looking for vanrq')
            if nr>50:
                print('Exceeded limit of requests while searching for van, calling it prob doesnt work')
                print('Going into recursion')
                req =self.generateVanRequest(driver) 
            if driver.requests[nr*-1].path == "/app/commerce/api/v1/users/590820/calendar/Van":
                print('found van request')
                req=driver.requests[-1*nr]
            else:
                nr+=1
        self.van_Request = req
        return req


    def checkSchedule(self, driver):
        if(self.van_Request is None):
            self.generateVanRequest(driver)
        time.sleep(3)
        van_req = self.van_Request
        r= requests.get(van_req.url,headers=van_req.headers )
        jsn=json.loads(r.text)
        self.log(jsn['firstOpenWindow']['deliveryWindow']['startsAt'])
        print("checkSchedule: "+ jsn['firstOpenWindow']['deliveryWindow']['startsAt'])
        return datetime.datetime.fromisoformat(jsn['firstOpenWindow']['deliveryWindow']['startsAt'])
        
    def verifyTimes(self, sch):
        now = datetime.datetime.now(timezone('Europe/Warsaw'))
        print("verifyTimes: now:"+ str(now)+" | sch: "+ str(sch))
        allowed_td = datetime.timedelta(int(sys.argv[1]))
        if sch - now <=allowed_td:
            print('Found')
            self.dayfocused = sch.day
            return True
        else:
            return False


    def acceptDelivery(self,driver):
        if driver.find_elements_by_class_name('ps-active-y') != []:
            driver.find_element_by_class_name('header-delivery').click()
            time.sleep(3)
        else:
            driver.find_element_by_class_name('header-delivery').click()
            time.sleep(2)
            driver.find_element_by_class_name('header-delivery').click()
        time.sleep(2)
        driver.find_element_by_class_name('available').click()
        days = driver.find_element_by_class_name('days-inner')
        selected =days.find_element_by_class_name('active')

        num = re.findall('[0-9]+', selected.text)

        
        print("selected: "+str(num)+" matched: "+str(self.dayfocused))
        if self.dayfocused in num:
            print("selefted: "+str(num)+"matched: "+str(self.dayfocused))
            #driver.find_element_by_xpath("/html/body/div[1]/div/div[3]/div/div[1]/div[2]/div[2]/div[2]/div/div/div[3]/div[2]/div/div[2]").click()
        else:
            print('shit fucced')
    def run(self):
        if(int(sys.argv[1])<=1):
            raise ValueError
        driver = self.login()
        self.generateVanRequest(driver)
        reserved = False
        while reserved != True:
            print('run: beginning of while loop')
            sch = self.checkSchedule(driver)
            if self.verifyTimes(sch):
                print('passed:ending')
                self.acceptDelivery(driver)
                reserved = True
            else:
                print('run: goin to sleep, ')
                time.sleep(60)
                print('run: end of sleep')
        time.sleep(300)

if __name__ == "__main__":
    b = friscoBot()
    b.run()
