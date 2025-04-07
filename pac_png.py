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
import os
import requests
from urllib.parse import urlparse
from retry import retry
import urllib3
import re

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edge/91.0.864.59",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]
@retry(tries=3, delay=1, backoff=2)
def download_file(pdf_url, output_path):
    response = requests.get(pdf_url, verify=False, stream=True)
    
    # 尝试从 Content-Disposition 获取文件名
    content_disposition = response.headers.get('content-disposition')
    if content_disposition:
        filename = re.findall("filename=(.+)", content_disposition)
        if filename:
            filename = filename[0].strip('"')
        else:
            filename = os.path.basename(urlparse(pdf_url).path)
    else:
        filename = os.path.basename(urlparse(pdf_url).path)
        
    # 如果没有文件名或者为空, 根据 Content-Type 生成一个文件名
    if not filename:
        content_type = response.headers.get("Content-Type", "")
        if "jpeg" in content_type.lower():
            ext = ".jpg"
        elif "png" in content_type.lower():
            ext = ".png"
        else:
            ext = ""
        filename = "downloaded_image" + ext

    final_path = os.path.join(output_path, filename)
    with open(final_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)

def download_pdfs_from_file(input_file, output_dir, error_file, start_from=1):
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
 
    # 创建一个集合用于存放唯一的链接，去重
    unique_urls = set()
 
    # 读取文本文件中的所有行，并记录原始索引位置
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            unique_urls.add(line.strip())
 
    # 获取PDF文件数量
    total_pdfs = len(unique_urls)
    unique_urls = list(unique_urls)
 
    # 从指定位置开始下载PDF文件
    for idx in range(start_from - 1, total_pdfs):
        pdf_url = unique_urls[idx]
        try:
            # 下载PDF文件并保存至输出目录
            print(f'Downloading file {idx + 1}/{total_pdfs}: {pdf_url}')
            # 直接传入输出目录，不带文件名
            download_file(pdf_url, output_dir)
            print(f'\nDownloaded {pdf_url}')
        except Exception as e:
            # 输出错误信息至指定文件
            print(f'\nFailed to download {pdf_url}: {str(e)}')
            with open(error_file, 'a', encoding='utf-8') as err_file:
                err_file.write(f'{pdf_url}\n')

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
            # print(html)
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

saveroot = r"F:\cache\pachong"
with open("names.txt", 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()

        input_file_path = os.path.join(os.path.join(saveroot, line), "url.txt")
        output_directory = os.path.join(saveroot, line)
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
        error_output_file = "F:\\cache\\pachong\\false-url.txt"
        start_download_from = 1  #从第几个url开始

        if not os.path.exists(Path(os.path.join(saveroot,line))):
            os.makedirs(Path(os.path.join(saveroot,line)))
        subsaveroot = Path(os.path.join(saveroot,line))
        # keyword = "{} filetype:png".format(line)
        keyword = line
        save_path = Path(os.path.join(subsaveroot, "url.txt"))
        total_pages = 1
        scrape_pages(keyword, save_path, total_pages)
        print("begin download")
        download_pdfs_from_file(input_file_path, output_directory, error_output_file, start_from=start_download_from)

# keyword = "运-20"
# save_path = "F:/cache/pachong/result.txt"
# total_pages = 200
# scrape_pages(keyword, save_path, total_pages)
