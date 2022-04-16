import sys
import requests
import pandas as pd
import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

START_DATE = '20050502'
START_PAGE = 4
ITEM_PER_PAGE = 15


def get_urls(user_id, max_index, page=1):
    urls = []
    for index in range((page - 1) * ITEM_PER_PAGE, max_index * ITEM_PER_PAGE, ITEM_PER_PAGE):
        urls.append(f"https://book.douban.com/people/{user_id}/collect"
                    f"?start={index}&sort=time&rating=all&filter=all&mode=grid")
    return urls


def export(user_id):
    driver = webdriver.Chrome()

    driver.get('https://book.douban.com/')
    time.sleep(3)
    driver.get(f"https://book.douban.com/people/{user_id}/collect")
    WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'paginator')))

    paginator = driver.find_element_by_class_name('paginator')

    max_index = int(paginator.find_elements_by_tag_name("a")[-2].text)
    print(f"Total {max_index} pages")
    urls = get_urls(user_id, max_index, START_PAGE)
    page = START_PAGE
    for url in urls:
        page_data = []
        print(f"Getting page {page}: {url}")
        driver.get(url)
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.CLASS_NAME, 'subject-item')))
        items = driver.find_elements_by_class_name('subject-item')

        for item in items:
            db_url_element = item.find_elements_by_tag_name('a')[1]
            db_url = db_url_element.get_attribute("href")
            title = db_url_element.get_attribute('title')

            short_note = item.find_element_by_class_name('short-note')

            span = short_note.find_element_by_tag_name('span')
            rating = span.get_attribute('class').replace('rating', '').replace('-t', '')
            if not rating.isdigit():
                rating = None

            comment_date = short_note.find_element_by_class_name('date').text.replace('读过', '').strip()
            comment = item.find_element_by_class_name('comment').text

            # get book details
            driver.execute_script(f"window.open('{db_url}')")
            windows = driver.window_handles
            driver.switch_to.window(windows[1])
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'info')))
            book_info = driver.find_element_by_id('info')

            author = None
            origin_title = None
            isbn = None
            for line in book_info.text.splitlines():
                value = line.split()[1]
                if line.startswith('作者:'):
                    author = value
                if line.startswith('ISBN:'):
                    isbn = value
                if line.startswith('原作名:'):
                    origin_title = value
                if line.startswith('统一书号:'):
                    if isbn is None:
                        isbn = value

            driver.close()
            driver.switch_to.window(windows[0])

            data = {'title': title,
                    'rating': rating,
                    'isbn': isbn if isbn is not None else 'NO_ISBN',
                    'date': comment_date,
                    'comment': comment,
                    'origin_title': origin_title,
                    'author': author,
                    'url': db_url,
                    'peopleUrl': url,
                    'page': page
                    }
            print(data)
            page_data.append(data)

        print(f"Saving page {page}")
        df = pd.DataFrame(page_data)
        df.to_csv('book.csv', mode='a', index=False, header=False)
        page_data.clear()
        page = page + 1

    time.sleep(random.uniform(3, 7))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('请输入dbID，关于如何运行此程序请参照：',
              'https://github.com/fisheepx/douban-to-imdb')
        sys.exit()
    if len(sys.argv) == 3:
        START_DATE = sys.argv[2]
    print(f'开始抓取{START_DATE + "之后的" if START_DATE != "20050502" else "所有"}book数据...')
    export(sys.argv[1])
