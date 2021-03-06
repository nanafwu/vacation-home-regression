import requests
from bs4 import BeautifulSoup
import re
from time import sleep
import csv

"""
Predicting nightly vacation home rental prices in NYC
Scrapers last tested as of 07/17
"""


def make_soup(url):
    headers = {
        'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) '
                       'Gecko/20100101 Firefox/32.0')}
    response = requests.get(url, headers=headers)
    print('Fetched ', url)
    page = response.text
    soup = BeautifulSoup(page, "lxml")
    return soup


def scrape_homeaway_house(url):
    """
    Scrape individaul Homeaway url
    """
    soup = make_soup(url)

    # Get latitude, longitude
    geo_lat_tag = soup.find(
        'meta', {'property': 'homeaway:location:latitude'})
    geo_long_tag = soup.find(
        'meta', {'property': 'homeaway:location:longitude'})

    if geo_lat_tag and geo_long_tag:
        geo_lat = geo_lat_tag['content']
        geo_long = geo_long_tag['content']

    else:
        geo_lat_search = re.search(r'\"latitude\":([\d\.]*),', soup.text)
        geo_long_search = re.search(
            r'\"longitude\":(\-[\d\.]*),', soup.text)
        if (geo_lat_search and geo_long_search):
            geo_lat = geo_lat_search.group(1)
            geo_long = geo_long_search.group(1)

    sleeps = None
    bedrooms = None
    bathrooms = None
    minimum_stay = None

    # Amenities
    amenities_details_tag = soup.find('div', class_='amenity-details')

    if amenities_details_tag is None:
        return []

    amenities_tag = amenities_details_tag.findAll(
        'div', class_='amenity-detail')

    for amenity_tag in amenities_tag:
        amenity_title_tag = amenity_tag.find('div', {'class': 'amenity-title'})
        amenity_title = amenity_title_tag.text.strip()
        amenity_value_tag = amenity_tag.find('div', {'class': 'amenity-value'})
        amenity_value = amenity_value_tag.text.strip()
        if (amenity_title == 'Sleeps'):
            sleeps = amenity_value
        elif (amenity_title == 'Bedrooms'):
            bedrooms = amenity_value
        elif (amenity_title == 'Bathrooms'):
            bathrooms = amenity_value
        elif (amenity_title == 'Minimum Stay'):
            minimum_stay = amenity_value

    # Rating
    rating_tag = soup.find(
        'meta', {'itemprop': 'ratingValue'})
    rating = rating_tag['content'] if rating_tag else None

    # Number_reviews
    number_reviews_tag = soup.find(
        'meta', {'itemprop': 'reviewCount'})
    number_reviews = number_reviews_tag[
        'content'] if number_reviews_tag else None

    # Title
    title_tag = soup.find(
        'meta', {'property': 'og:title'})
    title = title_tag['content'] if title_tag else None

    # Price Quote
    price_tag = soup.find('div', class_='price-large')
    price = price_tag.text.strip() if price_tag else None
    if geo_lat and geo_long:
        rental_info = [url, price, title, geo_lat, geo_long, rating,
                       number_reviews, sleeps, bedrooms, bathrooms,
                       minimum_stay]
    else:
        rental_info = []
    return rental_info


def scrape_homeaway_rentals():
    with open('data/homeaway_urls_nyc_ALL.txt', 'r') as f:
        lines = f.readlines()

    with open('data/homeaway_rentals_nyc_ALL.txt', 'a+') as homeaway_file:
        for i, url in enumerate(lines):
            url = url.strip()
            print('Processing ', i)
            sleep(1)
            rental_info = scrape_homeaway_house(url)
            if rental_info:
                writer = csv.writer(homeaway_file, delimiter='\t')
                print(rental_info)
                writer.writerow(rental_info)
                homeaway_file.flush()
    homeaway_file.close()


def scrape_homeaway_house_description(url):
    """
    Get Homeaway house's full title and description
    """
    soup = make_soup(url)
    header_text = ''
    description_text = ''

    header_tag = soup.find('h1', class_='listing-headline')
    if header_tag:
        header_subtag = header_tag.find('span', class_='listing-headline-text')
        if header_subtag:
            header_text = header_subtag.text.strip().lower()

    description_tag = soup.find('div', class_='prop-desc-txt')
    if description_tag:
        description_text = description_tag.text.strip().lower()
        description_text = re.sub(r'\n', ' ', description_text)
    return [url, header_text, description_text]


