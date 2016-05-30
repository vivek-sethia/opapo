from bs4 import BeautifulSoup
from src.vendor.aws_signed_request import aws_signed_request
from xml.dom import minidom

import requests
import json
import re
import locale

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


def scrape_amazon_site(public_key, private_key, associate_tag, url):

    # url = 'http://www.amazon.com/dp/B0047E0EII/ref=azfs_379213722_HutzlerBananaSlicer_1'
    # url = 'http://www.amazon.com/Apple-MMGG2LL-MacBook-13-3-Inch-VERSION/dp/B01EIUP20U/ref=
    # sr_1_3?s=pc&ie=UTF8&qid=1463238054&sr=1-3&keywords=apple+macbook+air'
    # url = 'http://www.amazon.com/Harry-Potter-Sorcerers-Stone-Illustrated/dp/0545790352/ref=
    # sr_1_5?s=books&ie=UTF8&qid=1463325600&sr=1-5&keywords=harry+potter'

    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    r = requests.get(url.strip(), headers=headers)

    data = r.text

    soup = BeautifulSoup(data, 'html.parser')
    json_data = {}

    title_el = soup.find("span", {"id": "productTitle"})
    if not(title_el is None):
        json_data['title'] = title_el.text.encode('utf-8').strip()

    price_el = soup.find("span", {"id": "priceblock_ourprice"})
    if not(price_el is None):
        json_data['price'] = str(price_el.text).strip()

    shipping_el = soup.find("span", {"id": "ourprice_shippingmessage"})
    if not(shipping_el is None):
        json_data['shipping'] = str(shipping_el.text).strip().lstrip('&').strip()

    json_data['rating'] = {}

    rating_el = soup.find("div", {"id": "avgRating"})
    if not(rating_el is None):
        json_data['rating']['average'] = str(rating_el.text).strip()

    review_count_el = soup.find("span", {"id": "acrCustomerReviewText"})
    if not(review_count_el is None):
        review_count = re.findall(r'\d+(?:,\d+)?', review_count_el.text)[0]
        json_data['rating']['review_count'] = locale.atoi(review_count)

    review_summary_el = soup.find('div', {'id': 'revSum'})
    if not(review_summary_el is None):

        for review_row_el in review_summary_el.find_all('tr', {'class': 'a-histogram-row'}):
            if not(review_row_el is None):

                review_name_el = review_row_el.select("a:nth-of-type(1)")
                review_rating_el = review_row_el.select("a:nth-of-type(3)")
                if review_name_el and review_rating_el:
                    json_data['rating'][review_name_el[0].text] = review_rating_el[0].text

    image_el = soup.find("img", {"id": "landingImage"})
    if not(image_el is None):
        json_data['image'] = image_el.attrs["src"]

    brand_el = soup.find("a", {"id": "brand"})
    if not(brand_el is None):
        json_data['brand'] = brand_el.text

    title_el_block = soup.select('div[id*="Title"]')[0]
    if not(title_el_block is None):
        author_row_el = title_el_block.find("span", {"class": "author"})

        if not(author_row_el is None):
            author_el = author_row_el.find("span")

            if not(author_el is None):
                json_data['author'] = str(author_el.text).strip().rstrip("(Author)").strip()

    merchant_row_el = soup.find("div", {"id": "merchant-info"})
    if not(merchant_row_el is None):
        merchant_el = merchant_row_el.find("a")

        if not(merchant_el is None):
            json_data['merchant'] = merchant_el.text

    savings_row_el = soup.find("tr", {"id": "regularprice_savings"})
    if not(savings_row_el is None):
        savings_el = savings_row_el.find("td", {"class": "a-color-price"})

        if not(savings_el is None):
            json_data['savings'] = str(savings_el.text).strip()

    availability_row_el = soup.find("div", {"id": "availability"})
    if not(availability_row_el is None):
        availability_el = availability_row_el.find("span")

        if not(availability_el is None):
            json_data['availability'] = str(availability_el.text).strip()

    features_row_el = soup.find("div", {"id": "feature-bullets"})
    if not(features_row_el is None):
        json_data['features'] = {}
        index = 1

        for feature_el in features_row_el.find_all("li", {"id": ""}):
            if not(feature_el is None):
                json_data['features'][index] = feature_el.text
                index += 1

    promotions_row_el = soup.find("div", {"id": "promotions_feature_div"})
    if not(promotions_row_el is None):
        promotion_el = promotions_row_el.find("li")

        if not(promotion_el is None):
            json_data['promotion'] = str(promotion_el.text).strip()

    similar_items_el_block = soup.find("div", {"id": "purchase-sims-feature"})
    if not(similar_items_el_block is None):
        json_data['similarItems'] = {}
        index = 1

        for similar_items_elRow in similar_items_el_block.find_all("li"):
            if not(similar_items_elRow is None):
                similar_items_el = similar_items_elRow.find(lambda tag: tag.name == 'div' and 'data-rows' in tag.attrs)
                if not(similar_items_el is None):
                    json_data['similarItems'][index] = similar_items_el.text
                    index += 1

    categories_el_block = soup.find("div", {"id": "wayfinding-breadcrumbs_feature_div"})
    if not(categories_el_block is None):
        json_data['categories'] = {}
        index = 1

        for categories_el in categories_el_block.find_all("li", {"class": ""}):
            if not(categories_el is None):
                json_data['categories'][index] = categories_el.text
                index += 1

    frequently_bought_el_block = soup.find("form", {"id": "sims-fbt-form"})
    if not(frequently_bought_el_block is None):

        json_data['frequently_bought_together'] = {}
        index = 1

        for frequently_bought_el in frequently_bought_el_block.find_all("label"):
            if not(frequently_bought_el is None):

                if index == 1:
                    index += 1
                else:
                    frequently_bought_el_name = frequently_bought_el.find("a")
                    if not(frequently_bought_el_name is None):

                        json_data['frequently_bought_together'][index] = {}
                        json_data['frequently_bought_together'][index]['name'] = frequently_bought_el_name.text

                        frequently_bought_el_price = frequently_bought_el.find("span", {"class": "a-color-price"})
                        if not(frequently_bought_el_price is None):
                            json_data['frequently_bought_together'][index]['price'] = frequently_bought_el_price.text

                        frequently_bought_el_availability = frequently_bought_el.find("span", {
                            "class": "a-size-base a-color-success"})
                        if not(frequently_bought_el_availability is None):
                            json_data['frequently_bought_together'][index]['availability'] = \
                                frequently_bought_el_availability.text

                        frequently_bought_el_merchant = frequently_bought_el.find("span", {
                            "class": "a-size-base a-color-secondary a-text-normal"})
                        if not(frequently_bought_el_merchant is None):
                            json_data['frequently_bought_together'][index]['merchant'] = \
                                frequently_bought_el_merchant.text

                        index += 1

    reviews_el_block = soup.find("div", {"id": "customer-reviews_feature_div"})
    if not(reviews_el_block is None):
        json_data['reviews'] = {}
        index = 1

        for reviews_el in reviews_el_block.select('div[id*="rev-"]'):
            if not(reviews_el is None):
                json_data['reviews'][index] = {}

                review_rating_el = reviews_el.select("a:nth-of-type(1)")[0]
                if not(review_rating_el is None):
                    json_data['reviews'][index]['review_rating'] = str(review_rating_el.attrs['title']).strip()

                review_by_el = reviews_el.select("a:nth-of-type(3)")[0]
                if not(review_by_el is None):
                    json_data['reviews'][index]['reviewed_by'] = str(review_by_el.text).strip()

                reviewed_on_el = review_by_el.find_next("span")
                if not(reviewed_on_el is None):
                    json_data['reviews'][index]['reviewed_on'] = str(reviewed_on_el.text).strip().lstrip('on ')

                review_data_el = reviews_el.select('div[id*="revData-"]')[0].find("div")
                if not(review_data_el is None):
                    json_data['reviews'][index]['text'] = str(review_data_el.text).strip()
                    index += 1

    details_el_block = soup.find("table", {"id": "productDetails_detailBullets_sections1"})
    if not(details_el_block is None):
        json_data['details'] = {}
        pattern = re.compile("review", flags=re.IGNORECASE)

        for details_el in details_el_block.find_all("tr"):
            if not(details_el is None):

                detail_key_el = details_el.find("th")
                detail_value_el = details_el.find("td")

                if not(detail_key_el is None) and not(detail_value_el is None) and \
                        (pattern.search(detail_key_el.text) is None):
                    json_data['details'][str(detail_key_el.text).strip()] = str(detail_value_el.text).strip()

    competitors_el_block = soup.find("div", {"id": "mbc"})
    if not(competitors_el_block is None):
        json_data['competitors'] = {}
        index = 1

        for competitor_el in competitors_el_block.find_all("div", {"class": "mbc-offer-row"}):
            if not(competitor_el is None):

                json_data['competitors'][index] = {}

                competitor_price_el = competitor_el.find("span", {"class": "a-color-price"})
                if not(competitor_price_el is None):
                    json_data['competitors'][index]['price'] = str(competitor_price_el.text).strip()

                competitor_name_el = competitor_el.find("span", {"class": "mbcMerchantName"})
                if not(competitor_name_el is None):
                    json_data['competitors'][index]['merchant'] = str(competitor_name_el.text).strip()
                    index += 1

    json_data['ASIN'] = json_data['details']['ASIN']
    json_data['questions'] = get_customer_questions(json_data['ASIN'])
    json_data['UPC'] = get_product_upc(public_key, private_key, associate_tag, json_data['ASIN'])

    data = {}
    data['id'] = json_data['UPC']
    data['scraped_data'] = json_data

    return data


