import yaml
import argparse
import os
from scrape_fb import get_cookies, download_my_friends, download_mutual_friends, download_profiles


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', default='data.yaml', nargs='?')
    parser.add_argument('-s', '--skip_mutual', action='store_true')
    parser.add_argument('-p', '--skip_profiles', action='store_true')
    args = parser.parse_args()

    cookies = get_cookies()

    if os.path.exists(args.filename):
        data = yaml.load(open(args.filename))
    else:
        data = {'friends': {}}

    try:
        download_my_friends(data, cookies)

        if not args.skip_mutual:
            download_mutual_friends(data, cookies)

        if not args.skip_profiles:
            download_profiles(data, cookies)
    finally:
        yaml.safe_dump(data, open(args.filename, 'w'), allow_unicode=True)
