# crawler for news

import urllib.request #用來建立請求
import urllib.parse
from bs4 import BeautifulSoup
import re

base_url = "https://tw.appledaily.com/new/realtime"
headers = {}
headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'

post_source = "apple_news_realtime"
time_re = r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})"
num_re = re.compile(u"[0-9]+")
page_count = 1

def crawler():
    for page in range(1, 3):
        url = base_url+"/"+str(page)
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req)

        url_content = str(resp.read().decode('utf-8'))
        soup = BeautifulSoup(url_content, 'html.parser')
        news_title = soup.find_all("li", class_="rtddt")
        
        for title in news_title:
            print(title.get_text())


if __name__ == "__main__":
    crawler()