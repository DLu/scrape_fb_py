# scrape_fb_py
A tool for scraping Ye Olde Book of Faces into easily parsable yaml format.

Based on [https://github.com/ben-pr-p/selenium-friends-scraper](https://github.com/ben-pr-p/selenium-friends-scraper)

### Requirements
 * selenium
 * BeautifulSoup

You will also need selenium set up to use Chrome. I just followed [the instructions here](https://gist.github.com/ziadoz/3e8ab7e944d02fe872c3454d17af31a5) (particularly the Install ChromeDriver section)

### Usage
`python scrape.py`

This should open a browser window for you to login with. Those credentials will be saved in `cookies.yaml`. Once it does that, it will
 * Download a list of all of your friends
 * Download a list of your mutual friends (i.e. which of your friends are friends with which other of your friends)
 * Download and parse your friends profile. A lot of web scraping wizardry goes into making the profile easy to read.

### Discussion
The script here is provided for personal usage / education only. It provides a systematic way of retrieving information
that you already had access to. However, the author will not take any responsibility if Mark Z doesn't like what you're up to.
