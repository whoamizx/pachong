import os
import requests
from urllib.parse import urlparse
from retry import retry
import urllib3
import re
 
urllib3.disable_warnings()
 
@retry(tries=3, delay=1, backoff=2)
def download_file(pdf_url, output_path):
    response = requests.get(pdf_url, verify=False, stream=True)
    content_disposition = response.headers.get('content-disposition')
    if content_disposition:
        filename = re.findall("filename=(.+)", content_disposition)
        if filename:
            output_path = os.path.join(output_path, filename[0])
    with open(output_path, 'wb') as file:
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
            if '.pdf' in line:
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
            parsed_url = urlparse(pdf_url)
            filename = os.path.basename(parsed_url.path)
            output_path = os.path.join(output_dir, filename)
            download_file(pdf_url, output_path)
            print(f'\nDownloaded {pdf_url}')
        except Exception as e:
            # 输出错误信息至指定文件
            print(f'\nFailed to download {pdf_url}: {str(e)}')
            with open(error_file, 'a', encoding='utf-8') as err_file:
                err_file.write(f'{pdf_url}\n')
        finally:
            pass
 
input_file_path = "F:\\cache\\保险单\\保险单.txt"
output_directory = "F:\\cache\\保险单\\pdf"
error_output_file = "F:\\cache\\保险单\\false-url.txt"
start_download_from = 1  #从第几个url开始
 
# 调用函数下载PDF文件，传入开始下载的位置参数和错误输出文件路径
download_pdfs_from_file(input_file_path, output_directory, error_output_file, start_from=start_download_from)