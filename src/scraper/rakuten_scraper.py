from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from vaderSentiment.vaderSentiment import sentiment
from watson_developer_cloud import ToneAnalyzerV3

import requests
import json
import locale
import re

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

def get_rakuten_page(id):

    browser = webdriver.PhantomJS()
    rak_url = 'http://www.rakuten.com/sr/searchresults#qu=' + id
    browser.get(rak_url)
    html_source = browser.page_source

    browser.quit()

    return html_source


def get_float(rating):
        for token in rating.split():
                 try:
                     # if this succeeds, you have your (first) float
                     print float(token), "is a float"
                     return float(token)
                 except ValueError:
                     print token, "is something else"

def get_text(element):
    return element.text.encode('utf-8').strip()

def scrape_rakuten_site_external(upc, name, config):
    data = {
        'scraped_data': ''
    }
    if upc == '':
        return data


    html_source = get_rakuten_page(upc)



    soup = BeautifulSoup(html_source, 'html.parser')


    results_el = soup.find("div",{"class":"product-details"})


    if results_el and not (results_el is None):
        prod_url = soup.find("a", {"class": "title"}).attrs["href"]
        rakuten_data = scrape_rakuten_site(prod_url, config)
        rakuten_data['scraped_data']['product_link'] = prod_url
        return rakuten_data
    else:
            name = re.sub('\(.*\)', '', name)
            html_source = get_rakuten_page(name)
            soup = BeautifulSoup(html_source, 'html.parser')

            results_el = soup.find("div",{"class":"product-details"})
            if results_el and not (results_el is None):
                    prod_url = soup.find("a", {"class": "title"}).attrs["href"]
                    rakuten_data = scrape_rakuten_site(prod_url, config)
                    rakuten_data['scraped_data']['product_link'] = prod_url
                    return rakuten_data

