from .utils import grab, extract_friends, pause

MUTUAL_PATTERN = 'https://m.facebook.com/{username}/friends?mutual=1'
MUTUAL_PATTERN2 = 'https://m.facebook.com/profile.php?v=friends&mutual=1&id={user_id}'


def get_mutual_friends_url(key):
    if type(key) != int:
        return MUTUAL_PATTERN.format(username=key)
    else:
        return MUTUAL_PATTERN2.format(user_id=key)


def download_mutual_friends(data, cookies):
    completed = 0
    for user_key, D in sorted(data['friends'].items()):
        if 'friends' in D and 'more_url' not in D:
            completed += 1
            continue
        while True:
            if 'friends' not in D:
                D['friends'] = []

            if len(D['friends']) == 0:
                url = get_mutual_friends_url(user_key)
            elif 'more_url' in D:
                url = D['more_url']
            else:
                break

            count = 0
            friends, more_url = extract_friends(grab(url, cookies))
            for m_username, realname in friends:
                if m_username not in data['friends']:
                    print 'Adding', realname
                    data['friends'][m_username] = {'name': realname}
                if m_username not in D['friends']:
                    D['friends'].append(m_username)
                    count += 1
            if more_url is None:
                if 'more_url' in D:
                    del D['more_url']
                if len(D['friends']) == 0:
                    print D['name'], 0
                    break
            else:
                D['more_url'] = more_url

            print D['name'], 'now has %d mutual friends.' % len(D['friends'])
            pause()

        D['friends'] = list(sorted(set(D['friends'])))
        completed += 1

        print '%d/%d' % (completed, len(data['friends']))
