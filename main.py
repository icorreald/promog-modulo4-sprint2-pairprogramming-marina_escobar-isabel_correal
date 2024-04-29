#%%
# API SPOTIFY --------------------------------------------------------------------------------------------------------
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

import pandas as pd
import numpy as np

from src import api_soporte as api

sp = api.credenciales()

lista_discos = ['https://open.spotify.com/album/5eyZZoQEFQWRHkV2xgAeBw?si=QfZUzkisSweWF6f5Zw48SQ', # debut
                'https://open.spotify.com/album/6tgMb6LEwb3yj7BdYy462y?si=KMuHR1gFSUabKJnnBBpmfA', # fearless
                'https://open.spotify.com/album/6S6JQWzUrJVcJLK4fi74Fw?si=Y28PyIx-S2KlQj7MHk11TA', # speak now (deluxe)
                'https://open.spotify.com/intl-es/album/1KVKqWeRuXsJDLTW0VuD29?si=4ObfYoNORsaeV85ZUdfxZw', # red
                'https://open.spotify.com/album/1yGbNOtRIgdIiGHOEBaZWf?si=cQmUCtaYTq2MXY-G9jA8-Q', # 1989 deluxe
                'https://open.spotify.com/album/6DEjYFkNZh67HP7R9PSZvv?si=XTd1zjmRSI-yMgw9tB1Stg', # reputa
                'https://open.spotify.com/album/1NAmidJlEaVgA3MpcPFYGq?si=VyPthD5zR5yqq27y4qgUyw', # lover
                'https://open.spotify.com/album/1pzvBxYgT6OVwJLtHkrdQK?si=KtiGk4TYQCapyGHhnZwavA', # folklore
                'https://open.spotify.com/album/6AORtDjduMM3bupSWzbTSG?si=hcY11QxLR4OX8LDkNVtwOw', # evermore
                'https://open.spotify.com/album/3lS1y25WAhcqJDATJK70Mq?si=XPoxfq8iTU6GVBKZK9sMfg', # midnights (3am)
                'https://open.spotify.com/album/5H7ixXZfsNMGbIE5OBSpcb?si=idsuy6fzS0GIUdFBYqOKGQ'] # ttpd (2am)

lista_uri = []
for link in lista_discos:
    lista_uri.append(link.split('/')[-1].split('?')[0])

lista_datos_discos = []
for uri in lista_uri:
    lista_datos_discos.append(sp.album(uri))

dataframe_discos = {'disco':[],
                    'release_date': [],
                    'markets': [],
                    'label': [],
                    'total_tracks': []}
for disco in lista_datos_discos:
    dataframe_discos['disco'].append(disco['name'])
    dataframe_discos['release_date'].append(disco['release_date'])
    dataframe_discos['markets'].append(disco['available_markets'])
    dataframe_discos['label'].append(disco['label'])
    dataframe_discos['total_tracks'].append(disco['total_tracks'])

df = pd.DataFrame(dataframe_discos)
df.to_csv('files/general_info_albums.csv')

lista_uri_tracks = []
track_info = {'name': [],
            'album': [],
            'release_date': [],
            'track_number': [],
            'id': [],
            'uri': []}

for disco in [lista_datos_discos[10]]:
    album_name = disco['name']
    track_info['album'].extend([album_name] * len(disco['tracks']['items']))

    album_date = disco['release_date']
    track_info['release_date'].extend([album_date] * len(disco['tracks']['items']))
    for track in disco['tracks']['items']:
        track_info['name'].append(track['name'])
        track_info['track_number'].append(track['track_number'])
        track_info['id'].append(track['id'])
        track_info['uri'].append(track['uri'])
        

track_info_df = pd.DataFrame(track_info)

track_audio_ft = {'uri': [],
            'acousticness': [],
            'danceability': [],
            'energy': [],
            'instrumentalness': [],
            'liveness': [],
            'loudness': [],
            'speechiness': [],
            'tempo': [],
            'valence': [],
            'popularity': [],
            'duration_ms': []
            }

for uri in track_info['uri']:
    datos = sp.audio_features(uri)
    track_audio_ft['uri'].append(datos[0]['uri'])
    track_audio_ft['acousticness'].append(datos[0]['acousticness'])
    track_audio_ft['danceability'].append(datos[0]['danceability'])
    track_audio_ft['energy'].append(datos[0]['energy'])
    track_audio_ft['instrumentalness'].append(datos[0]['instrumentalness'])
    track_audio_ft['liveness'].append(datos[0]['liveness'])
    track_audio_ft['loudness'].append(datos[0]['loudness'])
    track_audio_ft['speechiness'].append(datos[0]['speechiness'])
    track_audio_ft['tempo'].append(datos[0]['tempo'])
    track_audio_ft['valence'].append(datos[0]['valence'])
    track_audio_ft['duration_ms'].append(datos[0]['duration_ms'])

    track = sp.track(uri)
    track_audio_ft['popularity'].append(track["popularity"])


track_audio_ft_df =pd.DataFrame(track_audio_ft)

df_merged = pd.merge(track_info_df, track_audio_ft_df, on='uri', how='left')

df_merged.to_csv('files/ts_spotify_fearless-red-ttpd.csv', index=False)

#%%
# MERGE ALL ALBUMS --------------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np

df_ts_spotify1 = pd.read_csv('files/taylor_swift_spotify.csv', index_col=0)
df_ts_spotify2 = pd.read_csv('files/ts_spotify_fearless-red-ttpd.csv')

albumes = ['Taylor Swift',
            'Fearless Platinum Edition',
            'Speak Now (Deluxe Edition)',
            'Red (Deluxe Edition)',
            '1989 (Deluxe Edition)',
            'reputation',
            'Lover',
            'folklore (deluxe version)',
            'evermore (deluxe version)',
            'Midnights (3am Edition)']

df_spotify = df_ts_spotify1[df_ts_spotify1['album'].isin(albumes)].reset_index(drop=True)

df_concatenado = pd.concat([df_spotify, df_merged], ignore_index=True)

df_concatenado.to_csv('files/all_songs_audio_data.csv')

#%%
# INFO ALBUM --------------------------------------------------------------------------------------------------------
import pandas as pd

from bs4 import BeautifulSoup
import requests

