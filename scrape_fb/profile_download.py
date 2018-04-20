from .utils import grab, pause
from .profile_parse import parse_profile
import os

PROFILE_PATTERN = 'https://m.facebook.com/{username}/about'
PROFILE_PATTERN2 = 'https://m.facebook.com/profile.php?v=info&id={user_id}'

CACHED_PROFILE_FOLDER = 'raw_profiles'


def get_profile_url(key):
    if type(key) != int:
        return PROFILE_PATTERN.format(username=key)
    else:
        return PROFILE_PATTERN2.format(user_id=key)


def get_raw_profile(key, cookies):
    url = get_profile_url(key)
    s = grab(url, cookies)
    pause()
    return s


def save_raw_profile(key, raw):
    if not os.path.exists(CACHED_PROFILE_FOLDER):
        os.mkdir(CACHED_PROFILE_FOLDER)
    filename = os.path.join(CACHED_PROFILE_FOLDER, str(key))
    with open(filename, 'w') as f:
        f.write(raw)


def get_profile(key, cookies, save=True, use_cached=True):
    cached_filename = os.path.join(CACHED_PROFILE_FOLDER, str(key))
    if use_cached and os.path.exists(cached_filename):
        raw = open(cached_filename).read()
    else:
        raw = get_raw_profile(key)

    try:
        profile = parse_profile(raw)
    except:
        profile = None
        save = True
    if save:
        save_raw_profile(key, raw)

    return profile


def get_all_cached_profiles():
    profiles = []
    for fn in os.listdir(CACHED_PROFILE_FOLDER):
        full = os.path.join(CACHED_PROFILE_FOLDER, fn)
        profiles.append(full)
    return profiles


def download_profiles(data, cookies):
    for user_key, D in sorted(data['friends'].items()):
        if 'profile' in D:
            continue
        profile = get_profile(user_key, cookies)
        if profile:
            print 'Got profile for', user_key
            D['profile'] = profile
