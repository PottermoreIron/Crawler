import csv, os, re, json, random, time
import requests
from bs4 import BeautifulSoup
from itertools import islice

urls_files_path = 'cities.csv'
city_urls = []
food_base_url = 'https://you.ctrip.com/fooditem/city/s0-p1.html'
# 按点评分排序
restaurant_base_url = 'https://you.ctrip.com/restaurantlist/city/s0-p1.html?ordertype=3'
restaurant_detail_base_url = 'https://you.ctrip.com'
foodItems = []
restaurants = []
# clean symbol like '\n','\u3000','.','、','【','《》','-','·',',','。'
re_str = r'\\\w(\d{4})?|\.|\s|、|【|】|《|》|-|•|，|。|？|！|：|；|‘|”|·'


def handleCsvData():
    if os.path.exists(urls_files_path):
        with open(urls_files_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            # 不读表头
            for row in islice(reader, 1, None):
                url_info = {'province': row[0], 'city': row[1], 'id': row[2], 'url': row[3]}
                city_urls.append(url_info)
    else:
        print("The file doesn't exists")


def getHTMLText(url):
    try:
        # 伪装头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE '
        }
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return "Network ERROR"


# get city's food and related restaurants
def handleFoodInfo(city, html):
    food_one_city = []
    soup = BeautifulSoup(html, 'lxml')
    food_list = soup.select('.foodlist')
    for food_info in food_list:
        # get 'where to eat' data
        restaurants_list = food_info.select('p > a')
        arr = []
        for restaurant in restaurants_list:
            arr.append(re.sub(re_str, '', restaurant.string))
        food = {'name': re.sub(re_str, '', food_info.select('dt > a')[0].string),
                'restaurants': arr}
        food_one_city.append(food)
    # print(city, food_one_city)
    return food_one_city


def handleRestaurantInfo(city, html):
    soup = BeautifulSoup(html, 'lxml')
    restaurant_detail_urls = []
    urls = soup.select('.rdetailbox dt > a')
    for url in urls:
        restaurant_detail_urls.append(url['href'])
    return restaurant_detail_urls


def handleRestaurantDetail(html):
    soup = BeautifulSoup(html, 'lxml')
    cuisine = []
    items = soup.select('.s_sight_con dd > a')
    for item in items:
        cuisine.append(re.sub(re_str, '', item.string))
    restaurant = {'name': re.sub(re_str, '', soup.select('.f_left h1')[0].text),
                  'price': '' if not soup.find(class_='price') else soup.find(class_='price').string[1:],
                  'cuisine': cuisine,
                  # Notification error
                  'specialities': '' if len(soup.select('.text_style p')) == 0 or len(
                      soup.select('.text_style p span')) > 0 else re.sub(re_str, "",
                                                                         soup.select('.text_style p')[
                                                                             0].string).split(','),
                  'overall_score': '' if len(soup.select('dt .score')) == 0 else
                  soup.select('dt .score')[0].text.split('/')[0],
                  'taste_score': '' if len(soup.select('dd .score')) == 0 else soup.select('dd .score')[0].string,
                  'environment_core': '' if len(soup.select('dd .score')) <= 1 else soup.select('dd .score')[1].string,
                  'service_score': '' if len(soup.select('dd .score')) <= 2 else soup.select('dd .score')[2].string}
    return restaurant


def parseHTML(city, html1, html2):
    food_list = handleFoodInfo(city, html1)
    restaurant_list = []
    restaurants_detail_urls = handleRestaurantInfo(city, html2)
    for url in restaurants_detail_urls:
        url = restaurant_detail_base_url + url
        # print(url)
        html = getHTMLText(url)
        restaurant = handleRestaurantDetail(html)
        restaurant_list.append(restaurant)
    print(city)
    print('food', food_list)
    print('restaurant', restaurant_list)
    return food_list, restaurant_list


def main():
    # food url:https://you.ctrip.com/fooditem/beijing1/so-p1.html
    # restaurant url:https://you.ctrip.com/restaurantlist/beijing1/s0-p1.html?ordertype=3
    # restaurant detail:https://you.ctrip.com/food/beijing1/78793329.html

    handleCsvData()
    for city in city_urls:
        food_url = food_base_url.replace("city", city['url'])
        restaurant_url = restaurant_base_url.replace("city", city['url'])
        # sleep
        t = random.randint(1, 5)
        time.sleep(t)
        # get html
        food_html = getHTMLText(food_url)
        restaurant_html = getHTMLText(restaurant_url)
        # deal with the html
        res1, res2 = parseHTML(city['city'], food_html, restaurant_html)
        # save
        foodItems.append(res1)
        restaurants.append(res2)


if __name__ == '__main__':
    main()
