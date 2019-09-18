from flask import render_template
from flyingcolors import app
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
import pandas as pd
import psycopg2

user = 'postgres'
host = 'localhost'
dbname = 'observations'
db = create_engine('postgres://%s%s/%s' %(user,host,dbname))
con = None
con = psycopg2.connect(database = dbname, user = user)

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
