import requests
import json
import csv

# Add new features using latitude, longitude and Google's Places API

data_file_TS_distances = 'data/homeaway_urls_times_square.csv'
data_file_subway_counts = 'data/homeaway_urls_subway.csv'


def nearby_subway_count(lat, long):
    """
    Count # subway stations within a 1 mile radius
    https://developers.google.com/places/web-service/search
    """
    # api_key = 'AIzaSyDp5YP40O02jkGRN2hQ3uVwnPckSDSxjTU' # nana - last used
    # 07/17 2pm
    api_key = 'AIzaSyDgm8KI2voT4pNCA-AakvqzwRr_oE_PDXI'  # li - last used 07/15 9pm
    api_url = ('https://maps.googleapis.com/maps/api/place/nearbysearch/json?'
               + 'location=' + repr(lat) + ',' + repr(long)
               + '&radius=800'
               + '&type=subway_station'
               + '&key=' + api_key)
    response = requests.get(api_url).text
    resp_obj = json.loads(response)
    subway_stations = resp_obj['results']
    return len(subway_stations)


def write_subway_counts():
    """
    One time collection of data from Google API for subway counts
    """
    with open(data_file_subway_counts, 'a+') as homeaway_file:
        writer = csv.writer(homeaway_file, delimiter='\t')
        for i, row in enumerate(df.as_matrix()[3717:]):
            url = row[0]
            lat = row[3]
            long = row[4]
            subway_count = nearby_subway_count(lat, long)
            data = [i, url, lat, long, subway_count]
            print(data)
            writer.writerow(data)
            homeaway_file.flush()
    homeaway_file.close()


def distance_to_times_square(lat, long):
    """
    Calculate distance (in meter) to drive to Times Square
    using public transportation with Google API
    https://developers.google.com/maps/documentation/distance-matrix/intro
    """
    times_square_lat = '40.759171'
    times_square_long = '-73.985517'
    # api_key = 'AIzaSyBO_xmtgW62tEXaDNaofO9LZ0GOVGLtmDw' # nana - last used
    # 07/15 5pm
    api_key = 'AIzaSyB4ZjNy5zx8Ed32i3I7sGVBgKeR3s20dD4'  # li - last used 07/14 9:30pm
    api_url = ('https://maps.googleapis.com/maps/api/distancematrix/json?units=imperial'
               + '&origins=' + repr(lat) + ',' + repr(long)
               + '&destinations=' + times_square_lat + ',' + times_square_long
               + '&key=' + api_key)
    response = requests.get(api_url).text
    resp_obj = json.loads(response)
    distance = resp_obj['rows'][0]['elements'][0]['distance']['value']
    return distance


def write_driving_distance():
    """
    One time collection of data from Google API for driving distance to Times Square
    """
    with open(data_file_TS_distances, 'a+') as homeaway_file:
        writer = csv.writer(homeaway_file, delimiter='\t')
        for i, row in enumerate(df.as_matrix()):
            url = row[0]
            lat = row[3]
            long = row[4]
            distance = distance_to_times_square(lat, long)
            data = [i, url, lat, long, distance]
            print(data)
            writer.writerow(data)
            homeaway_file.flush()
    homeaway_file.close()

# Store data collected from Google about each rental in a separate file
# because of API quotas

# Run these functions once

# write_subway_counts()
# write_driving_distance() #DONE

# doesn't work?
# nearby_subway_count('40.675552', '-73.942836')
