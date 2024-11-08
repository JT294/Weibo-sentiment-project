# -*- coding:utf-8 -*-
import sys

sys.path.append("..")
import re
import time
import datetime
import json 
import requests
import csv
import random
import queue
import threading
from comments import *

from bs4 import BeautifulSoup
from hour_fenge import hour_fenge


mutex = threading.Lock()
search_url = 'https://s.weibo.com/weibo?q={}&typeall=1&suball=1&timescope=custom:{}:{}&Refer=g&page={}'  # 要访问的微博搜索接口URL
# cookie 需要先切换到手机端
cookie = '__bid_n=18457f28f7ca24f1b94207; FPTOKEN=30$3Jo1FS9IEFRFualpPSQpHIYjRrArzQpiMgOSxyOu/fpFNk4jVMRrma34d7KTFB5Gb8X45w9emXOXpjqoxHx5eA0QsYAchRkATXoAEttk+PZpYU7lwo/gUKL2XtrC4I6p4+VpLDvQ6Z3I+K7s0v7wbsJ/SewXMFE4ahp/VPWwFgUJla4lPVsgipG5KAtqg/aB2AJQs10gYA4MT6iKbSu03miWknCOSwHz8bgRSk0iVGFDwHfmACpIgIOjZjNbVBVOZ7oxXJZgZCdcwiK7vVEqtVso0kqK8A+gJUpfvFE1zQ/C6JDMT4qggpBYQcl9SUCpxT4TAZVFh+I5L52LD9zlwjBL+bi3gFLJ3IxmNm9OPy7ff3+6wPJ5Y+keRXgNDx+z|X4f3vK3MRPGuflTKxrEfbOTgLkJAraTROti6ZFiENcw=|10|6beb0bdaf87bd3afabf382ce2c990327; _T_WM=92414019129; XSRF-TOKEN=c22e63; WEIBOCN_FROM=1110005030; mweibo_short_token=5e93f4bf50; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5eZFd3B2Wp8Yh6HkYFyb6H5JpX5K-hUgL.FoqcehMRS0zcSK52dJLoIpzLxKqLBozLBonLxKqLBo5LBKzt; MLOGIN=1; SCF=AgULrA_zkxWUi2KVxFVNa2wr4WGcnhZN4WjB042Gp7spBbQSSUPfBGPe2LNKVVQfBpiZXcgsmvI_ce9JsQ3oG9M.; SUB=_2A25Odh-2DeRhGeBI61UZ9yzKzjyIHXVtmKH-rDV6PUJbktANLXf3kW1NRrgkezZAxSyMCwt16QU0He2iOrr5kTDp; SSOLoginState=1668444134; ALF=1671036134; M_WEIBOCN_PARAMS=uicode%3D20000061%26fid%3D4835736236595973%26oid%3D4835736236595973'

"""抓取关键词某一页的数据"""
headers = {
    'Accept':'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763',
    'cookie': 'SINAGLOBAL=9628880691683.602.1667923920840; ULV=1667923920849:1:1:1:9628880691683.602.1667923920840:; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5eZFd3B2Wp8Yh6HkYFyb6H5JpX5KMhUgL.FoqcehMRS0zcSK52dJLoIpzLxKqLBozLBonLxKqLBo5LBKzt; PC_TOKEN=2f2730f847; ALF=1699979977; SSOLoginState=1668443977; SCF=AgULrA_zkxWUi2KVxFVNa2wr4WGcnhZN4WjB042Gp7spNmGogO4UYb7R7GfxkX_m_lPJvaDxKxQn-bhQoK52sc4.; SUB=_2A25Odh8cDeRhGeBI61UZ9yzKzjyIHXVtAnfUrDV8PUNbmtAKLW3ukW9NRrgke1daL2xvSiK4akAhcez9dF02GbR1; XSRF-TOKEN=-3Bt4MSFvxWOWlPAXGWOB1tP; WBPSESS=5Ld0GzbJEqrtDVXXNVAT18GSjPMzPLjVK9BTCbqi-C5iwX89OSoFq338A3u6FxefjHMbwvvJXjWmaWG6cpJwgQ0am9e5D3ahRF_xD3x8-zUnxeADYgwY6n5gLXkWqIskhFDzjl8NliLYzPh6TzHT1Q=='

}