def scrape_homeaway_rentals_descriptions():
    """
    Scrape additional description information needed to model data
    """
    with open('data/homeaway_urls_nyc_ALL.txt', 'r') as f:
        lines = f.readlines()

    with open('data/homeaway_rentals_nyc_descriptions.txt', 'a+') as homeaway_file:
        for i, url in enumerate(lines):
            url = url.strip()
            print('Processing ', i)
            sleep(1)
            rental_info = scrape_homeaway_house_description(url)
            if rental_info:
                writer = csv.writer(homeaway_file, delimiter='\t')
                print(rental_info)
                writer.writerow(rental_info)
                homeaway_file.flush()
    homeaway_file.close()


def scrape_homeaway_house_amenities(url):
    """
    Scrape individaul Homeaway url's amenities
    """
    soup = make_soup(url)
    description_tag = soup.find('div', class_='property-description')

    description_text = description_tag.text.strip().lower() if description_tag else ''

    amenities_tag = soup.find('div', {'id': 'amenities-container'})
    amenities_text = amenities_tag.text.strip().lower() if amenities_tag else ''
    amenities_text = ' '.join(amenities_text.split())

    has_elevator = ('elevator' in description_text) or (
        'elevator' in amenities_text)
    has_patio = 'deck / patio' in amenities_text
    has_concierge = ('concierge' in description_text) or (
        'concierge' in amenities_text)

    pool_tag = soup.find('div', {'id': 'poolSpa'})
    has_pool = True if pool_tag else False
    floor_area = None

    floor_area_search = re.search(
        r'floor area: ([\d]*) sq\. ft\.', amenities_text)

    if (floor_area_search):
        floor_area = floor_area_search.group(1)

    return [url, has_elevator, has_concierge, has_patio, has_pool, floor_area]


def scrape_homeaway_rentals_amenities():
    """
    Scrape additional information needed to model data
    """
    with open('data/homeaway_urls_nyc_ALL.txt', 'r') as f:
        lines = f.readlines()

    with open('data/homeaway_rentals_nyc_amenities_ALL.txt', 'a+') as homeaway_file:
        for i, url in enumerate(lines):
            url = url.strip()
            print('Processing ', i)
            sleep(1)
            rental_info = scrape_homeaway_house_amenities(url)
            if rental_info:
                writer = csv.writer(homeaway_file, delimiter='\t')
                print(rental_info)
                writer.writerow(rental_info)
                homeaway_file.flush()
    homeaway_file.close()


def scrape_home_away_listing(results_list_url, home_file):
    print('Scraping ', results_list_url)
    base_url = 'https://www.homeaway.com'
    soup = make_soup(results_list_url)

    # Find house listings
    header_link_tags = soup.findAll('h3', class_='hit-headline')
    home_urls = []
    for h in header_link_tags:
        link_tags = h.find_all('a', class_='hit-url')
        link_tag = link_tags[0]
        home_url = base_url + link_tag['href']
        home_file.write(home_url + '\n')
        home_urls.append(home_url)

    print('Found {} urls'.format(len(home_urls)))

    # Find next listings url to scrape
    next_link_tag = soup.findAll('link', {'rel': 'next'})
    next_link = None
    if next_link_tag:
        next_link = base_url + \
            next_link_tag[0]['href']

    return next_link


def scrape_home_away_listings_all():
    """
    Scrape for NYC
    """
    results_url = (
        'https://www.homeaway.com/results/new-york/'
        'new-york-city/region:1737/')

    home_file = open('data/homeaway_urls_nyc_ALL.txt', 'a+')
    # print(results_url)
    while results_url:
        results_url = scrape_home_away_listing(results_url, home_file)
    home_file.close()


# Standard boilerplate to call the main() function.
if __name__ == '__main__':
    # scrape_homeaway_rentals_amenities()
    scrape_homeaway_rentals_descriptions()