from selenium import webdriver  
from webdriver_manager.chrome import ChromeDriverManager  
from selenium.webdriver.common.keys import Keys  
from selenium.webdriver.support.ui import Select 

from time import sleep

pd.set_option('display.max_columns', None)

data_album = {'album': [],
                'sales': [],
                'awards': [],
                'score_critic': [],
                'score_public': []}

driver = webdriver.Chrome()
driver.get('https://en.wikipedia.org/wiki/Taylor_Swift_albums_discography')
sleep(1)
for child in range(3, 13):
    data_album['album'].append(driver.find_element('css selector', f'#mw-content-text > div.mw-content-ltr.mw-parser-output > table:nth-child(13) > tbody > tr:nth-child({child}) > th').text)
    data_album['sales'].append((driver.find_element('css selector', f'#mw-content-text > div.mw-content-ltr.mw-parser-output > table:nth-child(13) > tbody > tr:nth-child({child}) > td:nth-child(13)').text).split('\n')[0])

driver = webdriver.Chrome()

# no voy a poner el último aquí porque hay aún pocas reviews aún
for disco in ['taylor-swift', 'fearless', 'speak-now', 'red', '1989', 'reputation', 'lover', 'folklore', 'evermore', 'midnights']:
    url = f'https://www.metacritic.com/music/{disco}/taylor-swift'
    driver.get(url)
    sleep(1)

    data_album['score_critic'].append(driver.find_element('css selector', '#main > div:nth-child(2) > div:nth-child(1) > div.left > div.module.product_data.product_data_summary > div > div.summary_wrap > div.section.product_scores > div.details.main_details > div > div > a > div').text)
    data_album['score_public'].append(driver.find_element('css selector', '#main > div:nth-child(2) > div:nth-child(1) > div.left > div.module.product_data.product_data_summary > div > div.summary_wrap > div.section.product_scores > div.details.side_details > div > div > a > div').text)
    
data_album_df = pd.DataFrame(data_album)

data_album_df.to_csv('files/album_info.csv')

#%%
# LYRICS SCRAPPING --------------------------------------------------------------------------------------------------------
lyrics = {'song':[], 'lyrics': []}
driver = webdriver.Chrome()

canciones = [
    'Fortnight',
    'The Tortured Poets Department',
    'My Boy Only Breaks His Favorite Toys',
    'Down Bad',
    'So Long, London',
    'But Daddy I Love Him',
    'Fresh Out The Slammer',
    'Florida!!!',
    'Guilty as Sin?',
    "Who's Afraid of Little Old Me?",
    'I Can Fix Him (No Really I Can)',
    'loml',
    'I Can Do It With A Broken Heart',
    'The Smallest Man Who Ever Lived',
    'The Alchemy',
    'Clara Bow',
    'The Black Dog',
    'imgonnagetyouback',
    'The Albatross',
    'Chloe or Sam or Sophia or Marcus',
    'How Did it End?',
    'So High School',
    'I Hate it Here',
    'thanK you aiMee',
    'I Look in Peoples Windows',
    'The Prophecy',
    'Cassandra',
    'Peter',
    'The Bolter',
    'Robin',
    'The Manuscript'           
    ]

canciones_mod = [
    'fortnight',
    'the-tortured-poets-department',
    'my-boy-only-breaks-his-favorite-toys',
    'down-bad',
    'so-long-london',
    'but-daddy-i-love-him',
    'fresh-out-the-slammer',
    'florida',
    'guilty-as-sin',
    'whos-afraid-of-little-old-me',
    'i-can-fix-him-no-really-i-can',
    'loml',
    'i-can-do-it-with-a-broken-heart',
    'the-smallest-man-who-ever-lived',
    'the-alchemy',
    'clara-bow',
    'the-black-dog',
    'imgonnagetyouback',
    'the-albatross',
    'chloe-or-sam-or-sophia-or-marcus',
    'how-did-it-end',
    'so-high-school',
    'i-hate-it-here',
    'thank-you-aimee',
    'i-look-in-peoples-windows',
    'the-prophecy',
    'cassandra',
    'peter',
    'the-bolter',
    'robin',
    'the-manuscript'
]

for cancion, cancion_mod in zip(canciones, canciones_mod):
    
    driver.get(f'https://genius.com/Taylor-swift-{cancion_mod}-lyrics')

    # cookies
    try:
        driver.find_element('css selector', '#onetrust-accept-btn-handler').click()
    except:
        pass
    
    # Añade el título de la canción
    lyrics['song'].append(cancion)
    
    # lyrics
    lyrics['lyrics'].append(driver.find_element('css selector', '#lyrics-root > div:nth-child(2)').text)
    
    sleep(3)

lyrics = pd.DataFrame(lyrics)
lyrics.to_csv('files/lyrics_new_album.csv')

#%%
# TOURS --------------------------------------------------------------------------------------------------------
df_conciertos = pd.read_csv('files/Taylor_Train.csv', encoding='ISO-8859-1')

df_conciertos['Tour'] = df_conciertos['Tour'].map({'Fearless_Tour': 'fearless', 'Speak_Now_World_Tour': 'speak now', 'The_Red_Tour': 'red', 'The_1989_World_Tour': '1989', 'Reputation_Stadium_Tour': 'reputation'})

def tour_id(valor):
    if valor == 'fearless':
        return 'ts02'
    elif valor == 'speak now':
        return 'ts03'
    elif valor == 'red':
        return 'ts04'
    elif valor == '1989':
        return 'ts05'
    elif valor == 'reputation':
        return 'ts06'

df_conciertos['tour_id'] = df_conciertos['Tour'].apply(tour_id)

df_conciertos.to_csv('files/concerts_per_tour.csv', index=False)

#%%
# EDITAR DATASETS --------------------------------------------------------------------------------------------------------
album_info = pd.read_csv('files/album_info.csv', index_col=0)
album_info['tour_revenue'] = ('No Tour', 66246496, 123678576, 150184971, 250733097, 345675146, 'No Tour', 'No Tour', 'No Tour', 'No Tour')
album_info['sales'] = album_info['sales'].apply(lambda x : int(x.replace(',', '').replace('[B]', '').replace('[D]', '').replace('[H]', '').replace('US:', '').strip()))
album_info['tour_id'] = ['No Tour', 'ts02', 'ts03', 'ts04', 'ts05', 'ts06', 'No Tour', 'No Tour', 'No Tour', 'No Tour']
album_info.to_csv('files/album_info.csv', index=False)


