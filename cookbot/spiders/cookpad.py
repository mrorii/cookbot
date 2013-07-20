#!/usr/bin/env python

import os
import re
import urlparse

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector

from cookbot.items import CookpadRecipe


class CookpadSpider(CrawlSpider):
    name = 'cookpad'
    allowed_domains = ['cookpad.com']
    download_delay = 1

    start_urls = [
        'http://cookpad.com/category/11',   # Meat
        'http://cookpad.com/category/10',   # Vegetable
        'http://cookpad.com/category/12',   # Fish
        'http://cookpad.com/category/2',    # Rice
        'http://cookpad.com/category/6',    # Pasta / Gratin
        'http://cookpad.com/category/9',    # Noodles
        'http://cookpad.com/category/15',   # Stew, soup
        'http://cookpad.com/category/14',   # Salad
        'http://cookpad.com/category/1607', # "Nabemono"
        'http://cookpad.com/category/1641', # "Konamono"
        'http://cookpad.com/category/13',   # Egg / Soy
        'http://cookpad.com/category/1436', # Seaweed, konjac
        'http://cookpad.com/category/1371', # Sauce, dressing
        'http://cookpad.com/category/221',  # Cookie
        'http://cookpad.com/category/79',   # Cheese cake
        'http://cookpad.com/category/78',   # Pie
        'http://cookpad.com/category/431',  # Chocolate
        'http://cookpad.com/category/721',  # Cold sweets
        'http://cookpad.com/category/731',  # Japanese sweets
        'http://cookpad.com/category/741',  # Other sweets
    ]

    rules = (
        # Follow pagination
        Rule(SgmlLinkExtractor(allow=(r'category/\d+\?page=\d+',)), follow=True),

        # Extract recipes
        Rule(SgmlLinkExtractor(allow=(r'recipe/\d+',)), callback='parse_recipe')
    )

    def parse_recipe(self, response):
        hxs = HtmlXPathSelector(response)
        recipe = CookpadRecipe()

        recipe['id'] = int(re.findall(r'recipe/(\d+)', response.url)[0])
        recipe['name'] = hxs.select("//div[@id='recipe-title']/h1/text()")[0] \
                            .extract().strip()
        recipe['author'] = int(
            hxs.select("//a[@id='recipe_author_name']/@href").re('(\d+)')[0]
        )
        recipe['description'] = ''.join(hxs.select("//div[@id='description']/text()") \
                                           .extract()).strip()

        ingredient_path = "//div[@id='ingredients']/div[@id='ingredients_list']/div[@class='ingredient_row']"

        base_ingredients = hxs.select(
            "{}/div[@class='ingredient_name']/text()".format(ingredient_path)
        ).extract()

        link_ingredients = hxs.select(
            "{}/div[@class='ingredient_name']/a/text()".format(ingredient_path)
        ).extract()

        recipe['ingredients'] = base_ingredients + link_ingredients

        referer = response.request.headers.get('Referer')
        recipe['category'] = int(os.path.basename(urlparse.urlsplit(referer).path))

        categories = hxs.select("//div[@id='category_list']/ul/li/a/@href").re(r'\d+')
        recipe['categories'] = map(lambda category: int(category), categories)

        try:
            recipe['report_count'] = int(
                hxs.select("//li[@id='tsukurepo_tab']/a/span/text()").re('(\d+)')[0]
            )
        except:
            recipe['report_count'] = 0

        try:
            recipe['comment_count'] = int(
                hxs.select("//li[@id='comment_tab']/a/span/text()").re('(\d+)')[0]
            )
        except:
            recipe['comment_count'] = 0


        for text in ('advice', 'history'):
                recipe[text] = ''.join(hxs.select("//div[@id='{}']/text()".format(text))
                                          .extract()).strip()

        recipe['related_keywords'] = hxs.select("//div[@class='related_keywords']/a/text()") \
                                        .extract()

        image_main = hxs.select("//div[@id='main-photo']/img/@src").extract()
        recipe['image_main'] = image_main[0] if image_main else []

        recipe['images_instruction'] = hxs.select(
            "//dd[@class='instruction']/div/div[@class='image']/img/@src").extract()

        return recipe
