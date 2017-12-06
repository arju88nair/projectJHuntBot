import scrapy
import re
import datetime
import logging
# import RAKE
from calendar import timegm
from datetime import datetime
import hashlib
# from fuzzywuzzy import fuzz

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
            request.meta['category'] = url[2]
            request.meta['type'] = url[3]
            yield request

    def parse_node(self, response, node):

        item = {}
        source = response.meta.get('source')
        title = node.xpath('title/text()', ).extract_first()
        item['title'] = title
        item['link'] = node.xpath('link/text()').extract_first()
        item['published'] = node.xpath('pubDate/text()').extract_first()
        description = node.xpath('description/text()').extract_first()
        item['summary'] = cleanhtml(description)
        item['source'] = response.meta.get('source')
        if source == "The Guardian":
            item['media'] = node.xpath("*[local-name()='content'][@width='460']/@url").extract_first()
        else:
            item['media'] = node.xpath("*[local-name()='content']/@url").extract_first()

        item['category'] = response.meta.get('category')
        item['type'] = response.meta.get('type')
        item['uTag'] = hashlib.sha256(
            str(title).encode('utf-8')).hexdigest()[:16]
        item['created_at'] = str(datetime.now())
        db[response.meta.get('category')].insert_one(item)


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    return cleantext
