import re
import requests
from bs4 import BeautifulSoup
from random import randint
from time import sleep

ID_PATTERN = re.compile('/profile.php\?id=(\d+)(&fref=fr_tab)?')


def pause():
    sleep(randint(2, 5))


def grab(url, cookies):
    r = requests.get(url, cookies=cookies)
    if r.status_code != 200:
        print r.status_code
        print r.text
        exit(0)
    return r.text


def resolve_url(url, cookies):
    r = requests.get(url, cookies=cookies)
    if r.status_code != 200:
        print r.status_code
        print r.text
        exit(0)
    return r.url


def match_friend_link(href):
    m = ID_PATTERN.match(href)
    if m:
        return int(m.group(1))
    if 'mailto' in href:
        return None
    username = href[1:].split('?')[0]
    if not ('.php' in username or '/' in username):
        return username


def extract_friends_from_element(content):
    friends = []
    next_link = None
    for l in content.find_all('a'):
        if 'href' not in l.attrs:
            continue
        href = l['href']
        m = ID_PATTERN.match(href)
        real_name = l.text
        if real_name in ['Timeline', 'Following']:
            continue
        if m:
            friends.append((int(m.group(1)), l.text))
            continue
        username = href[1:].split('?')[0]
        if not ('.php' in username or '/' in username):
            friends.append((username, l.text))
        elif 'more' in l.text.lower():
            if href[0] == '/':
                href = 'http://m.facebook.com' + href
            next_link = href

    return friends, next_link


def extract_friends(raw_html):
    content = BeautifulSoup(raw_html, 'html.parser').find('div', {"id": "root"})
    return extract_friends_from_element(content)
