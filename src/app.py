from flask import Flask, Response
from scraper.amazon_scraper import scrape_site

app = Flask(__name__)

@app.route('/')
def process_request():
    data = scrape_site()
    resp = Response(data, status=200, mimetype='application/json')
    return resp

if __name__ == '__main__':
    app.run()