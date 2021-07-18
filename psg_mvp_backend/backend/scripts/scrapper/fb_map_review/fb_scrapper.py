"""
Selenium Facebook scrapper to scrape the review session.
Auth is not handled.

TODO: this is a script badly written by a freelancer

To run:
    1. change CHROME_DRIVER_PATH
    2. >> python run_all <path to your url input file>


"""
# -*- coding: utf-8 -*-
import time
import pandas as pd
from os import path

from seleniumwire import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

import traceback
import typer


CHROME_DRIVER_PATH = "./chromedriver"
fb_page = "https://www.facebook.com/caixinbeauty/reviews/?ref=page_internal"


def convert_month(month):
    months_english = {'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
                      'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11',
                      'December': '12'}

    months_french = {'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04', 'mai': '05', 'juin': '06',
                     'juillet': '07', 'août': '08', 'septembre': '09', 'octobre': '10', 'novembre': '11',
                     'décembre': '12'}

    if month in months_french:
        return months_french[month]
    if month in months_english:
        return months_english[month]


class Articless:
    def __init__(self):
        self.articles_list = []
        self.recommend_elements = []


    def append_articles(self, article_element):
        self.articles_list.append(article_element)


    def append_recommend_container_elements(self, element):
        self.recommend_elements.append(element)


class Users:
    def __init__(self):
        self.users_list = []
        self.recommend_status = []
        self.user_comment = []
        self.post_date = []
        self.user_profile_review = []
        self.page_url = []

    def append_user(self, user, counter):
        self.users_list.append(user)


    def append_recommend(self, recommend):
        self.recommend_status.append(recommend)


    def append_commentary(self, comment):
        self.user_comment.append(comment)


    def append_date(self, date):
        self.post_date.append(date)


    def append_user_profile(self, user_href):
        self.user_profile_review.append(user_href)


    def append_page_url(self, url):
        self.page_url.append(url)



def defining_driver():
    """
    Please change the webdriver path to your corresponding one

    :return:
    """
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--start-maximized')
    options.add_argument('window-size=1536x824')
    wire_options = {
        'connection_timeout': 1000
    }
    driver = webdriver.Chrome("./chromedriver", seleniumwire_options=wire_options, options=options)
    return driver


def get_all_articles_main_container_in_current_page(driver):
    global UserClass
    global Articles
    global counter_skip

    try:
        WebDriverWait(driver, 50).until(EC.invisibility_of_element_located((By.XPATH, '//span[@class="uiMorePagerLoader pam uiBoxWhite noborder"]')))
        time.sleep(3)
        articles = WebDriverWait(driver, 50).until(EC.visibility_of_all_elements_located((By.XPATH, '//div[@role="article"]')))
        print("articles:", articles)
        for article in articles:
            try:
                user = article.find_element_by_xpath('.//a[@aria-hidden="true"]')
                assert user.get_attribute('data-ft') is not None
            except:
                try:
                    user = article.find_element_by_xpath('.//span[@aria-hidden="true"]')
                    assert user.get_attribute('data-ft') is not None
                except:
                    continue

            user_name = user.get_attribute('title')
            UserClass.append_user(user_name, counter_skip)
            nex_div_img = user.find_element_by_xpath('.//div[@class="_38vo"]').find_element_by_tag_name('div').find_element_by_tag_name('img')
            UserClass.append_user_profile(nex_div_img.get_attribute('src'))
            element = user.find_element_by_xpath("./following-sibling::div")
            Articles.append_recommend_container_elements(element)

            parent_one = user.find_element_by_xpath("..")
            parent_two = parent_one.find_element_by_xpath("..")
            goal = parent_two.find_element_by_xpath("..")
            Articles.append_articles(goal)

        #GET RECOM STATUS
        for ele in Articles.recommend_elements:
            status_container_h5 = ele.find_element_by_tag_name('h5')
            status = status_container_h5.find_element_by_tag_name('i')
            if status.get_attribute('className') == '_51mq img sp_OkVielxDWJh sx_9bfe1b':
                UserClass.append_recommend(recommend='Does not recommend')
            elif status.get_attribute('className') == '_51mq img sp_OkVielxDWJh sx_844e6e':
                UserClass.append_recommend(recommend='Recommends')
            #GET DATE
            date = ele.find_element_by_xpath('.//div[@data-testid="story-subtitle"]').find_element_by_tag_name('abbr').get_attribute('innerText')
            UserClass.append_date(date)


        #GET COMMENT
        for ele in Articles.articles_list:
            final_parag = ''
            try:
                comment_element = ele.find_element_by_xpath('.//div[@data-testid="post_message"]')
                try:
                    see_more = comment_element.find_element_by_xpath('.//a[@class="see_more_link"]')
                    see_more.click()
                except:
                    pass
                paragraphes_element = comment_element.find_elements_by_tag_name('p')
                for parag in paragraphes_element:
                    final_parag += parag.get_attribute('innerText') + "\n"
                UserClass.append_commentary(final_parag)
            except:
                ll = traceback.format_exc()
                UserClass.append_commentary("No commentary found")
    except Exception as e:
        ll = traceback.format_exc()
        print(ll)
        raise Exception("Please Send This message to your freelencer as screenshot %s" % str(e))


