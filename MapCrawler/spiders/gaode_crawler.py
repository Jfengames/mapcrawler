#!/usr/bin/python3
#coding=utf-8

import scrapy
from scrapy.exceptions import CloseSpider
from urllib import parse
import json

from MapCrawler.items import PoiInfoItem
from MapCrawler.database_operations import GaodeMapSceneDbOper

import logging
logger = logging.getLogger(__name__)

from MapCrawler.toolskit import city_grids,ZHENGZHENGPOLYLINE
from MapCrawler.config import KEYS


class GaodeCrawler(scrapy.Spider):
    name = 'GaoDe'

    urls_prex ='http://restapi.amap.com/v3/place/polygon'
    search_url = 'https://ditu.amap.com/detail/get/detail'

    items_crawled = 0

    grid_num = 0

    def start_requests(self):
        """
        先爬取1km×1km的方格
        :return:
        """
        # jinshui_adcode='410105' #金水区的adcode
        # start_long_lat = '34.808881,113.652670'
        # resolution = 0.01 # 直接加到经纬度上，大概1km
        self.db= GaodeMapSceneDbOper()
        self.keys = self._next_key()
        self.key_using = self.next_key()


        parameters = {
            # 'polygon':'113.652670,34.808881,113.642670,34.798881',
            'types':'120000',# 居民区
            'offset':20,#每页最大数据
            'key':self.key_using

            # 'children':1,
            # 'city':'郑州',
            # 'citylimit':'true'
        }

        zhengzhou_grids = city_grids(ZHENGZHENGPOLYLINE,0.01)

        for grid in zhengzhou_grids:
            logger.info('请求第%s个网格'%self.grid_num)
            self.grid_num+=1
            parameters['polygon']= ','.join([str(i) for i in grid])
            url = '%s?%s'%(self.urls_prex,parse.urlencode(parameters))
            # logger.info('产生区域搜索请求：%s'%url)
            yield scrapy.Request(url,callback=self.parse_region_pois)


    def parse_region_pois(self,response):
        """
        通过区域搜索，解析目标POI，并yiele对应目标POI的请求
        :param response:
        :return:
        """
        res = json.loads(response.text)
        if res['status'] == '0':
            logger.error('返回数据有误')
            if res['info'] == 'DAILY_QUERY_OVER_LIMIT':
                raise CloseSpider('所有Key都已超限')


        _url,_para = response.url.split('?')
        query_para = parse.parse_qsl(_para)
        query_para = dict(query_para)
        parameters = {
            # 'key':query_para['key'],
            'citylimit':'true',
        }

        for poi in res.get('pois'):
            if self.db.is_item_exist_by_id(poi['id'])\
                    and not self.db.is_shape_null(poi['id']):
                continue

            # 生成每个poi的搜索url
            add_para = {'keywords':poi['name'],
                        'city':poi['cityname'],
                        'citylimit':'true',
                        'id':poi['id']}
            add_para.update(parameters)
            poi_url = '%s?%s'%(self.search_url,parse.urlencode(add_para))
            yield scrapy.Request(poi_url,callback=self.parse_target_poi)


        #检查是否有下一页
        # if query_para.get('page'):
        #     current_page = int(query_para['page'])
        # else:
        #     current_page = 1
        current_page = query_para.get('page') or 1
        current_poi_num = (int(current_page)-1)*int(query_para['offset']) + \
            len(res['pois'])
        logger.debug('当前页面为%s，当前poi数量为%s，返回的count数为%s'%(current_page,current_poi_num,res['count']))
        if current_poi_num < int(res['count']):
            query_para['page'] = int(current_page)+1
            url = '%s?%s'%(_url,parse.urlencode(query_para))
            logger.debug('生成下一页：%s'%url)
            yield scrapy.Request(url,callback=self.parse_region_pois)

    def parse_target_poi(self,response):
        """
        解析目标POI的response，并保存需要的信息到items
        :param response:
        :return:
        """
        res = json.loads(response.text)
        item = PoiInfoItem()
        logger.debug('边界搜索url：%s\nresponse:%s'%(response.url,response.text))
        try:
            base = res['data']['base']
            item['id'] = base['poiid']
            item['province'] = 'NULL'
            item['city'] = base['city_name']
            item['name'] = base['name']
            item['city_adcode'] = base['city_adcode']
            item['address'] = base['address']
            item['district'] = base.get('bcs','NULL')
            item['center_long'] = float(base['x'])
            item['center_lat'] = float(base['y'])
            item['type'] = base['new_keytype']
            item['typecode'] = base['new_type']
            item['classify'] = base['classify']
            item['area'] = base.get('geodata',{}).get('aoi',[{}])[0].get('area') or 0
            item['shape'] = res['data'].get('spec',{}).get('mining_shape',{}).get('shape') or 'NULL'

            yield item
            self.items_crawled+=1

        except:
            logger.debug('获取详情有误')


    def next_key(self):
        """
        每次换一次key
        :return:
        """
        _k = next(self.keys)
        logger.debug('使用下一个key:%s'%_k)
        return _k

    def _next_key(self):
        """
        key的迭代器
        :return:
        """
        for k in KEYS:
            yield k
