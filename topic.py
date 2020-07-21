import json
import os

import requests
from bs4 import BeautifulSoup


def parse_organize_page(html):
    bs = BeautifulSoup(html, features="lxml")
    labels = bs.find_all(name="div", attrs={"class": "zm-tag-editor-labels"})
    if not labels:
        raise ValueError("no labels")
    labels = labels[-1]
    children = labels.findChildren("a", recursive=False)
    for child in children:
        print(child.attrs.get('data-token'))
        print(child.attrs.get('data-topicid'))
        print(child.attrs.get('href'))


if __name__ == '__main__':
    with open('organize_root.html') as f:
        html = f.read()
        parse_organize_page(html)
