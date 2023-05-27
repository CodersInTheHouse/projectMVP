import streamlit as st 
import pandas as pd
import pyodbc
from datetime import date, timedelta
import datetime
import calendar
import numpy as np
import spotipy.util as util
import spotipy
from spotipy.oauth2 import SpotifyOAuth


clientID= st.secrets['clientID']
clientSe = st.secrets['clientSe']
redirect='http://localhost:7777/callback'    

st.set_page_config(page_title= "Spotipi trends Data", page_icon=":bar_chart:", layout="wide")


# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource
def init_connection():
    connected = False
    while (connected==False):
        conn = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};SERVER="
            + st.secrets["server"]
            + ";DATABASE="
            + st.secrets["database"]
            + ";UID="
            + st.secrets["username"]
            + ";PWD="
            + st.secrets["password"],
            timeout=30
        )
        try:
            connected = True
            conn.cursor().execute('select top 1 from charts')
        except pyodbc.Error as error:
            if error.args[0] == "08S01":
                connected= False
                conn.close()
    return conn




conn = init_connection()

#SIDE BAR 
st.sidebar.header('Please choose the items below:')

#SELECT COUNTRY
country = st.sidebar.multiselect(
    'Select country', ['Argentina' ,'Australia' ,'Brazil', 'Austria', 'Belgium' ,'Colombia', 'Bolivia', 'Denmark' ,'Bulgaria' ,'Canada' ,'Chile' ,'Costa Rica', 'Czech Republic',
    'Finland' ,'Dominican Republic', 'Ecuador' ,'El Salvador' ,'Estonia' ,'France',
    'Germany' ,'Global', 'Greece', 'Guatemala', 'Honduras', 'Hong Kong', 'Hungary',
    'Iceland', 'Indonesia', 'Ireland', 'Italy', 'Japan', 'Latvia', 'Lithuania',
    'Malaysia', 'Luxembourg', 'Mexico', 'Netherlands', 'New Zealand', 'Nicaragua',
    'Norway', 'Panama', 'Paraguay', 'Peru' ,'Philippines', 'Poland', 'Portugal',
    'Singapore', 'Spain', 'Slovakia', 'Sweden', 'Taiwan', 'Switzerland', 'Turkey',
    'United Kingdom', 'United States', 'Uruguay', 'Thailand', 'Andorra', 'Romania',
    'Vietnam' ,'Egypt', 'India', 'Israel', 'Morocco', 'Saudi Arabia',
    'South Africa', 'United Arab Emirates', 'Russia', 'Ukraine' ,'South Korea'], max_selections=2,
)

#Select date
with st.sidebar.expander(label='Report month'):
    max_year = 2021
    max_month = 12
    report_year = st.selectbox(label='year',options= range(max_year, 2016, -1),label_visibility='hidden')
    month_abbr = calendar.month_abbr[1:]
    report_month_str = st.radio(label='month', options=month_abbr, index=max_month - 1, horizontal=True,label_visibility='hidden')
    report_month = month_abbr.index(report_month_str) + 1

#BUTTON
buttonSearch = st.sidebar.button('Search')

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=300)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

@st.cache_data(ttl=300)
def run_queryDF(query):
    return pd.read_sql(query,conn)

def createSentence(lista: list):
    sentence = f"('{lista[0]}'"
    if len(lista) > 1:
        for c in range(1, len(lista)):
            sentence += ",'" + lista[c] + "'"
    sentence += ")"
    return sentence

def prettySentence(list:list):
    text = ','.join(list)
    if(len(list)>1):
        text = text.replace(f',{list[-1]}',f' and {list[-1]}')
    return text

def isAllCorrect() -> bool:
    return len(country) > 0

#Tabs
tab0, tab1, tab2 = st.tabs(['Query','Current','Top'])

if buttonSearch:
    if isAllCorrect():
        #Funcion que retorna los paises seleccionados en forma de query
        sentence = createSentence(country)
        pSentence = prettySentence(country)
        
        with tab0:
            data = run_queryDF(f"select * from charts as ps where ps.region IN {sentence} and month(ps.date) = {report_month} and year(ps.date)={report_year};")
            st.table(data)

        with tab1:   
            scope = "user-read-recently-played"       
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=clientID,client_secret=clientSe,redirect_uri=redirect,scope=scope))
            results = sp.current_user_recently_played(limit=10)
            recent = pd.DataFrame.from_dict(results)
            st.table(recent)
            #for idx, item in enumerate(results['items']):
            #    track = item['track']
            #    print(idx, track['artists'][0]['name'], " – ", track['name'])

            

        with tab2:
            scope = "user-top-read"
            sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=clientID,client_secret=clientSe,redirect_uri=redirect,scope=scope))
            results = sp.current_user_top_artists(limit=10)
            topA = pd.DataFrame.from_dict(results)
            st.table(topA)
            for idx, artist in enumerate(results['items']):
                print(idx, artist['name'],artist['popularity'],artist['genres'],artist['images'][0])
            results = sp.current_user_top_tracks()
            topT = pd.DataFrame.from_dict(results)
            st.table(topT)
            for idx, item in enumerate(results['items']):
                artists=[artist['name'] for artist in item['artists']]
                print(idx, item['name'],artists)

    else:
        st.warning("Sorry, there's been a problem filling those boxes 🧐🧐")
        st.info("Please check and hit that search button again! 🤞")
else:
    with tab0:
        st.info("Welcome to our webpage!")
        st.write("Here you can see really curious facts about your current spotify trends!")
        st.success("To visualizes the graphics. Fill the boxes on your left 👈")
    
    with tab1:
        st.info("Here you will see a line chart of the query you just performed!")
    
    with tab2:
        st.info("Here you will see a bar chart of the query you just performed!")
    



    

#HIDE LINES MENU AND MADE WITH STREAMLIT 
hide_st_style = """
              <style>
              #MainMenu {visibility:hidden;}
              footer {visibility:hidden;}
              </style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