def scrape_rakuten_site(prod_url, config):

      r = requests.get(prod_url)

      data = r.text

      soup = BeautifulSoup(data, 'html.parser')
      json_data = {}

      title_el = soup.find("h1", {"id": "product-title-heading"})
      if not(title_el is None):
          json_data['title'] = str(title_el.text).strip()

      price_el = soup.find("span", {"class": "price"})
      if not (price_el is None):
          ##price_el = get_text(price_el)
          json_data['price'] = (price_el.text).strip()


      savings_el = soup.find("div", {"class": "text-muted"})
      if not (savings_el is None):
          json_data['savings'] = (savings_el.text).strip()


      shipping_el = soup.find(text="+ free shipping")
      if not (shipping_el is None):
          shipping_el = 'FREE'
          json_data['shippingCost'] = shipping_el
      else:
          shipping_el = 'EXTRA'
          json_data['shippingCost'] = shipping_el


      image_el = soup.find("img", {"id": "productmain"})
      if not(image_el is None):
          json_data['image'] = image_el.attrs["src"]


      brand_el = soup.find("td", {"class": "tab-table"})
      if not(brand_el is None):
          json_data['brand'] = MfgPart_el.text

      merchant_el = soup.find("div", {"class": "seller"})
      if not (merchant_el is None):
          json_data['merchant'] = str(merchant_el.text)

      availability_el = soup.find("strong", {"class": "text-success"})
      if not(availability_el is None):
          json_data['availability'] = get_text(availability_el)


 #   return_in_el = soup.find("span", {"id": "vi-ret-accrd-txt"})
 #   if not (return_in_el is None):
 #        json_data['returnIn'] = (return_in_el.text).strip()

      prod_description_el = soup.find("div", {"itemprop": "description"})
      if not (prod_description_el is None):
          json_data['ProdDescription'] = (prod_description_el.text).strip()

      link_to_buy_el = soup.find("a", {"a": "add-to-cart-main.add-to-cart.btn_btn"})
      if not (link_to_buy_el is None):
          json_data['linkToBuy'] = (link_to_buy_el.text).strip()

      json_data['reviews'] = {}
      json_data['rating'] = {}


      average_rating_block_el = soup.find("div", {"class": "rating-summary"})
      if not (average_rating_block_el is None):
          average_rating_el = average_rating_block_el.find("strong")

          if not(average_rating_el is None):
             json_data['rating']['average'] = get_text(average_rating_el)
             json_data['average'] = get_text(average_rating_el)
             #debug='jon'
             #print debug
             #print get_text(average_rating_el)
             #print debug



      review_count_el = soup.find("strong", {"class": "rating-indicator"})
      if not (review_count_el is None):
          json_data['rating']['review_count'] = int(str((review_count_el.text).strip()))
          json_data['review_count'] = int(str((review_count_el.text).strip()))

      #user_ratingEl_block = soup.findAll("div", {"class": "review-avg"})
      #json_data['rating']['stats'] = {}
      #if not(user_ratingEl_block is None):
       #  index = 1

         #for user_ratingEl in soup.findAll("div", {"class": "review-avg"}):
          #  if not(user_ratingEl is None):


                   #             review_rating_el = user_ratingEl.findAll("i", {"class": "fa fa-circle"}) or user_ratingEl.findAll("i", {"class": "fa fa-circle"})

                   #             if not(review_rating_el is None):
                   #               rating_score = len(review_rating_el)
                   #               rating_score = str(rating_score)
                    #              json_data['rating']['stats'][index+ ' star'] = rating_score

                    #            index +=1

      statsblock_el = soup.findAll("div", {"id": "ratings"})
      json_data['rating']['stats'] = {}
      index3 = 5
      if not(statsblock_el is None):
              for stats_el in soup.findAll("div", {"class": "rating-indicator"}):

                              debug = 'start'
                              debug2 = 'close'
                              #print debug

                              rating_score = stats_el.contents[0]
                              #print rating_score
                              name = str(index3)
                              #print name
                              #print debug2
                              json_data['rating']['stats'][name+ ' star'] = str(rating_score)
                              index3 -=1


      reviews_el_block = soup.findAll("p", {"class": "dotdotdot"})


      if not(reviews_el_block is None):
                json_data['reviews'] = {}
                index2 = 1
                overall_sentiment = 0


                for reviewsEl in soup.findAll("p", {"class": "dotdotdot"}):

                    if not(reviewsEl is None):

                        json_data['reviews'][index2] = {}

                        #reviewed_by_el = reviewsEl.find("em", {"class": "review-avg"})
                        #if not(reviewed_by_el is None):
                        #   json_data['reviews'][index2]['reviewed_by'] = reviewed_by_el.text.strip()




                        reviewDescription_el = reviewsEl.contents[0]

                        ##debug = 'review'
                        ##print reviewDescription_el
                        ##print debug



                        all_reviews = ''

                        if not(reviewDescription_el is None) and not(reviewDescription_el is None):
                            json_data['reviews'][index2]['text'] = str(reviewDescription_el)
                            all_reviews += str(reviewDescription_el)
                            review_sentiment = sentiment(str(reviewDescription_el))
                            overall_sentiment = review_sentiment


                            index2 += 1
                            if all_reviews != '':
                                all_tones = get_tone(all_reviews, config)
                                json_data['tones'] = str(all_tones)
                                db = 'start'
                                db2 = 'end'
                                print db
                                print overall_sentiment
                                print db2
                                json_data['overall_sentiment'] = overall_sentiment


#soup.find('div', class_='detail_date').find('dt', #text='Date').find_next_sibling('dd').text


      value = soup.find(text="Overall Satisfaction").findNext('dt').contents[0]
      #if not(reviewDescription_el is None):
      #   get_value = get_float(value)
      #   get_value = str(get_value)


      ease = soup.find(text="Value").findNext('dt').contents[0]
      performance = soup.find(text="Ease of Use").findNext('dt').contents[0]
      over = soup.find(text="Overall Satisfaction").findPrevious('dt').contents[0]

      get_over = get_float(over)
      get_over = str(get_over)

      get_ease = get_float(ease)
      get_ease = str(get_ease)

      get_performance = get_float(performance)
      get_performance = str(get_performance)

      get_value = get_float(value)
      get_value = str(get_value)

      json_data['Over'] = get_over
      json_data['Value'] = get_value
      json_data['Ease of Use'] = get_ease
      json_data['Performance'] = get_performance






      data = {
              'scraped_data': json_data
          }
          # print(product_data)

      return data

def get_tone(text, config):

    tones = {}
    tone_analyzer = ToneAnalyzerV3(
        username=config['WDC_TA_USER_NAME'],
        password=config['WDC_TA_PASSWORD'],
        version=config['WDC_TA_VERSION'])

    result_tone = tone_analyzer.tone(text=text)

    if result_tone is not None:
            tones = {}
            for category in result_tone['document_tone']['tone_categories']:
                category_name = category['category_id'].replace('_tone', '')
                category_name = str(category_name)
                tones[category_name] = {
                    'tone_names': [],
                    'scores': []
                }
                for tone in category['tones']:
                    tones[category_name]['tone_names'].append(str(tone['tone_name']))
                    tones[category_name]['scores'].append(tone['score'])
                    print tones

    return tones