UserClass = Users()
Articles = Articless()
counter_skip = 0



def fb_scapper(clinic_uuid, fb_page):
    global UserClass
    UserClass = Users()
    global Articles
    Articles = Articless()
    global counter_skip
    counter_skip = 0

    driver = defining_driver()
    driver.get(fb_page)
    clicked=False


    while True:
        try:
            to_scroll_into_view = WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.XPATH, '//div[@class="clearfix uiMorePager stat_elem _4288 _52jv"]')))
            actions = ActionChains(driver)
            actions.move_to_element(to_scroll_into_view).perform()
            if clicked is False:
                try:
                    time.sleep(2)
                    container_close = driver.find_element_by_xpath('//div[@class="_62up"]')
                    a = container_close.find_element_by_tag_name('a')
                    a.click()
                    time.sleep(1)
                    clicked = True
                except:
                    pass
            time.sleep(2)
        except Exception as e:
            break

    time.sleep(10)
    get_all_articles_main_container_in_current_page(driver=driver)
    print(UserClass.users_list)
    print(len(UserClass.users_list))
    print("\n")
    print(UserClass.recommend_status)
    print(len(UserClass.recommend_status))
    print("\n")
    print(UserClass.user_comment)
    print(len(UserClass.user_comment))
    print("\n")
    print(UserClass.post_date)
    print(len(UserClass.post_date))
    print("\n")
    print(UserClass.user_profile_review)
    print(len(UserClass.user_profile_review))

    for item in range(len(UserClass.users_list)):
        UserClass.append_page_url(fb_page)


    df = pd.DataFrame({"User_Name":UserClass.users_list,
                       "Recommendation_Status":UserClass.recommend_status,
                       "User_Comment":UserClass.user_comment,
                       "User_Interaction_Date":UserClass.post_date,
                       "User_Profile":UserClass.user_profile_review,
                       "Page_Source":UserClass.page_url
                       })
    print(df)
    df["clinic_uuid"] = clinic_uuid
    # df.to_csv('LaMerClinic.csv', encoding='utf-8')
    df.to_csv('./scrap_results/%s.csv' % (clinic_uuid), encoding='utf-8')

def run_one(clinic_uuid, url):
    try:
        output_name = './scrap_results/%s.csv' % (clinic_uuid)
        if path.exists(output_name):
            print("%s is done, skipped" % clinic_uuid)
        else:
            fb_scapper(clinic_uuid, url)
    except Exception as e:
        df = pd.DataFrame({"error":"true", "url":url, "clinic_uuid":clinic_uuid})
        df.to_csv('./scrap_results/error_%s.csv' % (clinic_uuid), encoding='utf-8')
        print("Failed on %s with url %s" % clinic_uuid, url)


# def run_all(input_file):
#     failed_cnt = 0
#     with open(input_file, 'r') as f:
#         lines = f.readlines()
#         for line in lines:
#             tokens = line.split()
#             print(tokens)
#
#             try:
#                 output_name = './scrap_results/%s_%s.csv' % (tokens[0], tokens[1])
#                 if path.exists(output_name) or tokens[1] in skips :
#                     print("%s is done, skipped" % tokens[1])
#                     continue
#
#                 fb_scapper(tokens[0], tokens[1], tokens[2])
#             except Exception as e:
#                 failed_cnt += 1
#                 print("Failed on url %s" % tokens[2])
#
#     print("failed_cnt: ", failed_cnt)

if __name__ == "__main__":
    # typer.run(fb_scapper)
    #typer.run(run_all)
    typer.run(run_one)
