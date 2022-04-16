import sys
import time
import pandas as pd
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException


def login():
    driver = webdriver.Chrome()
    driver.get('https://www.imdb.com/registration/signin')
    element = driver.find_element_by_id('signin-perks')
    driver.execute_script("arguments[0].setAttribute('style', 'color: red;font-size: larger; font-weight: 700;')",
                          element)
    driver.execute_script("arguments[0].innerText = '请登录自己的IMDB账号, 程序将等待至登录成功。'", element)
    current_url = driver.current_url
    while True:
        WebDriverWait(driver, 600).until(EC.url_changes(current_url))
        new_url = driver.current_url
        if new_url == 'https://www.imdb.com/?ref_=login':
            break
    print('IMDB登录成功')
    return driver


def mark(is_unmark=False, rating_ajust=0):
    df = pd.read_csv('movie.csv', header=None)
    df = df.iloc[::-1].reset_index(drop=True)

    driver = login()
    success_marked = 0
    success_unmarked = 0
    can_not_found = []
    already_marked = []
    never_marked = []

    for index, row in df.iterrows():
        movie_name = row[0]

        # 如果只标记为看过并没有打过分，then mark as 1 star
        if not row[1]:
            movie_rate = 1
        else:
            movie_rate = int(row[1]) * 2 + rating_ajust

        imdb_id = row[2]
        if not imdb_id or not imdb_id.startswith('tt'):
            can_not_found.append(movie_name)
            print('无法在IMDB上找到：', movie_name)
            continue

        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, 'suggestion-search')))
        search_bar = driver.find_element_by_id('suggestion-search')
        search_bar.send_keys(imdb_id)
        search_bar.submit()
        time.sleep(3)

        if is_unmark:
            driver.find_element_by_xpath('//div[@data-testid="hero-rating-bar__user-rating__score"]')
        else:
            driver.find_element_by_xpath('//div[@data-testid="hero-rating-bar__user-rating"]')

        rate_btn_xpath = '//div[@data-testid="hero-rating-bar__user-rating"]/button'
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, rate_btn_xpath))
        )
        driver.find_element_by_xpath(rate_btn_xpath).click()

        if is_unmark:
            driver.find_element_by_xpath("//div[@class='ipc-starbar']/following-sibling::button[2]").click()
            print(f'电影删除打分成功：{movie_name}({imdb_id})')
            success_unmarked += 1
        else:
            from selenium.webdriver.common.action_chains import ActionChains
            # 新版IMDB页面如果不先将鼠标移动到相应星星处再点击则则点击无效
            star_ele_xpath = f'//button[@aria-label="Rate {movie_rate}"]'
            WebDriverWait(driver, 3).until(
                EC.visibility_of_element_located((By.XPATH, star_ele_xpath))
            )
            star_ele = driver.find_element_by_xpath(star_ele_xpath)
            try:
                mark_action = ActionChains(driver).move_to_element(star_ele).click()
                mark_action.perform()
                confirm_rate_ele_xpath = "//div[@class='ipc-starbar']/following-sibling::button"
                driver.find_element_by_xpath(confirm_rate_ele_xpath).click()
                print(f'电影打分成功：{movie_name}({imdb_id}) → {movie_rate}★')
                success_marked += 1
            except ElementClickInterceptedException:
                if is_unmark:
                    never_marked.append(f'{movie_name}({imdb_id})')
                    print(f'并没有在IMDB上打过分：{movie_name}({imdb_id})')
                else:
                    already_marked.append(f'{movie_name}({imdb_id})')
                    print(f'Failed to rate, maybe already rated: {movie_name}({imdb_id})')

                # search bar not interactable after close, better refresh
                # close_button_xpath = "//div[@class='ipc-promptable-base__close']/button"
                # driver.find_element_by_xpath(close_button_xpath).click()
                driver.refresh()
                continue

        time.sleep(random.uniform(1, 3))
    driver.close()

    print('***************************************************************************')
    if is_unmark:
        print(f'成功删除了 {success_unmarked} 部电影的打分')
        print(f'有 {len(can_not_found)} 部电影没能在IMDB上找到：', can_not_found)
        print(f'有 {len(never_marked)} 部电影并没有在IMDB上打过分：', never_marked)
    else:
        print(f'成功标记了 {success_marked} 部电影')
        print(f'有 {len(can_not_found)} 部电影没能在IMDB上找到：', can_not_found)
        print(f'有 {len(already_marked)} 部电影已经在IMDB上打过分：', already_marked)
    print('***************************************************************************')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'unmark':
        mark(True)
    elif len(sys.argv) > 1:
        if sys.argv[1] not in ['-2', '-1', '0', '1', '2']:
            print('分数调整范围不能超过±2分(默认 -1分)，请参照：',
                  'https://github.com/fisheepx/douban-to-imdb')
            sys.exit()
        else:
            mark(False, int(sys.argv[1]))
    else:
        mark()
