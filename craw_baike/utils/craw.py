#!/usr/bin/env python
# coding=utf-8

from bs4 import BeautifulSoup
import re
import urlparse
import urllib2
import os
import pymysql

actor = u'\n\u6f14\u5458\n' #line 81 
movie = u'\n\u7535\u5f71\n'

mysql_db = pymysql.connect(host="localhost", user="root", passwd='nlp', db="kg_movie", use_unicode=True, charset="utf8mb4")
mysql_cursor = mysql_db.cursor()
    
insert_actor_command = 'INSERT INTO actor (actor_id, actor_bio, actor_chName, actor_foreName, actor_nationality, actor_constellation, actor_birthPlace, actor_birthDay, actor_repWorks, actor_achiem, actor_brokerage ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '
insert_movie_command = 'INSERT INTO movie (movie_id, movie_bio, movie_chName, movie_foreName, movie_prodTime, movie_prodCompany, movie_director, movie_screenwriter, movie_genre, movie_star, movie_length, movie_rekeaseTime, movie_language, movie_achiem ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ) '
insert_actor_movie_command = 'INSERT INTO actor_to_movie (actor_id, movid_id ) VALUES (%s, %s) ' 
insert_movie_genre_command = 'INSERT INTO movie_to_genre (movie_id, genre_id ) VALUES (%s, %s) ' # id 是整数，pymysql不支持%i %d这种，都用%s

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
        response = urllib2.urlopen(url)
        if response.getcode() != 200:
            return None

        return response.read()

# HTML parser
class HTMLParser(object):
    def _get_new_urls(self, page_url, soup):
        new_urls = []

        links = soup.find_all('a', href=re.compile(r"/item/"))
#        links = soup.find_all('a', href=re.compile(r"/item/"))
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
        actor_info = [u'id', u'简介',  u'中文名', u'外文名', u'国籍', u'星座', u'出生地', u'出生日期', u'代表作品', u'主要成就', u'经纪公司']

        for tag in actor_info:
            detail_list.append(basic[tag])
        return tuple(detail_list)

    def _get_new_data(self, soup, count):
        basic = {
            u'id' : int,
            u'简介': None,
            u'中文名': None,
            u'外文名': None,
            u'国籍': None,
            u'星座': None,
            u'出生地': None,
            u'出生日期': None,
            u'代表作品': None,
            u'主要成就' : None,
            u'经纪公司': None
        }

        open_tag = soup.find_all("span", class_ = "taglist")
        tag = self._get_from_findall(open_tag)

        #if actor in tag or movie in tag : 
        if actor in tag : 
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
            res_data = self.dict_to_list(basic) 
            count = count + 1
            
            print "检测到新目标，目前共采集总数： ", count -1 

            return res_data, count
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
    def __init__(self):
        self.datas = []
    
    def collect_data(self, data):
        if data is None:
            return None

        mysql_cursor.execute(insert_actor_command, data)

        #self.datas.append(data)

    def output_HTML(self):
        fout = open("baike_spider_output.HTML", "w")
        fout.write("<HTML>")
        fout.write('<meta charset="utf-8">')
        fout.write("<head>")
        fout.write("<title>百度百科Python页面爬取相关数据</title>")
        fout.write("</head>")
        fout.write("<body>")
        fout.write('<h1style="text-align:center">在百度百科中爬取相关数据展示</h1>')
        fout.write("<table>")
        for data in self.datas:
            fout.write("<tr>")
            fout.write("<td>%s</td>" % data["url"])
            fout.write("<td><ahref='%s'>%s</a></td>" %(data["url"].encode("utf-8"),data["title"].encode("utf-8")))
            fout.write("<td>%s</td>" %data["summary"].encode("utf-8"))
            #fout.write("<td>%s</td>" %data["basic"].encode("utf-8"))
            fout.write("</tr>")
        fout.write("</table>")
        fout.write("</body>")
        fout.write("</HTML>")

class SpiderMain():
    def craw(self, root_url, page_counts):
        count = 1
        UrlManager.add_new_url(root_url)
        while UrlManager.has_new_url(): # still has url
            new_url =UrlManager.get_new_url()
            #print "\ncrawed %d :%s" % (count, new_url)
            HTML_cont =HTMLDownloader.download(new_url)
            new_urls, new_data, count =HTMLParser.parse(new_url, HTML_cont, count)
            UrlManager.add_new_urls(new_urls)
            HTMLOutputer.collect_data(new_data)
            if count == page_counts+1:
                break
        #HTMLOutputer.output_HTML()

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

    print"\nCraw is done, please go to"+os.path.dirname(os.path.abspath('__file__')) + " to see the resultin baike_spider_output.HTML"
