#!/usr/bin/env python
# coding=utf-8

from __future__ import absolute_import
from __future__ import division     
from __future__ import print_function


from baidu_baike.items import BaiduBaikeItem
import scrapy
from scrapy.http import Request
from bs4 import BeautifulSoup

class BaiduBaikeSpider(scrapy.Spider, object):
    name = 'baidu'
    start_urls = ['https://baike.baidu.com/item/%E5%91%A8%E6%98%9F%E9%A9%B0/169917?fr=aladdin']

    def _get_from_findall(self, tag_list):
        result = []        
                           
        for slist in tag_list:
            tmp = slist.get_text()
            result.append(tmp)
        return result

    def parse(self, response):
        page_category = response.xpath("//dd[@id='open-tag-item']/span[@class='taglist']/text()").extract()
        page_category = [l.strip() for l in page_category]
        print("page_category: ", page_category)
        item = BaiduBaikeItem()
        if u'演员' in page_category:
            print("Get a actor page")
            item['movie_chName'] = None
            item['movie_foreName'] = None
            item['actor_chName'] = response.xpath("//dd[@class='lemmaWgt-lemmaTitle-title']/h1/text()").extract()[0].strip()
#            item['actor_foreName'] = response.xpath()
            soup = BeautifulSoup(response.text, 'lxml')
            summary_node = soup.find("div", class_ = "lemma-summary")
            item['actor_bio'] = summary_node.get_text().replace("\n"," ")

            all_basicInfo_Item = soup.find_all("dt", class_="basicInfo-item name")
            basic_item = self._get_from_findall(all_basicInfo_Item)
            basic_item = [s.strip() for s in basic_item]
            all_basicInfo_value = soup.find_all("dd", class_ = "basicInfo-item value" )
            basic_value = self._get_from_findall(all_basicInfo_value)
            basic_value = [s.strip() for s in basic_value]
#            print("basic_item: ", basic_item)
#            print("basic_value: ", basic_value)
            for i, info in enumerate(basic_item):
                info = info.replace(u"\xa0", "")
                if info == u'中文名':
                    item['actor_chName'] = basic_value[i]
                elif info == u'外文名':
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
            elif u'电影' in page_category:
                
            yield item
#            print("############################\npage_title: ", item['actor_chName'], item['actor_bio'], sum)
