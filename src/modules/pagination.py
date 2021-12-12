from bs4 import BeautifulSoup


def check_has_next_page(html_bs: BeautifulSoup):
    """
    Determines if there's a next page available in a BS4 HTML results page.
    :param html_bs:
    :return:
    """
    next_div = html_bs.find('div', attrs={'class': 'pagination'}).find_all('span', attrs={'class': 'next'})

    return len(next_div) > 0
