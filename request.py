import json
import os

import requests
from bs4 import BeautifulSoup


def get_question():
    url = "https://www.zhihu.com/question/268760922"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36",
        "Referer": "https://www.google.com/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code == 200:
        filename = "question.html"
        with open(filename, mode="w") as f:
            f.write(resp.text)
    else:
        print(f"resp status: <{resp.status_code}>")


def parse_question_keywords():
    html = get_question_html()
    if not html:
        return
    bs = BeautifulSoup(html, features="lxml")
    keywords = bs.find_all(name="div", attrs={"class": "Tag QuestionTopic"})
    result = []
    for kw in keywords:
        result.append(kw.text.strip())
    print(f"keywords: <{result}>")


def parse_question_content():
    html = get_question_html()
    if not html:
        return
    bs = BeautifulSoup(html, features="lxml")
    content = bs.find(name="script", attrs={"id": "js-initialData"})
    # print(f'content:\n{content.string.strip()}')
    content = json.loads(content.string.strip())
    for key, value in content.items():
        print("---" * 30)
        print(f"{key}: {value}")
        print("---" * 30)


def get_question_html():
    filename = "question.html"
    if not os.path.isfile(filename):
        return
    with open(filename) as f:
        html = f.read()
    return html


def get_topic_feeds():
    offset = 0
    limit = 10
    params = {
        "include": "data[?(target.type=topic_sticky_module)].target.data[?(target.type=answer)].target.content,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[?(target.type=topic_sticky_module)].target.data[?(target.type=answer)].target.is_normal,comment_count,voteup_count,content,relevant_info,excerpt.author.badge[?(type=best_answerer)].topics;data[?(target.type=topic_sticky_module)].target.data[?(target.type=article)].target.content,voteup_count,comment_count,voting,author.badge[?(type=best_answerer)].topics;data[?(target.type=topic_sticky_module)].target.data[?(target.type=people)].target.answer_count,articles_count,gender,follower_count,is_followed,is_following,badge[?(type=best_answerer)].topics;data[?(target.type=answer)].target.annotation_detail,content,hermes_label,is_labeled,relationship.is_authorized,is_author,voting,is_thanked,is_nothelp;data[?(target.type=answer)].target.author.badge[?(type=best_answerer)].topics;data[?(target.type=article)].target.annotation_detail,content,hermes_label,is_labeled,author.badge[?(type=best_answerer)].topics;data[?(target.type=question)].target.annotation_detail,comment_count;",
        "offset": offset,
        "limit": limit,

    }
    topic_id = 19556950
    url = f"https://www.zhihu.com/api/v4/topics/{topic_id}/feeds/timeline_activity"

    # paging --> next 下一页
    # paging --> data[] -> question -> id
    resp = requests.get(url, params=params, headers=get_headers())
    print_resp(resp)


def get_question_answers():
    question_id = 393472382
    offset = 0
    limit = 10
    params = {
        'include': 'data[*].is_normal,admin_closed_comment,reward_info,'
                'is_collapsed,annotation_action,annotation_detail,collapse_reason,'
                'is_sticky,collapsed_by,suggest_edit,comment_count,can_comment,'
                'content,editable_content,voteup_count,reshipment_settings,comment_permission,'
                'created_time,updated_time,review_info,relevant_info,question,excerpt,'
                'relationship.is_authorized,is_author,voting,is_thanked,is_nothelp,is_labeled,'
                'is_recognized,paid_info,paid_info_content;data[*].mark_infos[*].url;data[*].'
                'author.follower_count,badge[*].topics',
        'offset': offset,
        'limit': limit,
        'sort_by': 'default',
        'platform': 'desktop',
    }
    url = f'https://www.zhihu.com/api/v4/questions/{question_id}/answers'
    
    resp = requests.get(url, params=params, headers=get_headers())
    print_resp(resp)


def get_headers():
    headers = {
       # "Cookie": "_xsrf=9rsPCBdbtJjxnIqXHvTiI9nCQj0pLksz; KLBRSID=fe0fceb358d671fa6cc33898c8c48b48|1589278057|1589275134",
        "Host": "www.zhihu.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0",
    }
    return headers


def print_resp(resp):
    if resp.status_code == 200:
        result = resp.json()
    else:
        print(f"status: {resp.status_code}")
        print(f"text: \n{resp.text}")
        return
    
    for key, value in result.items():
        print(key, value)


def get_meta_info():
    with open('hot1.html') as f:
        html = f.read()
    bs = BeautifulSoup(html, features="lxml")
    meta = bs.find(name="meta", attrs={'itemprop': 'url'})
    # print(f'meta tag: {meta}')
    # for m in meta:
    #     print(m.attrs)
    if meta:
        print(f'meta content: {meta.attrs["content"]}')
        content = meta.attrs["content"]
        *_, token = content.rsplit('/', 1)
        print(f'meta token: {token}')


if __name__ == "__main__":
    # parse_question_keywords()
    # parse_question_content()
    # get_topic_feeds()
    # get_question_answers()
    get_meta_info()