#%%
# LIMPIEZA DATASETS --------------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np

df_conciertos = pd.read_csv('files/concerts_per_tour.csv')

def to_int(valor):
    try:
        return int(valor.replace(',', '').replace('$', ''))
    except:
        return np.nan
    
def percent(valor):
    try:
        valores = valor.split('/')
        pc1 = int(valores[0].strip().replace(',',''))
        pc2 = int(valores[1].strip().replace(',',''))
        porcentaje = pc2 * 100 / pc1

        return porcentaje
    
    except:
        return np.nan
    
string = '7,463 / 7,463'
valores = string.split('/')
pc1 = int(valores[0].strip().replace(',',''))
pc2 = int(valores[1].strip().replace(',',''))
porcentaje = int(pc2 * 100 / pc1)

df_conciertos['revenue'] = df_conciertos['revenue'].apply(to_int)

df_conciertos['attendance'] = df_conciertos['attendance'].apply(percent)

df_conciertos['attendance'] = df_conciertos['attendance'].fillna(df_conciertos['attendance'].median())

df_con = df_conciertos.copy()

for album in df_conciertos['tour'].unique():
    mask = df_conciertos['tour'] == album
    df_conciertos.loc[mask, 'revenue'] = df_conciertos.loc[mask, 'revenue'].fillna(df_conciertos.loc[mask, 'revenue'].median())

df_conciertos.to_csv('files/concerts_per_tour.csv')


#%%
# GÉNEROS --------------------------------------------------------------------------------------------------------
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()

lista_total = []
for disco in ['debut', 'fearless', 'red', '1989', 'reputation', 'lover', 'folklore', 'evermore', 'the tortured poets department']:
    driver.get('https://www.google.com/')
    try:
        driver.maximize_window()
    except:
        pass

    try:
        driver.find_element('css selector', '#W0wltc > div').click()
    except:
        pass
    
    driver.find_element('css selector', '#APjFqb').send_keys(f'{disco} taylor swift genre songs',  Keys.ENTER)
    sleep(3)

    
    try:
        texto = driver.find_element('css selector', '#tU52Vb > div > div > div:nth-child(1) > div > div.EyBRub').text
        print('Encontrao')

        lista_total.append(texto.replace('/','').split('\n'))
    except:
        print('Uhhhh error')
   
lista_con_todo = []

for lista in lista_total:
    datos_por_disco = [lista[0]]
    lista_auxiliar = []
    for i,v in enumerate(lista):
        if 'Géneros' in v or 'genre' in v:
            lista_auxiliar.append(lista[i+1:-1])
            
    genero_canciones = [[lista_auxiliar[0][i], lista_auxiliar[0][i+1]] for i in range(0, len(lista_auxiliar[0]), 2)]

    for lista in genero_canciones:
        for i, elemento in enumerate(lista):
            if '·' in elemento:
                lista[i] = elemento.split(' · ')
    datos_por_disco.append(genero_canciones)
    lista_con_todo.append(datos_por_disco)


lista_diccionarios = []
for lista in lista_con_todo:
    lista_diccionarios.append({lista[0]: lista[1]})
    
filas = []
for diccionario in lista_diccionarios:
    for artista, generos_canciones in diccionario.items():
        for genero_cancion in generos_canciones:
            genero = genero_cancion[0]
            if isinstance(genero_cancion[1], list):
                for cancion in genero_cancion[1]:
                    filas.append([artista, genero, cancion])
            else:
                cancion = genero_cancion[1]
                filas.append([artista, genero, cancion])
    
df_generos = pd.DataFrame(filas, columns=['album', 'genre', 'song'])

df_generos.to_csv('genero_por_canciones.csv', index=False)

#%%
# GÉNEROS --------------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np

df = pd.read_csv('files/all_songs_audio_data.csv', index_col=0)

categorias = ['acousticness', 'danceability', 'energy', 'instrumentalness',
       'liveness', 'loudness', 'speechiness', 'tempo', 'valence']
album = df['album'].unique()
df_2 = {'album': album, 'category': categorias}

df__2 = pd.DataFrame(df_2)

df_auxiliar = df.groupby('album')[['acousticness', 'danceability', 'energy', 'instrumentalness',
       'liveness', 'loudness', 'speechiness', 'tempo', 'valence']].mean().reset_index()

diccionario = {'album':[], 'category': [], 'mean':[]}
for album in df_auxiliar['album'].unique():
    tupla = (album, )
    
from sklearn.preprocessing import MinMaxScaler

# Crear el objeto MinMaxScaler
scaler = MinMaxScaler(feature_range=(0,1))

# Seleccionar las columnas numéricas que quieres normalizar
columns_to_normalize = ['acousticness', 'danceability', 'energy', 'instrumentalness',
       'liveness', 'loudness', 'speechiness', 'tempo', 'valence']

# Normalizar las columnas seleccionadas
df_auxiliar[columns_to_normalize] = scaler.fit_transform(df_auxiliar[columns_to_normalize])

melted_df = pd.melt(df_auxiliar, id_vars=["album"], value_vars=['acousticness', 'danceability', 'energy', 'instrumentalness',
       'liveness', 'loudness', 'speechiness', 'tempo', 'valence'], var_name="categoria", value_name="promedio")

diccionario_album = {'1989 (Deluxe Edition)':'1989', 'Fearless Platinum Edition':'Fearless', 'Lover':'Lover',
       'Midnights (3am Edition)':'Midnights', 'Red (Deluxe Edition)':'Red',
       'Speak Now (Deluxe Edition)':'Speak Now',
       'THE TORTURED POETS DEPARTMENT: THE ANTHOLOGY':'the tortured poets department', 'Taylor Swift':'Taylor Swift',
    'evermore (deluxe version)':'Evermore', 'folklore (deluxe version)':'Folklore',
       'reputation':'Reputation'}

nombres_categorias = {'acousticness' : 'acústico',
                      'danceability' : 'danzabilidad',
                      'energy' : 'energía',
                      'instrumentalness' : 'instrumental',
                      'liveness' : 'directo',
                      'loudness' : 'volumen',
                      'speechiness' : 'liricismo',
                      'tempo' : 'tempo',
                      'valence' : 'positividad'                      
                      }

