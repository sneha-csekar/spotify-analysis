# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 00:24:51 2021

@author: sneha
"""
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Setting HTML session metrics
def set_session():
    hsession = requests.Session()
    home_page = 'https://spotifycharts.com/regional/us/weekly/'
    hdrs =  {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'}
    return hsession, home_page, hdrs

# Weekly Top 200 charts for year 2021
def get_top200(week_values):
    top200_df = pd.DataFrame()
    for w in week_values:
        hsession, home_page, hdrs = set_session()
        weekly_url = home_page + w

        rank_list = []
        track_artist_list = []
        track_list = []
        artist_list = []
        stream_count_list = []
        track_uri_list = []

        page_response = hsession.get(weekly_url,headers = hdrs)
        soup_weekly=BeautifulSoup(page_response.content.decode("utf-8"),"html.parser")
                
        for td in soup_weekly.find_all('td', {'class':'chart-table-position'}):
            rank_list.append((td.get_text()))

        for td in soup_weekly.find_all('td', {'class':'chart-table-track'}):
            track_artist_list.append((td.get_text()))
        
        track_list = [i.split('\n')[1] for i in track_artist_list]
        artist_list = [i.split('\n')[2][3:] for i in track_artist_list]
        
        for td in soup_weekly.find_all('td', {'class':'chart-table-streams'}):
            stream_count_list.append((td.get_text()))
        
        for td in soup_weekly.findAll('td', {'class':'chart-table-image'}):
            for a in td.findAll('a', attrs={'href' : True}):
                track_uri_list.append((a['href']))    
        
        weekly_df = pd.DataFrame({'Week':w, 'Rank':rank_list, 'Track':track_list,'Artist':artist_list,'Streams':stream_count_list, 'Track_uri':track_uri_list})
        top200_df = top200_df.append(weekly_df, ignore_index=True)
        
    return top200_df

# Audio features for the tracks in Weekly Top 200 charts for year 2021
def get_audio_features(charts_df):
    # environment variable for Spotify Web API
    os.environ['SPOTIPY_CLIENT_ID'] = 'bca953c53c564fe4aa19e0c4085d66d3'
    os.environ['SPOTIPY_CLIENT_SECRET'] = '92edefb80299482fae0dfb8f0aa4a2bb'
    spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

    # Extract audio features for Distinct songs in Top 200 charts of 2021
    unq_track_uris = set(charts_df['Track_uri'])
    
    top200_audiofeatures = pd.DataFrame()
    for track_uri in unq_track_uris:
        out = spotify.audio_features(tracks = [track_uri])
        df = pd.DataFrame(out)
        df['Track_uri'] = track_uri
        
        id = track_uri.split("/")[4]
        metadata = spotify.track(id)
        pop_score = metadata.get('popularity')
        df['Popularity'] = pop_score
        
        top200_audiofeatures = top200_audiofeatures.append(df)
    return top200_audiofeatures

def main():
    # Home page and week extraction
    hsession, home_page, hdrs = set_session()
    page_response = hsession.get(home_page,headers = hdrs)
    soup_data=BeautifulSoup(page_response.content.decode("utf-8"),"html.parser")
    weeks=[item['data-value'] for item in soup_data.find('div', {'data-type':'date'}).find_all('li', attrs={'data-value' : True})] 

    # Select only the weeks in year 2021
    crawl_weeks= weeks[8:60]

    
    # Extract top 200 charts and audio features for distinct songs in the 2021 top charts
    print('Extracting from USA top 200 charts for year 2021...')
    top200_charts_df = get_top200(crawl_weeks)
    print('Extracting audio features for songs in top 200 charts for year 2021...')
    top200_audiofeatures_df = get_audio_features(top200_charts_df)
    
    # Export to csv       
    top200_charts_df.to_csv(r'E:\Projects\Spotify 2021 charts\Spotify data\Scraped data\2021\Top200_Weekly_charts.csv', index = False)
    top200_audiofeatures_df.to_csv(r'E:\Projects\Spotify 2021 charts\Spotify data\Scraped data\2021\Top200_Weekly_audiofeatures.csv', index = False)

if __name__ == "__main__":
    main()