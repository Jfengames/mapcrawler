# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PoiAbstractItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    """
    {
      "id": "B01730ISAP",
      "name": "青年居易",
      "type": "商务住宅;住宅区;住宅小区",
      "typecode": "120302",
      "biz_type": [],
      "address": "丰庆路与东风路交叉口北丰庆路2号",
      "location": "113.649028,34.804686",
      "tel": "0371-65796595",
      "distance": [],
      "biz_ext": {
        "rating": [],
        "cost": "15119.00"
      },
      "pname": "河南省",
      "cityname": "郑州市",
      "adname": "金水区",
      "importance": [],
      "shopid": [],
      "shopinfo": "0",
      "poiweight": []
    },
    """
    pname  = scrapy.Field() #省份
    cityname = scrapy.Field() #城市
    adname = scrapy.Field() #高徳adname
    typecode = scrapy.Field()
    importance = scrapy.Field()
    shopid = scrapy.Field()
    shopinfo = scrapy.Field()
    poiweight =scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()
    type=  scrapy.Field()
    typecode=  scrapy.Field()
    biz_type=  scrapy.Field()
    address=  scrapy.Field()
    location=  scrapy.Field()
    tel =  scrapy.Field()
    distance=  scrapy.Field()
    biz_ext=  scrapy.Field()

class PoiDetailItem(scrapy.Item):
    business = scrapy.Field() #
    city_adcode = scrapy.Field() #
    city_name = scrapy.Field() #
    classify = scrapy.Field() #
    code = scrapy.Field() #
    area = scrapy.Field() #
    name = scrapy.Field() #
    mainpoi = scrapy.Field() #
    navi_geametry = scrapy.Field() #
    new_keytype = scrapy.Field() #
    new_type = scrapy.Field() #
    tag = scrapy.Field() #
    building_types = scrapy.Field() #
    opening_data = scrapy.Field() #
    shape = scrapy.Field() #
    center = scrapy.Field()
    level = scrapy.Field()
