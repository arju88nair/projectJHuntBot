import scrapy

class Job_Categories_Item(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field()

class Job_Item(scrapy.Item):
    title = scrapy.Field()
    hiringOrganization = scrapy.Field()
    experienceRequirements = scrapy.Field()
    jobLocation = scrapy.Field()
    skills = scrapy.Field()
    JobDescription = scrapy.Field()
    baseSalary = scrapy.Field()
    jobPoster = scrapy.Field()
    date = scrapy.Field()
    link = scrapy.Field()
    jobType = scrapy.Field()
    jobCategory = scrapy.Field()
    depth = scrapy.Field()
    jobCategoryLink = scrapy.Field()
