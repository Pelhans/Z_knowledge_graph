#!/usr/bin/env python
# coding=utf-8
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from utils import views

if __name__ == '__main__':
    while True:
        question = raw_input()
        answer = views.search(question.decode('utf-8'))
        print("Your question is : ", question, "\nAnswer: ", answer)
