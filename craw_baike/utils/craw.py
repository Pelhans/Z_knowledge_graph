#!/usr/bin/env python
# coding=utf-8

from bs4 import BeautifulSoup
import re
import urlparse
import urllib2
import sys, os
import pymysql
import basic_info

actor = u'\n\u6f14\u5458\n' #line 91 演员的unicode 码,下面是电影的
movie = u'\n\u7535\u5f71\n'

basic_attr = {}
basic_list = []
target = sys.argv[1]
if target == 'actor':
    target = actor
    insert_command = basic_info.insert_actor_command
    basic_attr = basic_info.actor_attr
    basic_list = basic_info.actor_info
elif target == 'movie':
    target = movie
    insert_command = basic_info.insert_movie_command
    basic_attr = basic_info.movie_attr
    basic_list = basic_info.movie_info

mysql_db = pymysql.connect(host="localhost", user="root", passwd='nlp', db="kg_movie", use_unicode=True, charset="utf8mb4")
mysql_cursor = mysql_db.cursor()
    
# manage the url
class UrlManager(object):
    def __init__(self):
        self.new_urls = set()
        self.old_urls = set()

    def add_new_url(self, url):
        if url is None:
            raise Exception
        if url not in self.new_urls and url not in self.old_urls:
            self.new_urls.add(url)

    def add_new_urls(self, urls):
        if urls is None or len(urls) == 0:
            pass
        else:
            for url in urls:
                self.add_new_url(url)

    def has_new_url(self):
        return len(self.new_urls) != 0

    def get_new_url(self):
        new_url = self.new_urls.pop()
        self.old_urls.add(new_url)
        return new_url

# HTL download
class HTMLDownloader(object):
    def download(self, url):
        if url is None:
            return None
        response = urllib2.urlopen(url.encode('utf-8'))
        if response.getcode() != 200:
            return None

        return response.read()

# HTML parser
class HTMLParser(object):
    def _get_new_urls(self, page_url, soup):
        new_urls = []

        links = soup.find_all('a', href=re.compile(r"/item/"))
        for link in links:
            new_url = link["href"]
            new_full_url = urlparse.urljoin(page_url, new_url)
            new_urls.append(new_full_url)
        return new_urls

    def _get_from_findall(self, tag_list):
        result = []
        
        for slist in tag_list:
            tmp = slist.get_text()
            result.append(tmp)
        return result

    def dict_to_list(self, basic):
        detail_list = list()
        #actor_info = basic.keys() # dict不能保证 key按照初始化时的顺序存储

        for tag in basic_list:
            detail_list.append(basic[tag])
        return tuple(detail_list)

    def _get_new_data(self, soup, count):
        basic = basic_attr
        
        open_tag = soup.find_all("span", class_ = "taglist")
        tag = self._get_from_findall(open_tag)

        #if actor in tag or movie in tag : 
        if target in tag : 
            summary_node = soup.find("div", class_ = "lemma-summary")
            basic[u'简介'] = summary_node.get_text().replace("\n"," ")
            basic['id'] = count
            
            basic_node = soup.find("div", class_ = "basic-info cmn-clearfix")
            all_basicInfo_item = soup.find_all("dt", class_ = "basicInfo-item name" )
            basic_item = self._get_from_findall(all_basicInfo_item)
            basic_item = [s.strip() for s in basic_item]
            all_basicInfo_value = soup.find_all("dd", class_ = "basicInfo-item value" )
            basic_value = self._get_from_findall(all_basicInfo_value)
            basic_value = [s.strip() for s in basic_value]

            for i, item in enumerate(basic_item):
                if basic.has_key(item):
                    basic[item] = basic_value[i].replace("\n","")
            #res_data = self.dict_to_list(basic)
            count = count + 1
            
            print "检测到新目标，目前共采集总数： ", count - 1 

            return basic, count
        else:
            return None, count

    def parse(self, page_url, HTML_cont, count):
        if page_url is None or HTML_cont is None:
            return None

        soup = BeautifulSoup(HTML_cont, "html.parser", from_encoding="utf-8")
        new_urls = self._get_new_urls(page_url, soup)
        new_data, count = self._get_new_data(soup, count)
        return new_urls, new_data, count

class HTMLOutputer(object):
    def collect_data(self, data, count_er_id):
        if data is None:
            return count_er_id
        if sys.argv[1] == 'actor':
            count_er_id = self.get_actor_movie(data, count_er_id)
        data = HTMLParser.dict_to_list(data)
        mysql_cursor.execute(insert_command, data) # 将获得的数据插入到Mysql数据库中

        return count_er_id

    def get_actor_movie(self, data, count_actor_movie):

        if data is None:
            return count_er_id
        pres = data[u'代表作品'].strip()
        pres = re.split(u'[，、]', pres)
        actor_id = data['id']
        movie_id = 0
        
        print "sadsadasdas", pres

        for pre in pres:
            print "pre: ", pre
            movie_id = mysql_cursor.execute(basic_info.search_movie_id % (pre))
            if movie_id != 0:
                print "count_actor_movie: ", count_actor_movie
                count_actor_movie = count_actor_movie + 1
                mysql_cursor.execute(basic_info.insert_actor_movie_command, (count_actor_movie, actor_id, movie_id ))

        return count_actor_movie

class SpiderMain():
    def craw(self, root_url, page_counts):
        count = 1
        count_er_id = 0
        if sys.argv[1] == 'actor':
            count_er_id = mysql_cursor.execute( basic_info.get_largest_amid)
            print count_er_id
        elif sys.argv[1] == 'movie':
            count_er_id = mysql_cursor.execute( basic_info.get_largest_mgid)
        UrlManager.add_new_url(root_url)
        while UrlManager.has_new_url(): # still has url
            new_url =UrlManager.get_new_url()
            HTML_cont =HTMLDownloader.download(new_url)
            new_urls, new_data, count =HTMLParser.parse(new_url, HTML_cont, count)
            UrlManager.add_new_urls(new_urls)
            count_er_id = HTMLOutputer.collect_data(new_data, count_er_id)
            if count == page_counts+1:
                break

if __name__=="__main__":
    mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    print "\nWelcome to use baike_spider:)"
    UrlManager = UrlManager()
    HTMLDownloader = HTMLDownloader()
    HTMLParser = HTMLParser()
    HTMLOutputer = HTMLOutputer()

    root_url = "https://baike.baidu.com/item/%E5%BC%A0%E6%B6%B5%E4%BA%88"  #爬虫入口，默认是张涵予百科主页
    page_counts = input("Enter you want tocraw how many pages:" )  #想要爬取的数量,没爬取到目标分类下的不计数
    SpiderMain = SpiderMain()
    SpiderMain.craw(root_url,page_counts)   #启动爬虫

    #提交所有的insert 操作
    mysql_cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    mysql_db.commit()
    mysql_cursor.close()
    mysql_db.close()

