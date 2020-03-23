# from selenium import webdriver
#
# options = webdriver.ChromeOptions()
# options.add_argument('--headless')
# browser = webdriver.Chrome(options=options)
# browser.get('https://myscore.ru')
# print(browser.page_source)

import datetime

import requests

date_time = '12.05.2019 17:00'

a = datetime.datetime.strptime(date_time, '%d.%m.%Y %H:%M')


class A:

    def __init__(self, amount):
        self.amount = amount
        self.var = self.get_var()

    @staticmethod
    def get_var():
        num = int(requests.get('http://number.com').text)
        return num + 1 + 3 - 8


class B:

    def __init__(self, amount):
        self.amount = amount

    @property
    def var(self):
        num = int(requests.get('http://number.com').text)
        return num + 1 + 3 - 8