melted_df['album']= melted_df['album'].map(diccionario_album)
melted_df['categoria']= melted_df['categoria'].map(nombres_categorias)

melted_df.to_csv('files/radas_powerbi.csv')

#%%
# FECHA_ALBUMS_TUITS --------------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np

df = pd.read_csv('files/taylor_tuits_limpio.csv')

def to_album(valor):
    if '2009' in valor or '2010' in valor:
        return 'speak now'
    elif '2011' in valor or '2012' in valor:
        return 'red'
    elif '2013' in valor or '2014' in valor or '2015' in valor:
        return '1989'
    elif '2016' in valor or '2017' in valor:
        return 'reputation'
    elif '2018' in valor or '2019' in valor:
        return 'lover'
    elif '2020' in valor or '2021' in valor:
        return 'folklore'
    elif '2022' in valor or '2023' in valor:
        return 'midnights'
    
df['album'] = df['date'].apply(to_album)

df.to_csv('files/tuits_nuevo.csv')

#%%
# LIMPIEZA_LETRAS_CANCIONES --------------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
import re

pd.set_option('display.max_columns', None)

df_lyrics2 = pd.read_csv('files/lyrics.csv')
df_last_album = pd.read_csv('files/lyrics_new_album.csv', index_col=0)

df_genres = pd.read_csv('files/genres_to_songs.csv')

df_last_album['lyrics'] = df_last_album['lyrics'].apply(lambda x : re.sub(r'\[.*?\]', '', x).strip().replace('\n', '  '))

df_last_album['Album'] = 'The Tortured Poets Department'

df_last_album = df_last_album.reindex(columns = ['song', 'Album', 'lyrics'])

df_last_album.columns = ['Song', 'Album', 'Lyrics']

albumes = ['Red (Taylor’s Version)', 
           'Lover',
           '1989 (Deluxe)',
           'Midnights (3am Edition)',
           'Taylor Swift',
           'Speak Now (Deluxe)',
           'Fearless (Taylor’s Version)',
           'reputation',
           'evermore (deluxe version)',
           'folklore (deluxe version)',
           'folklore',
           'evermore',
           'Speak Now',
           '1989 (Taylor’s Version)']

df_lyrics_filtrado = df_lyrics2[df_lyrics2['Album'].isin(albumes)]

diccionario = {}

for track in df_lyrics_filtrado['Song']:
    
    df_especific = df_lyrics_filtrado[df_lyrics_filtrado['Song'] == track]
    cadena = "  ".join(df_especific['Lyric'])
    diccionario[track] = cadena
    
df_lyrics_clean = df_lyrics_filtrado.drop_duplicates(subset = 'Song')

lista_a_dropear = []

for cancion in df_lyrics_clean['Song']:
    
    if '[From the Vault]' in cancion:
        lista_a_dropear.append(cancion)
        
df_lyrics_clean = df_lyrics_clean[~df_lyrics_clean['Song'].isin(lista_a_dropear)]

df_lyrics_clean['Lyrics'] = df_lyrics_clean.apply(lambda x : diccionario[x['Song']], axis=1)

df_lyrics_clean.drop(columns = ['Lyric', 'Previous Lyric', 'Next Lyric', 'Multiplicity'], inplace=True)

df_lyrics_clean = df_lyrics_clean.reset_index().drop('index', axis=1)
df_lyrics = pd.concat([df_lyrics_clean, df_last_album], ignore_index=True)

df_lyrics['Song'] = df_lyrics['Song'].apply(lambda x : x.replace(' (Taylor’s Version)', ''))
df_lyrics['Song'] = df_lyrics['Song'].apply(lambda x : x.replace('(Taylor’s Version)', ''))
df_lyrics['Album'] = df_lyrics['Album'].apply(lambda x : x.replace(' (Taylor’s Version)', ''))
df_lyrics['Album'] = df_lyrics['Album'].apply(lambda x : x.replace(' (Deluxe)', ''))
df_lyrics['Song'] = df_lyrics['Song'].apply(lambda x : x.replace(' (Pop Version)', ''))
df_lyrics['Song'] = df_lyrics['Song'].apply(lambda x : x.replace('(Radio Edit)', ''))

diccionario_cambios = {'...Ready for It?' : '…Ready for It?',
                       'So It Goes...' : 'So It Goes…',
                       '’tis the damn season' : '‘tis the damn season',
                       'l​ong story short' : 'long story short',
                       "Who's Afraid of Little Old Me?" : 'Who’s Afraid of Little Old Me?',
                       'You’re Not Sorry' : "You're Not Sorry",
                       'You’re On Your Own, Kid' : "You're on Your Own, Kid",
                       'Would’ve, Could’ve, Should’ve' : "Would've, Could've, Should've"}

df_lyrics['Song'] = df_lyrics['Song'].map(diccionario_cambios).fillna(df_lyrics['Song'])

words = ['In ', 'On ', 'At ', 'By ', 'For ', 'With ', 'From ', 'To ', 'Into ', 'Onto ', 'Of ', 'About ', 'Above ', 'Below ', 'Under ', 'Over ', 'Through ', 'Between ', 'Among ', 'Within ', 'The ', 'But ', 'A ', 'Oh ', 'Oh,', 'It ', 'If ', 'How ', 'Where ', 'When ', 'What ', 'Who ', 'Why ', 'But ', 'Because ', 'An ', 'And ', 'May ']
pattern = r"'[^ ]*"
df_lyrics['Lyrics'] = df_lyrics['Lyrics'].apply(lambda x : re.sub(pattern, '', x))

for word in words:
    df_lyrics['Lyrics'] = df_lyrics['Lyrics'].str.replace(word , ' ')
    df_lyrics['Lyrics'] = df_lyrics['Lyrics'].str.replace(f' {word.lower()}' , ' ')
    
df_lyrics['song'] = df_lyrics['Song'].str.lower().str.strip()
df_genres['song'] = df_genres['song'].str.lower().str.strip()

df_genres = df_genres.merge(df_lyrics, left_on='song', right_on='song', how='left')

df_genres.drop(['song', 'album'], axis=1, inplace=True)

df_genres = df_genres.reindex(columns = ['Album', 'Song', 'genre', 'Lyrics'])

