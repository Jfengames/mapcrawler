# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from MapCrawler.items import PoiDetailItem,PoiAbstractItem

class MapcrawlerPipeline(object):
    def open_spider(self,spider):
        self.abstract_file = open('摘要.txt','w',encoding='utf-8')
        self.detail_file = open('详情.txt','w',encoding='utf-8')

    def process_item(self, item, spider):

        if isinstance(item, PoiAbstractItem):
            self.abstract_file.write(item.__str__())
        if isinstance(item,PoiDetailItem):
            self.detail_file.write(item.__str__())

        return item

    def close_spider(self,spider):
        self.abstract_file.close()
        self.detail_file.close()