def get_number(s):
    try:  # 如果能运行int(s)语句，返回True（字符串s是浮点数）
        int(s)
        return int(s)
    except ValueError:  # ValueError为Python的一种标准异常，表示"传入无效的参数"
        pass  # 如果引发了ValueError这种异常，不做任何事情（pass：不做任何事情，一般用做占位语句）
    return 0


def time_process(time):
    time = str(time)
    if '月' in time:
        if '年' not in time:
            dangqian_year = datetime.datetime.now().strftime('%Y')
            time = dangqian_year + '-' + time
        time = time.replace(r'年', '-').replace(r'月', '-').replace(r'日', '')
    if time.startswith('今天'):
        dangqian_date = datetime.datetime.now().strftime('%Y-%m-%d')
        time = time.replace(r'今天', dangqian_date + ' ')
    if time.endswith('分钟前'):
        dangqian_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        time = dangqian_time
    return time


def fetch_weibo_data(keyword, start_time, end_time, page_id):
    time.sleep(random.randint(5, 20))
    resp = requests.get(search_url.format(keyword, start_time, end_time, page_id), headers=headers)
    soup = BeautifulSoup(resp.text, 'lxml')
    if (str(soup.select_one('.card-wrap').select_one('p').text).startswith('抱歉')):  # 此次搜索条件的判断，如果没有相关搜索结果！退出...
        print("此次搜索条件无相关搜索结果！\n请重新选择条件筛选...")
        return -1
    all_contents = soup.select('.card-wrap')

    wb_count = 0
    mblog = []  # 保存处理过的微博
    for card in all_contents:
        if (card.get('mid') != None):  # 如果微博ID不为空则开始抓取
            wb_id = str(card.get('mid'))  # 微博ID
            wb_username = card.select_one('.txt').get('nick-name')  # 微博用户名
            href = card.select_one('.from').select_one('a').get('href')
            re_href = re.compile('.*com/(.*)/.*')
            wb_userid = re_href.findall(href)[0]  # 微博用户ID
            wb_content = card.select_one('.txt').text.strip()  # 微博内容
            wb_create = card.select_one('.from').select_one('a').text.strip()  # 微博创建时间
            wb_url = 'https:' + str(card.select_one('.from').select_one('a').get('href'))  # 微博来源URL
            wb_createtime = time_process(wb_create)
            wb_forward = str(card.select_one('.card-act').select('li')[0].text).strip()  # 微博转发数
            wb_forwardnum = get_number(wb_forward)
            wb_comment = str(card.select_one('.card-act').select('li')[1].text).strip()  # 微博评论数
            wb_commentnum = get_number(wb_comment)
            wb_like = str(card.select_one('.card-act').select('li')[2].select("span")[1].text)  # 微博点赞数
            wb_likenum = get_number(wb_like)

            params = {"containerid": "100505" + wb_userid}
            h = {
                'Accept':'application/json, text/plain, */*',
                'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
            }
            url_user = "https://m.weibo.cn/api/container/getIndex?"
            # 这里在读取时很容易被ban，需要优化休眠时长
            time.sleep(random.randint(5, 20))
            r_user = requests.get(url_user, params=params, headers=h)
            if r_user.status_code != 200:
                print("访问失败！！！")
                exit(0)
            r = r_user.json()
            info = r["data"]["userInfo"]
            followers = info.get("followers_count")
            following = info.get("follow_count")
            tweets = info.get("statuses_count")

            # 获取用户地址
            location = "未知"
            try:
                p = {"containerid": "230413" + wb_userid}
                p["page"] = str(page_id)
                js = requests.get(url_user, params=p, headers=h)
                js = js.json()
                if js["ok"]:
                    weibos = js["data"]["cards"]
                    # 如果需要检查cookie，在循环第一个人的时候，就要看看仅自己可见的信息有没有，要是没有直接报错
                    for w in weibos:
                        if w["card_type"] == 9:
                            if w["mblog"]["region_name"]:
                                location = w["mblog"]["region_name"].split(" ")[1]
                            break
            except Exception as err:
                print(err)

            # 爬取评论区
            all_comments = []
            # if wb_commentnum > 0:
            #     try:
            #         comment = comments(weibo_id=wb_id, cookie=cookie)
            #         all_comments = comment.main()
            #     except Exception as err:
            #         print(err)
            
            blog = [
                wb_id, wb_userid, wb_username, wb_content, wb_createtime,
                wb_forwardnum, wb_commentnum, wb_likenum,
                followers, following, tweets, location,
                wb_url, all_comments
            ]

            mblog.append(blog)
            wb_count = wb_count + 1  # 表示此页的微博数

    print("--------- 正在爬取第%s页 --------- " % page_id + "当前页微博数：" + str(wb_count))
    return mblog


