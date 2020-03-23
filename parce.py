import datetime
import re
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException

from decorators import close_browser
from locators import MatchPageSelectors, LeaguePageSelectors
from bs4 import BeautifulSoup


class Base:

    def __init__(self, wait=5, *args, **kwargs):
        pass

    @staticmethod
    def id_to_link(match_id):
        pattern = 'https://www.flashscore.com/match/{}/#match-statistics;0'
        return pattern.format(match_id)


class LeaguePage(Base):
    def __init__(self, link, wait=5, *args, **kwargs):
        super().__init__()
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(wait)
        self.link = link
        self.page_source = self.get_page_source()
        self.matches_ids = self.get_matches_ids()
        self.matches_links = self.get_matches_links()

    def get_page_source(self) -> str:
        self.browser.get(self.link)
        button = self.browser.find_element(*LeaguePageSelectors.SHOW_MORE_MATCHES_BUTTON)
        while True:
            try:
                self.browser.execute_script(LeaguePageSelectors.SCROLL_TO_BOTTOM_SCRIPT)
                button.click()
                time.sleep(3)
            except StaleElementReferenceException:
                break
        page_source = self.browser.page_source
        self.browser.close()
        return page_source

    def get_matches_ids(self):
        soup = BeautifulSoup(self.page_source, 'lxml')
        html_matches = soup.find_all(attrs={'class': 'event__match'})
        ids = [match.attrs.get('id')[4:] for match in html_matches]
        return ids

    def get_matches_links(self):
        links = [self.id_to_link(id_) for id_ in self.matches_ids]
        return links


class MatchPage(Base):

    def __init__(self, wait=5, *args, **kwargs):
        super().__init__()
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(wait)
        self.id = kwargs.get('id')

        if kwargs.get('link'):
            self.link = kwargs.get('link')
        else:
            self.link = self.id_to_link(self.id)

        self.page_source = self.get_page_source()
        self.soup = self.get_page_soup()
        self.date_time = self.get_date_time()
        self.tournament = self.get_tournament()
        self.round = self.get_round()
        self.country = self.get_country()
        self.team_1 = self.get_team_1_name()
        self.team_2 = self.get_team_2_name()

    def get_page_source(self):
        self.browser.get(self.link)
        page_source = self.browser.page_source
        self.browser.close()
        return page_source

    def get_page_soup(self):
        return BeautifulSoup(self.page_source, 'lxml')

    def get_date_time(self):
        date_time_soup = self.soup.find(attrs=MatchPageSelectors.DATA_TIME_SELECTOR)
        date_time = datetime.datetime.strptime(date_time_soup.text, '%d.%m.%Y %H:%M')
        return date_time

    def get_page_data(self):
        # data_time = self.soup.find(attrs=MatchPageSelectors.DATA_TIME_SELECTOR).text
        # data = re.match(r'(.*) ', data_time).group(1)
        # return data
        pass

    def get_page_time(self):
        # data_time = self.soup.find(attrs=MatchPageSelectors.DATA_TIME_SELECTOR).text
        # time = re.match(r'.* (.*)', data_time).group(1)
        # return time
        pass

    def get_tournament(self):
        tournament_soup = self.soup.select_one(MatchPageSelectors.TOURNAMENT_AND_ROUND_SELECTOR)
        tournament = re.match(r'(.*) - ', tournament_soup.text).group(1)
        return tournament

    def get_country(self):
        country_soup = self.soup.select_one(MatchPageSelectors.COUNTRY_SELECTOR)
        country = re.match(r'\w*', str(country_soup.next)).group(0)
        return country

    def get_round(self):
        round_soup = self.soup.select_one(MatchPageSelectors.TOURNAMENT_AND_ROUND_SELECTOR)
        round_ = int(re.match(r'.*Round (\d+)', round_soup.text).group(1))
        return round_

    def get_team_1_name(self):
        name = self.soup.select_one('.home-box .tname a').text
        return name

    def get_team_2_name(self):
        name = self.soup.select_one('.away-box .tname a').text
        return name


class Team():

    def __init__(self, match):
        self.soup = match.soup
        self.name = None
        self.match = match
        self.goals = None
        self.ball_possession = None
        self.goal_attempts = None
        self.shots_on_goal = None
        self.shots_of_goal = None
        self.blocked_shots = None
        self.free_kicks = None
        self.corner_kicks = None
        self.offsides = None
        self.goalkeeper_saves = None
        self.fouls = None
        self.total_passes = None
        self.completed_passes = None
        self.tackles = None
        self.attacks = None
        self.dangerous_attacks = None
        self.odd = None


class HomeTeam(Team):
    pass


class AwayTeam(Team):
    pass



    def __str__(self):
        return self.name


def get_data(link) -> dict:
    browser = webdriver.Chrome()
    browser.implicitly_wait(5)
    browser.get(link)
    stat_text_groups = browser.find_elements_by_css_selector('#tab-statistics-0-statistic>.statRow>.statTextGroup')
    stats = []
    my_dict = {}
    date = browser.find_element_by_css_selector('#utime').text
    my_dict.update({'date': date})
    team_1 = {}
    team_2 = {}
    first_team_goals = browser.find_elements_by_css_selector('.current-result .scoreboard')[0]
    second_team_goals = browser.find_elements_by_css_selector('.current-result .scoreboard')[1]
    team_1.update({'goals': first_team_goals.text})
    team_2.update({'goals': second_team_goals.text})
    team_1_name = browser.find_element_by_css_selector('.team-text.tname-home')
    team_2_name = browser.find_element_by_css_selector('.team-text.tname-away')
    odds = browser.find_elements_by_css_selector('.odds.value')
    team_1.update({'name': team_1_name.text, 'odd': odds[0].text})
    team_2.update({'name': team_2_name.text, 'odd': odds[2].text})
    for i in stat_text_groups:
        field = i.find_element_by_css_selector('.statText--titleValue').text
        home_value = i.find_element_by_css_selector('.statText--homeValue').text
        away_value = i.find_element_by_css_selector('.statText--awayValue').text
        team_1.update({field: home_value})
        team_2.update({field: away_value})
    my_dict.update({'team_1': team_1, 'team_2': team_2})
    browser.close()
    return my_dict


if __name__ == '__main__':
    # a = LeaguePage('https://www.flashscore.ru/football/england/premier-league-2018-2019/results/', wait=3)
    pass
