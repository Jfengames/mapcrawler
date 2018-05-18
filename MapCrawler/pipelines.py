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

        # self.items_to_add.append(item)
        # logger.debug('收到新的item，等待插入数据库，当前队列里为%s'%len(self.items_to_add))
        # if len(self.items_to_add) >= BATCH_INSERT_NUM:
        #     self.db.replace_items(self.items_to_add)
        #     self.items_to_add.clear()
        #     logger.debug('批量插入数据库完成')

        # 在收到验证信息后才能添加到数据库里
        verify_info = {'id':'B01730ISAP',
                       'shape':'113.648035,34.803979;113.648025,34.805128;113.648042,34.805202;113.64812,34.805244;113.648236,34.805258;113.649989,34.805279;113.650049,34.805266;113.650081,34.805224;113.650091,34.804984;113.6501,34.804339;113.650101,34.804251;113.650065,34.804233;113.649274,34.804143;113.648357,34.804023;113.648035,34.803979'}
        if item['id'] == verify_info['id']:
            #  收到验证信息
            if item['shape'] == verify_info['shape']:
                # 没有收到假信息
                # 更新数据库
                logger.debug('信息验证无误，更新到数据库，更新数量为%s，并清空队列'%len(self.items_to_add))
                self.db.replace_items(self.items_to_add)
                self.items_to_add.clear()

            else:
                #收到假信息
                logger.error('信息验证未通过，需要丢弃队列信息')
                self.items_to_add.clear()
        else:
            # 不是验证信息，放入队列
            self.items_to_add.append(item)
            logger.debug('收到item，放入队列，当前队列长度%s'%len(self.items_to_add))


        return item

    def close_spider(self,spider):
        # self.abstract_file.close()
        # self.detail_file.close()

        if self.items_to_add:
            self.db.replace_items(self.items_to_add)
            logger.debug('队列里的剩余item插入数据库')



