import scrapy
import re
import datetime
import logging
import time
import RAKE
from datetime import datetime
import hashlib
from scrapy.spiders import XMLFeedSpider
from pymongo import MongoClient
from PCscrapy.scrapLinks import Links
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

logging.basicConfig(filename='weird.log', level=logging.WARNING)
start = time.time()

connection = MongoClient('mongodb://localhost:27017/Test')
db = connection.Test


class Spider(XMLFeedSpider):
    name = "scrap"
    allowed_domains = ["feeds.feedburner.com"]
    itertag = 'item'
    logging.getLogger('scrapy').setLevel(logging.WARNING)

    def start_requests(self):

        for url in Links:
            request = scrapy.Request(url=url[0], callback=self.parse)
            request.meta['source'] = url[1]
            request.meta['category'] = url[2]
            request.meta['type'] = url[3]
            request.meta['url'] = url[0]
            logging.error('For ' + url[0] + ' in ' + url[2])
            yield request

    def parse_node(self, response, node):
        item = {}
        source = response.meta.get('source')
        title = node.xpath('title/text()').extract_first()
        item['title'] = title
        item['link'] = node.xpath('link/text()').extract_first()
        item['published'] = node.xpath('pubDate/text()').extract_first()
        description = node.xpath('description/text()').extract_first()
        item['summary'] = cleanhtml(description)
        item['source'] = response.meta.get('source')
        if source == "The Guardian":
            item['media'] = node.xpath("*[local-name()='content'][@width='460']/@url").extract_first()
        else:
            media = node.xpath("*[local-name()='content']/@url").extract_first()
            thumb = node.xpath("*[local-name()='thumbnail']/@url").extract_first()
            full = node.xpath("fullimage/text()").extract_first()
            if media:
                item['media'] = media
            elif thumb:
                item['media'] = thumb
            elif full:
                item['media'] = full
            else:
                item['media'] = ''

        item['category'] = response.meta.get('category')
        item['type'] = response.meta.get('type')
        item['uTag'] = hashlib.sha256(
            title.encode('utf-8')).hexdigest()[:16]
        item['created_at'] = str(datetime.now())
        Rake = RAKE.Rake('stopwords_en.txt')
        words = Rake.run(title)
        tagWordArray = []
        for word in words:
            tagWordArray.append(word[0].title())
        item['tags'] = tagWordArray
        db[response.meta.get('category')].insert_one(item)

    def handle_spider_closed(spider, reason):
        logging.info('Work time:', time.time() - start)

    dispatcher.connect(handle_spider_closed, signals.spider_closed)


def cleanhtml(raw_html):
    if (raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, ' ', raw_html)
        return cleantext
    else:
        return ""
