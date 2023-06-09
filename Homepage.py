import streamlit as st
import pandas as pd
import pyodbc
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import requests
import streamlit as st
from streamlit_lottie import st_lottie
from PIL import Image
from streamlit_option_menu import option_menu
from datetime import date, timedelta
import calendar
from pathlib import Path


clientID= st.secrets['clientID']
clientSe = st.secrets['clientSe']
redirect='http://localhost:7777/callback' 

# ---- HEADER SECTION ----
st.set_page_config(page_title="SpotiChart", page_icon=":sound:", layout="wide")

#### Loading assets #####
# PATH SETTINGS 
current_dir =Path(__file__).parent if '__file__' in locals() else Path.cwd()
css_file = current_dir/'styles'/'main.css'

profile_alan_ph = current_dir/'assets'/'alan.jpeg'
profile_katy_ph = current_dir/'assets'/'katy.png'
profile_tabata_ph = current_dir/'assets'/'tabata.png'

#DESCRIPTIONS 
NAMEALAN= 'Alan Florez'
DESCRIPTIONALAN= ' Spotify API PRO'
NAMEKATY='Katy Diaz'
DESCRIPTIONKATY='Front-End Developer'
NAMETABATA='Tabata Llach'
DESCRIPTIONTABATA='Back-end developer'


#to grant access to the user's spotify data
scope = "user-top-read"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id = clientID, client_secret = clientSe,redirect_uri = redirect, scope = scope))


selected = option_menu(
        menu_title=None, 
        options=['Home', 'Graphics', 'About Us'],
        icons=['house-fill', 'bar-chart-line-fill', 'envelope-fill'],
        menu_icon='cast', 
        default_index=0,
        orientation= 'horizontal',
)


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

# Perform query.
# Uses st.cache_data to only rerun when the query changes or after 10 min.
@st.cache_data(ttl=300)
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        return cur.fetchall()

@st.cache_data(ttl=300)
def run_queryDF(query):
    return pd.read_sql(query, conn)

#format sentences to query
def createSentence(lista: list):
    sentence = f"('{lista[0]}'"
    if len(lista) > 1:
        for c in range(1, len(lista)):
            sentence += ",'" + lista[c] + "'"
    sentence += ")"
    return sentence

#query of the top songs (recently) played by the user
def queryRecently():
    artist_name=[]
    track_name=[]
    track_url=[]
    recent = sp.current_user_top_tracks(limit=10, time_range= 'short_term') #dict

    for track in recent['items']:
        track_name.append(track['name'])
        artist_name.append(track['artists'][0]['name'])
        track_url.append(track["preview_url"])

    recent = pd.DataFrame({'artist':artist_name,'track':track_name, 'url': track_url}) #df
    return recent

#query of the top artist played by the user
def queryTArtists():
    results = sp.current_user_top_artists(limit=10, time_range= 'long_term')
    artist_name=[]
    popularity=[]
    genres=[]
    images=[]
    for artist in results['items']:
        print("Here")
        print(artist)
        genres.append(artist['genres'])
        images.append(artist['images'][0]['url'])
        artist_name.append(artist['name'])
        popularity.append(artist['popularity'])
        
    topA = pd.DataFrame({'artist':artist_name,'popularity':popularity,'genres':genres,'url_image':images}) #df
    return topA

def queryTSongs():
    results = sp.current_user_top_tracks(limit=10, time_range= 'long_term')
    artist_name=[]
    track_name=[]
    track_url=[]
    
    for track in results['items']:
        track_name.append(track['name'])
        artist_name.append(track['artists'][0]['name'])
        track_url.append(track["preview_url"])

    recent = pd.DataFrame({'artist':artist_name,'track':track_name, 'url': track_url}) #df
    return recent



def display_Home():
    with st.container():
        st.subheader("Hi, This is Spotichart :wave:")
        st.title("Let's give a try to our page,we have a lot of options to explore")
    with st.container():
        st.write("---")
        left_column, right_column = st.columns(2)
        with left_column:
            st.header("What SpotiChart Do")
            st.write(
                """
                Spoticharts is a website that is customized according to your musical tastes, allows you to discover related music and offers you the possibility to compare the popularity of songs and playlists over time, giving you a more complete and enriching music experience.
                """
            )
            st.write("[Our DataFrame >](https://www.kaggle.com/datasets/dhruvildave/spotify-charts)")
        with right_column:
            # ---- LOAD ASSETS ----
            try:
                r = requests.get("https://assets2.lottiefiles.com/private_files/lf30_fjln45y5.json")
                lottie_coding = r.json()
            except (e) as e:
                print(e)
            
            st_lottie(lottie_coding, height=300, key="coding")

