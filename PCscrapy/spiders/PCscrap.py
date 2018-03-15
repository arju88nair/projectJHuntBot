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
from random import shuffle
from PCscrapy.geography import tags
from bson.json_util import dumps
import pprint



import json

now = datetime.now()

start = time.time()

connection = MongoClient('mongodb://localhost:27017/Culminate')
db = connection.Culminate


class Spider(XMLFeedSpider):
    """
        Active main spider which crawls through the links provided

    """
    name = "scrap"
    allowed_domains = ["feeds.feedburner.com"]
    itertag = 'item'

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.basicConfig(
        level=logging.DEBUG,
        format=
        '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%a, %d %b %Y %H:%M:%S',
        filename='weird.log',
        filemode='w')

    def start_requests(self):
        shuffle(Links)

        for url in Links:
            request = scrapy.Request(url=url[0], callback=self.parse)
            request.meta['source'] = url[1]
            request.meta['category'] = url[2]
            request.meta['type'] = url[3]
            request.meta['url'] = url[0]
            # logging.error('For ' + url[0] + ' in ' + url[2])
            yield request

    """
    
    Parsing block for the default rss 
    
    """

    def parse_node(self, response, node):
        item = {}
        source = response.meta.get('source')
        category = response.meta.get('category')
        # self.logger.info('Hi, this is a <%s> node!: %s', self.itertag, ''.join(node.extract()))

        title = node.xpath('title/text()').extract_first()
        item['title'] = cleanhtml(title)
        if title:
            item['link'] = node.xpath('link/text()').extract_first()
            item['published'] = node.xpath('pubDate/text()').extract_first()
            description = node.xpath('description/text()').extract_first()
            description = cleanhtml(description)
            item['summary'] = description
            item['source'] = response.meta.get('source')
            tagText=str(title)+str(description)
            # countryClass=tags.getCountry(tagText)

            # if len(countryClass) > 0:
            #
            #     item['category'] = "India"
            # else:
            item['category'] = response.meta.get('category')

            if source == "The Guardian":
                item['image'] = node.xpath("*[local-name()='content'][@width='460']/@url").extract_first()
            else:
                media = node.xpath("*[local-name()='content']/@url").extract_first()
                thumb = node.xpath("*[local-name()='thumbnail']/@url").extract_first()
                full = node.xpath("fullimage/text()").extract_first()
                image = node.xpath("image/text()").extract_first()
                enclosure = node.xpath("enclosure/@url").extract_first()
                if media:
                    item['image'] = media
                elif thumb:
                    item['image'] = thumb
                elif enclosure:
                    item['image'] = enclosure
                elif image:
                    item['image'] = image
                elif full:
                    item['image'] = full


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
            db.Temp.insert_one(item)
            insertingBlock(item, source, category)

    def handle_spider_closed(spider, reason):
        # randomiseInsert()
        # popularInsert()

    dispatcher.connect(handle_spider_closed, signals.spider_closed)


def cleanhtml(raw_html):
    """
    To remove html tags in the summary
    """
    if raw_html is not None:
        cleanr = re.compile(r'<w:(.*)>(.*)</w:(.*)>')
        cleantext = re.sub(cleanr, ' ', raw_html)
        cleanr = re.compile(r'<[^>]+>')
        cleantext = re.sub(cleanr, ' ', cleantext)
        cleanr = re.compile('&apos;')
        cleantext = re.sub(cleanr, "'", cleantext)
        cleanr = re.compile('&.*?;')
        cleantext = re.sub(cleanr, '', cleantext)
        cleanr = re.compile('\n')
        cleantext = re.sub(cleanr, '', cleantext)
        cleanr = re.compile('{.*?}')
        cleantext = re.sub(cleanr, '', cleantext)
        cleanr = re.compile('/.*?/')
        cleantext = re.sub(cleanr, '', cleantext)
        cleanr = re.compile('table.MsoNormalTable')
        cleantext = re.sub(cleanr, '', cleantext)
        cleantext = cleantext.strip()
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


# def randomiseInsert():
#     temp = list(db.Temp.find({}, {'_id': False}))
#     shuffle(temp)
#     if temp:
#         for item in temp:
#             insertingBlock(item, item['source'], item['category'])
#         db.Temp.drop()
#         logging.info('Work time:' + str(time.time() - start))
#         logging.info('Ended at ' + now.strftime("%Y-%m-%d %H:%M"))


def popularInsert():
    popular = list(db.PopularPosts.aggregate([
        {
            '$lookup':
                {
                    'from': "Main",
                    'localField': "idPost",
                    'foreignField': "uTag",
                    'as': "Main"
                }
        },
        {
            '$project': {
                '_id': 1,
                "idPost": 1,
                "Main": 1,
                "count": {'$size': "$users"}

            }
        },

        {'$sort': {'count': -1, 'created_at': -1}},
        {
            '$limit': 8
        }
    ]))
    db.Popular.remove()
    for item in popular:
        db.Popular.insert(item)

