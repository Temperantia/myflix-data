from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as OptionsFirefox
from selenium.webdriver.chrome.options import Options as OptionsChrome
from json import load, dump
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from threads import threads
from time import perf_counter
from firebase import video_collection

DEBUG = True
CONTINUE = False
BROWSER = 'chrome'
BROWSER_NUM = 1
if DEBUG:
  BROWSER_NUM = 1
TIME_OUT = 5

# TODO
# STARRING MISSING
# CAST IMAGES ARE NOT LOADED
# VIDEO MISSING KEY, ACCESS FOR 1 DAY ONLY
# STUART LITTLE : DOUBLE CHARACTER
# COLLISION IN MONONOKE

base_url = 'https://www.imdb.com'
options = OptionsFirefox() if BROWSER == 'firefox' else OptionsChrome()
options.add_argument('--headless')
options.add_argument('log-level=2')
browsers = []
source = load(open('data/videos.json', 'r', encoding='utf-8'))
data = {}

def search_page(browser, url_search_with_year, url_search):
    browser.get(url_search_with_year)
    WebDriverWait(browser, TIME_OUT).until(
        EC.presence_of_element_located((By.ID, 'pagecontent')))
    try:
        return browser.find_element_by_class_name('result_text').find_element_by_tag_name(
            'a').get_attribute('href').split('?')[0]
    except:
        browser.get(url_search)
        WebDriverWait(browser, TIME_OUT).until(
        EC.presence_of_element_located((By.ID, 'pagecontent')))
        try:
            return browser.find_element_by_class_name('result_text').find_element_by_tag_name(
            'a').get_attribute('href').split('?')[0]
        except:
            return None

def main_page(browser, id, url_title):
    global data
    browser.get(url_title)
    WebDriverWait(browser, TIME_OUT).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'pagecontent')))
    try:
        image = browser.find_element_by_class_name('poster').find_element_by_tag_name('img').get_attribute('src')
        data[id]['tallBoxArt'] = image
    except:
        data[id]['tallBoxArt'] = None
    try:
        if DEBUG:
            print('Getting cast')
        lines = browser.find_element_by_class_name('cast_list').find_elements_by_xpath(
        '//tr[contains(@class, "odd") or contains(@class, "even")]')
        cast = []
        for line in lines:
            info = line.find_elements_by_tag_name('td')
            image = info[0].find_element_by_tag_name(
                'img').get_attribute('loadlate')
            name = info[1].find_element_by_tag_name('a').text
            character = info[3].find_elements_by_tag_name('a')
            character_name = character[0].text
            episodes = character[1].text if len(character) > 1 else None
            cast.append({'image': image, 'name': name,
                        'character': character_name, 'episodes': episodes})
        data[id]['cast'] = cast
    except:
        data[id]['cast'] = None
"""     try:
      return browser.find_element_by_class_name('slate_wrapper').find_element_by_class_name(
        'slate').find_element_by_tag_name('a').get_attribute('href')
    except:
      return None """



def trailer_page(browser, id, url_trailer):
    global data
    if not url_trailer:
      data[id]['trailer'] = None
      return

"""     browser.get(url_trailer)
    video = WebDriverWait(browser, 5).until(
        EC.presence_of_element_located((By.TAG_NAME, 'video')))
    data[id]['trailer'] = video.get_attribute(
        'src').split('?')[0]
 """

def credits_page(browser, id, url_title):
    global data
    try:
      browser.get(url_title + 'companycredits')
      credits = {}
      WebDriverWait(browser, TIME_OUT).until(
        EC.presence_of_element_located((By.ID, 'pagecontent')))
      categories = browser.find_elements_by_class_name('dataHeaderWithBorder')
      lists = browser.find_elements_by_class_name('simpleList')
      for index, category in enumerate(categories):
          credits[category.text] = []
          elements = lists[index].find_elements_by_tag_name('li')
          for element in elements:
              credits[category.text].append(element.text)
      data[id]['credits'] = credits
    except:
      data[id]['credits'] = None


def imdb(id, index):
    global browsers
    browser = browsers[index % BROWSER_NUM]
    data[id] = {}

    title = source[id]['title']
    year = str(source[id]['releaseYear'])
    url_search_with_year = 'https://www.imdb.com/find?q=' + \
        str(quote_plus(title + ' ' + year))
    url_search = 'https://www.imdb.com/find?q=' + \
        str(quote_plus(title))

    try:
        if DEBUG:
            print('entering search for ' + title)
        url_title = search_page(browser, url_search_with_year, url_search)
        if not url_title:
            return
        if DEBUG:
            print('entering main for ' + title)
        main_page(browser, id, url_title)
        if DEBUG:
            print('entering credits for ' + title)
        credits_page(browser, id, url_title)
        if DEBUG:
            print('entering trailer for ' + title)
        trailer_page(browser, id, title)
    except Exception as e:
        print(e)
        print(title)
    print ('Uploading ' + id)
    video_collection.document(id).update(data[id])

def launch():
    for i in range(BROWSER_NUM):
        if BROWSER == 'firefox':
            browsers.append(webdriver.Firefox(options=options))
        else:
            browsers.append(webdriver.Chrome(options=options))

    tic = perf_counter()

    if DEBUG:
        imdb('28631029', 0)
    else:
        ids = []
        for index, id in enumerate(source):
            if CONTINUE and source[id]['tallBoxArt'] is not None:
                continue
            ids.append((id, index,))
            if index != 0 and index % BROWSER_NUM == 0:
                threads(imdb, ids, 0.02)
                ids = []
                print(str(index) + ' out of ' + str(len(source)))
                print(perf_counter() - tic)



    for browser in browsers:
      browser.close()

if DEBUG:
  launch()
