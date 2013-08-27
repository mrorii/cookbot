#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        # きょうの料理
        'http://cookpad.com/category/10',   # 野菜のおかず
        'http://cookpad.com/category/11',   # お肉のおかず
        'http://cookpad.com/category/12',   # 魚介のおかず
        'http://cookpad.com/category/2',    # ごはんもの
        'http://cookpad.com/category/6',    # パスタ・グラタン
        'http://cookpad.com/category/9',    # 麺
        'http://cookpad.com/category/15',   # シチュー・スープ・汁物
        'http://cookpad.com/category/14',   # サラダ
        'http://cookpad.com/category/1627', # コロッケ・メンチカツ
        'http://cookpad.com/category/1607', # 鍋もの
        'http://cookpad.com/category/1641', # 粉もの
        'http://cookpad.com/category/13',   # たまご・大豆加工品
        'http://cookpad.com/category/1436', # 海藻・乾物・こんにゃく
        'http://cookpad.com/category/1371', # ソース・ドレッシング
        'http://cookpad.com/category/1643', # ヘルシーおかず

        # お菓子
        'http://cookpad.com/category/221',  # クッキー
        'http://cookpad.com/category/79',   # チーズケーキ
        'http://cookpad.com/category/407',  # パウンドケーキ
        'http://cookpad.com/category/336',  # スポンジケーキ
        'http://cookpad.com/category/76',   # ロールケーキ
        'http://cookpad.com/category/399',  # シフォンケーキ
        'http://cookpad.com/category/339',  # タルト
        'http://cookpad.com/category/78',   # パイ
        'http://cookpad.com/category/431',  # チョコレートのお菓子
        'http://cookpad.com/category/59',   # マフィン
        'http://cookpad.com/category/772',  # スコーン
        'http://cookpad.com/category/727',  # マドレーヌ・フィナンシェ
        'http://cookpad.com/category/402',  # プリン
        'http://cookpad.com/category/427',  # シュークリーム
        'http://cookpad.com/category/721',  # 冷たいお菓子
        'http://cookpad.com/category/1291', # ホットケーキミックスを使ったお菓子
        'http://cookpad.com/category/726',  # 電子レンジで作れるお菓子
        'http://cookpad.com/category/731',  # 和菓子
        'http://cookpad.com/category/1452', # 野菜を使ったお菓子
        'http://cookpad.com/category/1416', # おから・豆腐・豆乳を使ったお菓子
        'http://cookpad.com/category/741',  # その他のお菓子
        'http://cookpad.com/category/1453', # アレルギー対策のお菓子
        'http://cookpad.com/category/1565', # クリーム・ソース・ジャム

        # パン
        'http://cookpad.com/category/74',   # ハードブレッド
        'http://cookpad.com/category/445',  # テーブルブレッド
        'http://cookpad.com/category/446,'  # 食パン
        'http://cookpad.com/category/447',  # 菓子パン
        'http://cookpad.com/category/448',  # デニッシュ・クロワッサン
        'http://cookpad.com/category/470',  # 天然酵母
        'http://cookpad.com/category/477',  # ピザ・野菜・おかず系パン
        'http://cookpad.com/category/478',  # アウトドア
        'http://cookpad.com/category/479',  # いろんなものでパン作り
        'http://cookpad.com/category/480',  # 揚げパン・ドーナツ
        'http://cookpad.com/category/481',  # 蒸しパン
        'http://cookpad.com/category/500',  # ホームベーカリーを使ったパン
        'http://cookpad.com/category/501',  # 世界各国のパン
        'http://cookpad.com/category/502',  # パンを使って
        'http://cookpad.com/category/781',  # ベーグル作り
        'http://cookpad.com/category/849',  # サンドイッチ・ハンバーガー
        'http://cookpad.com/category/1264', # デコレーションパン

        # その他
        'http://cookpad.com/category/1865', # 再現レシピ
        'http://cookpad.com/category/1843', # 夏に食べたい料理
        'http://cookpad.com/category/1651', # お弁当
        'http://cookpad.com/category/1600', # スパイス＆ハーブ
        'http://cookpad.com/category/1444', # おもてなし料理
        'http://cookpad.com/category/1664', # ドリンク
        'http://cookpad.com/category/1715', # 調理器具
        'http://cookpad.com/category/1529', # お正月の料理
        'http://cookpad.com/category/1510', # クリスマス
        'http://cookpad.com/category/1693', # 限られた食材で工夫
        'http://cookpad.com/category/1780', # ご当地料理
        'http://cookpad.com/category/1945', # 秋におすすめ料理
        'http://cookpad.com/category/1760', # バーベキュー・キャンプ料理
        'http://cookpad.com/category/1733', # 発酵食品・発酵調味料
        'http://cookpad.com/category/1756', # おつまみ
        'http://cookpad.com/category/1766', # 中華料理
        'http://cookpad.com/category/1909', # ハワイ料理
        'http://cookpad.com/category/1775', # Multilingual Recipes
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
                recipe[text] = ''.join(hxs.select("//div[@id='{0}']/text()".format(text))
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
