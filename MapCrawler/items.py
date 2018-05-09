# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MapcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    province  = scrapy.Field() #省份
    city = scrapy.Field() #城市
    resident = scrapy.Field() #居民区
    building = scrapy.Field() #建筑
    pass
