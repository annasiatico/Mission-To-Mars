from bs4 import BeautifulSoup
from splinter import Browser
import requests
import pandas as pd
import pymongo
from pprint import pprint

conn = "mongodb://localhost:27017"
client = pymongo.MongoClient(conn)
db = client.mars_db
collection = db.mars

def scrape():

    # collection.drop()

    #NASA Mars News
    #Define URL
    nasa_url = "https://mars.nasa.gov/news/"

    #Use requests to get site information
    nasa_response = requests.get(nasa_url)
    soup = BeautifulSoup(nasa_response.text, "lxml")

    #Collect the latest news title and paragraph text
    news_title = soup.find('div', class_='content_title').find('a').text
    news_para = soup.find('div', class_='rollover_description_inner').text
        

    #Featured image
    #Visit the url for JPL Featured Space Image
    featured_image_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"

    #Use requests for get site information
    feat_img_response = requests.get(featured_image_url)
    soup = BeautifulSoup(feat_img_response.text, "lxml")
    featured_img_url  = soup.find('article')['style']

    #Main page URL 
    image_url = 'https://www.jpl.nasa.gov'

    #Concatenate main page URL and featured image URL
    featured_img_url = image_url + featured_img_url
    featured_img_url_list = list(featured_img_url)
    featured_img_url_list1 = [''.join(featured_img_url_list[0:24])]
    featured_img_url_list2 = [''.join(featured_img_url_list[47:-3])]
    featured_image_url = ''.join(featured_img_url_list1 + featured_img_url_list2)

    #Mars Weather
    #Visit the Mars Weather twitter account
    mars_weather_url = 'https://twitter.com/marswxreport?lang=en'

    #Use requests to get site information
    mars_weather_response = requests.get(mars_weather_url)
    soup = BeautifulSoup(mars_weather_response.text, "lxml")
    latest_tweet = (soup.find('div', class_='js-tweet-text-container')).text


    #Mars Facts
    #Visit the Mars Facts webpage
    mars_facts_url = 'http://space-facts.com/mars/'

    #Use requests to get site information

    mars_facts_response = requests.get(mars_facts_url)
    soup = BeautifulSoup(mars_facts_response.text, "lxml")

    table_info = soup.find('table')
    all_table_info = table_info.find_all('tr')

    #Get labels and values
    labels = []
    values = []

    for tr in all_table_info:
        td_element = tr.find_all('td')
        labels.append(td_element[0].text)
        values.append(td_element[1].text)
        
    mars_facts_df = pd.DataFrame({"Label": labels, "Values": values})
    mars_facts_table = mars_facts_df.to_html(header = False, index = False)


    #Mars Hemispheres
    #Setup browser via Splinter
    executable_path = {'executable_path': 'chromedriver'}
    browser = Browser('chrome', **executable_path, headless = True)

    #Visit the USGS Astrogeology site
    usgs_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    browser.visit(usgs_url)

    urls = [(a.text, a['href']) for a in browser
            .find_by_css('div[class="description"] a')]

    hemis_img_urls = []

    for title,url in urls:
        img_dict = {}
        img_dict['title'] = title
        browser.visit(url)
        img_url = browser.find_by_css('img[class="wide-image"]')['src']
        img_dict['img_url'] = img_url
        hemis_img_urls.append(img_dict)

    browser.quit()

    #Insert document into collection
    mars_dict = {
        "news_title": news_title,
        "news_paragraph": news_para,
        "featured_image_url": featured_image_url,
        "mars_weather": latest_tweet,
        "fact_table": mars_facts_table,
        "hemisphere_images": hemis_img_urls
    }

    collection.insert(mars_dict)

#Verify results
# results = collection.find()
# for result in results:
#     pprint(result)
