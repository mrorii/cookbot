# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class Ingredient(Item):
    name = Field()
    quantity = Field()


class Recipe(Item):
    id = Field()
    name = Field()
    author = Field()
    description = Field()
    ingredients = Field()
    instructions = Field()
    published_date = Field()
    updated_date = Field()


class CookpadRecipe(Recipe):
    category = Field() # Stores only the main category
    categories = Field() # Stores all of the relevant categories, including parents
    report_count = Field()
    comment_count = Field()
    advice = Field()
    history = Field()
    image_main = Field()
    images_instruction = Field()
    related_keywords = Field()


class AllrecipesRecipe(Recipe):
    category = Field()
    prep_time = Field()
    cook_time = Field()
    rating = Field()
    nutrients = Field()
