#!/usr/bin/env python

import os
import re
import urlparse

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector

from cookbot.items import CookpadRecipe, Ingredient


class CookpadSpider(CrawlSpider):
    name = 'cookpad'
    allowed_domains = ['cookpad.com']
    download_delay = 1

    start_urls = [
        'http://cookpad.com/category/10',   # Vegetable
        'http://cookpad.com/category/11',   # Meat
        'http://cookpad.com/category/12',   # Fish
        'http://cookpad.com/category/2',    # Rice
        'http://cookpad.com/category/6',    # Pasta/ Gratin
        'http://cookpad.com/category/9',    # Noodles
        'http://cookpad.com/category/15',   # Stew, soup
        'http://cookpad.com/category/14',   # Salad
        'http://cookpad.com/category/1627', # Croquette
        'http://cookpad.com/category/1607', # "Nabemono"
        'http://cookpad.com/category/1641', # "Konamono"
        'http://cookpad.com/category/13',   # Egg / Soy
        'http://cookpad.com/category/1436', # Seaweed, konjac
        'http://cookpad.com/category/1371', # Sauce, dressing
        'http://cookpad.com/category/1643', # Healthy
        # 'http://cookpad.com/category/221',  # Cookie
        # 'http://cookpad.com/category/79',   # Cheese cake
        # 'http://cookpad.com/category/407',  # Pound cake
        # 'http://cookpad.com/category/336',  # Sponge cake
        # 'http://cookpad.com/category/76',   # Roll cake
        # 'http://cookpad.com/category/399',  # Chiffon cake
        # 'http://cookpad.com/category/339',  # Tarte
        # 'http://cookpad.com/category/78',   # Pie
        # 'http://cookpad.com/category/431',  # Chocolate
        # 'http://cookpad.com/category/59',   # Muffin
        # 'http://cookpad.com/category/772',  # Scone
        # 'http://cookpad.com/category/727',  # Madeleine
        # 'http://cookpad.com/category/402',  # Pudding
        # 'http://cookpad.com/category/427',  # Choux a la creme
        # 'http://cookpad.com/category/721',  # Cold sweets
        # 'http://cookpad.com/category/731',  # Japanese sweets
        # 'http://cookpad.com/category/741',  # Other sweets
        # 'http://cookpad.com/category/1565', # Cream / Sauce / Jam
        'http://cookpad.com/category/502', # recipes using bread
        'http://cookpad.com/category/849', # Sandwich / Hamburger
        'http://cookpad.com/category/1651', # Bento
        'http://cookpad.com/category/1600', # Spice & Herb
        'http://cookpad.com/category/1444', # Party
        'http://cookpad.com/category/1529', # Japanese New Year
        'http://cookpad.com/category/1510', # Christmas
        'http://cookpad.com/category/1780', # Regional
        'http://cookpad.com/category/1733', # Fermented items
        'http://cookpad.com/category/1756', # Appetizer (finger food)
        'http://cookpad.com/category/1680', # Yogurt
        'http://cookpad.com/category/1766', # Chinese
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

        # id
        recipe['id'] = int(re.findall(r'recipe/(\d+)', response.url)[0])

        # name
        recipe['name'] = hxs.select("//div[@id='recipe-title']/h1/text()")[0] \
                            .extract().strip()

        # author
        recipe['author'] = int(
            hxs.select("//a[@id='recipe_author_name']/@href").re('(\d+)')[0]
        )

        # description
        recipe['description'] = ''.join(hxs.select("//div[@id='description']/text()") \
                                           .extract()).strip()

        # ingredients
        ingredients = []
        ingredient_basepath = ("//div[@id='ingredients']/div[@id='ingredients_list']/"
                               "div[@class='ingredient ingredient_row']")
        ingredient_nodes = hxs.select(ingredient_basepath)
        for ingredient_node in ingredient_nodes:
            try:
                if ingredient_node.select('div/span/a'):
                    # keyword ingredient
                    name = ingredient_node.select('div[1]/span/a/text()').extract()[0]
                else:
                    # normal ingredient
                    name = ingredient_node.select('div[1]/span/text()').extract()[0]
                quantity = ingredient_node.select('div[2]/text()').extract()[0]
            except:
                continue

            ingredient = Ingredient()
            ingredient['name'] = name
            ingredient['quantity'] = quantity
            ingredients.append(ingredient)
        recipe['ingredients'] = ingredients

        # instructions
        recipe['instructions'] = hxs.select(
            "//dd[@class='instruction']/p/text()"
        ).extract()

        # leaf category
        referer = response.request.headers.get('Referer')
        recipe['category'] = int(os.path.basename(urlparse.urlsplit(referer).path))

        # all categories (including leaf, internal, and root nodes)
        categories = hxs.select("//div[@id='category_list']/ul/li/a/@href").re(r'\d+')
        recipe['categories'] = map(lambda category: int(category), categories)

        # report count
        try:
            recipe['report_count'] = int(
                ''.join(hxs.select("//li[@id='tsukurepo_tab']/a/span/text()").re('(\d+)'))
            )
        except:
            recipe['report_count'] = 0

        # comment count
        try:
            recipe['comment_count'] = int(
                ''.join(hxs.select("//li[@id='comment_tab']/a/span/text()").re('(\d+)'))
            )
        except:
            recipe['comment_count'] = 0

        # advice and history
        for text in ('advice', 'history'):
                recipe[text] = ''.join(hxs.select("//div[@id='{}']/text()".format(text))
                                          .extract()).strip()

        # related keywords
        recipe['related_keywords'] = hxs.select("//div[@class='related_keywords']/a/text()") \
                                        .extract()

        # main image
        image_main = hxs.select("//div[@id='main-photo']/img/@src").extract()
        recipe['image_main'] = image_main[0] if image_main else []

        # instruction images
        recipe['images_instruction'] = hxs.select(
            "//dd[@class='instruction']/div/div[@class='image']/img/@src").extract()

        # published date
        recipe['published_date'] = hxs.select(
            "//div[@id='recipe_id_and_published_date']/span[2]/text()").re('\d{2}/\d{2}/\d{2}')[0]

        # udpated date
        recipe['updated_date'] = hxs.select(
            "//div[@id='recipe_id_and_published_date']/span[3]/text()").re('\d{2}/\d{2}/\d{2}')[0]

        return recipe
