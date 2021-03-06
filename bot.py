#from seleniumwire import webdriver
from selenium import webdriver
import sys
import time
import requests
import brotli
import json
import datetime

##TODO

##remake generateVanReq so that it is not retarded
##Create actual control flow
##Make it actually work


class friscoBot():
    f = open('.pb.txt', 'r')
    crds = f.read()
    f.close()
    crds = crds.split(":",1)
    email = crds[0]
    passw = crds[1]

    def log(self, mes):
        f=open('log.txt','a')
        f.write(mes)
        f.close()

    def login(self):
        driver = webdriver.Chrome()
        driver.get("https://www.frisco.pl/")
        driver.find_element_by_xpath('//*[@id="header"]/div[1]/div/div[3]/div/a[1]').click()
        time.sleep(3)
        driver.find_elements_by_name("username")[0].send_keys(self.email)
        driver.find_elements_by_id("loginPassword")[0].send_keys(self.passw)
        driver.find_elements_by_xpath('/html/body/div[1]/div[2]/div/div[2]/div/div/form/section/button')[0].click()
        return driver

    def generateVanRequest(self, driver):
        try:
            driver.find_elements_by_xpath("//div[@class='day active']")[0].click()
            days = driver.find_elements_by_class_name('day')
            for d in days:
                d.click()
        except:
            print('Some error in calling van via ui')
            pass
        time.sleep(0.5)
        vanfound = False
        nr = 1
        while vanfound==False:
            if nr>50:
                print('Exceeded limit of requests while searching for van, calling it prob doesnt work')
                break
            if driver.requests[nr*-1].path == "/app/commerce/api/v1/users/590820/calendar/Van":
                vanfound = True
            else:
                nr+=1
        return driver.requests[-1*nr]


    def checkSchedule(self, driver):
        time.sleep(1)
        driver.find_element_by_class_name('header-delivery').click()
        time.sleep(1)
        van_req = self.generateVanRequest(driver)
        print(van_req.response)
        r= requests.get(van_req.url,headers=van_req.headers )
        jsn=json.loads(r.text)
        return datetime.datetime.fromisoformat(jsn['firstOpenWindow']['deliveryWindow']['startsAt'])
        
    def verifyTimes(self, sch):
        now = datetime.datetime.now()
        if(int(sys.argv[1])<=1):
            raise ValueError
        now = datetime.datetime.now()
        allowed_td = datetime.timedelta(days=int(sys.argv[1]))
        if sch-now >= datetime.timedelta(days=1) and sch- allowed_td >= now:
            print('Found')
            return True
        else:
            return False

    def run(self):
        driver = self.login()
        reserved = False
        while not reserved:
            sch = checkSchedule(driver)
            if verifyTimes():
                print('ending')



if __name__ == "__main__":
    b = friscoBot()
    b.run()
