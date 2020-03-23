from selenium.webdriver.common.by import By


class LeaguePageSelectors:

    SHOW_MORE_MATCHES_BUTTON = (By.CLASS_NAME, 'event__more')
    MATCH = (By.CSS_SELECTOR, '.event__match')
    SCROLL_TO_BOTTOM_SCRIPT = 'window.scrollTo(0, document.body.scrollHeight);'


class MatchPageSelectors:
    DATA_TIME_SELECTOR = {'id': 'utime'}
    TOURNAMENT_AND_TOUR_SELECTOR = {'class': 'description__country'}
    COUNTRY_SELECTOR = '.description__country'
    TOURNAMENT_AND_ROUND_SELECTOR = '.description__country>a'
    TEAM_1_SELECTOR = '.home-box .tname a'
    TEAM_2_SELECTOR = '.away-box .tname a'