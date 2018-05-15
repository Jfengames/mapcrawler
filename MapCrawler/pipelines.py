# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from MapCrawler.items import PoiInfoItem
from MapCrawler.database_operations import GaodeMapSceneDbOper

import logging
logger = logging.getLogger(__name__)

BATCH_INSERT_NUM = 100

class MapcrawlerPipeline(object):
    def open_spider(self,spider):
        # self.abstract_file = open('摘要.txt','w',encoding='utf-8')
        # self.detail_file = open('详情.txt','w',encoding='utf-8')
        self.db = GaodeMapSceneDbOper()
        self.items_to_add = []

    def process_item(self, item, spider):
        #
        # if isinstance(item, PoiAbstractItem):
        #     self.abstract_file.write(item.__str__()+'\n')
        # if isinstance(item,PoiDetailItem):
        #     self.detail_file.write(item.__str__()+'\n')
        self.items_to_add.append(item)
        logger.debug('收到新的item，等待插入数据库，当前队列里为%s'%len(self.items_to_add))
        if len(self.items_to_add) >= BATCH_INSERT_NUM:
            self.db.replace_items(self.items_to_add)
            self.items_to_add.clear()
            logger.debug('批量插入数据库完成')

        return item

    def close_spider(self,spider):
        # self.abstract_file.close()
        # self.detail_file.close()

        if self.items_to_add:
            self.db.replace_items(self.items_to_add)
            logger.debug('队列里的剩余item插入数据库')



