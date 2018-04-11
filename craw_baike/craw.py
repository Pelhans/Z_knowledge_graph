#!/usr/bin/env python
# coding=utf-8

from bs4 import BeautifulSoup
import re
import urlparse
import urllib2
import os

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
            raise Exception
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

    def _get_new_data(self, page_url, soup):
        res_data = {}

        res_data["url"] = page_url
        title_node = soup.find("dd", class_ = "lemmaWgt-lemmaTitle-title").find("h1")
        res_data["title"] = title_node.get_text()
        summary_node = soup.find("div", class_ = "lemma-summary")
        res_data["summary"] = summary_node.get_text()

        return res_data

    def parse(self, page_url, HTML_cont ):
        if page_url is None or HTML_cont is None:
            return None

        soup = BeautifulSoup(HTML_cont, "html.parser", from_encoding="utf-8")
        new_urls = self._get_new_urls(page_url, soup)
        new_data = self._get_new_data(page_url, soup)
        return new_urls, new_data

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
            print "\ncrawed %d :%s" % (count, new_url)
            HTML_cont =HTMLDownloader.download(new_url)
            new_urls, new_data =HTMLParser.parse(new_url, HTML_cont)
            UrlManager.add_new_urls(new_urls)
            HTMLOutputer.collect_data(new_data)
            if count == page_counts:
                break
            count = count + 1
        HTMLOutputer.output_HTML()

if __name__=="__main__":
    print "\nWelcome to use baike_spider:)"
    UrlManager = UrlManager()
    HTMLDownloader = HTMLDownloader()
    HTMLParser = HTMLParser()
    HTMLOutputer = HTMLOutputer()

    root_url = "https://baike.baidu.com/item/Python/407313?fr=aladdin"
    page_counts = input("Enter you want tocraw how many pages:" )  #想要爬取的数量
    SpiderMain = SpiderMain()
    SpiderMain.craw(root_url,page_counts)   #启动爬虫
    print"\nCraw is done, please go to"+os.path.dirname(os.path.abspath('__file__')) + " to see the resultin baike_spider_output.HTML"
