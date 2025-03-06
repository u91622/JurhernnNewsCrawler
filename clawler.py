# -*- coding: utf-8 -*-
"""clawler.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1dJAU5yc8JFUnm9Nntq_hSWvVFWomroZC
"""

pip install pillow
pip install wordcloud
pip install matplotlib
pip install jieba
pip install numpy指令安裝套件。

!wget https://github.com/adobe-fonts/source-han-sans/raw/release/OTF/SourceHanSansTW-Regular.otf

import time
import random
import requests
import csv
import re
from html import unescape  # 處理 HTML 實體編碼

class CnyesNewsSpider:

    def get_newslist_info(self, page=1, limit=30):
        """
        從 Cnyes API 獲得新聞列表資訊
        """
        headers = {
            'Origin': 'https://news.cnyes.com/',
            'Referer': 'https://news.cnyes.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        }
        try:
            r = requests.get(f"https://api.cnyes.com/media/api/v1/newslist/category/headline?page={page}&limit={limit}", headers=headers)
            r.raise_for_status()  # 確認請求成功
            return r.json()['items']['data']
        except requests.exceptions.RequestException as e:
            print(f"請求失敗: {e}")
            return None

    def clean_text(self, text):

        if not text:
            return ""
        # 解析 HTML 實體（將 &lt; 替換為 < 等）
        text = unescape(text)
        # 移除所有 HTML 標籤（包括錯誤嵌套的情況）
        text = re.sub(r'<[^>]*>', '', text)
        # 處理一些常見的特殊符號或空白字符
        text = re.sub(r'[\r\n\t]+', ' ', text)  # 替換換行符與製表符為空格
        text = re.sub(r'\s+', ' ', text)  # 壓縮多餘的空格
        # 去掉首尾空格
        text = text.strip()
        return text

    def extract_clean_text(self, news_item):
        """
        從新聞資料中擷取乾淨的文字內容，並清理雜訊
        """
        return {
            "ID": news_item.get("newsId", ""),
            "標題": self.clean_text(news_item.get("title", "")),
            "概要": self.clean_text(news_item.get("summary", "")),
            "內文": self.clean_text(news_item.get("content", "")),
            "關鍵字": ", ".join(news_item.get("keyword", [])),
            "發布時間": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(news_item.get("publishAt", 0))),
            "分類": news_item.get("categoryName", ""),
            "網址": f'https://news.cnyes.com/news/id/{news_item.get("newsId", "")}'
        }

    def save_to_csv(self, news_data, filename="cnyes_news.csv"):
        """
        將新聞資料儲存至 CSV
        """
        if not news_data:
            print("沒有資料可寫入 CSV。")
            return

        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "標題", "概要", "內文", "關鍵字", "發布時間", "分類", "網址"])
                for news in news_data:
                    writer.writerow(news.values())
            print(f'新聞已儲存至 {filename}')
        except Exception as e:
            print(f"儲存至 CSV 時發生錯誤: {e}")

if __name__ == "__main__":
    cnyes_news_spider = CnyesNewsSpider()
    all_news = []
    page = 1
    news_per_page = 30
    target_count = 300

    while len(all_news) < target_count:
        newslist_info = cnyes_news_spider.get_newslist_info(page=page, limit=news_per_page)
        if not newslist_info:
            break
        # 過濾新聞資料，並清洗文字
        all_news.extend([cnyes_news_spider.extract_clean_text(news) for news in newslist_info])
        page += 1
        time.sleep(random.uniform(2, 5))  # 避免被反爬蟲偵測

    if all_news:
        cnyes_news_spider.save_to_csv(all_news[:target_count])
    else:
        print("未能取得任何新聞資料。")

_import pandas as pd
import re

# 讀取 CSV 檔案
file_path = 'cnyes_news2.csv'  # 修改為您的檔案路徑
df = pd.read_csv(file_path, encoding='utf-8')

# 定義清理函數
def clean_text(text):
    if isinstance(text, str):
        return re.sub(r'[^a-zA-Z\u4e00-\u9fff]+', ' ', text)
    return text

# 清理資料
df_cleaned = df.applymap(clean_text)

# 儲存清理後的檔案
df_cleaned.to_csv('cnyes_news_cleaned.csv', index=False, encoding='utf-8')
print("清理後的檔案已儲存為 'cnyes_news_cleaned.csv'")