df_genres = df_genres.sort_values('Song', ascending=True)

df_genres.to_csv('files/taylor_full_lyrics_w_genre.csv', index=False)

#%%
# LIMPIEZA_TWITTER --------------------------------------------------------------------------------------------------------
df_tuits = pd.read_csv('files/TaylorSwift13.csv')

df_tuits.drop('created_at', axis=1, inplace=True)

df_tuits['date'] = df_tuits['date'].apply(lambda x : x.replace('+00:00', ''))

df_tuits['media'] = df_tuits['media'].apply(lambda x : 1 if isinstance(x, str) else 0)
df_tuits['outlinks'] = df_tuits['outlinks'].apply(lambda x : 0 if x == '[]' else 1)
df_tuits['quotedTweet'] = df_tuits['quotedTweet'].apply(lambda x : 1 if isinstance(x, str) else 0)
df_tuits['retweetedTweet'] = df_tuits['retweetedTweet'].apply(lambda x : 1 if isinstance(x, str) else 0)

df_tuits['content'] = df_tuits['content'].apply(lambda x : x.replace('\n', ' '))

df_tuits['users'] = df_tuits.apply(lambda x : re.findall(r'@\S+', x['content']), axis=1)

df_citados = df_tuits[['content', 'date', 'users']]

df_tuits.drop('users', axis=1, inplace=True)

df_citados = df_citados.explode('users')

df_citados.dropna(subset='users', inplace = True)

df_tuits.to_csv('files/taylor_tuits_limpio.csv', index=False)
df_citados.to_csv('files/taylor_tuits_citados.csv', index=False)

#%%
# RADAR_SPOTIFY --------------------------------------------------------------------------------------------------------
df = pd.read_csv('files/all_songs_audio_data.csv', index_col=0)

df_auxiliar = df.groupby('album')[['acousticness', 'danceability', 'energy', 'instrumentalness',
       'liveness', 'loudness', 'speechiness', 'tempo', 'valence']].mean().reset_index()

diccionario = {'album':[], 'category': [], 'mean':[]}

melted_df = pd.melt(df_auxiliar, id_vars=["album"], value_vars=['acousticness', 'danceability', 'energy', 'instrumentalness',
       'liveness', 'loudness', 'speechiness', 'tempo', 'valence'], var_name="categoria", value_name="promedio")

nombres_albumes = {'1989 (Deluxe Edition)' : '1989',
                   'Fearless Platinum Edition' : 'Fearless',
                   'Midnights (3am Edition)' : 'Midnights',
                   'Lover' : 'Lover',
                   'Red (Deluxe Edition)' : 'Red',
                   'Speak Now (Deluxe Edition)' : 'Speak Now',
                   'THE TORTURED POETS DEPARTMENT: THE ANTHOLOGY' : 'The Tortured Poets Department',
                   'Taylor Swift' : 'Taylor Swift',
                   'evermore (deluxe version)' : 'Everore',
                   'folklore (deluxe version)' : 'Folklore',
                   'reputation' : 'Reputation'}

nombres_categorias = {'acousticness' : 'acústico',
                      'danceability' : 'danzabilidad',
                      'energy' : 'energía',
                      'instrumentalness' : 'instrumental',
                      'liveness' : 'directo',
                      'loudness' : 'volumen',
                      'speechiness' : 'liricismo',
                      'tempo' : 'tempo',
                      'valence' : 'positividad'                      
                      }

melted_df['album'] = melted_df['album'].apply(lambda x: nombres_albumes.get(x, x))
melted_df['categoria'] = melted_df['categoria'].apply(lambda x: nombres_categorias.get(x, x))

melted_df.to_csv('files/all_songs_audio_data_radar.csv', index = False)

#%%
# RECONOCIMIENTOS --------------------------------------------------------------------------------------------------------
from src import wiki_scrap as ws
import pandas as pd

df = ws.get_rewards('https://en.wikipedia.org/wiki/List_of_awards_and_nominations_received_by_Taylor_Swift')

df = pd.DataFrame(df)

df['Type'] = df.apply(lambda x : 'Canción' if '"' in x['Recipient'] else ('Artista' if x['Recipient'] == 'Swift' else 'Álbum'), axis=1)

df['Award'] = df['Award'].apply(lambda x : x.strip())

df.to_csv('files/awards_info.csv')

#%%
# ORDEN_CANCIONES --------------------------------------------------------------------------------------------------------
import pandas as pd
import numpy as np
df = pd.read_csv('files/taylor_full_lyrics_w_genre.csv')

