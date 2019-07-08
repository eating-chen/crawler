from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import math
from openpyxl import Workbook

#創建excel
wb = Workbook()
ws = wb.active
ws.append(['名字', '電話', '網址'])
#使用chrome的webdriver
chrome_options=Options()
chrome_options.add_argument('--headless')
browser = webdriver.Chrome(chrome_options=chrome_options)

#先取得頁碼
browser.get('https://sale.591.com.tw/?shType=list&regionid=17')
browser.implicitly_wait(10) 
total_num = browser.find_element_by_class_name('pageNum-form').get_attribute('data-total')
browser.close()

print(int(total_num))
page = math.ceil(int(total_num)/30)
count = 0
for idx in range(0, page, 1):
    browser = webdriver.Chrome(chrome_options=chrome_options)
    rows = idx*30
    browser.get('https://sale.591.com.tw/?shType=list&regionid=17&firstRow='+str(rows)+'&totalRows='+str(total_num))
    browser.implicitly_wait(5) 
    element = browser.find_elements_by_class_name('houseList-item-main')
    for l in element:
        browser1 = webdriver.Chrome(chrome_options=chrome_options)
        this_url = l.find_element_by_tag_name('a').get_attribute('href')
        browser1.get(this_url)
        browser1.implicitly_wait(5)
        person = ''
        phone = ''
        try:
            person = browser1.find_element_by_class_name('info-span-name').text
            phone = browser1.find_element_by_class_name('info-host-word').text
        except:
            person = "no_man"
            phone = browser1.find_element_by_class_name('phone-number').text
        print(person, " ", phone)
        ws.append([person, phone, this_url])
        browser1.close()
    browser.close()

wb.save('for_sonic.xlsx')
