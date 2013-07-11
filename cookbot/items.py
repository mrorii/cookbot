# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field


class Recipe(Item):
    id = Field()
    name = Field()
    author = Field()
    description = Field()
    ingredients = Field()
    directions = Field()


class CookpadRecipe(Recipe):
    category = Field()
    report_count = Field()
    comment_count = Field()
    # memo = Field()
    # history = Field()


class AllrecipesRecipe(Recipe):
    category = Field()
    prep_time = Field()
    cook_time = Field()
    rating = Field()
    nutrients = Field()
