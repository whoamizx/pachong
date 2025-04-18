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
        url = f'https://www.bing.com/search?q={urllib.parse.quote(keyword)}&first={page}'
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

            # 获取所有 h2 元素
            # 爬pdf
            h2_elements = soup.find_all('h2')


            with open(save_path, 'a', encoding='utf-8') as f:
                for h2 in h2_elements:
                    a_tag = h2.find('a')  # 查找 h2 内的 a 标签
                    if a_tag and 'href' in a_tag.attrs:  # 确保 a 标签存在且包含 href 属性
                        href = a_tag['href']  # 获取 href 值
                        f.write(href + '\n')
                        num += 1

            print(f"已保存 {i+1} 页，共保存了 {num} 个网址")

        except Exception as e:
            print(f"第 {i+1} 页出错: {e}")

    driver.quit()
    print(f"爬取完成，共保存了 {num} 个网址")

keyword = "运-20"
save_path = "F:/cache/pachong/result.txt"
total_pages = 1
scrape_pages(keyword, save_path, total_pages)
