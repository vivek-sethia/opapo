from bs4 import BeautifulSoup

import requests

url = 'http://www.amazon.com/Apple-MMGG2LL-MacBook-13-3-Inch-VERSION/dp/B01EIUP20U/ref=sr_1_3?s=pc&ie=UTF8&qid=1463238054&sr=1-3&keywords=apple+macbook+air';

r  = requests.get(url)

data = r.text

soup = BeautifulSoup(data, 'html.parser')

titleEl = soup.find("span", {"id": "productTitle"})
if not(titleEl is None):
    title = str(titleEl.text).strip()
    print('title = ' + title)


priceEl = soup.find("span", {"id": "priceblock_ourprice"})
if not(priceEl is None):
    price = str(priceEl.text).strip()
    print('price = ' + price)
    #print(priceEl.attrs)
    #print(priceEl.style)
    #print(priceEl.attrs["class"])

ratingEl = soup.find("div", {"id": "avgRating"})
if not(ratingEl is None):
    rating = str(ratingEl.text).strip()
    print('rating = ' + rating)

imageEl = soup.find("img", {"id": "landingImage"})
if not(imageEl is None):
    image = imageEl.attrs["src"]
    print('image = ' + image)

brandEl = soup.find("a", {"id": "brand"})
if not(brandEl is None):
    brand = brandEl.text
    print('brand = ' + brand)


savingsElRow = soup.find("tr", {"id": "regularprice_savings"})
if not(savingsElRow is None):
    savingsEl = savingsElRow.find("td", {"class": "a-color-price"})
    if not(savingsEl is None):
        savings = str(savingsEl.text).strip()
        print('savings = ' + savings)

availabilityElRow = soup.find("div", {"id": "availability"})
if not(availabilityElRow is None):
    availabilityEl = availabilityElRow.find("span")
    if not(availabilityEl is None):
        availability = str(availabilityEl.text).strip()
        print('availability = ' + availability)

featuresElRow = soup.find("div", {"id": "feature-bullets"})
if not(featuresElRow is None):
    features = ""
    for featureEl in featuresElRow.find_all("li", {"id": ""}):
        if not(featureEl is None):
            features += featureEl.text + ' , '
    print('features = ' + features.rstrip(' , '))

promotionsElRow = soup.find("div", {"id": "promotions_feature_div"})
if not(promotionsElRow is None):
    promotionEl = promotionsElRow.find("li")
    if not(promotionEl is None):
        promotion = str(promotionEl.text).strip()
        print('promotion = ' + promotion)

# questionsElRow = soup.find("div", {"class": "askTeaserQuestions"})
# if not(questionsElRow is None):
#     questions = ""
#     # featuresEl = featuresElRow.find_all("li", {"id": ""})
#     for questionEl in questionsElRow.select('div[id*="question"]'):
#         questions += questionEl.text + ' , '
#     print('features = ' + questions.rstrip(' , '))

#descIframeEl = soup.find("iframe", {"id": "product-description-iframe"})
#if not(descIframeEl is None):
#    print(descIframeEl)
#descriptionEl = soup.find("div", {"class": "productDescriptionWrapper"})
#print('description = ' + descriptionEl.text)