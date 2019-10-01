#common modules
import pandas as pd
import matplotlib.pyplot as plt
import time
import pickle
import datetime
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import psycopg2
import csv

from collections import OrderedDict
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import numpy as np
from sklearn import metrics

from geopy.distance import great_circle
from shapely.geometry import MultiPoint

import dateutil.relativedelta

user_reference_point = [41.27763488, -87.13232721]
user_observe_date = '2019-09-21'

def get_closest_cluster_point(clusters,reference):
    #print(clusters)
    closest_point = min(clusters, key=lambda point: great_circle(point,reference).m)
    return tuple(closest_point)

def get_features_one_cluster_month(date,cluster_id,climate_pd):
    lat = int(cluster_id.split('_')[0].split('lat')[1])
    lon = int(cluster_id.split('_')[1].split('lon')[1])
    month_ratio = 0
    monthval = date.strftime("%m")
    ppt_m1 = get_predict_precip_minus_one_month(climate_pd,date,cluster_id)
    ppt_m2 = get_predict_precip_minus_two_month(climate_pd,date,cluster_id)
    ppt_m3 = get_predict_precip_minus_three_month(climate_pd,date,cluster_id)
    tmean_m1 = get_predict_tmean_minus_one_month(climate_pd,date,cluster_id)
    tmean_m2 = get_predict_tmean_minus_two_month(climate_pd,date,cluster_id)
    tmean_m3 = get_predict_tmean_minus_three_month(climate_pd,date,cluster_id)
    classification = 0
    month = int(monthval)
    returndict = {'depend_var':month_ratio,'ppt_m1':ppt_m1,'ppt_m2':ppt_m2,'ppt_m3':ppt_m3,'tmean_m1':tmean_m1,'tmean_m2':tmean_m2,'tmean_m3':tmean_m3,'classification': classification,'lat':lat,'lon':lon,'month':month}
    return returndict

def get_date_minus_one(date):
    date2 = date - dateutil.relativedelta.relativedelta(months=1)
    datereturn = date2.strftime("%m")
    return datereturn

def get_date_minus_two(date):
    date2 = date - dateutil.relativedelta.relativedelta(months=2)
    datereturn = date2.strftime("%m")
    return datereturn

def get_date_minus_three(date):
    date2 = date - dateutil.relativedelta.relativedelta(months=3)
    datereturn = date2.strftime("%m")
    return datereturn

def get_predict_precip_minus_one_month(climate_data,month,cluster_id):
    date = get_date_minus_one(month)
    ppt_date = "ppt_{}".format(date)
    row = climate_data.loc[climate_data['id']==cluster_id]
    val = row[ppt_date].iloc[0]
    return val

def get_predict_precip_minus_two_month(climate_data,month,cluster_id):
    date = get_date_minus_two(month)
    ppt_date = "ppt_{}".format(date)
    row = climate_data.loc[climate_data['id']==cluster_id]
    val = row[ppt_date].iloc[0]
    return val

def get_predict_precip_minus_three_month(climate_data,month,cluster_id):
    date = get_date_minus_three(month)
    ppt_date = "ppt_{}".format(date)
    row = climate_data.loc[climate_data['id']==cluster_id]
    val = row[ppt_date].iloc[0]
    return val

def get_predict_tmean_minus_one_month(climate_data,month,cluster_id):
    date = get_date_minus_one(month)
    ppt_date = "tmean_{}".format(date)
    row = climate_data.loc[climate_data['id']==cluster_id]
    val = row[ppt_date].iloc[0]
    return val

def get_predict_tmean_minus_two_month(climate_data,month,cluster_id):
    date = get_date_minus_two(month)
    ppt_date = "tmean_{}".format(date)
    row = climate_data.loc[climate_data['id']==cluster_id]
    val = row[ppt_date].iloc[0]
    return val

def get_predict_tmean_minus_three_month(climate_data,month,cluster_id):
    date = get_date_minus_three(month)
    ppt_date = "tmean_{}".format(date)
    row = climate_data.loc[climate_data['id']==cluster_id]
    val = row[ppt_date].iloc[0]
    return val


def get_classifier():
    pk1file = open('trained_QDA_Sep30.pk1','rb')
    QDA_classifier = pickle.load(pk1file)
    pk1file.close()
    return QDA_classifier

def get_climate_normals():
    climate_normals = pd.read_csv('Trimmed_Climate_Normals.csv', index_col=0)
    return climate_normals

def get_cluster_coords():
    climate_normals = get_climate_normals()
    all_cluster_coords = []
    for i in range(len(climate_normals)):
        clat = climate_normals['lat'].iloc[i]
        clon = climate_normals['lon'].iloc[i]
        all_cluster_coords.append(tuple([clat,clon]))
    return all_cluster_coords

def get_closest_point_id(all_cluster_coords,reference_point):
    closest_point = get_closest_cluster_point(all_cluster_coords,reference_point)
    closest_point_id = "lat{}_lon{}_id".format(closest_point[0],closest_point[1])
    return closest_point_id

def get_X_userinput(all_cluster_coords,observe_date,location):
    format_observe_date = datetime.datetime.strptime(observe_date, "%Y-%m-%d")
    closest_point_id = get_closest_point_id(all_cluster_coords,location)
    climate_normals = get_climate_normals()
    features_returned = get_features_one_cluster_month(format_observe_date,closest_point_id,climate_normals)
    val = []
    val.append(features_returned)
    features_returned_pd = pd.DataFrame(val)
    X_userinput = features_returned_pd[['ppt_m1','ppt_m2','ppt_m3','tmean_m1','tmean_m2','tmean_m3','lat','lon','month']]
    return X_userinput

def get_prediction_from_input(observe_date,location):
    class_QDA = get_classifier()
    all_cluster_coords = get_cluster_coords()
    X_userinput = get_X_userinput(all_cluster_coords,observe_date,location)
    user_pred = class_QDA.predict(X_userinput)
    return user_pred[0]

prediction = get_prediction_from_input(user_observe_date,user_reference_point)
print("got a prediction")
print(prediction)