def isAllCorrect(list:list):
    return not len(list)==0

def list2String(list:list):
    if(len(list)==1):
        return ''.join(list[0])
    else:
        str=' '
        for i in list:
            str += i+', '
        return str.rsplit(',',1)[0]

def matchFinder(dtA:pd.DataFrame,dtB:pd.DataFrame,colA:str,colB:str):
    match=[]
    for index, rowA in dtA.iterrows():
        for index, rowB in dtB.iterrows():
            if rowA[colA]==rowB[colB]:
                match.append(rowA[colA])
    return match


def display_Graphs():
    with st.container():
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
            'South Africa', 'United Arab Emirates', 'Russia', 'Ukraine' ,'South Korea'], max_selections=1,
        )
        #Select date
        with st.sidebar.expander(label='Report month'):
            max_year = 2021
            max_month = 12
            report_year = st.selectbox(label='year',options= range(max_year, 2016, -1),label_visibility='hidden')
            month_abbr = calendar.month_abbr[1:]
            report_month_str = st.radio(label='month', options=month_abbr, index=max_month - 1, horizontal=True,label_visibility='hidden')
            report_month = month_abbr.index(report_month_str) + 1
        
        buttonSearch = st.sidebar.button('Search')
        
        #Tabs
        tab0, tab1, tab2,tab3 = st.tabs(['Query :memo:','Current :clock1:',':female-singer: Top artists:male-singer:','Top songs :musical_note::fire:'])
        
        if buttonSearch:
            if isAllCorrect(country):
                #Funcion que retorna los paises seleccionados en forma de query
                sentence = createSentence(country)
                data = run_queryDF(f"select * from charts as ps where ps.region IN {sentence} and month(ps.date) = {report_month} and year(ps.date)= {report_year};")
                with tab0:
                    df2 = data[['rank', 'title', 'artist', 'url']].copy()
                    df2 = df2.set_index('rank')
                    st.table(df2)

                def writeStyle(sentence, color, size=16):
                    st.markdown(f'<p style="color:{color};font-size:{size}px;">{sentence}</p>', unsafe_allow_html=True)
                
                with tab1:
                    st.write('### Your current tastes')
                    recent = queryRecently()
                    with st.container():
                        col1, col2, col3 = st.columns((4,3,3))
                        with col1:
                            writeStyle("Artist", "white")
                            for artist in recent.loc[:,"artist"]:
                                st.write("")
                                writeStyle(artist, "#1e81b0")
                                st.write("")
                        
                        with col2:
                            writeStyle("Song", "white")
                            for track in recent.loc[:,"track"]:
                                col2.write("")
                                writeStyle(track, "#abdbe3")
                                col2.write("")
                        
                        with col3:
                            writeStyle("Preview", "white")
                            for url in recent.loc[:,"url"]:
                                st.audio(url, format='audio/mp3')
                    
                    with st.container():
                        st.write('### Comparison')
                        m=matchFinder(data,recent,'title','track')
                        if len(m)==0:
                            st.info("No matches found! 	:eyes: :pleading_face: :cold_face:")
                        else:
                            st.info('You have tastes that match old trends!')
                            col1, col2, col3 = st.columns((4,3,3))
                            matches=data[data['title'].isin(m)]
                            df2 = matches[['rank', 'title', 'artist', 'url']].copy()
                            
                            with col1:
                                
                                writeStyle("Artist", "white")
                                for artist in df2.loc[:,"artist"]:
                                    writeStyle(artist, "#1e81b0")
                            
                            with col2:
                                writeStyle("Song", "white")
                                for track in df2.loc[:,"title"]:
                                    writeStyle(track, "#abdbe3")
                            
                            with col3:
                                writeStyle("Url", "white")
                                for url in df2.loc[:,"url"]:
                                    st.write(f'[Our DataFrame >]({url})')
                
                with tab2:
                    st.write('### Your top artists of all times')
                    tArtists = queryTArtists()
                    with st.container():
                        col1, col2 = st.columns(2)
                        
                        def write(row):
                            st.image(row['url_image'], width=200)
                            st.write(f'#### {row["artist"]}')
                            sentence = f'Popularity: {row["popularity"]}'
                            writeStyle(sentence, 'grey')
                            sentence = f'Genres: {list2String(row["genres"])}'
                            writeStyle(sentence, 'grey')
                        
                        for index, row in tArtists.iterrows():
                            if index % 2 == 0:
                                with col1:
                                    write(row)
                            else:
                                with col2:
                                    write(row)
                    
                    m=matchFinder(data,tArtists,'artist','artist')
                    with st.container():
                        writeStyle("Comparison", "white", 26)
                        if len(m)==0:
                            st.info("No matches found! 	:eyes: :pleading_face: 	:cold_face:")
                        else:
                            st.info(f'Hey, you have artists shining in {report_year}!')

                            col1, col2, col3 = st.columns((4,3,3))
                            matches=data[data['artist'].isin(m)]
                            df2 = matches[['rank', 'title', 'artist', 'url']].copy()
                            
                            with col1:
                                writeStyle("Artist", "white")
                                for artist in df2.loc[:,"artist"]:
                                    writeStyle(artist, "#1e81b0")
                            
                            with col2:
                                writeStyle("Song", "white")
                                for track in df2.loc[:,"title"]:
                                    writeStyle(track, "#abdbe3")
                            
                            with col3:
                                writeStyle("Url", "white")
                                for url in df2.loc[:,"url"]:
                                    st.write(f'[Listen in Spotify]({url})')
                
                with tab3:
                    st.write('### Your top songs of all times')
                    tSongs = queryTSongs()
                    
                    with st.container():
                        col1, col2, col3 = st.columns((4,3,3))
                        with col1:
                            writeStyle("Artist", "white")
                            for artist in tSongs.loc[:,"artist"]:
                                st.write("")
                                writeStyle(artist, "#1e81b0")
                                st.write("")
                        
                        with col2:
                            writeStyle("Song", "white")
                            for track in tSongs.loc[:,"track"]:
                                col2.write("")
                                writeStyle(track, "#abdbe3")
                                col2.write("")
                        
                        with col3:
                            writeStyle("Preview", "white")
                            for url in tSongs.loc[:,"url"]:
                                st.audio(url, format='audio/mp3')
                    
                    m=matchFinder(data, tSongs,'title','track')
                    with st.container():
                        st.write('### Comparison')
                        if len(m)==0:
                            st.info("No matches found! 	:eyes: :pleading_face: :cold_face:")
                        else:
                            st.info('You have tastes that match old trends!')
                            
                            col1, col2, col3 = st.columns((4,3,3))
                            matches=data[data['title'].isin(m)]
                            df2 = matches[['rank', 'title', 'artist', 'url']].copy()
                            
                            with col1:
                                writeStyle("Artist", "white")
                                for artist in df2.loc[:,"artist"]:
                                    writeStyle(artist, "#1e81b0")
                            
                            with col2:
                                writeStyle("Song", "white")
                                for track in df2.loc[:,"title"]:
                                    writeStyle(track, "#abdbe3")
                            
                            with col3:
                                writeStyle("Url", "white")
                                for url in df2.loc[:,"url"]:
                                    st.write(f'[Listen in Spotify]({url})')
                
            else:
                st.warning("Sorry, there's been a problem filling those boxes 🧐🧐")
                st.info("Please check and hit that search button again! 🤞")
        else:
            with tab0:
                st.write("Here you can see really curious facts about your current spotify trends!")
                st.success("To visualizes the graphics. Fill the boxes on your left 👈")
            with tab1:
                st.info("Here you will see a comparison against your most current activity!")
            with tab2:
                st.info("Here you will see a comparison against the people you've heard the most!")
            with tab3:
                st.info("Here you will see a comparison against the songs you've heard the most!")

