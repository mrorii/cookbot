#!/usr/bin/env python

import os
import re
import urlparse

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector

from cookbot.items import AllrecipesRecipe


class AllrecipesSpider(CrawlSpider):
    name = 'allrecipes'
    allowed_domains = ['allrecipes.com']
    download_delay = 1

    start_urls = [
        'http://allrecipes.com/Recipes/World-Cuisine/African/main.aspx',
        'http://allrecipes.com/Recipes/World-Cuisine/Asian/Chinese/main.aspx',
        'http://allrecipes.com/Recipes/World-Cuisine/Asian/Japanese/Main.aspx',
        'http://allrecipes.com/Recipes/World-Cuisine/Asian/Korean/Main.aspx',
        'http://allrecipes.com/Recipes/World-Cuisine/Asian/Indian/Main.aspx',
        'http://allrecipes.com/Recipes/World-Cuisine/Asian/Thai/main.aspx',
        'http://allrecipes.com/Recipes/World-Cuisine/European/Eastern-European/main.aspx',
        'http://allrecipes.com/Recipes/World-Cuisine/European/French/main.aspx',
        'http://allrecipes.com/Recipes/World-Cuisine/European/German/main.aspx',
        'http://allrecipes.com/Recipes/World-Cuisine/European/Greek/main.aspx',
        'http://allrecipes.com/Recipes/World-Cuisine/European/Italian/main.aspx',
        'http://allrecipes.com/Recipes/World-Cuisine/Middle-Eastern/main.aspx',
        'http://allrecipes.com/Recipes/World-Cuisine/Latin-American/Mexican/main.aspx',
        'http://allrecipes.com/Recipes/USA-Regional-and-Ethnic/Cajun-and-Creole/main.aspx',
        'http://allrecipes.com/Recipes/USA-Regional-and-Ethnic/Southern-Recipes/Southern-Cooking-by-State/main.aspx',
    ]

    rules = (
        # Follow pagination
        Rule(SgmlLinkExtractor(allow=(r'Recipes/.+/.+/main.aspx\?Page=\d+',)), follow=True),

        # Extract recipes
        Rule(SgmlLinkExtractor(allow=(r'Recipe/.+/Detail.aspx',)), callback='parse_recipe')
    )

    def parse_recipe(self, response):
        hxs = HtmlXPathSelector(response)
        recipe = AllrecipesRecipe()

        recipe['name'] = hxs.select("//h1[@id='itemTitle']/text()")[0].extract().strip()

        referer = response.request.headers.get('Referer')
        category = os.path.dirname(urlparse.urlsplit(referer).path)
        recipe['category'] = category if not category.startswith('/Recipes/') \
                                      else category[len('/Recipes/'):]

        try:
            recipe['author'] = int(
                hxs.select("//span[@id='lblSubmitter']/a/@href").re('(\d+)')[0]
            )
        except:
            pass

        try:
            recipe['description'] = hxs.select("//span[@id='lblDescription']/text()")[0] \
                                       .extract().strip()
        except:
            pass

        try:
            recipe['rating'] = float(
                hxs.select("//meta[@itemprop='ratingValue']/@content").extract()[0]
            )
        except:
            pass

        recipe['ingredients'] = hxs.select("//span[@class='ingredient-name']/text()") \
                                   .extract()

        recipe['directions'] = hxs.select("//div[@class='directLeft']/ol/li/span/text()") \
                                  .extract()

        recipe['nutrients'] = {}
        recipe['nutrients']['calories'] = int(
            hxs.select("//span[@id='litCalories']/text()").extract()[0]
        )

        def parse_nutrient(name):
            return hxs.select(
                "//span[@itemprop='{}Content']/following-sibling::*/text()".format(name)
            ).extract()[0].replace(' ', '')

        for nutrient_type in ('fat', 'cholesterol', 'fiber', 'sodium',
                              'carbohydrate', 'protein'):
            try:
                recipe['nutrients'][nutrient_type] = parse_nutrient(nutrient_type)
            except:
                pass
        return recipe
