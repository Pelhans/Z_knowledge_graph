#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import
from __future__ import division     
from __future__ import print_function


from hudong_baike.items import HudongBaikeItem
import scrapy
from scrapy.http import Request
from bs4 import BeautifulSoup
import re
import urlparse

class HudongBaikeSpider(scrapy.Spider, object):
    name = 'hudong'
    allowed_domains = ["www.baike.com"]
#    start_urls = ['http://www.baike.com/wiki/%E5%94%90%E4%BC%AF%E8%99%8E%E7%82%B9%E7%A7%8B%E9%A6%99']
    start_urls = ['http://www.baike.com/wiki/%E5%91%A8%E6%98%9F%E9%A9%B0&prd=button_doc_entry'] # zhouxingchi
    
    def _get_from_findall(self, tag_list):
        result = []        
                           
        for slist in tag_list:
            tmp = slist.get_text()
            result.append(tmp)
        return result

    def parse(self, response):
        page_category = response.xpath('//dl[@id="show_tag"]/dd[@class="h27"]/a/text()').extract()
        page_category = [l.strip() for l in page_category]
        item = HudongBaikeItem()

        # tooooo ugly,,,, but can not use defaultdict
        for sub_item in [ 'actor_bio', 'actor_chName', 'actor_foreName', 'actor_nationality', 'actor_constellation', 'actor_birthPlace', 'actor_birthDay', 'actor_repWorks', 'actor_achiem', 'actor_brokerage','movie_bio', 'movie_chName', 'movie_foreName', 'movie_prodTime', 'movie_prodCompany', 'movie_director', 'movie_screenwriter', 'movie_genre', 'movie_star', 'movie_length', 'movie_rekeaseTime', 'movie_language', 'movie_achiem' ]:
            item[sub_item] = None

        if u'演员' in page_category:
            print("Get a actor page")
            soup = BeautifulSoup(response.text, 'lxml')
            summary_node = soup.find("div", class_ = "summary")
            item['actor_bio'] = summary_node.get_text().replace("\n"," ")

            item_box = response.xpath('//div[@class="module zoom"]//strong/text()').extract()
            value_str = response.xpath('//div[@class="module zoom"]//span')
            value_box = value_str.xpath('string(.)').extract()
                                          
            basic_item = [ re.sub(u"[\n ：]", r"", str) for str in item_box ]
            basic_value = [re.sub(u"[\n ：]", r"", str) for str in value_box ]
            print("item_box, ",  len(basic_item), basic_item)
            print("item_value: ", len(basic_value), basic_value)

            for i, info in enumerate(basic_item):
                info = info.replace(u"\xa0", "")
                print("info: ", info)
                if info == u'中文名':
                    item['actor_chName'] = basic_value[i]
                elif info == u'英文名':
                    item['actor_foreName'] = basic_value[i]
                elif info == u'国籍':
                    item['actor_nationality'] = basic_value[i]
                elif info == u'星座':
                    item['actor_constellation'] = basic_value[i]
                elif info == u'出生地':
                    item['actor_birthPlace'] = basic_value[i]
                elif info == u'出生日期':
                    item['actor_birthDay'] = basic_value[i]
                elif info == u'代表作品':
                    item['actor_repWorks'] = basic_value[i]
                elif info == u'主要成就':
                    item['actor_achiem'] = basic_value[i]
                elif info == u'经纪公司':
                    item['actor_brokerage'] = basic_value[i]
            yield item
        elif u'电影' in page_category:
            print("Get a movie page!!")

            soup = BeautifulSoup(response.text, 'lxml')
            summary_node = soup.find("div", class_ = "summary")
            item['movie_bio'] = summary_node.get_text().replace("\n"," ")
                              
            item_box = response.xpath('//div[@class="module zoom"]//strong/text()').extract()
            value_str = response.xpath('//div[@class="module zoom"]//span')
            value_box = value_str.xpath('string(.)').extract()

            basic_item = [ re.sub(r"[\n ]", r"", str) for str in item_box ]
            basic_value = [re.sub(r"[\n ]", r"", str) for str in value_box ]
            print("item_box, ",  len(basic_item), basic_item)
            print("item_value: ", len(basic_value), basic_value)

            for i, info in enumerate(basic_item):
                info = info.replace(u"\xa0", "")
                if info == u'中文名':
                    item['movie_chName'] = basic_value[i]
                elif info in [u'外文名', u'别名'] :
                    item['movie_foreName'] = basic_value[i]
                elif info == u'出品时间':
                    item['movie_prodTime'] = basic_value[i]
                elif info == u'出品公司':
                    item['movie_prodCompany'] = basic_value[i]
                elif info == u'导演':
                    item['movie_director'] = basic_value[i]
                elif info == u'编剧':
                    item['movie_screenwriter'] = basic_value[i]
                elif info in [u'类型', u'类别']:
                    item['movie_genre'] = basic_value[i]
                elif info == u'主演':
                    item['movie_star'] = basic_value[i]
                elif info == u'片长':
                    item['movie_length'] = basic_value[i]
                elif info == u'上映时间':
                    item['movie_rekeaseTime'] = basic_value[i]
                elif info == u'对白语言':
                    item['movie_language'] = basic_value[i]
                elif info == u'主要成就':
                    item['movie_achiem'] = basic_value[i]
            yield item

        new_urls = response.xpath("//a/@href").extract()
        print("new_urls: ", new_urls)
        for link in new_urls:
            yield scrapy.Request(link, callback=self.parse)
