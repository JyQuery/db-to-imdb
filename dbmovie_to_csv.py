import sys
import requests
import pandas as pd
import time
import random
import configparser
from datetime import datetime
from bs4 import BeautifulSoup

config = configparser.ConfigParser()
config.read('config')
USER_AGENT = config['Movie']['UserAgent']
START_DATE = config['Movie']['AfterDate']
DATE_FORMAT = '%Y-%m-%d'
START_PAGE = int(config['Movie']['StartPage'])
DB_USER = config['Movie']['DBUser']
CATEGORY = config['Movie']['Category']
IS_OVER = False


def get_rating(rating_class):
    """
    :param rating_class: string
    :return: int
    example: "rating1-t" => 1
                "rating2-t" => 2
    """
    return int(rating_class[6])


def get_imdb_id(url):
    r = requests.get(url, headers={'User-Agent': USER_AGENT})
    soup = BeautifulSoup(r.text, 'lxml')
    info_area = soup.find(id='info')
    imdb_id = None
    try:
        if info_area:
            for index in range(-1, -len(info_area.find_all('span')) + 1, -1):
                imdb_id = info_area.find_all('span')[index].next_sibling.strip()
                if imdb_id.startswith('tt'):
                    break
        else:
            print('不登录无法访问此电影页面：', url)
    except:
        print('无法获得IMDB编号的电影页面：', url)
    finally:
        return imdb_id if not imdb_id or imdb_id.startswith('tt') else None


def get_info(url, page, category='collect'):
    page_data = []
    r = requests.get(url, headers={'User-Agent': USER_AGENT})
    soup = BeautifulSoup(r.text, "lxml")
    movie_items = soup.find_all("div", {"class": "item"})

    if len(movie_items) > 0:
        for item in movie_items:
            time.sleep(random.uniform(2, 7))
            # meta data
            douban_link = item.a['href']
            title = item.find("li", {"class": "title"}).em.text

            rating = item.find(
                "span", {"class": "date"}).find_previous_siblings()
            if len(rating) > 0:
                rating = get_rating(rating[0]['class'][0])
            else:
                rating = None

            comment = item.find("span", {"class": "comment"})
            if comment is not None:
                comment = comment.contents[0].strip()

            comment_date = item.find("span", {"class": "date"})
            if comment_date is not None:
                comment_date = comment_date.contents[0].strip()

            imdb = get_imdb_id(douban_link)

            if datetime.strptime(comment_date, DATE_FORMAT) <= datetime.strptime(START_DATE, DATE_FORMAT):
                global IS_OVER
                IS_OVER = True
                break

            this_data = {'title': title,
                         'rating': rating,
                         'imdb': imdb if imdb is not None else "NO_IMDB_LINK",
                         'date': comment_date,
                         'comment': comment,
                         'url': douban_link,
                         'peopleUrl': url,
                         'page': page
                         }
            print(this_data)
            page_data.append(this_data)

        df = pd.DataFrame(page_data)
        match category:
            case 'wish':
                result_file = 'movie-wish.csv'
            case 'do':
                result_file = 'movie-do.csv'
            case _:
                result_file = 'movie.csv'

        df.to_csv(result_file, mode='a', index=False, header=False)
        print(f"Saved {category} page {page}, total {len(df.index)} movies.")


def get_max_index(user_id, category='collect'):
    url = f"https://movie.douban.com/people/{user_id}/{category}"
    r = requests.get(url, headers={'User-Agent': USER_AGENT})
    soup = BeautifulSoup(r.text, "lxml")

    paginator = soup.find("div", {"class": "paginator"})
    if paginator is not None:
        max_index = paginator.find_all("a")[-2].get_text()
    else:
        max_index = 1
    print(f'总共 {max_index} 页')
    return int(max_index)


def url_generator(user_id, page=1, category='collect'):
    max_index = get_max_index(user_id, category)
    for index in range((page - 1) * 15, max_index * 15, 15):
        yield f"https://movie.douban.com/people/{user_id}/{category}" \
              f"?start={index}&sort=time&rating=all&filter=all&mode=grid"


def export(category=CATEGORY):
    page_no = START_PAGE
    urls = url_generator(DB_USER, page_no, category)
    for url in urls:
        if IS_OVER:
            break
        print(f'Getting {category} page {page_no}: {url}...')
        get_info(url, page_no, category)
        page_no += 1


def check_user_exist(user_id):
    r = requests.get(f'https://movie.douban.com/people/{user_id}/', headers={'User-Agent': USER_AGENT})
    soup = BeautifulSoup(r.text, 'lxml')
    if '页面不存在' in soup.title:
        return False
    else:
        return True


if __name__ == '__main__':
    if not check_user_exist(DB_USER):
        print('请输入正确的dbID，如何查找自己的dbID 请参照：',
              'https://github.com/fisheepx/douban-to-imdb')
        sys.exit()

    print(f'Getting {CATEGORY} data after {START_DATE}...')
    export()

