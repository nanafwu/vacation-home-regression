import requests
from bs4 import BeautifulSoup
import re
from time import sleep
import csv

"""
* HomeAway (owns VRBO)*:
- Unique Id. E.g. 284875
- Viewed 93 times in last 48 hours
- Review Score
- # Reviews
- Property Type. E.g. cabin
- Sleeps. E.g. 6
- # Bedrooms
- # Bathrooms
- Minimum # Night Stays
- Owner Member since
- Response Time. E.g. Within 12 hours
- Response Rate. E.g. 100%
- Calendar last updated: July 11, 2017
- Amenities: Hot Tub
- Floor Area: E.g. 1200 sq ft
- Ideally:
  - # Pictures
  - Distance from town center
  - Different price differences
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
    no geo https://www.homeaway.com/vacation-rental/p1110252vb
    Returns []
    url = url + '&arrivalDate=11/10/2017&departureDate=11/12/2017'
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
    with open('homeaway_urls_nyc_ALL.txt', 'r') as f:
        lines = f.readlines()

    with open('homeaway_rentals_nyc_ALL.txt', 'a+') as homeaway_file:
        for i, url in enumerate(lines[555:]):
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


def process_homeaway_rentals():
    with open('homeaway_rentals_nyc.txt', 'r') as homeaway_file:
        for line in csv.reader(homeaway_file, delimiter='\t'):
            print(line)


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

    home_file = open('homeaway_urls_nyc_ALL.txt', 'a+')
    # print(results_url)
    while results_url:
        results_url = scrape_home_away_listing(results_url, home_file)
    home_file.close()


# Standard boilerplate to call the main() function.
if __name__ == '__main__':
    scrape_homeaway_rentals()
