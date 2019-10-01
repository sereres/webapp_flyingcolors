from flask import render_template
from flask import request
from flyingcolors import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2
import pickle
import urllib3
import json
http = urllib3.PoolManager()

from collections import OrderedDict
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import numpy as np
from sklearn import metrics

from geopy.distance import great_circle
from shapely.geometry import MultiPoint
import PredictForUserInput


username = 'postgres'
db_name = 'butterflies_dragonflies'    

con = None
con = psycopg2.connect(database = db_name, user = username)


@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
            title = 'Home', user = { 'nickname': 'Sereres' },
            )

@app.route('/input')
def observations_input():
    return render_template("input.html")

@app.route('/output')
def observations_output():
    #pull 'date' from input field and store it
    observe_date = request.args.get('date')
    observe_place = request.args.get('address')
    #get the count of observations from the date
    print(observe_date)
    print(observe_place)

    apikey_places = []
    with open('flyingcolors/apikey1.txt', 'r') as file:
        apikey_places = file.read()

    apikey_geocode = []
    with open('flyingcolors/apikey2.txt', 'r') as file:
        apikey_geocode = file.read()

    address_split = tuple(str(x) for x in observe_place.split(' '))
    s="+"
    formatted_address = s.join(address_split)

    google_geocodeURLFormat = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s"
    googlegeocodeURL = google_geocodeURLFormat % (formatted_address,apikey_geocode)
    print("url = %s" % googlegeocodeURL)

    request_address = http.request('GET',googlegeocodeURL)
    jaddress = json.loads(request_address.data)
    lattitude = jaddress['results'][0]['geometry']['location']['lat']
    longitude = jaddress['results'][0]['geometry']['location']['lng']

    user_reference_point = [lattitude,longitude]

    #googleplacesURL_format = "https://maps.googleapis.com/maps/api/place/search/json?location=%f,%f&key=%s&rankby=distance&types=park"
    googleplacesURL_format = "https://maps.googleapis.com/maps/api/place/search/json?location=%f,%f&key=%s&radius=10000&types=park"
    googleplacesURL = googleplacesURL_format % (lattitude,longitude,apikey_places)
    print("url = %s" % googleplacesURL)

    request_parks = http.request('GET',googleplacesURL)
    jparks = json.loads(request_parks.data)

    #j['results'][4]['geometry']['viewport']['northeast']
    #j['results'][4]['geometry']['viewport']['southwest']
    #millenium_park_count_test = """select count(*) from observations_table where lattitude < {} and 
    #lattitude > {} and longitude < {} and longitude > {} and dragonfly_id='0'""".format(lat_ne,lat_sw,lon_ne,lon_sw)
    #millenium_park_count_test = pd.read_sql_query(millenium_park_count_test,con)
    #millenium_park_count_test.head()

    parkcount = []
    parknumber = 0

    for park in jparks['results']:
        park_place_id = park['place_id']
        park_ne = park['geometry']['viewport']['northeast']
        park_sw = park['geometry']['viewport']['southwest']
        print(park['name'])
        dragonfly_query = """select count(*) from wildlife_data where latitude < {} and latitude > {} and longitude < {} and longitude > {} and iconic_taxon_name='47792'""".format(park_ne['lat'],park_sw['lat'],park_ne['lng'],park_sw['lng'])
        butterfly_query = """select count(*) from wildlife_data where latitude < {} and latitude > {} and longitude < {} and longitude > {} and iconic_taxon_name='Insecta'""".format(park_ne['lat'],park_sw['lat'],park_ne['lng'],park_sw['lng'])
        dragonflies = pd.read_sql_query(dragonfly_query,con)
        butterflies = pd.read_sql_query(butterfly_query,con)
        butterfly_count = 0
        dragonfly_count = 0
        for i in butterflies['count']:
            butterfly_count = i
        for i in dragonflies['count']:
            dragonfly_count = i

        print("butterfly count in park query")
        print(butterfly_count)
        print("dragonfly count in park query")
        print(dragonfly_count)
        entry = tuple((parknumber,dragonfly_count,butterfly_count,park['name'],park_place_id))
        parkcount.append(entry)
        parknumber = parknumber + 1

    print("parkcount before sorting ")
    print(parkcount)

    #the below is how to sort a tuple based on the index key. for dragonfly sort, use 1, for butterfly sort, use 2.
    #sorts in increasing order though.
    #sorted(tuples, key = last) 
    sorted_dragonfly_increasing = sorted(parkcount,key = lambda x: x[1])
    sorted_butterfly_increasing = sorted(parkcount,key = lambda x: x[2])
    print("parkcount sorted ")
    print(sorted_butterfly_increasing)

    #new_tup = tuples[::-1] supposedly reverses a tuple? because the third argument is the step size, which is negative here
    sorted_butterfly = sorted_butterfly_increasing[::-1]
    sorted_dragonfly = sorted_dragonfly_increasing[::-1]

    print("parkcount decreasing for butterflies")
    print(sorted_butterfly)

    print("parkcount decreasing for dragonflies")
    print(sorted_dragonfly)

    #use the classifier
    prediction = PredictForUserInput.get_prediction_from_input(observe_date,user_reference_point)
    #if prediction is 0 look for butterflies if prediction is 1 look for dragonflies


    prevalent_species = "boo"
    habitat_preference = "foo"
    parkname1 = "first placeholder"
    park1_id = "placeholder"
    parkname2 = "second placeholder"
    park2_id = "placeholder"
    parkname3 = "third placeholder"
    park3_id = "placeholder"

    if prediction==1:
        parkname1 = sorted_dragonfly[0][3]
        park1_id = sorted_dragonfly[0][4]
        parkname2 = sorted_dragonfly[1][3]
        park2_id = sorted_dragonfly[1][4]
        parkname3 = sorted_dragonfly[2][3]
        park3_id = sorted_dragonfly[2][4]
        prevalent_species = "dragonflies"
        habitat_preference = " places near water, streambanks, ponds, and riverbanks"
    else:
        parkname1 = sorted_butterfly[0][3]
        park1_id = sorted_butterfly[0][4]
        parkname2 = sorted_butterfly[1][3]
        park2_id = sorted_butterfly[1][4]
        parkname3 = sorted_butterfly[2][3]
        park3_id = sorted_butterfly[2][4]
        prevalent_species = "butterflies"
        habitat_preference = " places near large meadows of flowers and flowering trees"



    picture_ref = "https://i.imgur.com/vkuJXAq.jpg"
    return render_template("output.html", prevalent_species=prevalent_species, habitat_preference=habitat_preference, parkname1=parkname1, parkname2 = parkname2, parkname3=parkname3, park1_id = park1_id, park2_id = park2_id, park3_id = park3_id)


