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
    """
        Active main spider which crawls through the links provided

    """
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

    """
    
    Parsing block for the default rss 
    
    """

    def parse_node(self, response, node):
        item = {}
        source = response.meta.get('source')
        category = response.meta.get('category')
        self.logger.info('Hi, this is a <%s> node!: %s', self.itertag, ''.join(node.extract()))

        title = node.xpath('title/text()').extract_first()
        item['title'] = title
        item['link'] = node.xpath('link/text()').extract_first()
        item['published'] = node.xpath('pubDate/text()').extract_first()
        description = node.xpath('description/text()').extract_first()
        item['summary'] = cleanhtml(description)
        item['source'] = response.meta.get('source')
        if source == "The Guardian":
            item['image'] = node.xpath("*[local-name()='content'][@width='460']/@url").extract_first()
        else:
            media = node.xpath("*[local-name()='content']/@url").extract_first()
            thumb = node.xpath("*[local-name()='thumbnail']/@url").extract_first()
            full = node.xpath("fullimage/text()").extract_first()
            enclosure = node.xpath("enclosure/@url").extract_first()
            if media:
                item['image'] = media
            elif thumb:
                item['image'] = thumb
            elif enclosure:
                item['image'] = enclosure
            elif full:
                item['image'] = full


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
        insertingBlock(item, source, category)

    def handle_spider_closed(spider, reason):
        logging.info('Work time:' + str(time.time() - start))

    dispatcher.connect(handle_spider_closed, signals.spider_closed)


def cleanhtml(raw_html):
    """
    To remove html tags in the summary
    """
    if raw_html is not None:
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, ' ', raw_html)
        cleanr = re.compile('&.*?;')
        cleantext = re.sub(cleanr, '', cleantext)
        cleanr = re.compile('\n')
        cleantext = re.sub(cleanr, '', cleantext)
        cleantext=cleantext.strip()
        return cleantext
    else:
        return ""


def insertingBlock(item, source, category):
    """

       Inserting  function with respect to the collection name parsed

       """

    if db[category].count() == 0:
        db[category].insert_one(item)
    else:
        tags = str(item['uTag'])
        if db.Main.find_one(
                {'uTag': tags}, {'_id': 1}):
            pass
        else:
            insertDoc = db.Main.insert_one(item)
            db[category].insert_one(item)
            if insertDoc:
                logging.debug('Inserted new for ' + category + "   for  " + source
                              )
                logging.debug('\n')
            else:
                logging.debug('Error in insertion for ' +
                              category + "   for  " + source)
                logging.debug('\n')
