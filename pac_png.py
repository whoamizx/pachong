import urllib.parse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import random
from selenium.webdriver.chrome.options import Options
import time
import os
from pathlib import Path

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edge/91.0.864.59",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]

def scrape_pages(keyword, save_path, total_pages):
    
    num = 0

    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(f"user-agent={random.choice(user_agents)}")

    service = Service(executable_path='F:\download\chromedriver\chromedriver-win64\chromedriver.exe')

    driver = webdriver.Chrome(service=service, options=chrome_options)

    for i in range(total_pages):
        page = 10 * i + 1
        time.sleep(random.uniform(2, 5))
        url = 'https://image.baidu.com/search/index?tn=baiduimage&ipn=r&ct=201326592&cl=2&lm=&st=-1&fm=index&fr=&hs=0&xthttps=111110&sf=1&fmq=&pv=&ic=0&nc=1&z=&se=&showtab=0&fb=0&width=&height=&face=0&istype=2&ie=utf-8&word=' + keyword
        driver.get(url)

        # 等待页面加载
        time.sleep(random.uniform(2, 5))

        try:
            elem = driver.find_element(By.TAG_NAME, "body")
            print(elem.text)
            no_of_pagedowns = 15
            while no_of_pagedowns:
                elem.send_keys(Keys.PAGE_DOWN)
                time.sleep(0.2)
                no_of_pagedowns -= 1

            # 等待一下，确保页面完全加载后再获取页面源代码
            time.sleep(random.uniform(1, 2))
            html = driver.page_source
            print(html)
            soup = BeautifulSoup(html, 'html.parser')
            
            # 爬取一级页面中所有图片
            img_tags = soup.find_all('img')
            with open(save_path, 'a', encoding='utf-8') as f:
                for img in img_tags:
                    src = img.get('src')
                    if src:
                        full_src = urllib.parse.urljoin(url, src)
                        f.write(full_src + '\n')
                        num += 1

            print(f"已保存 {i+1} 页，共保存了 {num} 个网址")

        except Exception as e:
            print(f"第 {i+1} 页出错: {e}")

    driver.quit()
    print(f"爬取完成，共保存了 {num} 个网址")


with open("names.txt", 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not os.path.exists(Path(os.path.join(saveroot,line))):
            os.makedirs(Path(os.path.join(saveroot,line)))
        subsaveroot = Path(os.path.join(saveroot,line))
        # keyword = "{} filetype:png".format(line)
        keyword = line
        save_path = Path(os.path.join(subsaveroot, "url.txt"))
        total_pages = 2
        scrape_pages(keyword, save_path, total_pages)

keyword = "运-20"
save_path = "F:/cache/pachong/result.txt"
total_pages = 200
scrape_pages(keyword, save_path, total_pages)