@app.route('/output_timeseries')
def observations_output_timeseries():
    #pull 'date' from input field and store it
    observe_date = request.args.get('date')
    observe_place = request.args.get('address')
    #get the count of observations from the date
    print(observe_date)
    print(observe_place)

    apikey_places = []
    with open('flyingcolors/apikey1.txt', 'r') as file:
        apikey_places = file.read()

    apikey_geocode = []
    with open('flyingcolors/apikey2.txt', 'r') as file:
        apikey_geocode = file.read()

    address_split = tuple(str(x) for x in observe_place.split(' '))
    s="+"
    formatted_address = s.join(address_split)

    google_geocodeURLFormat = "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s"
    googlegeocodeURL = google_geocodeURLFormat % (formatted_address,apikey_geocode)
    print("url = %s" % googlegeocodeURL)

    request_address = http.request('GET',googlegeocodeURL)
    jaddress = json.loads(request_address.data)
    lattitude = jaddress['results'][0]['geometry']['location']['lat']
    longitude = jaddress['results'][0]['geometry']['location']['lng']

    googleplacesURL_format = "https://maps.googleapis.com/maps/api/place/search/json?location=%f,%f&key=%s&rankby=distance&types=park"
    googleplacesURL = googleplacesURL_format % (lattitude,longitude,apikey_places)
    print("url = %s" % googleplacesURL)

    request_parks = http.request('GET',googleplacesURL)
    jparks = json.loads(request_parks.data)

    #j['results'][4]['geometry']['viewport']['northeast']
    #j['results'][4]['geometry']['viewport']['southwest']
    #millenium_park_count_test = """select count(*) from observations_table where lattitude < {} and 
    #lattitude > {} and longitude < {} and longitude > {} and dragonfly_id='0'""".format(lat_ne,lat_sw,lon_ne,lon_sw)
    #millenium_park_count_test = pd.read_sql_query(millenium_park_count_test,con)
    #millenium_park_count_test.head()

    parkcount = []
    parknumber = 0

    for park in jparks['results']:
        #print(park)
        park_ne = park['geometry']['viewport']['northeast']
        park_sw = park['geometry']['viewport']['southwest']
        print(park['name'])
        dragonfly_query = """select count(*) from observations_table where lattitude < {} and lattitude > {} and longitude < {} and longitude > {} and butterfly_id='0'""".format(park_ne['lat'],park_sw['lat'],park_ne['lng'],park_sw['lng'])
        butterfly_query = """select count(*) from observations_table where lattitude < {} and lattitude > {} and longitude < {} and longitude > {} and dragonfly_id='0'""".format(park_ne['lat'],park_sw['lat'],park_ne['lng'],park_sw['lng'])
        dragonflies = pd.read_sql_query(dragonfly_query,con)
        butterflies = pd.read_sql_query(butterfly_query,con)
        butterfly_count = 0
        dragonfly_count = 0
        for i in butterflies['count']:
            butterfly_count = i
        for i in dragonflies['count']:
            dragonfly_count = i

        print("butterfly count in park query")
        print(butterfly_count)
        print("dragonfly count in park query")
        print(dragonfly_count)
        entry = tuple((parknumber,dragonfly_count,butterfly_count,park['name']))
        parkcount.append(entry)
        parknumber = parknumber + 1

    print("parkcount sorted ")
    print(parkcount)

    #the below is how to sort a tuple based on the index key. for dragonfly sort, use 1, for butterfly sort, use 2.
    #sorts in increasing order though.
    #sorted(tuples, key = last) 
    sorted_butterfly_increasing = sorted(parkcount,key = lambda x: x[2])
    sorted_dragonfly_increasing = sorted(parkcount,key = lambda x: x[1])
    print("parkcount sorted ")
    print(sorted_butterfly_increasing)

    #new_tup = tuples[::-1] supposedly reverses a tuple? because the third argument is the step size, which is negative here
    sorted_butterfly = sorted_butterfly_increasing[::-1]
    sorted_dragonfly = sorted_dragonfly_increasing[::-1]

    print("parkcount decreasing ")
    print(sorted_butterfly)


    query = "SELECT date, count(*) from observations_table where butterfly_id='0' and date='%s' group by date order by date" %observe_date
    print(query)
    query_results = pd.read_sql_query(query,con)
    print(query_results)
    data = []
    the_result = returnvalue_butterfly(observe_date)
    dragonfly_result = returnvalue_dragonfly(observe_date)
    print(dragonfly_result)

    prevalent_species = "boo"
    habitat_preference = "foo"
    parkname1 = "first placeholder"
    parkname2 = "second placeholder"
    parkname3 = "third placeholder"

    if dragonfly_result > the_result:
        parkname1 = sorted_dragonfly[0][3]
        parkname2 = sorted_dragonfly[1][3]
        parkname3 = sorted_dragonfly[2][3]
        prevalent_species = "dragonflies"
        habitat_preference = " places near water, streambanks, ponds, and riverbanks"
    else:
        parkname1 = sorted_butterfly[0][3]
        parkname2 = sorted_butterfly[1][3]
        parkname3 = sorted_butterfly[2][3]
        prevalent_species = "butterflies"
        habitat_preference = " places near large meadows of flowers and flowering trees"

    for i in range(0,query_results.shape[0]):
        data.append(dict(date=query_results.iloc[i]['date'],count=query_results.iloc[i]['count']))
    return render_template("output_timeseries.html", data=data, the_result=the_result, dragonfly_result=dragonfly_result, prevalent_species=prevalent_species, habitat_preference=habitat_preference, parkname1=parkname1, parkname2 = parkname2, parkname3=parkname3)

@app.route('/output_simple')
def observations_output_simple():
    #pull 'date' from input field and store it
    observe_date = request.args.get('date')
    #get the count of observations from the date
    print(observe_date)
    query = "SELECT date, count(*) from observations_table where date='%s' group by date order by date" %observe_date
    print(query)
    query_results = pd.read_sql_query(query,con)
    print(query_results)
    data = []
    the_result = returnvalue_butterfly(observe_date)
    dragonfly_result = returnvalue_dragonfly(observe_date)
    print(dragonfly_result)

    prevalent_species = "boo"
    habitat_preference = "foo"

    if dragonfly_result > the_result:
        prevalent_species = "dragonflies"
        habitat_preference = " places near water, streambanks, ponds, and riverbanks"
    else:
        prevalent_species = "butterflies"
        habitat_preference = " places near large meadows of flowers and flowering trees"

    for i in range(0,query_results.shape[0]):
        data.append(dict(date=query_results.iloc[i]['date'],count=query_results.iloc[i]['count']))
    return render_template("output.html", data=data, the_result=the_result, dragonfly_result=dragonfly_result, prevalent_species=prevalent_species, habitat_preference=habitat_preference)