def display_About():
    st.title('Meet the ✨PANES✨ team')
    st.write('---')
    st.subheader('Our team is conformed by a group of 3 gay people 💋')
    #LOAD CSS AND IMAGE
    with st.container():
        with open(css_file) as f:
            st.markdown("<style>{}</style>".format(f.read()), unsafe_allow_html=True)
        profile_alan = Image.open(profile_alan_ph)
        profile_katy =Image.open(profile_katy_ph)
        profile_tabata =Image.open(profile_tabata_ph)
        col1, col2, col3 =st.columns(3, gap='small')
        with col1:
            st.image(profile_alan, width=200)
            st.title(NAMEALAN)
            st.write(DESCRIPTIONALAN)
        with col2:
            st.image(profile_katy, width=200)
            st.title(NAMEKATY)
            st.write(DESCRIPTIONKATY)
        with col3:
            st.image(profile_tabata, width=200)
            st.title(NAMETABATA)
            st.write(DESCRIPTIONTABATA)

if selected == 'Home':
    display_Home()
elif selected == 'Graphics':
    display_Graphs()
elif selected == 'About Us':
    display_About()

#HIDE LINES MENU AND MADE WITH STREAMLIT 
hide_st_style = """
                <style>
                #MainMenu {visibility:hidden;}
                footer {visibility:hidden;}
                </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
