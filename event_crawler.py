import logging
import math
import time

import datetime
from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import config
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType


def parse_date(month, day):
    date = datetime.datetime.strptime(f'{month} {day} {datetime.datetime.today().year}', '%b %d %Y')
    date = date.replace(tzinfo=datetime.timezone.utc)

    # because the year is not provided and old events are not provided past date must be a year later
    current_date = datetime.datetime.today()
    current_date = current_date.replace(tzinfo=datetime.timezone.utc)
    is_date_in_past = (date - current_date).total_seconds() < 0
    if is_date_in_past:
        date = date.replace(year=date.year + 1)

    return date


def parse_entry(li: WebElement):
    link_node = li.find_element(By.CSS_SELECTOR, ".meta a")
    title = link_node.get_attribute("title").strip()
    url = link_node.get_attribute("href")
    venue = li.find_element(By.CSS_SELECTOR, ".meta .toh").get_attribute("innerHTML").strip()
    month = li.find_element(By.CSS_SELECTOR, ".meta .up-month").get_attribute("innerHTML").strip()
    day = li.find_element(By.CSS_SELECTOR, ".meta .up-day").get_attribute("innerHTML").strip()[:2]

    return {
        "title": title,
        "url": url,
        "date": parse_date(month, day),
        "location": venue
    }


def is_ready(browser):
    return browser.execute_script(r"""
        return document.readyState === 'complete'
    """)


def is_in_next_couple_weeks(entry):
    limit_date = datetime.datetime.today() + datetime.timedelta(weeks=config.SHOW_NEXT_WEEKS)
    limit_date = limit_date.replace(tzinfo=datetime.timezone.utc)
    is_in_next_couple_weeks = (entry["date"] - limit_date).total_seconds() < 0
    return is_in_next_couple_weeks


class EventCrawler:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        self.browser = webdriver.Chrome(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install(), options=options)

    def __del__(self):
        self.browser.close()

    def crawl_entries(self):
        logging.info(f'Crawling: {config.CRAWLER_URL}')

        # open webpage and wait for it to load
        self.browser.get(config.CRAWLER_URL)

        WebDriverWait(self.browser, 5).until(is_ready)

        # count events

        amount_events = int(''.join([c for c in self.browser.title[:3] if c.isdigit()]))
        logging.info(f'Found {amount_events} events')

        amount_clicks_load_more = math.ceil((amount_events - 15) / 15.0)

        # click on load more button up to 3 times
        for i in range(amount_clicks_load_more):
            self.browser.execute_script('document.getElementById("show_more_events").click()')
            time.sleep(1)
            WebDriverWait(self.browser, 5).until(is_ready)

        event_selector = ".resgrid-ul li.item.event-item.box-link"
        event_elements = self.browser.find_elements(By.CSS_SELECTOR, event_selector)

        entries = []
        for li in event_elements:
            entries.append(parse_entry(li))

        entries = list(filter(is_in_next_couple_weeks, entries))

        logging.info(entries)

        return entries
