import datetime
import re
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from locators import MatchPageSelectors, LeaguePageSelectors
from bs4 import BeautifulSoup


class Base:

    def __init__(self, wait=5, *args, **kwargs):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.browser = webdriver.Chrome(options=options)
        self.browser.implicitly_wait(wait)
        pass

    @staticmethod
    def id_to_link(match_id):
        pattern = 'https://www.flashscore.com/match/{}/#match-statistics;0'
        return pattern.format(match_id)


class LeaguePage(Base):
    def __init__(self, link, *args, **kwargs):
        super().__init__(*args, **kwargs)
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id = kwargs.get('id')

        if kwargs.get('link'):
            self.link = kwargs.get('link')
        else:
            self.link = self.id_to_link(self.id)

        self.page_source = self._get_page_source()
        self.soup = self._get_page_soup()
        self.date_time = self._get_date_time()
        self.tournament = self._get_tournament()
        self.round = self._get_round()
        self.country = self._get_country()
        self.team_1 = self._create_team_1()
        self.team_2 = self._create_team_2()

    def _get_page_source(self):
        self.browser.get(self.link)
        page_source = self.browser.page_source
        self.browser.close()
        return page_source

    def _get_page_soup(self):
        return BeautifulSoup(self.page_source, 'lxml')

    def _get_date_time(self):
        date_time_soup = self.soup.find(attrs=MatchPageSelectors.DATA_TIME_SELECTOR)
        date_time = datetime.datetime.strptime(date_time_soup.text, '%d.%m.%Y %H:%M')
        return date_time

    def _get_tournament(self):
        tournament_soup = self.soup.select_one(MatchPageSelectors.TOURNAMENT_AND_ROUND_SELECTOR)
        tournament = re.match(r'(.*) - ', tournament_soup.text).group(1)
        return tournament

    def _get_country(self):
        country_soup = self.soup.select_one(MatchPageSelectors.COUNTRY_SELECTOR)
        country = re.match(r'\w*', str(country_soup.next)).group(0)
        return country

    def _get_round(self):
        round_soup = self.soup.select_one(MatchPageSelectors.TOURNAMENT_AND_ROUND_SELECTOR)
        round_ = int(re.match(r'.*Round (\d+)', round_soup.text).group(1))
        return round_

    def _create_team_1(self):
        return HomeTeam(self)

    def _create_team_2(self):
        return AwayTeam(self)


class Team:

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

    def __str__(self):
        return self.name

    def get_name(self, selector):
        name = self.soup.select_one(selector).text
        return name

    def get_goals(self, selector):
        goals = self.soup.select_one(selector).text
        return goals


class HomeTeam(Team):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.get_name(MatchPageSelectors.TEAM_HOME_NAME)
        self.goals = self.get_goals(MatchPageSelectors.TEAM_HOME_GOALS)

        # stats from table
        self.ball_possession = self._get_stat(1)
        self.goal_attempts = self._get_stat(2)
        self.shots_on_goal = self._get_stat(3)
        self.shots_of_goal = self._get_stat(4)
        self.blocked_shots = self._get_stat(5)
        self.free_kicks = self._get_stat(6)
        self.corner_kicks = self._get_stat(7)
        self.offsides = self._get_stat(8)
        self.goalkeeper_saves = self._get_stat(9)
        self.fouls = self._get_stat(10)
        self.total_passes = self._get_stat(11)
        self.completed_passes = self._get_stat(12)
        self.tackles = self._get_stat(13)
        self.attacks = self._get_stat(14)
        self.dangerous_attacks = self._get_stat(15)

    def _get_stat(self, number_of_stat):
        value = self.soup.select('.statRow .statText--homeValue')[number_of_stat-1].text
        return value


class AwayTeam(Team):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = self.get_name(MatchPageSelectors.TEAM_AWAY_NAME)
        self.goals = self.get_goals(MatchPageSelectors.TEAM_AWAY_GOALS)

        # stats from table
        self.ball_possession = self._get_stat(1)
        self.goal_attempts = self._get_stat(2)
        self.shots_on_goal = self._get_stat(3)
        self.shots_of_goal = self._get_stat(4)
        self.blocked_shots = self._get_stat(5)
        self.free_kicks = self._get_stat(6)
        self.corner_kicks = self._get_stat(7)
        self.offsides = self._get_stat(8)
        self.goalkeeper_saves = self._get_stat(9)
        self.fouls = self._get_stat(10)
        self.total_passes = self._get_stat(11)
        self.completed_passes = self._get_stat(12)
        self.tackles = self._get_stat(13)
        self.attacks = self._get_stat(14)
        self.dangerous_attacks = self._get_stat(15)

    def _get_stat(self, number_of_stat):
        value = self.soup.select('.statRow .statText--awayValue')[number_of_stat-1].text
        return value


if __name__ == '__main__':
    a = LeaguePage('https://www.flashscore.ru/football/england/premier-league-2018-2019/results/', wait=3)
    pass
