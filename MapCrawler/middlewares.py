# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals,Request
from scrapy.exceptions import CloseSpider
import requests
import time
import json
from urllib import parse

import logging
logger = logging.getLogger(__name__)

from MapCrawler.toolskit import AdslProxyServer
from MapCrawler.config import KEYS

class MapcrawlerSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class GaodeVerifySpiderMiddleware(object):
    """
    在这里，每隔一定数量的detail请求就加一次验证请求
    """
    POI_DETAIL_NUM_TO_BE_VERIFIED  = 20
    SEARCH_URL = 'https://ditu.amap.com/detail/get/detail'
    VERIFY_PARA = {'id':'B01730ISAP'}
    VERIFY_URL = '%s?%s' % (SEARCH_URL, parse.urlencode(VERIFY_PARA))

    def __init__(self):
        self.poi_detail_num = 0

    def process_spider_output(self,response,result,spider):
        """
        检查result中detail请求的个数，当满足POI_DETAIL_NUM_TO_BE_VERIFIED后，加入验证请求
        :param response:
        :param result:
        :param spider:
        :return:
        """
        for res in result:
            if isinstance(res,Request):
                if res.url.split('?')[0] == self.SEARCH_URL:
                    # 这是个搜索边界的请求
                    self.poi_detail_num += 1
                    if self.poi_detail_num > self.POI_DETAIL_NUM_TO_BE_VERIFIED:
                        # 已经达到验证数量，加一个验证请求
                        logger.debug('生成验证URL.')
                        yield Request(self.VERIFY_URL,dont_filter=True,callback=spider.parse_target_poi)
                        self.poi_detail_num = 0
            # 原来的结果还要继续
            yield res




class MapcrawlerDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)



class GaodeVerifyMiddleware(object):
    """
    检查高德是否开启验证，并绕过验证
    """
    def __init__(self,settings):
        self.adsl_server = AdslProxyServer()



    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self,request,spider):
        """
        request上添加proxy
        :param request:
        :param spider:
        :return:
        """
        proxy_pre = request.url.split('://')[0]+'://'
        request.meta['proxy'] = proxy_pre + self.adsl_server.get_proxy()
        logger.debug('url：%s\n使用代理%s'%(request.url,request.meta['proxy']))

    def process_response(self,request,response,spider):
        """
        1. 判断是否出现验证信息，出现too fast信息
        2. 判断是否开始返回假数据，如已经开始返回假数据.
            这部分需要每间隔几次请求之后，就加一个已知正确结果的请求，如果返回错误信息，则该批次都删掉。是否放到pipeline里去做？

        :param request:
        :param response:
        :param spider:
        :return:
        """
        verify_info = {'id': 'B01730ISAP',
                       'shape': '113.648035,34.803979;113.648025,34.805128;113.648042,34.805202;113.64812,34.805244;113.648236,34.805258;113.649989,34.805279;113.650049,34.805266;113.650081,34.805224;113.650091,34.804984;113.6501,34.804339;113.650101,34.804251;113.650065,34.804233;113.649274,34.804143;113.648357,34.804023;113.648035,34.803979'}

        res = json.loads(response.text)
        if 'too fast' == res.get('data'):
            # 开启验证或更换ip
            logger.warning('高德开启验证，请验证')
            self.adsl_server.refresh_proxy()
            return request


        if res.get('data',{}).get('base',{}).get('poiid') == verify_info['id'] \
            and res['data']['spec']['mining_shape']['shape'] != verify_info['shape']:
            # 验证信息不对，高德返回假数据
            logger.error('验证信息不符，数据有毒')
            self.adsl_server.refresh_proxy()
            return response

            #开启验证或者更换ip

        # 数据无异常
        return response

    def process_exception(self,request,exception,spider):
        """
        可能出现的异常：
            1. 代理地址已经更新
        :param request:
        :param exception:
        :param spdier:
        :return:
        """
        logger.warning('出现异常:%s'%request.url)
        logger.warning(exception)
        using_proxy = request.meta['proxy'].split('://')[1]
        if using_proxy == self.adsl_server.proxy:
            # 使用当前的ip产生的异常，需要更换ip
            self.adsl_server.refresh_proxy()

        return request


class ApiQueryLimitedMiddleware(object):
    """
    POI搜索配额为每天2k次，超过之后返回
    {'info': 'DAILY_QUERY_OVER_LIMIT', 'infocode': '10003', 'status': '0'}
    检查返回的response，如果为上面内容后，将尝试用新的key

    """
    def __init__(self):
        self.keys = self.key_iteration()
        self.key_using = next(self.keys)

    def key_iteration(self):
        for k in KEYS:
            yield k

    def process_request(self,request,spider):
        """
        根据
        :param request:
        :param spider:
        :return:
        """
        if request.url.split('?')[0] == spider.urls_prex:
            # 仅对官方api需要使用key的链接
            _url, _para = request.url.split('?')
            query_para = dict(parse.parse_qsl(_para))
            if query_para['key'] != spider.key_using:
                # 队列中的请求未使用最新的key，需要重新调度
                query_para['key'] = spider.key_using
                new_url = '%s?%s' % (_url, parse.urlencode(query_para))
                logger.debug('更新调度队列中的key')
                return request.replace(url=new_url)

        # 非官方API不需要key，返回None继续请求
        return None

    def process_response(self,request,response,spider):
        """

        :param request:
        :param response:
        :param spider:
        :return:
        """
        res = json.loads(response.text)
        if res.get('info') == 'DAILY_QUERY_OVER_LIMIT':
            # 怀疑scrapy是异步，需要判断reqeust中的key是否与spider中key一致，一致时才需要更新key，
            # 不一致时，只需要使用spider中的key替换请求中key，并重新请求即可
            _url, _para = request.url.split('?')
            query_para = dict(parse.parse_qsl(_para))
            if query_para['key'] == spider.key_using:
                try:
                    spider.key_using = spider.next_key()
                    # 使用新的key，重新调度
                    query_para['key'] = spider.key_using
                    new_url = '%s?%s'%(_url,parse.urlencode(query_para))
                    logger.info('检查到KEY查询上限，使用新的key重新请求：%s'%spider.key_using)
                    return request.replace(url = new_url)

                except StopIteration:
                    logger.error('所有Key都已超限')
                    #此处不处理，放到spider中检查，并生成CloseSpider异常
                    return response
            else:
                query_para['key'] = spider.key_using
                new_url = '%s?%s'%(_url,parse.urlencode(query_para))
                logger.debug('请求中的key为旧的已超限的key，使用新的key重新请求:%s'%spider.key_using)
                return request.replace(url = new_url)

        return response




