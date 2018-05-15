#!/usr/bin/env python
# coding=utf-8

'''
包含各个表的属性定义等和程序逻辑无关的部分
'''

insert_actor_command = 'INSERT INTO actor (actor_id, actor_bio, actor_chName, actor_foreName, actor_nationality, actor_constellation, actor_birthPlace, actor_birthDay, actor_repWorks, actor_achiem, actor_brokerage ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '
insert_movie_command = 'INSERT INTO movie (movie_id, movie_bio, movie_chName, movie_foreName, movie_prodTime, movie_prodCompany, movie_director,    movie_screenwriter, movie_genre, movie_star, movie_length, movie_rekeaseTime, movie_language, movie_achiem ) VALUES (%s, %s, %s, %s, %s, %s, %s,    %s, %s, %s, %s, %s, %s, %s ) '
insert_actor_movie_command = 'INSERT INTO actor_to_movie (actor_id, movid_id ) VALUES (%s, %s) '
insert_movie_genre_command = 'INSERT INTO movie_to_genre (movie_id, genre_id ) VALUES (%s, %s) ' # id 是整数，pymysql不支持%i %d这种，都用%s

actor_attr = {        
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
actor_info = [u'id', u'简介',  u'中文名', u'外文名', u'国籍', u'星座', u'出生地', u'出生日期', u'代表作品', u'主要成就', u'经纪公司']


movie_attr = {
    u'id' : int, 
    u'简介': None,
    u'中文名': None,
    u'外文名': None,
    u'出品时间': None,
    u'出品公司': None,
    u'导演': None,
    u'编剧': None,
    u'类型': None,
    u'主演' : None,
    u'片长': None,
    u'上映时间': None,
    u'对白语言': None,
    u'主要成就': None
       }
movie_info = [u'id', u'简介',  u'中文名', u'外文名', u'出品时间', u'出品公司', u'导演',  u'编剧', u'类型', u'主演', u'片长', u'上映时间', u'对白语言', u'主要成就' ]
