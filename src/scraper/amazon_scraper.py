from bs4 import BeautifulSoup
from src.vendor.aws_signed_request import aws_signed_request
from xml.dom import minidom
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from vaderSentiment.vaderSentiment import sentiment
from watson_developer_cloud import ToneAnalyzerV3

import requests
import json
import re
import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def get_text(element):
    return element.text.encode('utf-8').strip()


def get_page_by_url(url):
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    r = requests.get(url.strip(), headers=headers)

    return r.text


def get_page_by_code(code):

    url = 'https://www.amazon.com/s/ref=nb_sb_noss?field-keywords=' + code

    soup = BeautifulSoup(get_page_by_url(url), 'html.parser')

    results_el = soup.find('a', {'class': 's-access-detail-page'})

    if not (results_el is None):
        url = results_el.attrs["href"]
        return url, get_page_by_url(url)


def scrape_amazon_site(config, format, product_id):

    json_data = {
        'details': {}
    }
    data = {
        'id': '',
        'scraped_data': ''
    }

    # url = 'http://www.amazon.com/dp/B0047E0EII/ref=azfs_379213722_HutzlerBananaSlicer_1'
    # url = 'http://www.amazon.com/Apple-MMGG2LL-MacBook-13-3-Inch-VERSION/dp/B01EIUP20U/ref=
    # sr_1_3?s=pc&ie=UTF8&qid=1463238054&sr=1-3&keywords=apple+macbook+air'
    # url = 'http://www.amazon.com/Harry-Potter-Sorcerers-Stone-Illustrated/dp/0545790352/ref=
    # sr_1_5?s=books&ie=UTF8&qid=1463325600&sr=1-5&keywords=harry+potter'

    if format == 'url':
        page_data = get_page_by_url(product_id)
        json_data['product_link'] = product_id
    else:
        if format == 'asin' or format == 'upc':
            json_data['details']['ASIN'] = product_id
            response = get_page_by_code(product_id)
            json_data['product_link'] = response[0]
            page_data = response[1]
        else:
            return data

    if page_data is None:
        return data

    soup = BeautifulSoup(page_data, 'html.parser')

    title_el = soup.find("span", {"id": "productTitle"})
    if not(title_el is None):
        json_data['title'] = get_text(title_el)

    price_el = soup.find("span", {"id": "priceblock_ourprice"})
    if not(price_el is None):
        json_data['price'] = get_text(price_el)

    shipping_el = soup.find("span", {"id": "ourprice_shippingmessage"})
    if not(shipping_el is None):
        json_data['shipping'] = get_text(shipping_el).lstrip('&').strip()

    json_data['rating'] = {}

    rating_el = soup.find("div", {"id": "avgRating"})
    if not(rating_el is None):
        json_data['rating']['average'] = get_text(rating_el)

    review_count_el = soup.find("span", {"id": "acrCustomerReviewText"})
    if not(review_count_el is None):
        review_count = re.findall(r'\d+(?:(?:,|\.)\d+)*', review_count_el.text)[0]
        json_data['rating']['review_count'] = locale.atoi(review_count)

    review_summary_el = soup.find('div', {'id': 'revSum'})
    if not(review_summary_el is None):
        json_data['rating']['stats'] = {}

        for review_row_el in review_summary_el.find_all('tr', {'class': 'a-histogram-row'}):
            if not(review_row_el is None):

                review_name_el = review_row_el.select("a:nth-of-type(1)")
                review_rating_el = review_row_el.select("a:nth-of-type(3)")
                if review_name_el and review_rating_el:
                    json_data['rating']['stats'][review_name_el[0].text] = review_rating_el[0].text

    image_el = soup.find("img", {"id": "landingImage"})
    if not(image_el is None):
        json_data['image'] = image_el.attrs["src"]

    brand_el = soup.find("a", {"id": "brand"})
    if not(brand_el is None):
        json_data['brand'] = get_text(brand_el)

    title_el_block = soup.select('div[id*="Title"]')
    if title_el_block and not(title_el_block is None):
        author_row_el = title_el_block[0].find("span", {"class": "author"})

        if not(author_row_el is None):
            author_el = author_row_el.find("span")

            if not(author_el is None):
                json_data['author'] = get_text(author_el).rstrip("(Author)").strip()

    merchant_row_el = soup.find("div", {"id": "merchant-info"})
    if not(merchant_row_el is None):
        merchant_el = merchant_row_el.find("a")

        if not(merchant_el is None):
            json_data['merchant'] = get_text(merchant_el)

    savings_row_el = soup.find("tr", {"id": "regularprice_savings"})
    if not(savings_row_el is None):
        savings_el = savings_row_el.find("td", {"class": "a-color-price"})

        if not(savings_el is None):
            json_data['savings'] = get_text(savings_el)

    availability_row_el = soup.find("div", {"id": "availability"})
    if not(availability_row_el is None):
        availability_el = availability_row_el.find("span")

        if not(availability_el is None):
            json_data['availability'] = get_text(availability_el)

    features_row_el = soup.find("div", {"id": "feature-bullets"})
    if not(features_row_el is None):
        json_data['features'] = []

        for feature_el in features_row_el.find_all("li", {"id": ""}):
            if not(feature_el is None):
                json_data['features'].append(get_text(feature_el))

    promotions_row_el = soup.find("div", {"id": "promotions_feature_div"})
    if not(promotions_row_el is None):
        promotion_el = promotions_row_el.find("li")

        if not(promotion_el is None):
            json_data['promotion'] = get_text(promotion_el)

    similar_items_el_block = soup.find("div", {"id": "purchase-sims-feature"})
    if not(similar_items_el_block is None):
        json_data['similarItems'] = []

        for similar_items_elRow in similar_items_el_block.find_all("li"):
            if not(similar_items_elRow is None):
                similar_items_el = similar_items_elRow.find(lambda tag: tag.name == 'div' and 'data-rows' in tag.attrs)
                if not(similar_items_el is None):
                    json_data['similarItems'].append(get_text(similar_items_el))

    categories_el_block = soup.find("div", {"id": "wayfinding-breadcrumbs_feature_div"})
    if not(categories_el_block is None):
        json_data['categories'] = []

        for categories_el in categories_el_block.find_all("li", {"class": ""}):
            if not(categories_el is None):
                json_data['categories'].append(get_text(categories_el))

    frequently_bought_el_block = soup.find("form", {"id": "sims-fbt-form"})
    if not(frequently_bought_el_block is None):

        json_data['frequently_bought_together'] = []
        index = -1

        for frequently_bought_el in frequently_bought_el_block.find_all("label"):
            if not(frequently_bought_el is None):

                if index == -1:
                    index += 1
                else:
                    frequently_bought_el_name = frequently_bought_el.find("a")
                    if not(frequently_bought_el_name is None):

                        json_data['frequently_bought_together'].append({})
                        json_data['frequently_bought_together'][index]['name'] = get_text(frequently_bought_el_name)

                        frequently_bought_el_price = frequently_bought_el.find("span", {"class": "a-color-price"})
                        if not(frequently_bought_el_price is None):
                            json_data['frequently_bought_together'][index]['price'] = get_text(frequently_bought_el_price)

                        frequently_bought_el_availability = frequently_bought_el.find("span", {
                            "class": "a-size-base a-color-success"})
                        if not(frequently_bought_el_availability is None):
                            json_data['frequently_bought_together'][index]['availability'] = \
                                get_text(frequently_bought_el_availability)

                        frequently_bought_el_merchant = frequently_bought_el.find("span", {
                            "class": "a-size-base a-color-secondary a-text-normal"})
                        if not(frequently_bought_el_merchant is None):
                            json_data['frequently_bought_together'][index]['merchant'] = \
                                get_text(frequently_bought_el_merchant)

                        index += 1

    details_el_block = soup.find("table", {"id": "productDetails_detailBullets_sections1"})
    if not(details_el_block is None):
        pattern = re.compile("review", flags=re.IGNORECASE)

        for details_el in details_el_block.find_all("tr"):
            if not(details_el is None):

                detail_key_el = details_el.find("th")
                detail_value_el = details_el.find("td")

                if not(detail_key_el is None) and not(detail_value_el is None) and \
                        (pattern.search(detail_key_el.text) is None):
                    json_data['details'][get_text(detail_key_el)] = get_text(detail_value_el)

    if json_data['details'].get('ASIN') is None:
        asin_el = soup.find("input", {"id": "ASIN"})
        if not(asin_el is None):
            json_data['details']['ASIN'] = get_text(asin_el)

    competitors_el_block = soup.find("div", {"id": "mbc"})
    if not(competitors_el_block is None):
        json_data['other_sellers'] = {}
        json_data['other_sellers']['details'] = []
        json_data['other_sellers']['average_price'] = 0
        index = 0
        sum = 0

        for competitor_el in competitors_el_block.find_all("div", {"class": "mbc-offer-row"}):
            if not(competitor_el is None):

                json_data['other_sellers']['details'].append({})

                competitor_price_el = competitor_el.find("span", {"class": "a-color-price"})
                if not(competitor_price_el is None):

                    competitor_price = re.findall(r'\d+(?:(?:,|\.)\d+)*', competitor_price_el.text)[0]
                    competitor_price = locale.atof(competitor_price)
                    sum += competitor_price
                    json_data['other_sellers']['details'][index]['price_num'] = competitor_price
                    json_data['other_sellers']['details'][index]['price'] = get_text(competitor_price_el)

                competitor_name_el = competitor_el.find("span", {"class": "mbcMerchantName"})
                if not(competitor_name_el is None):
                    json_data['other_sellers']['details'][index]['merchant'] = get_text(competitor_name_el)
                    index += 1

                json_data['other_sellers']['average_price'] = round(sum/index, 4)

    result = get_customer_reviews(soup, config)
    json_data['reviews'] = result[0]
    json_data['review_sentiments'] = result[1]
    json_data['review_tones'] = result[2]

    json_data['ASIN'] = json_data['details']['ASIN']
    json_data['questions'] = get_customer_questions(json_data['ASIN'])
    json_data['UPC'] = get_product_upc(config, json_data['ASIN'])

    data = {
        'id': json_data['UPC'],
        'scraped_data': json_data
    }

    return data


