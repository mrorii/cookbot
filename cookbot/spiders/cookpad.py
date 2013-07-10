#!/usr/bin/env python

from scrapy import log
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider

from cookbot.items import Recipe

class CookpadSpider(CrawlSpider):
    name = 'cookpad'
    allowed_domains = ['cookpad.com']
    download_delay = 3

    start_urls = [
        'http://cookpad.com/category/11', # Meat
        'http://cookpad.com/category/10', # Vegetable
    ]

    rules = (
        # Follow pagination
        Rule(SgmlLinkExtractor(allow=(r'category/\d+\?page=\d+',)), follow=True),

        # Extract recipes
        Rule(SgmlLinkExtractor(allow=(r'recipe/\d+',)), callback='parse_recipe')
    )

    def parse_recipe(self, response):
        hxs = HtmlXPathSelector(response)
        recipe = Recipe()
        recipe['name'] = hxs.select("//div[@id='recipe-title']/h1/text()").extract()
        recipe['author'] = hxs.select("//a[@id='recipe_author_name']/@href").extract()
        return recipe
