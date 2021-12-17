from bs4 import BeautifulSoup

from modules.logger import log, LogLevels


def check_has_next_page(html_bs: BeautifulSoup):
    """
    Determines if there's a next page available in a BS4 HTML results page.
    :param html_bs:
    :return:
    """
    log("Entering check_has_next_page method", LogLevels.LOG_LEVEL_DEBUG)

    next_div = html_bs.find('div', attrs={'class': 'pagination'}).find_all('span', attrs={'class': 'next'})

    return len(next_div) > 0