diccionario_tracks = {'Taylor Swift': ['01. Tim McGraw',
'02. Picture to Burn',
'03. Teardrops On My Guitar',
'04. A Place In This World',
'05. Cold as You',
'06. The Outside',
'07. Tied Together with a Smile',
'08. Stay Beautiful',
'09. Should’ve Said No',
'10. Mary’s Song (Oh My My My)',
'11. Our Song',
'12. I’m Only Me When I’m With You',
'13. Invisible',
'14. A Perfectly Good Heart',
'15. Teardrops on My Guitar (Pop Version)'],
                'Fearless': ["01. Fearless",
                                "02. Fifteen",
                                "03. Love Story",
                                "04. Hey Stephen",
                                "05. White Horse",
                                "06. You Belong with Me",
                                "07. Breathe",
                                "08. Tell Me Why",
                                "09. You're Not Sorry",
                                "10. The Way I Loved You",
                                "11. Forever & Always",
                                "12. The Best Day",
                                "13. Change"],
                'Speak Now':["01. Mine",
                                "02. Sparks Fly",
                                "03. Back to December",
                                "04. Speak Now",
                                "05. Dear John",
                                "06. Mean",
                                "07. The Story of Us",
                                "08. Never Grow Up",
                                "09. Enchanted",
                                "10. Better Than Revenge",
                                "11. Innocent",
                                "12. Haunted",
                                "13. Last Kiss",
                                "14. Long Live"],
                'Red': ["01. State of Grace",
                            "02. Red", "Treacherous",
                            "03. I Knew You Were Trouble",
                            "04. All Too Well",
                            "05. 22",
                            "06. I Almost Do",
                            "07. We Are Never Ever Getting Back Together",
                            "08. Stay Stay Stay",
                            "09. The Last Time",
                            "10. Holy Ground",
                            "11. Sad Beautiful Tragic",
                            "12. The Lucky One",
                            "13. Everything Has Changed",
                            "14. Starlight",
                            "15. Begin Again",
                            "16. The Moment I Knew",
                            "17. Come Back... Be Here",
                            "18. Girl at Home"],
                '1989':["01. Welcome to New York",
                            "02. Blank Space",
                            "03. Style",
                            "04. Out of the Woods",
                            "05. All You Had to Do Was Stay",
                            "06. Shake It Off",
                            "07. I Wish You Would",
                            "08. Bad Blood",
                            "09. Wildest Dreams",
                            "10. How You Get the Girl",
                            "11. This Love",
                            "12. I Know Places",
                            "13. Clean",
                            "14. Wonderland",
                            "16. You Are in Love",
                            "17. New Romantics"],
                'Reputation':["01. …Ready for It?",
                              "02. End Game",
                              "03. I Did Something Bad",
                              "04. Don't Blame Me",
                              "05. Delicate",
                              "06. Look What You Made Me Do",
                              "07. So It Goes...",
                              "08. Gorgeous",
                              "09. Gorgeous",
                              "10. Getaway Car",
                              "11. King of My Heart",
                              "12. Dancing with Our Hands Tied",
                              "13. Dress",
                              "14. This Is Why We Can't Have Nice Things",
                              "15. Call It What You Want",
                              "16. New Year's Day"],
                'Lover': ["01. I Forgot That You Existed",
                            "02. Cruel Summer",
                            "03. Lover",
                            "04. The Man",
                            "05. The Archer",
                            "06. I Think He Knows",
                            "07. Miss Americana & The Heartbreak Prince",
                            "08. Paper Rings",
                            "09. Cornelia Street",
                            "10. Death By A Thousand Cuts",
                            "11. London Boy",
                            "12. Soon You’ll Get Better",
                            "13. False God",
                            "14. You Need To Calm Down",
                            "15. Afterglow",
                            "16. ME!",
                            "17. It’s Nice To Have A Friend",
                            "18. Daylight"],
                'Folklore': ["01. the 1",
                            "02. cardigan",
                            "03. the last great american dynasty",
                            "04. exile",
                            "05. my tears ricochet",
                            "06. mirrorball",
                            "07. seven",
                            "08. august",
                            "09. this is me trying",
                            "10. illicit affairs",
                            "11. invisible string",
                            "12. mad woman",
                            "13. epiphany",
                            "14. betty",
                            "15. peace",
                            "16. hoax"],
                'Evermore': ["01. willow",
                            "02. champagne problems",
                            "03. gold rush",
                            "04. ’tis the damn season",
                            "05. tolerate it",
                            "06. no body, no crime",
                            "07. happiness",
                            "08. dorothea",
                            "09. coney island",
                            "10. ivy",
                            "11. cowboy like me",
                            "12. l​ong story short",
                            "13. marjorie",
                            "14. closure",
                            "15. evermore"],
                'Midnights': ["01. Lavender Haze",
                            "02. Maroon",
                            "03. Anti-Hero",
                            "04. Snow On The Beach",
                            "05. You’re On Your Own, Kid",
                            "06. Midnight Rain",
                            "07. Question...?",
                            "09. Vigilante Shit",
                            "10. Bejeweled",
                            "11. Labyrinth",
                            "12. Karma",
                            "13. Sweet Nothing",
                            "14. Mastermind",
                            "15. The Great War",
                            "16. Bigger Than The Whole Sky",
                            "17. Paris",
                            "18. High Infidelity",
                            "19. Glitch",
                            "20. Would’ve, Could’ve, Should’ve",
                            "21. Dear Reader"],
                'The Tortured Poets Department': ["01. Fortnight",
                            "02. The Tortured Poets Department",
                            "03. My Boy Only Breaks His Favorite Toys",
                            "04. Down Bad",
                            "05. So Long, London",
                            "06. But Daddy I Love Him",
                            "07. Fresh Out The Slammer",
                            "08. Florida!!!",
                            "09. Guilty as Sin?",
                            "10. Who’s Afraid of Little Old Me?",
                            "11. I Can Fix Him (No Really I Can)",
                            "12. loml",
                            "13. I Can Do It With A Broken Heart",
                            "14. The Smallest Man Who Ever Lived",
                            "15. The Alchemy",
                            "16. Clara Bow",
                            "17. The Black Dog",
                            "18. ​​imgonnagetyouback",
                            "19. The Albatross",
                            "20. Chloe or Sam or Sophia or Marcus",
                            "21. How Did It End?",
                            "22. So High School",
                            "23. I Hate It Here",
                            "24. ​​thanK you aIMee",
                            "25. I Look in People’s Windows",
                            "26. The Prophecy",
                            "27. Cassandra",
                            "28. Peter",
                            "29. The Bolter",
                            "30. Robin",
                            "31. The Manuscript"]}

df_album_indice = pd.DataFrame(diccionario_tracks.items(), columns=['Album', 'Song'])
df_album_indice = df_album_indice.explode('Song')
df_album_indice['Order'] = range(1, len(df_album_indice) + 1)

df_album_indice.to_csv('files/album_tracks_order.csv', index=False)

df = pd.read_csv('files/album_tracks_order.csv')

def songs_to(valor):
    if 'Forever & Always' in valor or 'Last Kiss' in valor or 'invisible string' in valor or 'Better Than Revenge' in valor or "Holy Ground" in valor:
        return 'Joe Jonas'
    elif 'Back to December' in valor:
        return 'Taylor Lautner'
    elif 'Dear John' in valor or "Ours" in valor or "Superman" in valor or "The Story of Us" in valor or 'Would’ve, Could’ve, Should’ve' in valor:
        return 'John Mayer'
    elif "We Are Never Ever Getting Back Together" in valor or "I Almost Do" in valor or "State of Grace" in valor or "All Too Well" in valor or "I Bet You Think About Me" in valor or "I Knew You Were Trouble" in valor:
        return 'Jake Gyllenhaal'
    elif "Out of the Woods" in valor or "Clean" in valor or "Style" in valor or "Is It Over Now?" in valor:
        return 'Harry Styles'
    elif "Getaway Car" in valor:
        return 'Tom Hiddleston'
    elif "High Infidelity" in valor:
        return "Calvin Harris"
    elif "...Ready For It?" in valor or "Mastermind" in valor or "End Game" in valor or "Delicate" in valor or "King of My Heart" in valor or "Dress" in valor or "Call It What You Want" in valor or "New Year's Day" in valor or "Lover" in valor or "Cruel Summer" in valor or "I Think He Knows" in valor or "Paper Rings" in valor or "Cornelia Street" in valor or "London Boy" in valor:
        return 'Joe Alwyn'
    elif 'This Is Why We' in valor or 'Innocent' in valor or 'I Forgot That' in valor or 'mad woman' in valor or 'Look What You' in valor:
        return 'Kanye West'
    else:
        return None
    
