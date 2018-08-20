# Z_knowledge_graph
从零开始的知识图谱生活

# 简介
从零开始搭建一个小型知识图谱，并实现语义搜索和KBQA功能。<br>

# 目录

* 爬虫
    * 百度百科爬虫，基于scrapy框架，爬取电影类数据，包含电影22219部，演员13967人    
    * 互动百科爬虫，使用scrapy， 爬取电影类数据，包含电影13866部，演员5931 人    
    * craw_without_spider 未使用scrapy 的百度百科爬虫,用于获取半结构化文本    
    * 微信公众号爬虫, 使用scrapy 框架对微信公众号文章进行爬取,用于获取非结构化文本    
    * 虎嗅网爬虫,基于scrapy, 爬取虎嗅网新闻类非结构化文本   
    * 豆瓣爬虫(后续计划)    

* 结构化数据到 RDF 
    * Direct Mapping    
    * D2RQ
* TODO

# 爬虫

## 百度百科爬虫

该爬虫对应与crawl 下的baidu_baike 文件夹。该爬虫基于scrapy框架，爬取电影类数据，包含电影22219部，演员13967人，演员电影间联系1942个，电影与类别间联系23238,其中类别为‘其他’的电影有10个。对应数据集可在[坚果云下载](https://www.jianguoyun.com/p/Dfga9AgQq_6CBxiw8Go)

### mysql建库
* 演员 ：爬取内容为 ID, 简介， 中文名，外文名，国籍，星座，出生地，出生日期，代表作品，主要成就，经纪公司；  
* 电影 ：ID，简介，中文名，外文名，出品时间，出品公司，导演，编剧，类型，主演，片长，上映时间，对白语言，主要成就；  
* 电影类型： 爱情，喜剧，动作，剧情，科幻，恐怖，动画，惊悚，犯罪，冒险，其他； 
* 演员->电影： 演员ID， 电影ID； 
* 电影-> 类型： 电影ID， 类型ID；

与其相对应的建表语句即要求请参考craw_without_spider/mysql/creat_sql.txt文件。 在修改目标库的名称后即可通过
```
mysql -uroot -pnlp < creat_sql.txt
```
创建数据库。

### 运行爬虫
直接运行 scrapy crawl baidu 即可

## 互动百科爬虫 

该爬虫对应与crawl 下的hudong_baike 文件夹。该爬虫基于scrapy框架，爬取电影类数据，包含电影13866部，演员5931人，演员电影间联系800个，电影与类别间联系14558,其中类别为‘其他’的电影有0个。对应数据集可在[坚果云下载](https://www.jianguoyun.com/p/Db3wsKQQq_6CBxi7tGs)

数据库的结构和百度百科的一致，也可通过creat_sql.txt 文件创建。    

通过 scrapy crawl hudong 运行爬虫。

## craw_without_spider

百科数据爬取爬虫，用于提取半结构化实体文本。该爬虫未使用scrapy框架.用于提取目标是百度百科里面的演员和电影。


### 运行爬虫程序
爬虫程序可爬取演员和电影两类，其中：  
* 爬取演员：python craw.py actor 
* 爬取电影：python craw.py movie 
用户应先爬取电影，这样在爬取演员时才可以建立演员->电影表。

## 微信公众号爬虫
微信公众号爬虫对应的文件夹是weixin_spider，该项目采用MYSQL作为存储数据库，pymysql接口。

### 运行程序

* 建立数据库： 建立数据库的命令放在creat_mysql.txt文件内，所以直接运行 mysql -u[username] -p[passwd] < creat_mysql.txt 建立数据库和表; 
* 运行爬虫: 爬虫名字是weixin，因此直接运行scrapy crawl weixin;  

## 虎嗅网爬虫
虎嗅网爬虫放在 news_spider 目录下，采用的是文件存储方式，爬取下来的新闻存放在news 目录下。

### 运行程序

直接运行 scrapy crawl huxiu 即可。

# 结构化数据到 RDF

结构化数据到RDF由两种主要方式，一个是通过[direct mapping](https://www.w3.org/TR/rdb-direct-mapping/)，另一个通过[R2RML](https://www.w3.org/TR/r2rml/#acknowledgements)语言这种，基于R2RML语言的方式更为灵活，定制性强。对于R2RML有一些好用的工具，此处我们使用d2rq工具，它基于R2RML-KIT。

## direct mapping
根据启发式规则，编写从数据库到RDF的映射。
TODO
## D2RQ
运行struct_to_rdf 下的 get_ttl.sh 脚本生成 mapping 文件和 最终的 NTriples 文件。文件存放在坚果云盘中，[百度百科](https://www.jianguoyun.com/p/DfRZwwoQq_6CBxjmkGw)、[互动百科](https://www.jianguoyun.com/p/Db9tA1AQq_6CBxjnkGw)。

# TODO:
* 增加基于sceapy框架的百度百科、互动百科、豆瓣三个网站的爬虫，获取半结构化信息    
* 根据zhishi.me建立的文章，使用属性传播等算法建立三个独立的知识图谱    
* 使用知识融合技术，对以上三个知识图谱进行内部融合和互相间融合    
* 对微信公众号、虎嗅网新闻的非结构化文本进行知识抽取，并与上面获得的知识图谱进行融合    
* 基于知识图谱建立语义搜索系统    
* ....
