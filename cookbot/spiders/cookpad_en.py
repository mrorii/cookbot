#!/usr/bin/env python

import os
import re
import urlparse

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector

from cookbot.items import CookpadRecipe, Ingredient


class CookpadEnSpider(CrawlSpider):
    name = 'cookpad_en'
    allowed_domains = ['en.cookpad.com']
    download_delay = 1

    start_urls = [
        'https://en.cookpad.com/categories/vegetables',
        'https://en.cookpad.com/categories/meat',
        'https://en.cookpad.com/categories/fish',
        'https://en.cookpad.com/categories/salad',
        'https://en.cookpad.com/categories/rice',
        'https://en.cookpad.com/categories/noodles',
        'https://en.cookpad.com/categories/pasta-gratin',
        'https://en.cookpad.com/categories/soup-stew',
        'https://en.cookpad.com/categories/bento',
        'https://en.cookpad.com/categories/tofu-soybeans',
        'https://en.cookpad.com/categories/egg',
        'https://en.cookpad.com/categories/flour',
        'https://en.cookpad.com/categories/sauce-dressing',
        'https://en.cookpad.com/categories/healthy-meal',
        'https://en.cookpad.com/categories/party',
        'https://en.cookpad.com/categories/spice-herb',
        'https://en.cookpad.com/categories/yogurt',
        'https://en.cookpad.com/categories/miso-vinegar-fermentation',
        'https://en.cookpad.com/categories/sea-vegetables',
        'https://en.cookpad.com/categories/hot-pot-and-nabe',
        'https://en.cookpad.com/categories/japanese-new-year',
        'https://en.cookpad.com/categories/regional',
        'https://en.cookpad.com/categories/christmas',
        'https://en.cookpad.com/categories/finger%20food',
        'https://en.cookpad.com/categories/bread',
        'https://en.cookpad.com/categories/korokke-croquette',
        'https://en.cookpad.com/categories/chinese',
    ]

    rules = (
        # Follow pagination
        Rule(SgmlLinkExtractor(allow=(r'categories/\S+/page/\d+',)), follow=True),

        # Extract recipes
        Rule(SgmlLinkExtractor(allow=(r'recipe/\d+',)), callback='parse_recipe')
    )

    def parse_recipe(self, response):
        hxs = HtmlXPathSelector(response)
        recipe = CookpadRecipe()

        # id
        recipe['id'] = int(re.findall(r'recipe/(\d+)', response.url)[0])

        # name
        recipe['name'] = hxs.select("//h1[@class='recipe_title']/text()")[0] \
                            .extract().strip()

        # description
        recipe['description'] = ''.join(hxs.select("//div[@class='summary']/p/text()") \
                                           .extract()).strip()

        # ingredients
        ingredients = []
        ingredient_basepath = ("//table[@class='ingredients_list']/"  # no tbody required
                               "tr[@class='ingredient_row']")
        ingredient_names = hxs.select("{}/td[@class='ingredient_name']/text()" \
                                      .format(ingredient_basepath)).extract()
        ingredient_quantities = hxs.select("{}/td[@class='ingredient_quantity']/text()" \
                                           .format(ingredient_basepath)).extract()
        ingredients = []
        for name, quantity in zip(ingredient_names, ingredient_quantities):
            ingredient = Ingredient()
            ingredient['name'] = name
            ingredient['quantity'] = quantity
            ingredients.append(ingredient)
        recipe['ingredients'] = ingredients

        # instructions
        recipe['instructions'] = hxs.select(
            "//div[@class='step_memo_text']/text()"
        ).extract()

        # advice and history
        recipe['advice'] = ' '.join(hxs.select("//div[@class='memo block']/p/text()").extract())
        recipe['history'] = ' '.join(hxs.select("//div[@class='history block']/p/text()").extract())

        return recipe
