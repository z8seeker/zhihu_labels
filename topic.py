from csv import DictWriter
from collections import deque
import os
import random
import time

import requests
from bs4 import BeautifulSoup


class ZhiHuException(Exception):
    pass


seen_topic_tokens = set()
topic_organize_queue = deque()
may_parent_queue = deque(maxlen=10)
topic_organize_url_template = "https://www.zhihu.com/topic/{}/organize"
headlines = ('topic_name', 'topic_token', 'topic_id')

SESSION = None


def get_session():
    global SESSION
    if session is None:
        session = requests.Session()
        session.mount('https://',
                      requests.adapters.HTTPAdapter(max_retries=5))
        session.mount('http://',
                      requests.adapters.HTTPAdapter(max_retries=5))
        session.headers.update({
            'cookie': ('_zap=d656ecf9-0ef2-4a91-96ef-597685ff5442; d_c0="ADBee6TjQBGPTkX2U6Gvwd3i277Qr22rnTs=|1589192418"; '
                       '_ga=GA1.2.1108184228.1589192422; '
                       '__utmz=51854390.1589252712.1.1.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/signin; '
                       '__utmv=51854390.100-1|2=registration_date=20121217=1^3=entry_date=20121217=1; '
                       'z_c0="2|1:0|10:1589270633|4:z_c0|92:Mi4xMTk0R0FBQUFBQUFBTUY1N3BPTkFFU1lBQUFCZ0FsVk5hYWFuWHdBNkRMQVI3VndBUzBnaWt3ZWEydTlUb1BWeV9R|eb26d2945a4bbc765691fd6f86bf3f5282637e3052846d0f66bb638883cda2a2"; '
                       'tst=r; _xsrf=bh0EnKnGK1hc4lYTOKwIZoLdM76kqUzb; q_c1=554efc3c45d24e33a8f7766468f9f5e5|1595327338000|1589252709000; '
                       '_gid=GA1.2.1904068253.1595328060; __utmc=51854390; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1594698724,1595328059,1595328076,1595387116; '
                       'Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1595387128; SESSIONID=qI5CQoG5mweVEwHrLhUOCg7Uw7e8T1i1sDCDSIcrLVX; '
                       'JOID=Wl0SA0mmMGwV7_9bRa7XstaAMtBb2nteVLSdHnfBSgtEqIIeNVOZfkLo8F5ANtVNS7gCExLDoNS6Qo9lAuL2aPQ=; osd=V1sXC0yrNmkd6vJdQKbSv9CFOtVW3H5WUbmbG3_ERw1BoIcTM1aRe0_u9VZFO9NIQ70PFRfLpdm8R4dgD-TzYPE=; '
                       '__utma=51854390.1108184228.1589192422.1595387089.1595391817.5; '
                       '__utmb=51854390.0.10.1595391817; KLBRSID=b33d76655747159914ef8c32323d16fd|1595391844|1595387087'),
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6',
            'cache-control': 'no-cache',
            'referer': 'https://www.zhihu.com/topic/19778298/organize',
        })

    return session


def write_csv(headlines, rows, filename):
    dir = os.path.dirname(os.path.realpath(__file__))
    fp = os.path.join(dir, filename)
    with open(fp, 'a+') as f:
        writer = DictWriter(f, fieldnames=headlines)
        # writer.writeheader()
        for row in rows:
            writer.writerow(row)


def parse_organize_page(html):
    bs = BeautifulSoup(html, features="lxml")
    labels = bs.find_all(name="div", attrs={"class": "zm-tag-editor-labels"})
    if len(labels) < 2:
        raise ValueError("labels less than 2")
    for label in labels:
        children = label.findChildren("a", recursive=False)
        yield from iter_topic_label(children)


def iter_topic_label(children):
    for child in children:
        topic = {
            "topic_name": child.text.strip(),
            "topic_token": child.attrs.get('data-token'),
            "topic_id": child.attrs.get('data-topicid'),
        }
        if topic['topic_token'] not in seen_topic_tokens:
            topic_organize_queue.append(topic["topic_token"])
            seen_topic_tokens.add(topic['topic_token'])
            yield topic


def fetch(url):
    s = get_session()
    resp = s.get(url, timeout=120)
    time.sleep(max(random.random() * 10, 5))
    if resp.status_code != 200:
        raise ZhiHuException(f'failed to get url: {url}')
    return resp.text


def main():
    root_topic_token = '19776749'
    topic_organize_queue.append(root_topic_token)
    while topic_organize_queue:
        topic_token = topic_organize_queue.popleft()
        may_parent_queue.append(topic_token)
        topic_url = topic_organize_url_template.format(topic_token)
        try:
            html = fetch(topic_url)
            rows = list(parse_organize_page(html))
            if rows:
                write_csv(headlines, rows, 'zhihu_topics.csv')
        except ZhiHuException as e:
            print(str(e))
            write_failed(topic_url)
        except Exception as e:
            print(str(e))
            break


def write_failed(url):
    with open('failed_urls.log', 'a+') as f:
        f.write(url + '\n')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("exit!")

    print('---' * 30)
    print(f'may_parent_queue: {may_parent_queue}')
    print(f'topic_organize_queue: {topic_organize_queue}')
    # root_topic_token = 19776749
    # root_topic_organize_url = topic_organize_url_template.format(root_topic_token)
    # resp = fetch(root_topic_organize_url)
    # print(f'html:\n{resp}')
    # with open('organize_middle.html') as f:
    #     html = f.read()
    #     topics = parse_organize_page(html)
    #     write_csv(headlines, topics, 'zhihu_topics.csv')
    #
    # print('deque', topic_organize_urls)