def get_customer_questions(asin):

    url = 'http://www.amazon.com/gp/ask-widget/askWidget.html?asin=' + asin
    r = requests.get(url)

    data = r.text

    soup = BeautifulSoup(data, 'html.parser')
    json_data = []

    questions_row_el = soup.find("div", {"class": "askTeaserQuestions"})

    if not(questions_row_el is None):
        index = 0

        for question_el in questions_row_el.select('div[id*="question"]'):
            json_data.append({})
            json_data[index]['question'] = get_text(question_el).lstrip('Question:').lstrip()
            answer_el = question_el.find_next_sibling("div")

            if not(answer_el is None):
                answer_text = answer_el.select("span:nth-of-type(2)")[0]
                answered_by = answer_el.select("span:nth-of-type(3)")[0]
                json_data[index]['answer'] = get_text(answer_text)
                json_data[index]['answered_by'] = get_text(answered_by)

            index += 1

    return json_data


def get_product_upc(config, asin):

    # generate signed URL
    url = aws_signed_request('com', {
            'Operation': 'ItemLookup',
            'ItemId': asin,
            'ResponseGroup': 'ItemAttributes'}, config['PUBLIC_KEY'], config['PRIVATE_KEY'], config['ASSOCIATE_TAG'])

    response = requests.get(url)
    xml = minidom.parseString(get_text(response))
    # print xml.toprettyxml()
    upc_el = xml.getElementsByTagName('UPC') or xml.getElementsByTagName('EAN')

    return upc_el[0].firstChild.nodeValue


