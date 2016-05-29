from bs4 import BeautifulSoup

import requests
import json
import re


def scrape_site(url):

    # url = 'http://www.amazon.com/dp/B0047E0EII/ref=azfs_379213722_HutzlerBananaSlicer_1'
    # url = 'http://www.amazon.com/Apple-MMGG2LL-MacBook-13-3-Inch-VERSION/dp/B01EIUP20U/ref=sr_1_3?s=pc&ie=UTF8&qid=1463238054&sr=1-3&keywords=apple+macbook+air'
    # url = 'http://www.amazon.com/Harry-Potter-Sorcerers-Stone-Illustrated/dp/0545790352/ref=sr_1_5?s=books&ie=UTF8&qid=1463325600&sr=1-5&keywords=harry+potter'

    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    r = requests.get(url, headers=headers)

    data = r.text

    soup = BeautifulSoup(data, 'html.parser')
    json_data = {}

    titleEl = soup.find("span", {"id": "productTitle"})
    if not(titleEl is None):
        json_data['title'] = str(titleEl.text).strip()


    priceEl = soup.find("span", {"id": "priceblock_ourprice"})
    if not(priceEl is None):
        json_data['price'] = str(priceEl.text).strip()


    shippingEl = soup.find("span", {"id": "ourprice_shippingmessage"})
    if not(shippingEl is None):
        json_data['shipping'] = str(shippingEl.text).strip().lstrip('&').strip()


    ratingEl = soup.find("div", {"id": "avgRating"})
    if not(ratingEl is None):
        json_data['rating'] = str(ratingEl.text).strip()


    imageEl = soup.find("img", {"id": "landingImage"})
    if not(imageEl is None):
        json_data['image'] = imageEl.attrs["src"]


    brandEl = soup.find("a", {"id": "brand"})
    if not(brandEl is None):
        json_data['brand'] = brandEl.text


    titleElBlock = soup.select('div[id*="Title"]')[0]
    if not(titleElBlock is None):
        authorRowEl = titleElBlock.find("span", {"class": "author"})

        if not(authorRowEl is None):
            authorEl = authorRowEl.find("span")

            if not(authorEl is None):
                json_data['author'] = str(authorEl.text).strip().rstrip("(Author)").strip()


    merchantElRow = soup.find("div", {"id": "merchant-info"})
    if not(merchantElRow is None):
        merchantEl = merchantElRow.find("a")

        if not(merchantEl is None):
            json_data['merchant'] = merchantEl.text


    savingsElRow = soup.find("tr", {"id": "regularprice_savings"})
    if not(savingsElRow is None):
        savingsEl = savingsElRow.find("td", {"class": "a-color-price"})

        if not(savingsEl is None):
            json_data['savings'] = str(savingsEl.text).strip()


    availabilityElRow = soup.find("div", {"id": "availability"})
    if not(availabilityElRow is None):
        availabilityEl = availabilityElRow.find("span")

        if not(availabilityEl is None):
            json_data['availability'] = str(availabilityEl.text).strip()


    featuresElRow = soup.find("div", {"id": "feature-bullets"})
    if not(featuresElRow is None):
        json_data['features'] = {}
        index = 1

        for featureEl in featuresElRow.find_all("li", {"id": ""}):
            if not(featureEl is None):
                json_data['features'][index] = featureEl.text
                index += 1


    promotionsElRow = soup.find("div", {"id": "promotions_feature_div"})
    if not(promotionsElRow is None):
        promotionEl = promotionsElRow.find("li")

        if not(promotionEl is None):
            json_data['promotion'] = str(promotionEl.text).strip()


    similarItemsElBlock = soup.find("div", {"id": "purchase-sims-feature"})
    if not(similarItemsElBlock is None):
        json_data['similarItems'] = {}
        index = 1

        for similarItemsElRow in similarItemsElBlock.find_all("li"):
            if not(similarItemsElRow is None):
                similarItemsEl = similarItemsElRow.find(lambda tag: tag.name == 'div' and 'data-rows' in tag.attrs)
                if not(similarItemsEl is None):
                    json_data['similarItems'][index] = similarItemsEl.text
                    index += 1


    categoriesElBlock = soup.find("div", {"id": "wayfinding-breadcrumbs_feature_div"})
    if not(categoriesElBlock is None):
        json_data['categories'] = {}
        index = 1

        for categoriesEl in categoriesElBlock.find_all("li", {"class": ""}):
            if not(categoriesEl is None):
                json_data['categories'][index] = categoriesEl.text
                index += 1


    frequentlyBoughtElBlock = soup.find("form", {"id": "sims-fbt-form"})
    if not(frequentlyBoughtElBlock is None):

        json_data['frequently_bought_together'] = {}
        index = 1

        for frequentlyBoughtEl in frequentlyBoughtElBlock.find_all("label"):
            if not(frequentlyBoughtEl is None):

                if index == 1:
                    index += 1
                else:
                    frequentlyBoughtElName = frequentlyBoughtEl.find("a")
                    if not(frequentlyBoughtElName is None):

                        json_data['frequently_bought_together'][index] = {}
                        json_data['frequently_bought_together'][index]['name'] = frequentlyBoughtElName.text

                        frequentlyBoughtElPrice = frequentlyBoughtEl.find("span", {"class": "a-color-price"})
                        if not(frequentlyBoughtElPrice is None):
                            json_data['frequently_bought_together'][index]['price'] = frequentlyBoughtElPrice.text

                        frequentlyBoughtElAvailability = frequentlyBoughtEl.find("span", {"class": "a-size-base a-color-success"})
                        if not(frequentlyBoughtElAvailability is None):
                            json_data['frequently_bought_together'][index]['availability'] = frequentlyBoughtElAvailability.text

                        frequentlyBoughtElMerchant = frequentlyBoughtEl.find("span", {"class": "a-size-base a-color-secondary a-text-normal"})
                        if not(frequentlyBoughtElMerchant is None):
                            json_data['frequently_bought_together'][index]['merchant'] = frequentlyBoughtElMerchant.text

                        index += 1


    reviewsElBlock = soup.find("div", {"id": "customer-reviews_feature_div"})
    if not(reviewsElBlock is None):
        json_data['reviews'] = {}
        index = 1

        for reviewsEl in reviewsElBlock.select('div[id*="rev-"]'):
            if not(reviewsEl is None):
                json_data['reviews'][index] = {}

                reviewRatingEl = reviewsEl.select("a:nth-of-type(1)")[0]
                if not(reviewRatingEl is None):
                    json_data['reviews'][index]['review_rating'] = str(reviewRatingEl.attrs['title']).strip()

                reviewByEl = reviewsEl.select("a:nth-of-type(3)")[0]
                if not(reviewByEl is None):
                    json_data['reviews'][index]['reviewed_by'] = str(reviewByEl.text).strip()

                reviewedOnEl = reviewByEl.find_next("span")
                if not(reviewedOnEl is None):
                    json_data['reviews'][index]['reviewed_on'] = str(reviewedOnEl.text).strip().lstrip('on ')

                reviewDataEl = reviewsEl.select('div[id*="revData-"]')[0].find("div")
                if not(reviewDataEl is None):
                    json_data['reviews'][index]['text'] = str(reviewDataEl.text).strip()
                    index += 1


    detailsElBlock = soup.find("div", {"id": "productDetails_db_sections"})
    if not(detailsElBlock is None):
        json_data['details'] = {}
        pattern = re.compile("review", flags=re.IGNORECASE)

        for detailsEl in detailsElBlock.find_all("tr"):
            if not(detailsEl is None):

                detailKeyEl = detailsEl.find("th")
                detailValueEl = detailsEl.find("td")

                if not(detailKeyEl is None) and not(detailValueEl is None) and (pattern.search(detailKeyEl.text) is None):
                    json_data['details'][str(detailKeyEl.text).strip()] = str(detailValueEl.text).strip()


    competitorsElBlock = soup.find("div", {"id": "mbc"})
    if not(competitorsElBlock is None):
        json_data['competitors'] = {}
        index = 1

        for competitorEl in competitorsElBlock.find_all("div", {"class": "mbc-offer-row"}):
            if not(competitorEl is None):

                json_data['competitors'][index] = {}

                competitorPriceEl = competitorEl.find("span", {"class": "a-color-price"})
                if not(competitorPriceEl is None):
                    json_data['competitors'][index]['price'] = str(competitorPriceEl.text).strip()

                competitorNameEl = competitorEl.find("span", {"class": "mbcMerchantName"})
                if not(competitorNameEl is None):
                    json_data['competitors'][index]['merchant'] = str(competitorNameEl.text).strip()
                    index += 1


    json_data['questions'] = get_customer_questions()

    product_data = json.dumps(json_data, sort_keys=True)
    # print(product_data)

    return product_data


def get_customer_questions():

    url = 'http://www.amazon.com/gp/ask-widget/askWidget.html?asin=B01EIUP20U'
    r = requests.get(url)

    data = r.text

    soup = BeautifulSoup(data, 'html.parser')
    json_data = {}

    questionsElRow = soup.find("div", {"class": "askTeaserQuestions"})

    if not(questionsElRow is None):
        index = 1

        for questionEl in questionsElRow.select('div[id*="question"]'):
            json_data[index] = {}
            json_data[index]['question'] = str(questionEl.text).strip().lstrip('Question:').lstrip()
            answerEl = questionEl.find_next_sibling("div")

            if not(answerEl is None):
                answerText = answerEl.select("span:nth-of-type(2)")[0]
                answeredBy = answerEl.select("span:nth-of-type(3)")[0]
                json_data[index]['answer'] = str(answerText.text).strip()
                json_data[index]['answered_by'] = str(answeredBy.text).strip()

            index += 1

    return json_data

