from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import dask.dataframe as dd

app = FastAPI()

def load_developer_data():
    return pd.read_parquet('Dataset/developer.parquet')

def load_user_data_final():
    return pd.read_parquet('Dataset/user_data.parquet')

def load_user_genre():
    return pd.read_parquet('Dataset/user_for_genre.parquet')

def load_best_developer():
    return pd.read_parquet('Dataset/developer_of_year.parquet')

def load_developer_reviews():
    return pd.read_parquet('Dataset/developer_review.parquet')

def load_modelo_recomendacion():
    return pd.read_parquet('Dataset/recomendar_juego.parquet')


def developer(desarrolladora):
    df_developer = load_developer_data()
    developer_filtrado = df_developer[df_developer['developer'] == desarrolladora]
    cantidad_anio = developer_filtrado.groupby('release_year')['item_id'].count()
    gratis_anio = (developer_filtrado[developer_filtrado['price'] == 0.0].groupby('release_year')['item_id'].count() / cantidad_anio * 100).fillna(0).astype(int)

    cantidad_anio_list = cantidad_anio.tolist()
    gratis_anio_list = gratis_anio.tolist()
    anios_list = cantidad_anio.index.tolist()

    resultados = {
        'Año': anios_list,
        'Cantidad de juegos': cantidad_anio_list,
        '% juegos gratis': gratis_anio_list
    }

    return resultados


def user_data(usuario):
    df_user_data_final = load_user_data_final()
    user_filtrado = df_user_data_final[df_user_data_final['user_id'] == usuario]
    if not user_filtrado.empty:
        cantidad_dinero = int(user_filtrado['total_spent'].iloc[0])
        items_totales = int(user_filtrado['item_count'].iloc[0])
        total_recomendaciones = float(user_filtrado['recommend'].iloc[0])

        return {
            'Usuario': usuario, 
            'Cantidad de dinero gastado': cantidad_dinero, 
            'Porcentaje de recomendación': total_recomendaciones, 
            'Items totales en biblioteca': items_totales
        }
    else:
        return {'Error': 'Usuario no encontrado'}


def user_for_genre(genero):
    df_user_genre = load_user_genre()
    df_genero = df_user_genre[df_user_genre['genres'] == genero]

    usuario_mas_horas = df_genero.groupby('user_id')['playtime_forever'].sum().idxmax()
    usuario_mas_horas_df = df_genero[df_genero['user_id'] == usuario_mas_horas].iloc[0]

    df_usuario_mas_horas = df_genero[df_genero['user_id'] == usuario_mas_horas]
    horas_por_anio = df_usuario_mas_horas.groupby('release_year')['playtime_forever'].sum().to_dict()

    return {
        "Usuario con más horas jugadas por género": usuario_mas_horas_df['user_id'], 
        "Género": usuario_mas_horas_df['genres'], 
        "Horas jugadas por año de lanzamiento": horas_por_anio
    }


def best_developer_year(year):
    df_best_developer = load_best_developer()
    df_year = df_best_developer[(df_best_developer['release_year'] == year) & (df_best_developer['recommend'] == True)]

    developer_recommendations = df_year.groupby('developer')['recommend'].count().reset_index()
    top_developers = developer_recommendations.nlargest(3, 'recommend')

    resultado = []
    for i in range(min(3, len(top_developers))):
        resultado.append({
            f"Puesto {i + 1}": top_developers.iloc[i]['developer'],
            "Recomendaciones": int(top_developers.iloc[i]['recommend'])
        })

    while len(resultado) < 3:
        resultado.append({
            f"Puesto {len(resultado) + 1}": 'N/A',
            "Recomendaciones": 0
        })

    return resultado


def developer_reviews_analysis(developer):
    df_developer_reviews = load_developer_reviews()
    df_filtrado = df_developer_reviews[df_developer_reviews['developer'] == developer]

    cantidad_positivos = df_filtrado[df_filtrado['sentiment_analysis'] == 2].shape[0]
    cantidad_negativos = df_filtrado[df_filtrado['sentiment_analysis'] == 0].shape[0]

    resultado = {
        "Desarrolladora": developer,
        "Análisis de sentimiento": {
            "Positivos": cantidad_positivos,
            "Negativos": cantidad_negativos
        }
    }

    return resultado


def recomendacion_juego(id_producto):
    df_modelo_recomendacion = load_modelo_recomendacion()
    juego_filtrado = df_modelo_recomendacion[df_modelo_recomendacion['item_id'] == id_producto]

    if juego_filtrado.empty:
        return {'Error': 'Producto no encontrado'}

    genero_juego = set(juego_filtrado['genres'].str.split(',').explode())
    juegos_recomendados = df_modelo_recomendacion[df_modelo_recomendacion['genres'].apply(lambda x: len(set(x.split(',')).intersection(genero_juego)) >= 1)]

    juego_filtrado_vector = np.array([1 if genre in juego_filtrado['genres'].iloc[0] else 0 for genre in genero_juego], dtype=np.float64)
    juegos_recomendados['similarity'] = juegos_recomendados['genres'].apply(lambda x: cosine_similarity([juego_filtrado_vector], [np.array([1 if genre in x else 0 for genre in genero_juego], dtype=np.float64)])[0][0])

    juegos_recomendados = juegos_recomendados.sort_values(['similarity', 'recommend_y'], ascending=[False, False])
    top_juegos_recomendados = juegos_recomendados.head(5)

    juegos_recomendados_dict = {'Debido a que te gustó ' + juego_filtrado['title'].iloc[0] + ', también podría interesarte...': top_juegos_recomendados[['title']].to_dict(orient='records')}

    return juegos_recomendados_dict


@app.get(path="/", response_class=HTMLResponse, tags=["Home"])
def home():
    return "<h1>Bienvenido a la API de Steam</h1>"


@app.get(path='/develop')
def develop(desarrollador: str):
    return developer(desarroll



@app.get('/userdata')
def userdata(usuario: str):
    return user_data(usuario)
    

@app.get(path = '/userforgenre')
def userforgenre(genero: str):
    return user_for_genre(genero)

    
@app.get(path = '/bestdeveloperyear')
def bestdeveloperyear(year: int):
    return best_developer_year(year)


@app.get('/developerreviewsanalisis')
def developerreviewsanalysis(developer: str):
    return developer_reviews_analysis(developer)


@app.get('/recomendacionjuego')
def recomendacionjuego(id_producto: int):
    return recomendacion_juego(id_producto)


