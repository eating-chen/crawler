import urllib.request #用來建立請求
import urllib.parse
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re

base_url = "https://www.mobile01.com/"
headers = {}
headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'

post_source = "mobile01"
time_re = r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2})"
num_re = re.compile(u"[0-9]+")
page_count = 1

# 與資料庫mongodb做連線
_client = MongoClient()
_db = _client.eating_project
_social_network_msg = _db.social_network_msg

# 確認是否在資料庫有無重複
def check_duplicate_in_mongodb(post_id, post_author, post_title, post_type):
    if _social_network_msg.count({'post_id':post_id, 'post_author':post_author, 'post_title':post_title, 'post_type':post_type}) > 1:
        return True
    else:
        return False

def parse_post(post_link):
    url = base_url+post_link
    print(url)
    request = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(request)

    url_content = str(resp.read().decode('utf-8'))
    soup = BeautifulSoup(url_content, 'html.parser')
    url = urllib.parse.urlparse(url)
    param_of_link = urllib.parse.parse_qs(url.query)

    entire_post = {}
    
    post_type = param_of_link['f'][0]
    post_id = param_of_link['t'][0]
    post_title = soup.find("h1", class_="topic").get_text()
    post_author = soup.select("article .fn > a")[0].get_text()
    post_datetime = re.search(time_re, soup.select("article .date")[0].get_text()).group(0)
    post_content = soup.select("article .single-post-content")[0].get_text()
    post_popular = ""
    post_popular_temp = re.findall(num_re, soup.select("article .info")[0].get_text())
    for num in post_popular_temp:
        post_popular += num
    post_comment = []
    # 處理留言的部份
    for idx in range(1, len(soup.select("article .info"))):
        comment_author = soup.select("article .fn > a")[idx].get_text()
        comment_datetime = re.search(time_re, soup.select("article .date")[idx].get_text()).group(0)
        comment_content = soup.select("article .single-post-content")[idx].get_text()
        post_comment.append({
            "comment_author": comment_author,
            "comment_content": comment_content,
            "comment_datetime": comment_datetime
            })
    # 確認資料庫有無這筆資料 
    if check_duplicate_in_mongodb(post_id, post_author, post_title, post_type) == True:
        print("post", post_id, 'duplicate in mongodb')
    else:
        entire_post = {
            "post_source": post_source,
            "post_type": post_type,
            "post_id": post_id,
            "post_author": post_author,
            "post_title": post_title,
            "post_content": post_content,
            "post_datetime": post_datetime,
            "post_popular": post_popular,
            "post_comment": post_comment
        }
        # 存入這則訊息
        _social_network_msg.insert_one(entire_post)
        print("insert: ", post_id)
    
def crawler(mobile01_type):
    # 每次搜尋前10頁的訊息把新的放入資料庫
    for page in range(1, 11):
        url = base_url+"topiclist.php?f="+mobile01_type+"&p="+str(page)
        # print(url)
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req)

        url_content = str(resp.read().decode('utf-8'))
        soup = BeautifulSoup(url_content, 'html.parser')
    
        list_tags = soup.find_all("a", class_="topic_gen")
        # 針對每個頁面parse
        for list_tag in list_tags:
            parse_post(list_tag['href'])

if __name__ == "__main__":
    mobile01_type = ['564']
    for m_type in mobile01_type:
        crawler(m_type)
