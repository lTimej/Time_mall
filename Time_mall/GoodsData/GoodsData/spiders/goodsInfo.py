import scrapy


class GoodsinfoSpider(scrapy.Spider):
    name = 'goodsInfo'
    allowed_domains = ['www.jd.com']
    start_urls = ['http://www.jd.com/']

    def parse(self, response):
        pass