"""抓取关键词多页的数据"""

def fetch_pages(keyword, start_time, end_time):
    resp = requests.get(search_url.format(keyword, start_time, end_time, '1'), headers=headers)
    soup = BeautifulSoup(resp.text, 'lxml')
    if (str(soup.select_one('.card-wrap').select_one('p').text).startswith('抱歉')):  # 此次搜索条件的判断，如果没有相关搜索结果！退出...
        print("此次搜索条件无相关搜索结果！\n请重新选择条件筛选...")
        return
    try:
        page_num = len(soup.select_one('.m-page').select('li'))  # 获取此时间单位内的搜索页面的总数量，
        page_num = int(page_num)
        print(start_time + ' 到 ' + end_time + " 时间单位内搜索结果页面总数为：%d" % page_num)
    except Exception as err:
        page_num = 1

    mblogs = []  # 此次时间单位内的搜索全部结果先临时用列表保存，后存入数据库
    for page_id in range(page_num):
        page_id = page_id + 1
        try:
            mblog = fetch_weibo_data(keyword, start_time, end_time, page_id)
            if mblog == -1:
                break
            mblogs.extend(mblog)  # 每页调用fetch_data函数进行微博信息的抓取
        except Exception as e:
            print(e)

    # 保存到csv
    file_path = 'D://学习资料//管科//商务智能//homework//课程大作业//Weibo_Spider2//results_SZ.csv'
    mutex.acquire()
    with open(file_path, 'a', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        for mblog in mblogs:
            writer.writerow(mblog)
    mutex.release()


def crawl(worklist):
    while not worklist.empty():
        work = worklist.get()
        fetch_pages(keyword, work[0], work[1])
        print(work[0] + ' 到 ' + work[1] + ' 时间单位内的数据爬取完成！\n')


class WB_spider(threading.Thread):
    def __init__(self, queue, thread_id):
        threading.Thread.__init__(self)
        self.queue = queue
        self.id = thread_id

    def run(self):
        crawl(self.queue)


if __name__ == '__main__':
    keyword = "上证指数"  # 输入keywords
    start_time = "2020-01-04-0"
    end_time = "2022-11-10-24"

    file_path = 'D://学习资料//管科//商务智能//homework//课程大作业//Weibo_Spider2//results_SZ.csv'
    with open(file_path, 'a', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        header = [
            '微博id', '用户id', '用户名', '正文', '发布时间',
            '转发数', '评论数', '点赞数',
            '用户粉丝数', '用户关注数', '用户推文数',
            '用户地址', '微博网址', '评论'
        ]
        writer.writerow(header)

    worklist = queue.Queue()
    time_start = time.time()
    hour_all = hour_fenge(start_time, end_time)
    for h in hour_all:
        worklist.put(h)

    NUM_WORKERS = 40
    threads = []
    for i in range(NUM_WORKERS):
        spider = WB_spider(worklist, f"thread-{i}")
        spider.setDaemon(True)
        spider.start()
        threads.append(spider)

    # 等待所有线程完成
    for t in threads:
        t.join()

    time_end = time.time()

    print('本次操作数据全部爬取成功，爬取用时秒数:', (time_end - time_start))
