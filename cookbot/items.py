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
    # memo = Field()
    # history = Field()
    report_count = Field()
    comment_count = Field()
