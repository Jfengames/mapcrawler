#!/usr/bin/python3
#coding=utf-8

import scrapy
from urllib import parse
import json

from MapCrawler.items import PoiStractItem

import logging
logger = logging.getLogger(__name__)


class GaodeCrawler(scrapy.Spider):
    name = 'GaoDe'

    def start_requests(self):
        """
        先爬取1km×1km的方格
        :return:
        """
        jinshui_adcode='410105' #金水区的adcode
        start_long_lat = '34.808881,113.652670'
        resolution = 0.01 # 直接加到经纬度上，大概1km

        urls_prex = [
            'http://restapi.amap.com/v3/place/polygon',
        ]

        parameters = {
            'key':'f628174cf3d63d9a3144590d81966cbd',
            'polygon':'113.652670,34.808881,113.642670,34.798881',
            'types':'120000',# 居民区
            'offset':20,#每页最大数据

            # 'children':1,
            # 'city':'郑州',
            # 'citylimit':'true'
        }

        for u in urls_prex:
            url = '%s?%s'%(u,parse.urlencode(parameters))
            # logger.info('产生区域搜索请求：%s'%url)
            yield scrapy.Request(url,callback=self.parse_region_pois)


    def parse_region_pois(self,response):
        """
        通过区域搜索，解析目标POI，并yiele对应目标POI的请求
        :param response:
        :return:
        """
        res = json.loads(response.text)
        if res['status'] == 0:
            raise scrapy.exceptions.IgnoreRequest('info:'%res['info'])

        search_url = 'https://ditu.amap.com/detail/get/detail'
        _url,_para = response.url.split('?')
        query_para = parse.parse_qsl(_para)
        query_para = dict(query_para)
        parameters = {
            'key':query_para['key'],
            'citylimit':'true',
        }

        for poi in res['pois']:
            # 保存poi摘要信息
            item = PoiStractItem()
            item.update(poi)
            yield(item)

            add_para = {'keywords':poi['name'],
                        'city':poi['cityname'],
                        id:poi['id']}
            add_para.update(parameters)
            poi_url = '%s?%s'%(search_url,parse.urlencode(add_para))
            yield scrapy.Request(poi_url,callback=self.parse_target_poi)

        #检查是否有下一页
        # if query_para.get('page'):
        #     current_page = int(query_para['page'])
        # else:
        #     current_page = 1
        current_page = query_para.get('page') or 1
        current_poi_num = (int(current_page)-1)*int(query_para['offset']) + \
            len(res['pois'])
        if current_poi_num < int(res['count']):
            query_para['page'] = current_page+1
            url = '%s?%s'%(_url,parse.urlencode(query_para))
            return scrapy.Request(url,callback=self.parse_region_pois)

    def parse_target_poi(self,response):
        """
        解析目标POI的response，并保存需要的信息到items
        :param response:
        :return:
        """
        res = json.loads(response.text)

        pass