df['Target'] = df['Song'].apply(songs_to)

df.to_csv('files/album_tracks_order.csv')

def lyrics_songs(valor):
    if 'Forever & Always' in valor:
        return "And I stare at the phone, he still hasn't called"

    elif 'Last Kiss' in valor:
        return "That July ninth, the beat of your heart"

    elif 'invisible string' in valor:
        return "Now I send their babies presents"

    elif 'Better Than Revenge' in valor:
        return "I had it all I had him right there where I wanted him"
    
    elif "Holy Ground" in valor:
        return "And I guess we fell apart in the usual way"
    
    elif 'Back to December' in valor:
        return "I miss your tan skin, your sweet smile"
    
    elif 'Dear John' in valor:
        return "Dear John, I see it all now that you're gone"
    
    elif "Ours" in valor:
        return "They'll judge it like they know about me and you"
    
    elif "Superman" in valor:
        return "Tall, dark, and Superman. He puts papers in his briefcase and drives away"
    
    elif "The Story of Us" in valor:
        return "And the story of us looks a lot like a tragedy now"
    
    elif "I Knew You Were Trouble" in valor:
        return "I guess you didn't care and I guess I liked that"
    
    elif 'Would’ve, Could’ve, Should’ve' in valor:
        return "Give me back my girlhood, it was mine first"
    
    elif "We Are Never Ever Getting Back Together" in valor:
        return "Talk to my friends, talk to me (talk to me), but we are never, ever, ever, ever getting back together"
    
    elif "I Almost Do" in valor:
        return "And I just wanna tell you it takes everything in me not to call you"
    
    elif "State of Grace" in valor:
        return "Love is a ruthless game unless you play it good and right"

    elif "All Too Well" in valor:
        return "And I, left my scarf there at your sister's house and you've still got it in your drawer even now"

    elif "I Bet You Think About Me" in valor:
        return "Does it make you feel sad that the love that you're lookin' for is the love that you had"
    
    elif "Out of the Woods" in valor:
        return "Remember when you hit the brakes too soon? Twenty stitches in a hospital room"
    
    elif "Clean" in valor or "Style" in valor:
        return "Ten months older, I won't give in. Now that I'm clean, I'm never gonna risk it"
  
    elif "Getaway Car" in valor:
        return "It's no surprise I turned you in 'cause us traitors never win"
    
    elif "High Infidelity" in valor:
        return "You know there's many different ways that you can kill the one you love. The slowest way is never loving them enough"
    
    elif "...Ready For It?" in valor:
        return "Knew I was a robber first time that he saw me stealing hearts and running off and never saying sorry"
   
    elif "Mastermind" in valor:
        return "What if I told you none of it was accidental dnd the first night that you saw me, nothing was gonna stop me?"
    
    elif "End Game" in valor:
        return "Big reputation, big reputation, oh, you and me, we got big reputations, and you heard about me"
    
    elif "Delicate" in valor:
        return "My reputation's never been worse, so you must like me for me"
    
    elif "King of My Heart" in valor:
        return "Is this the end of all the endings? My broken bones are mending"
    
    elif "Dress" in valor:
        return "Say my name and everything just stops, I don't want you like a best friend"

    elif "Call It What You Want" in valor:
        return "All the liars are calling me one, nobody's heard from me for months. I'm doing better than I ever was 'cause my baby's fit like a daydream"
    
    elif "New Year's Day" in valor:
        return "Please don't ever become a stranger whose laugh I could recognize anywhere"

    elif "Lover" in valor:
        return "I've loved you three summers now, honey, but I want 'em all"

    elif "Cruel Summer" in valor:
        return "I don't wanna keep secrets just to keep you. And I snuck in through the garden gate every night that summer just to seal my fate"
    
    elif "I Think He Knows" in valor:
        return "I am an architect, I'm drawing up the plans"

    elif "Paper Rings" in valor:
        return "I like shiny things, but I'd marry you with paper rings"

    elif "Cornelia Street" in valor:
        return "And I hope I never lose you, hope it never ends. I'd never walk Cornelia Street again"
    
    elif "London Boy" in valor:
        return 'And now I love high tea, stories from uni, and the West End'
    
    elif 'This Is Why We' in valor:
        return "And therein lies the issue, friends don't try to trick you, get you on the phone and mind-twist you"

    elif 'Innocent' in valor:
        return "It's okay, life is a tough crowd, thirty-two and still growin' up now"
    
    elif 'I Forgot That' in valor:
        return "I forgot that you existed. It isn't love, it isn't hate, it's just indifference"
    
    elif 'mad woman' in valor:
        return "I'm takin' my time, takin' my time 'cause you took everything from me"
    
    elif 'Look What You' in valor:
        return "I don't like your little games, don't like your tilted stage, the role you made me play"
    
    else:
        return None
    
df['Lyric'] = df['Song'].apply(lyrics_songs)

df.to_csv('files/album_tracks_order.csv')

