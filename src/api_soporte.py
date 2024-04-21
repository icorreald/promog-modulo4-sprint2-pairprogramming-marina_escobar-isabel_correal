#%%
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
# %%
import os
from dotenv import load_dotenv
load_dotenv('src/.env')
# %%

# CREDENCIALES
def credenciales():
    client_id = os.getenv('client_id')
    client_secret = os.getenv('client_secret')

    credenciales = SpotifyClientCredentials(client_id, client_secret)
    sp = spotipy.Spotify(client_credentials_manager=credenciales)

    return sp
# %%

# URI
def url_acortada(link):
    return link.split('/')[-1].split('?')[0]

def lista_uris(lista_origen, lista_salida):
    for playlist in lista_origen:
        uri = url_acortada(playlist)
        lista_salida.append(uri)
    
    return lista_salida

# %%

# EXTRAER CANCIONES
def extraer_canciones(conexion, playlist_URI):
    n_canciones = conexion.playlist_tracks(playlist_URI)['total']
    n_canciones = int(str(n_canciones + 100)[0])

    offset_api = 0
    all_data = []

    for _ in range(n_canciones):
        resultados_it = conexion.playlist_tracks(playlist_URI, offset=offset_api)['items']
        all_data.extend(resultados_it)
        offset_api += 100
    
    return all_data

#%%
def limpiar_datos(lista_canciones):
    basic_info= {'song': [], 
             'artist': [], 
             'date': [],
             'explicit': [],
             'uri': [],
             'popularity': [],
             'user': [],
             'links': [],
             'duration': []}
    for cancion in lista_canciones:
        basic_info['song'].append(cancion['track']['name'])
        basic_info['date'].append(cancion['added_at'])
        basic_info['explicit'].append(cancion['track']['explicit'])
        basic_info['uri'].append(cancion['track']['uri'])
        basic_info['popularity'].append(cancion['track']['popularity'])
        basic_info['user'].append(cancion['added_by']['id'])
        basic_info['links'].append(cancion['track']['external_urls']['spotify'])
        basic_info['duration'].append(cancion['track']['duration_ms'])

        lista_artistas = []
        for artista in cancion['track']['artists']:
            lista_artistas.append(artista['name'])
        basic_info['artist'].append(lista_artistas)

    df = pd.DataFrame(basic_info)
    df.to_csv('csv-archivos/canciones_spotify.csv')

    return df