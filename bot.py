from seleniumwire import webdriver
from pytz import timezone
import selenium
import sys
import time
import requests
import brotli
import json
import datetime

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

    def log(self, mes):
        f=open('log.txt','a')
        f.write(mes)
        f.close()

    def login(self):
        try:
            driver = webdriver.Chrome()
            driver.get("https://www.frisco.pl/")
            driver.find_element_by_xpath('//*[@id="header"]/div[1]/div/div[3]/div/a[1]').click()
            time.sleep(3)
            driver.find_elements_by_name("username")[0].send_keys(self.email)
            driver.find_elements_by_id("loginPassword")[0].send_keys(self.passw)
            driver.find_elements_by_xpath('/html/body/div[1]/div[2]/div/div[2]/div/div/form/section/button')[0].click()
            time.sleep(2)
            driver.find_element_by_class_name('header-delivery')
        except: 
            driver.quit()
            driver = self.login()
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
        return datetime.datetime.fromisoformat(jsn['firstOpenWindow']['deliveryWindow']['startsAt'])
        
    def verifyTimes(self, sch):
        now = datetime.datetime.now(timezone('Europe/Warsaw'))
        print(now)
        print(sch)
        allowed_td = datetime.timedelta(days=int(sys.argv[1]))
        if sch- allowed_td >= now:
            print('Found')
            return True
        else:
            return False

    def acceptDelivery(self,driver):
        if driver.find_elements_by_class_name('ps-active-y') != []:
            driver.find_element_by_class_name('header-delivery').click()
            time.sleep(3)
        driver.find_element_by_class_name('header-delivery').click()
        time.sleep(2)
        driver.find_element_by_class_name('available').click()
        driver.find_element_by_xpath("/html/body/div[1]/div/div[3]/div/div[1]/div[2]/div[2]/div[2]/div/div/div[3]/div[2]/div/div[2]").click()
        print('there was an attempt') 

    def run(self):
        if(int(sys.argv[1])<=1):
            raise ValueError
        driver = self.login()
        self.generateVanRequest(driver)
        reserved = False
        while not reserved:
            print('inside waiting for a suitable date')
            sch = self.checkSchedule(driver)
            if self.verifyTimes(sch):
                print('passed:ending')
                reserved = True
            else:
                print('goin to sleep, ')
                print(sch )
                time.sleep(60)
                print('rumble again')
        time.sleep(300)

if __name__ == "__main__":
    b = friscoBot()
    b.run()