import scrapy
import re
import logging
import time
import RAKE
from scrapy.http import Request
from datetime import datetime
from scrapy.spiders import XMLFeedSpider
from pymongo import MongoClient
from PJH.scrapLinks import Links
from PJH.items import Job_Item
from PJH.items import Job_Categories_Item
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from random import shuffle
from bson.json_util import dumps
from scrapy.shell import inspect_response
import hashlib

import pprint

import json

now = datetime.now()

start = time.time()

connection = MongoClient('mongodb://localhost:27017/PJH')
db = connection.Culminate


# class Spider(scrapy.Spider):
#     name = "scrap"
# 
#     def start_requests(self):
#         urls = [
#             'https://wiki.vtiger.com/index.php/Webservices_tutorials',
#         ]
#         for url in urls:
#             yield scrapy.Request(url=url, callback=self.parse)
# 
#     def parse(self, response):
# 
# 
#         filename = 'quotes-%s.html'
#         with open(filename, 'wb') as f:
#             f.write(response.body)
#         self.log('Saved file %s' % filename)


class Spider(XMLFeedSpider):
    """
        Active main spider which crawls through the links provided

    """
    name = "scrap"
    allowed_domains = [""]
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
        for url in Links:
            yield scrapy.Request(url=url[0], callback=self.parse)

    """

    Parsing block for the default rss

    """

    def parse(self, response):

        for j in response.xpath('//*[@type="tuple"]'):
            item = Job_Item()
            try:
                title=j.xpath('a/ul/li/text()').extract_first()
                item['title'] = title
                item['hiringOrganization'] = j.xpath('a/span[@class="org"]/text()').extract_first()
                item['link'] = j.xpath('a/@href').extract_first()
                item['experienceRequirements'] = j.xpath('a/span[@class="exp"]/text()').extract_first()
                item['jobLocation'] = j.xpath('a/span[@class="loc"]/span/text()').extract_first()
                item['skills'] = j.xpath('a/div/div/span[@class="skill"]/text()').extract_first()
                item['JobDescription'] = j.xpath('a/div/span[@class="desc"]/text()').extract_first()
                item['baseSalary'] = j.xpath('div/span[@class="salary  "]/text()').extract_first()
                item['jobPoster'] = j.xpath('div/div[@class="rec_details"]/a[@class="rec_name active"]/text()').extract_first()
                item['date'] = j.xpath('div/div[@class="rec_details"]/span[@class="date"]/text()').extract_first()
                item['uTag'] = hashlib.sha256(
                    title.encode('utf-8')).hexdigest()[:16]
                item['created_at'] = str(datetime.now())
                insertingBlock(item)


            except AttributeError:
                print("Baljh")


                
    def handle_spider_closed(spider, reason):
        print("Closed handle")

    dispatcher.connect(handle_spider_closed, signals.spider_closed)







def insertingBlock(item):
    """

       Inserting  function with respect to the collection name parsed

       """
    category='jobs'
    if db[category].count() == 0:
        db[category].insert_one(item)
    else:
        tags = str(item['uTag'])
        if db.jobs.find_one(
                {'uTag': tags}, {'_id': 1}):
            pass
        else:
            insertDoc = db.jobs.insert_one(item)
            db[category].insert_one(item)
            if insertDoc:
                logging.debug('Inserted new for ' + category + "   for  " + item['title']
                              )
                logging.debug('\n')
            else:
                logging.debug('Error in insertion for ' +
                              category + "   for  " + item['title'])
                logging.debug('\n')
