import logging
import config
import event_crawler
from feed_builder import EventFeed

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)


def write_to_file(content):
    logging.info(f'Writing to file {config.OUTPUT_FILE}')
    file = open(config.OUTPUT_FILE, "w")
    file.write(content)
    file.close()


def main():
    entries = event_crawler.crawl_entries()
    feed = EventFeed()
    feed.add_entries(entries)
    feed_xml = feed.get_rss()
    write_to_file(feed_xml)

    logging.info(f'Generated rss:\n {feed_xml}')


if __name__ == '__main__':
    main()
