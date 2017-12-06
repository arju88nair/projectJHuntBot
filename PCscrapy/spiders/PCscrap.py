import scrapy
import re

from scrapy.spiders import XMLFeedSpider

from pymongo import MongoClient
from PCscrapy.scrapLinks import Links

# from YahooScrape.items import YahooScrapeItem
connection = MongoClient('mongodb://localhost:27017/Test')
db = connection.Test


class Spider(XMLFeedSpider):
    name = "scrap"
    allowed_domains = ["feeds.feedburner.com"]
    itertag = 'item'

    def start_requests(self):
        for url in Links:
            request = scrapy.Request(url=url[0], callback=self.parse)
            request.meta['source'] = url[1]
            yield request

    def parse_node(self, response, node):
        response.meta.get('source')
        item = {}
        item['title'] = node.xpath('title/text()', ).extract_first()  # define XPath for title
        item['link'] = node.xpath('link/text()').extract_first()
        item['pubDate'] = node.xpath('updatedAt/text()').extract_first()
        description = node.xpath('description/text()').extract_first()
        item['description'] = cleanhtml(description)
        item['source'] = response.meta.get('source')
        db.Blah.insert_one(item)

        return node.xpath('title/text()', ).extract_first()


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext
