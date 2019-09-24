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

user = 'postgres'
host = 'localhost'
dbname = 'observations'
db = create_engine('postgres://%s%s/%s' %(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

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

    for park in jparks['results']:
        #print(park)
        park_ne = park['geometry']['viewport']['northeast']
        park_sw = park['geometry']['viewport']['southwest']
        print(park['name'])
        dragonfly_query = """select count(*) from observations_table where lattitude < {} and lattitude > {} and longitude < {} and longitude > {} and butterfly_id='0'""".format(park_ne['lat'],park_sw['lat'],park_ne['lng'],park_sw['lng'])
        butterfly_query = """select count(*) from observations_table where lattitude < {} and lattitude > {} and longitude < {} and longitude > {} and dragonfly_id='0'""".format(park_ne['lat'],park_sw['lat'],park_ne['lng'],park_sw['lng'])
        dragonfly_count = pd.read_sql_query(dragonfly_query,con)
        butterfly_count = pd.read_sql_query(butterfly_query,con)
        print("butterfly count in park query")
        print(butterfly_count)
        print("dragonfly count in park query")
        print(dragonfly_count)

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

    if dragonfly_result > the_result:
        prevalent_species = "dragonflies"
        habitat_preference = " places near water, streambanks, ponds, and riverbanks"
    else:
        prevalent_species = "butterflies"
        habitat_preference = " places near large meadows of flowers and flowering trees"

    for i in range(0,query_results.shape[0]):
        data.append(dict(date=query_results.iloc[i]['date'],count=query_results.iloc[i]['count']))
    return render_template("output.html", data=data, the_result=the_result, dragonfly_result=dragonfly_result, prevalent_species=prevalent_species, habitat_preference=habitat_preference)

@app.route('/output_simple')
def observations_output_simple():
    #pull 'date' from input field and store it
    observe_date = request.args.get('date')
    #get the count of observations from the date
    print(observe_date)
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

    if dragonfly_result > the_result:
        prevalent_species = "dragonflies"
        habitat_preference = " places near water, streambanks, ponds, and riverbanks"
    else:
        prevalent_species = "butterflies"
        habitat_preference = " places near large meadows of flowers and flowering trees"

    for i in range(0,query_results.shape[0]):
        data.append(dict(date=query_results.iloc[i]['date'],count=query_results.iloc[i]['count']))
    return render_template("output.html", data=data, the_result=the_result, dragonfly_result=dragonfly_result, prevalent_species=prevalent_species, habitat_preference=habitat_preference)

