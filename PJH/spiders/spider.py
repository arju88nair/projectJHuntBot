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
                item['title'] = j.xpath('a/ul/li/text()').extract_first()
                item['hiringOrganization'] = j.xpath('a/span[@class="org"]/text()').extract_first()
                item['link'] = j.xpath('a/@href').extract_first()
                item['experienceRequirements'] = j.xpath('a/span[@class="exp"]/text()').extract_first()
                item['jobLocation'] = j.xpath('a/span[@class="loc"]/span/text()').extract_first()
                item['skills'] = j.xpath('a/div/div/span[@class="skill"]/text()').extract_first()
                item['JobDescription'] = j.xpath('a/div/span[@class="desc"]/text()').extract_first()
                item['baseSalary'] = j.xpath('div/span[@class="salary  "]/text()').extract_first()
                item['jobPoster'] = j.xpath('div/div[@class="rec_details"]/a[@class="rec_name active"]/text()').extract_first()
                item['date'] = j.xpath('div/div[@class="rec_details"]/span[@class="date"]/text()').extract_first()
                yield item
                print(item)

            except AttributeError:
                print("Baljh")


                
    def handle_spider_closed(spider, reason):
        print("Closed handle")

    dispatcher.connect(handle_spider_closed, signals.spider_closed)


def parse_Categories(self, response):
    for j in response.xpath('//div[@class="lmrWrap wrap"]/div/div/div/a'):
        item = Job_Categories_Item()
        title = j.xpath('text()').extract_first()
        url = j.xpath('@href').extract_first()
        if title != [] and url != []:
            item['link'] = url[0]
            item['title'] = title[0]
            count = 0
            yield Request(url[0], callback=self.parse_jobs,
                          meta={'jobCategory': title[0], 'count': count, 'parentLink': url[0]})
            yield item


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

# def randomiseInsert():
#     temp = list(db.Temp.find({}, {'_id': False}))
#     shuffle(temp)
#     if temp:
#         for item in temp:
#             insertingBlock(item, item['source'], item['category'])
#         db.Temp.drop()
#         logging.info('Work time:' + str(time.time() - start))
#         logging.info('Ended at ' + now.strftime("%Y-%m-%d %H:%M"))
