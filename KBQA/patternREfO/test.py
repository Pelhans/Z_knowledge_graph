# coding: utf-8
# @athor: Zhejiang University
# Edit pelhans

import re
from refo import finditer, Predicate, Star, Any
import jieba.posseg as pseg
from jieba import suggest_freq
from SPARQLWrapper import SPARQLWrapper, JSON

sparql_base = SPARQLWrapper("http://localhost:3030/kg_demo_movie/query")

# SPARQL config
SPARQL_PREAMBLE = u"""
PREFIX : <http://www.kgdemo.com#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
"""

SPARQL_TEM = u"{preamble}\n" + \
             u"SELECT DISTINCT {select} WHERE {{\n" + \
             u"{expression}\n" + \
             u"}}\n"

INDENT = "    "


class Word(object):
    """treated words as objects"""
    def __init__(self, token, pos):
        self.token = token
        self.pos = pos


class W(Predicate):
    """object-oriented regex for words"""
    def __init__(self, token=".*", pos=".*"):
        self.token = re.compile(token + "$")
        self.pos = re.compile(pos + "$")
        super(W, self).__init__(self.match)

    def match(self, word):
        m1 = self.token.match(word.token)
        m2 = self.pos.match(word.pos)
        return m1 and m2


class Rule(object):
    def __init__(self, condition=None, action=None):
        assert condition and action
        self.condition = condition
        self.action = action

    def apply(self, sentence):
        matches = []
        for m in finditer(self.condition, sentence):
            i, j = m.span()
            matches.extend(sentence[i:j])
        if __name__ == '__main__':
            pass
#            print "----------applying %s----------" % self.action.__name__
        return self.action(matches)


def who_is_question(x):
    select = u"?x0"

    sparql = None
    for w in x:
        if w.pos == "nr" or w.pos == "x":
            e = u" ?a :actor_chName '{person}'. \n \
            ?a :actor_bio ?x0".format(person=w.token.decode("utf-8"))

            sparql = SPARQL_TEM.format(preamble=SPARQL_PREAMBLE,
                                       select=select,
                                       expression=INDENT + e)
            break
    return sparql


def where_is_from_question(x):
    select = u"?x0"

    sparql = None
    for w in x:
        if w.pos == "nr" or w.pos == "x":
            e = u" ?a :actor_chName '{person}'.\n \
            ?a :actor_birthPlace ?x0".format(person=w.token.decode("utf-8"))

            sparql = SPARQL_TEM.format(preamble=SPARQL_PREAMBLE,
                                       select=select,
                                       expression=INDENT + e)
            break
    return sparql


def whose_nationality_question(x):
    select = u"?x0"

    sparql = None
    for w in x:
        if w.pos == "nr" or w.pos == "x":
            e = u" ?a :movie_movie_chName '{person}'. \n \
            ?a :movie_movie_bio ?x0".format(person=w.token.decode("utf-8"))

            sparql = SPARQL_TEM.format(preamble=SPARQL_PREAMBLE,
                                       select=select,
                                       expression=INDENT + e)
            break
    return sparql


if __name__ == "__main__":
    default_questions = [
        u"周星驰是谁?",
        u"周星驰的出生地是哪里?",
        u"妖猫传的简介"
    ]

    suggest_freq(u"周星驰", True)
    suggest_freq(u"唐伯虎点秋香", True)
    suggest_freq(u"妖猫传", True)

    questions = default_questions[0:]

    seg_lists = []

    # tokenizing questions
    for question in questions:
        words = pseg.cut(question)
        seg_list = [Word(word.encode("utf-8"), flag) for word, flag in words]

        seg_lists.append(seg_list)

    # some rules for matching
    # TODO: customize your own rules here
    person = (W(pos="nr") | W(pos="x"))
    place = (W("出生地") | W("出生"))
    intro = (W("简介") | W("介绍"))
    
    rules = [

        Rule(condition=W(pos="r") + W("是") + person | \
                       person + W("是") + W(pos="r"),
             action=who_is_question),

        Rule(condition=person + Star(Any(), greedy=False) + place + Star(Any(), greedy=False),
             action=where_is_from_question),

        Rule(condition=person + Star(Any(), greedy=False) + intro,
             action=whose_nationality_question)

    ]

    # matching and querying
    for seg in seg_lists:
        # display question each
        for s in seg:
            print s.token,
        print

        for rule in rules:
            query = rule.apply(seg)

            if query is None:
#                print "Query not generated :(\n"
                continue
            
            # display corresponding query
            print query

            if query:
                sparql_base.setQuery(query)
                sparql_base.setReturnFormat(JSON)
                results = sparql_base.query().convert()

                if not results["results"]["bindings"]:
                    print "No answer found :("
                    continue

                for result in results["results"]["bindings"]:
                    print "Result: ", result["x0"]["value"]

                    print
