# -*- coding: utf-8 -*-
################################################################################
#
# Copyright (c) 2020 Baidu.com, Inc. All Rights Reserved
#
################################################################################

"""
获取B站某视频下的所有评论者，去重，然后抽取指定的数量

Authors: duvet
Date:    2020-10-28 14:24:25
"""

import sys
import re
import math
import random
import requests
from bs4 import BeautifulSoup as bs

# B站获取视频评论的接口，pn表示第几页，oid表示av号
REPLY_URL = 'https://api.bilibili.com/x/v2/reply?pn=%d&oid=%s&type=1&sort=1'
# 获得真随机数的接口，num表示需要几个数，max表示最大值
RANDOM_URL = 'https://www.random.org/integer-sets/?sets=1&num=%d&min=0&max=%d&sort=on&order=index&format=plain&rnd=new'

def get_pages_of_replies(aid):
    """获取评论一共有几页
    取第一页评论数据，然后用count（总数）除以size（每页的数量），并向上取整
    aid：视频av号
    """
    ret = requests.get(REPLY_URL % (1, aid))
    count = int(ret.json()['data']['page']['count'])
    size = int(ret.json()['data']['page']['size'])
    return math.ceil(count / size)

def get_aid(url):
    """获取视频的av号
    爬html里的meta信息，然后用正则表达式取出来
    url：视频的链接地址，可以是BV也可以是av
    """
    r = requests.get(url)
    html = bs(r.text, 'html.parser')
    url = html.find_all('meta', itemprop='url')[0]['content']
    m = re.match(r'.+av(\d+).+', url)
    aid = m.groups()[0]
    return aid

def get_uname_of_replies(aid, pn):
    """获取特定页的评论的人名（去重）
    注：置顶评论需要单独取
    aid：视频av号
    pn：页码
    """
    unames = []
    ret = requests.get(REPLY_URL % (pn, aid))
    if pn == 1:
        uname = ret.json()['data']['upper']['top']['member']['uname']
        unames.append(uname)
    for reply in ret.json()['data']['replies']:
        uname = reply['member']['uname']
        if not (uname in unames):
            unames.append(uname)
    return unames

def lottery(account_list, count):
    """抽奖
    从random.org取随机数序列作为list索引
    account_list：候选账户列表
    count：抽多少人
    """
    winners = []
    r = requests.get(RANDOM_URL % (count, len(account_list) - 1))
    for winner in r.text.split():
        winners.append(account_list[int(winner)])
    return winners

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("python3 b.py url count")
        sys.exit(1)
    url = sys.argv[1]
    count = int(sys.argv[2])
    account_list = []
    # 拿到av号
    aid = get_aid(url)
    # 拿到总页数
    pages = get_pages_of_replies(aid)
    # 循环拿到所有评论者（去重）
    for i in range(1, pages):
        unames = get_uname_of_replies(aid, i)
        for uname in unames:
            if not uname in account_list:
                account_list.append(uname)
    print("■■■■ 评论总人数为 %d 人 ■■■■" % (len(account_list)))
    print('\t'.join(account_list))
    print()
    print("■■■■ 抽取其中 %d 人 ■■■■" % (count))
    # 抽奖
    winners = lottery(account_list, count)
    print("■■■■ 获奖者为 ■■■■")
    print('\t'.join(winners))