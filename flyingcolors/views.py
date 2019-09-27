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

user = 'postgres'
host = 'localhost'
dbname = 'observations'
db = create_engine('postgres://%s%s/%s' %(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)


cluster_coords = pd.read_csv('cluster_coords.csv', index_col=0)
cluster_coords = cluster_coords.reset_index()

def get_closest_cluster_id(reference):
    cluster_array = [(37.358594, -88.919156), (41.80800418, -87.58900703), (39.4532783639, -87.4155096884), (39.4410783333, -88.1627361667), (42.2927100677, -85.148530556), (39.4712017408, -88.1936910734), (40.9798075632, -81.3047336788), (41.1012884709, -83.1792231645), (38.7248236493, -83.1785495849), (39.5817333333, -82.0146111167), (40.699795, -82.53702), (40.3729181, -82.3967142), (39.1298138333, -84.5002366667), (38.9642299915, -77.3278066023), (41.326536748, -81.4385604858), (38.7709536727, -77.2703889733), (38.94863, -77.3300333333), (37.7559179311, -83.9149260521), (36.6652793884, -84.4941940308), (39.5883851759, -79.9864799835), (38.7814325094, -76.710026823), (39.0982421491, -76.7286836462), (39.09078154, -77.12346602), (39.1265712307, -76.8781313699), (39.0171668581, -76.7995197217), (35.7945046404, -78.68952847), (35.5280715306, -82.3568541754), (35.8827725, -78.9871598), (35.8057043825, -79.0707965844), (35.8133333333, -81.1672222222), (34.8841629028, -82.2802352905), (33.2621033333, -87.5149916667), (33.4223913032, -86.7678254792), (34.419152039, -85.616389241), (34.2233266246, -86.161356589), (32.0110664637, -85.4421526885), (32.788461, -86.871655), (33.4582361919, -85.5765152047)]


    closest_point = min(cluster_array, key=lambda point: great_circle(point,reference).m)
    cluster_id = cluster_coords.loc[cluster_coords['lat']==closest_point[0]]['id'].iloc[0]

    return cluster_id

def give_prediction_cluster(i):
    predicted_vals = [ 0.08133105,  0.32852419,  0.30309675,  0.1462796 ,  0.50547807,
        0.14879099,  0.45418779,  0.509504  ,  0.37547686,  0.3989927 ,
        0.53068626,  0.48113189,  0.15364462,  0.05604594,  0.48559451,
        0.06206496,  0.05604594,  0.39873389,  0.21531968,  0.41763231,
        0.09202584,  0.12536452,  0.06414738,  0.09952614,  0.19211359,
        0.09186391,  0.41665311,  0.10375868,  0.07512975,  0.18850597,
       -0.06180867, -0.01777617, -0.05389357, -0.02757743, -0.03346074,
        0.03494131,  0.00904992]
    val = predicted_vals[i]
    print("val is")
    print(val)
    return val

def get_prediction_butterfly(time,lat,lon):
    #pk2_climatefile = open('formatted_climate_data_2018-03_2019-08.pk1','rb')
    #climate_data = pickle.load(pk2_climatefile)

    reference_point = [lat, lon]
    id_cluster = get_closest_cluster_id(reference_point)
    expected_ratio = give_prediction_cluster(id_cluster)

    return expected_ratio


def return_butterfly(date,place):
    pkfile = open('regressor_sep26.pk1','rb')
    regressor = picle.load(pkfile)
    return true

def returnvalue_butterfly(date):
    pk1_file3 = open('flyingcolors/butterfly_model.pck1','rb')
    model = pickle.load(pk1_file3)
    future = model.make_future_dataframe(periods=365)

    pk1_file1 = open('flyingcolors/butterfly_forecast.pck1','rb')
    butterfly_forecast = pickle.load(pk1_file1)
    butterfly_variable = 0
    print(butterfly_forecast.loc[butterfly_forecast['ds'] == date])
    for i in butterfly_forecast.loc[butterfly_forecast['ds']== date]['yhat']:
        butterfly_variable = i
        print("butterfly_variable")
        print(i)
    fig = model.plot(butterfly_forecast)
    fig.savefig("forecast.png")
    return butterfly_variable

def returnvalue_dragonfly(date):
    print("dragonflydate")
    print(date)
    pk1_file2 = open('flyingcolors/dragonfly_forecast.pck1','rb')
    dragonfly_forecast = pickle.load(pk1_file2)
    dragonfly_variable = 0
    print(dragonfly_forecast.loc[dragonfly_forecast['ds'] == date])
    for i in dragonfly_forecast.loc[dragonfly_forecast['ds']== date]['yhat']:
        dragonfly_variable = i
        print("dragonfly_variable")
        print(dragonfly_variable)
    return dragonfly_variable



@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
            title = 'Home', user = { 'nickname': 'Sereres' },
            )
@app.route('/db')
def observations_page():
    sql_query = """
                SELECT * FROM observations_table;
                 """

    query_results = pd.read_sql_query(sql_query,con)
    observations = ""
    for i in range (0,10):
        observations += query_results.iloc[i]['dragonfly_id']
        observations += "<br>"
    return observations

@app.route('/db_fancy')
def test1_page_fancy():
    sql_query = """ Select date, count(*) from observations_table where butterfly_id='0' group by date order by date """;
    query_results = pd.read_sql_query(sql_query,con)
    tabledata = ""
    query_results=pd.read_sql_query(sql_query,con)
    tabledata = []
    for i in range(0,query_results.shape[0]):
        tabledata.append(dict(date=query_results.iloc[i]['date'], count=query_results.iloc[i]['count']))
    return render_template('test1.html',tabledata=tabledata)

@app.route('/input')
def observations_input():
    return render_template("input.html")

@app.route('/input_simple')
def observations_input_simple():
    return render_template("input_simple.html")

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



    #USE THE BETTER MODEL WITH THE CLIMATE DATA
    predict_val = get_prediction_butterfly(observe_date,lattitude,longitude)



    prevalent_species = "boo"
    habitat_preference = "foo"
    parkname1 = "first placeholder"
    parkname2 = "second placeholder"
    parkname3 = "third placeholder"

    if predict_val < .2:
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
    return render_template("output.html", data=data, the_result=the_result, dragonfly_result=dragonfly_result, prevalent_species=prevalent_species, habitat_preference=habitat_preference, parkname1=parkname1, parkname2 = parkname2, parkname3=parkname3)


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