def get_customer_questions(asin):

    url = 'http://www.amazon.com/gp/ask-widget/askWidget.html?asin=' + asin
    r = requests.get(url)

    data = r.text

    soup = BeautifulSoup(data, 'html.parser')
    json_data = {}

    questions_row_el = soup.find("div", {"class": "askTeaserQuestions"})

    if not(questions_row_el is None):
        index = 1

        for question_el in questions_row_el.select('div[id*="question"]'):
            json_data[index] = {}
            json_data[index]['question'] = str(question_el.text).strip().lstrip('Question:').lstrip()
            answer_el = question_el.find_next_sibling("div")

            if not(answer_el is None):
                answer_text = answer_el.select("span:nth-of-type(2)")[0]
                answered_by = answer_el.select("span:nth-of-type(3)")[0]
                json_data[index]['answer'] = str(answer_text.text).strip()
                json_data[index]['answered_by'] = str(answered_by.text).strip()

            index += 1

    return json_data


def get_product_upc(public_key, private_key, associate_tag, asin):

    # generate signed URL
    url = aws_signed_request('com', {
            'Operation': 'ItemLookup',
            'ItemId': asin,
            'ResponseGroup': 'ItemAttributes'}, public_key, private_key, associate_tag)

    response = requests.get(url)
    xml = minidom.parseString(response.text.encode('utf-8'))
    upc_el = xml.getElementsByTagName('UPC')

    return upc_el[0].firstChild.nodeValue
