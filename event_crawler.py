import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime

import config


def parse_date(month, day):
    date = datetime.strptime(f'{month} {day} {datetime.today().year} +0000', '%b %d %Y %z')
    return date


def parse_entry(li):
    link_node = li.select_one("a")
    venue = li.select_one(".toh").text.strip()
    month = li.select_one(".up-month").text.strip()
    day = li.select_one(".up-day").text.strip()[:2]
    return {
        "title": link_node["title"],
        "url": link_node["href"],
        "date": parse_date(month, day),
        "location": venue
    }


def crawl_entries():
    logging.info(f'Crawling: {config.CRAWLER_URL}')
    html = requests.get(config.CRAWLER_URL).text
    soup = BeautifulSoup(html, 'html.parser')
    entries = []
    for li in soup.select(".resgrid-ul li.item.event-item.box-link"):
        entries.append(parse_entry(li))

    return entries
