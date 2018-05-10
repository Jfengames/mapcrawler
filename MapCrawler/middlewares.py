# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import requests
import time
import json

import logging
logger = logging.getLogger(__name__)

ADSL_IP_ADDR_URL = 'http://223.105.3.170:18888'

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


class AdslProxyMiddleware():
    """
    通过请求adsl拨号服务器建立proxy服务，并通过不断更换ip地址来避免被ban
    """


    def __init__(self,settings):
        """
        通过从固定ip服务器上获取代理服务器的ip地址。如果是固定ip服务器是本机，地址应为127.0.0.1:18888
        :param settings:
        :return:
        """
        self.adsl_ip_add_url = ADSL_IP_ADDR_URL
        self.auth = ('ss_adsl','thisisproxyip')
        self.re_fresh_proxy()

    def re_fresh_proxy(self,old_prxy=None):
        while True:
            proxy_ip = requests.get(self.adsl_ip_add_url,auth=self.auth).text
            self.proxy = 'http://'+proxy_ip
            if self.proxy == old_prxy:
                time.sleep(30)
                continue
            else:
                break
        logger.info('proxy ip地址从%s更新为-->%s'%(old_prxy,self.proxy))
        return self.proxy


    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)


    def process_request(self,request,spider):
        proxy = request.meta.get('proxy',None)
        # 使用最近的ip
        if proxy != self.proxy:
            request.meta['proxy'] = self.proxy
        return

    def process_response(self,request,response,spider):
        """
        验证resposne是否正确，如不正确，需要更换代理的ip，并重新请求request

        :param request:
        :param response:
        :param spider:
        :return:
        """

        def is_correct(response):
            """
            判断response字段是否正确
            :param response:
            :return:
            """
            if 'http://restapi.amap.com' in response.url:
                # 使用官方api
                res = json.loads(response.text)
                if res['status'] == '1' and res['info']=='OK':
                    # and 'shape' in response.text:
                    return True
                else:
                    return False
            else:
                # 非官方api
                if 'shape' in response.text:
                    return True
                else:
                    return False

        if is_correct(response):
            # 结果正确，返回response
            return response
        else:
            # 结果不正确，更新ip，重新请求
            old_proxy = request.meta['proxy']
            self.re_fresh_proxy(old_proxy)
            request.meta['proxy'] = self.proxy
            request.dont_filter = True
            return request


    def process_exception(self,request,exception,spider):
        """
        如果有异常，在这里处理
        :param request:
        :param exception:
        :param spider:
        :return:
        """

