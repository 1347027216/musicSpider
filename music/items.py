# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class WyMusicItem(scrapy.Item):
    # define the fields for your item here like:
    musicMenuName = scrapy.Field()
    musicMenuAuthor = scrapy.Field()
    musicMenuImg = scrapy.Field()
    musicMenuTime = scrapy.Field()
    musicMenuList = scrapy.Field()

class QqMusicItem(scrapy.Item):
    singerId = scrapy.Field()
    singerMid = scrapy.Field()
    singerName = scrapy.Field()
    singerImg = scrapy.Field()
    singerDisc = scrapy.Field()
    singerAchievement = scrapy.Field()
    singerMusic = scrapy.Field()
