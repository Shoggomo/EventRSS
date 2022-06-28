from feedgen.feed import FeedGenerator

import config


class EventFeed:

    def __init__(self):
        self.feed = self.__init_feed__()
        self.entries = []

    def __init_feed__(self):
        fg = FeedGenerator()
        # fg.id(config.FEED_LINK)
        fg.title(config.FEED_TITLE)
        fg.link(href=config.FEED_LINK, rel='alternate')
        fg.logo(config.FEED_LOGO)
        fg.subtitle(config.FEED_SUBTITLE)
        # fg.link(href='config.FEED_LINK, rel='self')
        fg.language('de')
        return fg

    def add_entries(self, entries):
        for entry in reversed(entries):
            fe = self.feed.add_entry()
            fe.id(entry["url"])
            fe.published(entry["date"])
            fe.title(entry["title"])
            fe.link(href=entry["url"])

    def get_rss(self):
        return self.feed.rss_str(pretty=True).decode("utf-8")