diccionario_tracks_col2 = {'Taylor Swift': ['01. Tim McGraw',
'02. Picture to Burn',
'03. Teardrops On My Guitar',
'04. A Place In This World',
'05. Cold as You',
'06. The Outside',
'07. Tied Together with a Smile',
'08. Stay Beautiful',
'09. Should’ve Said No',
'10. Mary’s Song (Oh My My My)',
'11. Our Song',
'12. I’m Only Me When I’m With You',
'13. Invisible',
'14. A Perfectly Good Heart',
'15. Teardrops on My Guitar (Pop Version)'],
                'Fearless': ["01. Fearless",
                                "02. Fifteen",
                                "03. Love Story",
                                "04. Hey Stephen",
                                "05. White Horse",
                                "06. You Belong with Me",
                                "07. Breathe",
                                "08. Tell Me Why",
                                "09. You're Not Sorry",
                                "10. The Way I Loved You",
                                "11. Forever & Always",
                                "12. The Best Day",
                                "13. Change"],
                'Speak Now':["01. Mine",
                                "02. Sparks Fly",
                                "03. Back to December",
                                "04. Speak Now",
                                "05. Dear John",
                                "06. Mean",
                                "07. The Story of Us",
                                "08. Never Grow Up",
                                "09. Enchanted",
                                "10. Better Than Revenge",
                                "11. Innocent",
                                "12. Haunted",
                                "13. Last Kiss",
                                "14. Long Live"],
                'Red': ["01. State of Grace",
                            "02. Red", "Treacherous",
                            "03. I Knew You Were Trouble",
                            "04. All Too Well",
                            "05. 22",
                            "06. I Almost Do",
                            "07. We Are Never Ever Getting Back Together",
                            "08. Stay Stay Stay",
                            "09. The Last Time",
                            "10. Holy Ground",
                            "11. Sad Beautiful Tragic",
                            "12. The Lucky One",
                            "13. Everything Has Changed",
                            "14. Starlight",
                            "15. Begin Again",
                            "16. The Moment I Knew",
                            "17. Come Back... Be Here",
                            "18. Girl at Home"],
                '1989':["01. Welcome to New York",
                            "02. Blank Space",
                            "03. Style",
                            "04. Out of the Woods",
                            "05. All You Had to Do Was Stay",
                            "06. Shake It Off",
                            "07. I Wish You Would",
                            "08. Bad Blood",
                            "09. Wildest Dreams",
                            "10. How You Get the Girl",
                            "11. This Love",
                            "12. I Know Places",
                            "13. Clean",
                            "14. Wonderland",
                            "16. You Are in Love",
                            "17. New Romantics"],
                'Reputation':["01. …Ready for It?",
                              "02. End Game",
                              "03. I Did Something Bad",
                              "04. Don't Blame Me",
                              "05. Delicate",
                              "06. Look What You Made Me Do",
                              "07. So It Goes...",
                              "08. Gorgeous",
                              "09. Gorgeous",
                              "10. Getaway Car",
                              "11. King of My Heart",
                              "12. Dancing with Our Hands Tied",
                              "13. Dress",
                              "14. This Is Why We Can't Have Nice Things",
                              "15. Call It What You Want",
                              "16. New Year's Day"],
                'Lover': ["01. I Forgot That You Existed",
                            "02. Cruel Summer",
                            "03. Lover",
                            "04. The Man",
                            "05. The Archer",
                            "06. I Think He Knows",
                            "07. Miss Americana & The Heartbreak Prince",
                            "08. Paper Rings",
                            "09. Cornelia Street",
                            "10. Death By A Thousand Cuts",
                            "11. London Boy",
                            "12. Soon You’ll Get Better",
                            "13. False God",
                            "14. You Need To Calm Down",
                            "15. Afterglow",
                            "16. ME!",
                            "17. It’s Nice To Have A Friend",
                            "18. Daylight"],
                'Folklore': ["01. the 1",
                            "02. cardigan",
                            "03. the last great american dynasty",
                            "04. exile",
                            "05. my tears ricochet",
                            "06. mirrorball",
                            "07. seven",
                            "08. august",
                            "09. this is me trying",
                            "10. illicit affairs",
                            "11. invisible string",
                            "12. mad woman",
                            "13. epiphany",
                            "14. betty",
                            "15. peace",
                            "16. hoax"],
                'Evermore': ["01. willow",
                            "02. champagne problems",
                            "03. gold rush",
                            "04. ’tis the damn season",
                            "05. tolerate it",
                            "06. no body, no crime",
                            "07. happiness",
                            "08. dorothea",
                            "09. coney island",
                            "10. ivy",
                            "11. cowboy like me",
                            "12. l​ong story short",
                            "13. marjorie",
                            "14. closure",
                            "15. evermore"],
                'Midnights': ["01. Lavender Haze",
                            "02. Maroon",
                            "03. Anti-Hero",
                            "04. Snow On The Beach",
                            "05. You’re On Your Own, Kid",
                            "06. Midnight Rain",
                            "07. Question...?",
                            "09. Vigilante Shit",
                            "10. Bejeweled",
                            "11. Labyrinth",
                            "12. Karma",
                            "13. Sweet Nothing",
                            "14. Mastermind",
                            "15. The Great War",
                            "16. Bigger Than The Whole Sky",
                            "17. Paris",
                            "18. High Infidelity",
                            "19. Glitch",
                            "20. Would’ve, Could’ve, Should’ve",
                            "21. Dear Reader"],
                'The Tortured Poets Department': ["01. Fortnight",
                            "02. The Tortured Poets Department",
                            "03. My Boy Only Breaks His Favorite Toys",
                            "04. Down Bad",
                            "05. So Long, London",
                            "06. But Daddy I Love Him",
                            "07. Fresh Out The Slammer",
                            "08. Florida!!!",
                            "09. Guilty as Sin?",
                            "10. Who’s Afraid of Little Old Me?",
                            "11. I Can Fix Him (No Really I Can)",
                            "12. loml",
                            "13. I Can Do It With A Broken Heart",
                            "14. The Smallest Man Who Ever Lived",
                            "15. The Alchemy",
                            "16. Clara Bow",
                            "17. The Black Dog",
                            "18. ​​imgonnagetyouback",
                            "19. The Albatross",
                            "20. Chloe or Sam or Sophia or Marcus",
                            "21. How Did It End?",
                            "22. So High School",
                            "23. I Hate It Here",
                            "24. ​​thanK you aIMee",
                            "25. I Look in People’s Windows",
                            "26. The Prophecy",
                            "27. Cassandra",
                            "28. Peter",
                            "29. The Bolter",
                            "30. Robin",
                            "31. The Manuscript"]}

import pandas as pd
import numpy as np

df = pd.read_csv('files/album_tracks_order.csv', index_col=0)

def no_digitos(cadena):
    return re.sub(r'^\d+\.\s*', '', cadena)

import re
df['Song_No_Number'] = df['Song'].apply(no_digitos)

df.to_csv('files/album_tracks_order.csv')