def get_customer_reviews(soup, config):

    all_reviews = ''
    json_data = {
        'reviews': [],
        'sentiments': [
            {'name': '1 star', 'data': []},
            {'name': '2 star', 'data': []},
            {'name': '3 star', 'data': []},
            {'name': '4 star', 'data': []},
            {'name': '5 star', 'data': []},
        ]
    }

    reviews_el_block = soup.find("div", {"id": "customer-reviews_feature_div"})
    if not(reviews_el_block is None):

        review_link_block_el = reviews_el_block.find("div", {"id": "revF"})
        if not(review_link_block_el is None):

            review_link_el = review_link_block_el.find("a")
            if not(review_link_el is None):

                review_link_href = review_link_el.attrs['href']

                for page in range(1, 4):
                    all_reviews += get_reviews_by_page(review_link_href, page, json_data['reviews'],
                                                       json_data['sentiments'])

    json_data['tones'] = get_tone(all_reviews, config)
    return json_data['reviews'], json_data['sentiments'], json_data['tones']


def get_reviews_by_page(review_link_href, page, reviews, sentiments):

    all_reviews = ''
    review_link_href = review_link_href + '&pageNumber=' + str(page)
    index = (page - 1) * 10

    review_page_data = BeautifulSoup(get_page_by_url(review_link_href), 'html.parser')

    review_container_el = review_page_data.find("div", {"id": "cm_cr-review_list"})
    if not(review_container_el is None):

        for reviews_el in review_container_el.find_all("div", {"class": "review"}):
            if not(reviews_el is None):

                reviews.append({})

                review_data_el = reviews_el.find("span", {"class": "review-text"})
                review_rating_el = reviews_el.find("i", {"class": "review-rating"}).find("span")

                if not(review_data_el is None) and not(review_rating_el is None):

                    reviews_text = get_text(review_data_el)
                    reviews[index]['text'] = reviews_text
                    all_reviews += reviews_text
                    review_sentiment = sentiment(reviews_text)
                    reviews[index]['sentiment'] = review_sentiment

                    review_rating = get_text(review_rating_el)
                    reviews[index]['review_rating'] = review_rating

                    if '1.0' in review_rating:
                        sentiments[0]['data'].append([review_sentiment['compound'], 1.0])
                    if '2.0' in review_rating:
                        sentiments[1]['data'].append([review_sentiment['compound'], 2.0])
                    if '3.0' in review_rating:
                        sentiments[2]['data'].append([review_sentiment['compound'], 3.0])
                    if '4.0' in review_rating:
                        sentiments[3]['data'].append([review_sentiment['compound'], 4.0])
                    if '5.0' in review_rating:
                        sentiments[4]['data'].append([review_sentiment['compound'], 5.0])

                    index += 1

    return all_reviews


def get_tone(text, config):

    tone_analyzer = ToneAnalyzerV3(
        username=config['WDC_TA_USER_NAME'],
        password=config['WDC_TA_PASSWORD'],
        version=config['WDC_TA_VERSION'])

    return tone_analyzer.tone(text=text)
