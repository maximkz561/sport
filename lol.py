import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from locators import MatchPageSelectors, LeaguePageSelectors


def func(link):
    driver = webdriver.Chrome()

    driver.implicitly_wait(5)
    driver.get(link)
    button = driver.find_element(*LeaguePageSelectors.SHOW_MORE_MATCHES_BUTTON)
    while True:
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            button.click()
            time.sleep(3)
        except StaleElementReferenceException:
            break
    return driver.page_source

if __name__ == '__main__':
    initial_page_source, page_source = func('https://www.flashscore.ru/football/england/premier-league-2018-2019/results/')