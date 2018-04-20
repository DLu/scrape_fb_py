from .utils import grab, resolve_url, extract_friends, pause

FRIENDS_PATTERN = 'https://m.facebook.com/{username}?v=friends'


def get_username(cookies):
    url = resolve_url('https://m.facebook.com/me', cookies)
    return url.split('/')[-1].split('?')[0]


def download_my_friends(data, cookies):
    while True:
        if len(data['friends']) == 0:
            username = get_username(cookies)
            url = FRIENDS_PATTERN.format(username=username)
        elif 'more_url' in data:
            url = data['more_url']
        else:
            return

        friends, more_url = extract_friends(grab(url, cookies))
        for username, realname in friends:
            if username not in data['friends']:
                data['friends'][username] = {'name': realname}
        if more_url is None:
            if 'more_url' in data:
                del data['more_url']
        else:
            data['more_url'] = more_url

        print 'You now have %d friends.' % len(data['friends'])
        pause()
