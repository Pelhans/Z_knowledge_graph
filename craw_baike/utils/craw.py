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


    def _get_new_data(self, page_url, soup, count):
        res_data = {}
        basic = {
            id : None,
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
            res_data["url"] = page_url
            title_node = soup.find("dd", class_ = "lemmaWgt-lemmaTitle-title").find("h1")
            res_data["title"] = title_node.get_text()
            summary_node = soup.find("div", class_ = "lemma-summary")
            res_data["summary"] = summary_node.get_text()
    
            basic_node = soup.find("div", class_ = "basic-info cmn-clearfix")
            all_basicInfo_item = soup.find_all("dt", class_ = "basicInfo-item name" )
            basic_item = self._get_from_findall(all_basicInfo_item)
            basic_item = [s.strip() for s in basic_item]
            all_basicInfo_value = soup.find_all("dd", class_ = "basicInfo-item value" )
            basic_value = self._get_from_findall(all_basicInfo_value)
            basic_value = [s.strip() for s in basic_value]

            for i, item in enumerate(basic_item):
                if basic.has_key(item):
                    basic[item] = basic_value[i]
           
            #res_data["basic"] = basic_node.get_text()
            count = count + 1

            return res_data, basic, count
        else:
            return None, None, count

    def parse(self, page_url, HTML_cont, count):
        if page_url is None or HTML_cont is None:
            return None

        soup = BeautifulSoup(HTML_cont, "html.parser", from_encoding="utf-8")
        new_urls = self._get_new_urls(page_url, soup)
        new_data, _, count = self._get_new_data(page_url, soup, count)
        return new_urls, new_data, count

class HTMLOutputer(object):
    def __init__(self):
        self.datas = []
    
    def collect_data(self, data):
        if data is None:
            return None
        self.datas.append(data)

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
            fout.write("<td>%s</td>" %data["basic"].encode("utf-8"))
            fout.write("</tr>")
        fout.write("</table>")
        fout.write("</body>")
        fout.write("</HTML>")

    def _get_actor_tag(self):
        actor_list = ()

        actor_bio = data["summary"].encode("utf-8")
        actor_chName = data["title"].encode("utf-8")

        where_foreName = data["basic"].find(u"外文名")
        actor_foreName = data["basic"][where_foreName + 4: ]

        where_nationality = data["basic"].find(u"国籍")
        where_constellation = data["basic"].find(u"星座")
        where_birthPlace = data["basic"].find(u"出生地")
        where_birthDay = data["basic"].find(u"出生日期")
        where_repWorks = data["basic"].find(u"代表作品")
        where_achiem = data["basic"].find(u"主要成就")
        where_brokerage = data["basic"].find(u"经纪公司")


        actor_list = ()
        return 0


class SpiderMain():
    def craw(self, root_url, page_counts):
        count = 0
        UrlManager.add_new_url(root_url)
        while UrlManager.has_new_url(): # still has url
            new_url =UrlManager.get_new_url()
            print "\ncrawed %d :%s" % (count, new_url)
            HTML_cont =HTMLDownloader.download(new_url)
            new_urls, new_data, count =HTMLParser.parse(new_url, HTML_cont, count)
            UrlManager.add_new_urls(new_urls)
            HTMLOutputer.collect_data(new_data)
            if count == page_counts:
                break
        HTMLOutputer.output_HTML()

if __name__=="__main__":
    print "\nWelcome to use baike_spider:)"
    UrlManager = UrlManager()
    HTMLDownloader = HTMLDownloader()
    HTMLParser = HTMLParser()
    HTMLOutputer = HTMLOutputer()

    #root_url = "https://baike.baidu.com/item/Python/407313?fr=aladdin"
    root_url = "https://baike.baidu.com/item/%E5%91%A8%E6%98%9F%E9%A9%B0/169917?fr=aladdin"
    page_counts = input("Enter you want tocraw how many pages:" )  #想要爬取的数量
    SpiderMain = SpiderMain()
    SpiderMain.craw(root_url,page_counts)   #启动爬虫

    print"\nCraw is done, please go to"+os.path.dirname(os.path.abspath('__file__')) + " to see the resultin baike_spider_output.HTML"
