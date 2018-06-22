import scrapy
import re
import datetime
import logging
import time
import RAKE
from scrapy.http import Request
from datetime import datetime
import hashlib
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
        try:
            jobc = response.meta['jobCategory']
            parentLink = response.meta['parentLink']
            count = 0
            print(response.xpath('//div[@class="srp_container fl"]'))
            for j in response.xpath('//div[@itemtype="http://schema.org/JobPosting"]'):
                item = Job_Item()
                print("d")
                item['jobCategory'] = jobc
                item['depth'] = count
                item['jobCategoryLink'] = parentLink
                item['link'] = j.xpath('a/@href').extract()
                item['title'] = j.xpath('a/span[@itemprop="hiringOrganization"]/text()').extract()
                item['experienceRequirements'] = j.xpath('a/span[@itemprop="experienceRequirements"]/text()').extract()
                item['jobLocation'] = j.xpath('a/span/span[@itemprop="jobLocation"]/text()').extract()
                item['skills'] = j.xpath('a/div/div/span[@itemprop="skills"]/text()').extract()
                item['JobDescription'] = j.xpath('a/div/span[@itemprop="description"]/text()').extract()
                item['baseSalary'] = j.xpath('div/span[@itemprop="baseSalary"]/text()').extract()
                item['jobPoster'] = j.xpath('div/div/a/text()').extract()
                item['date'] = j.xpath('div/div/span[@class="date"]/text()').extract()
                item['jobType'] = j.xpath('span/@class').extract()[1]
            next_page = response.xpath('//div[@class="pagination"]/a/@href').extract()
            if next_page != []:
                ind = response.xpath('//div[@class="pagination"]/a/button/text()').extract().index(u'Next')
                yield scrapy.Request(response.urljoin(next_page[ind]), callback=self.parse_jobs \
                                     , meta={'jobCategory': jobc, 'count': count, 'parentLink': parentLink})
        except exception as e:
            print(e)

        # self.logger.info('Hi, this is a <%s> node!: %s', self.itertag, ''.join(node.extract()))

        # title = node.xpath('title/text()').extract_first()
        # item['title'] = cleanhtml(title)
        # if title:
        #     item['link'] = node.xpath('link/text()').extract_first()
        #     item['published'] = node.xpath('pubDate/text()').extract_first()
        #     description = node.xpath('description/text()').extract_first()
        #     description = cleanhtml(description)
        #     item['summary'] = description
        #     item['source'] = response.meta.get('source')
        #     tagText=str(title)+str(description)
        #     countryClass=tags.getCountry(tagText)
        #
        #     if len(countryClass) > 0:
        #
        #         item['category'] = "India"
        #     else:
        #
        #         item['category'] = response.meta.get('category')
        #
        #     if source == "The Guardian":
        #         item['image'] = node.xpath("*[local-name()='content'][@width='460']/@url").extract_first()
        #     else:
        #         media = node.xpath("*[local-name()='content']/@url").extract_first()
        #         thumb = node.xpath("*[local-name()='thumbnail']/@url").extract_first()
        #         full = node.xpath("fullimage/text()").extract_first()
        #         image = node.xpath("image/text()").extract_first()
        #         enclosure = node.xpath("enclosure/@url").extract_first()
        #         if media:
        #             item['image'] = media
        #         elif thumb:
        #             item['image'] = thumb
        #         elif enclosure:
        #             item['image'] = enclosure
        #         elif image:
        #             item['image'] = image
        #         elif full:
        #             item['image'] = full
        #
        #
        #     item['type'] = response.meta.get('type')
        #     item['uTag'] = hashlib.sha256(
        #         title.encode('utf-8')).hexdigest()[:16]
        #     item['created_at'] = str(datetime.now())
        #     Rake = RAKE.Rake('stopwords_en.txt')
        #     words = Rake.run(title)
        #     tagWordArray = []
        #     for word in words:
        #         tagWordArray.append(word[0].title())
        #     item['tags'] = tagWordArray
        #     db.Temp.insert_one(item)
        #     insertingBlock(item, source, category)

    def handle_spider_closed(spider, reason):
        print("Closed handle")




    dispatcher.connect(handle_spider_closed, signals.spider_closed)



def parse_Categories(self,response):
    for j in response.xpath('//div[@class="lmrWrap wrap"]/div/div/div/a'):
        item = Job_Categories_Item()
        title = j.xpath('text()').extract()
        url = j.xpath('@href').extract()
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



