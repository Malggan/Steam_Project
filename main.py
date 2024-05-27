# Importaciones
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import virtualenv


df_developer = pd.read_parquet('Dataset/developer.parquet')
df_user_data_final = pd.read_parquet('Dataset/user_data.parquet')
df_user_genre = pd.read_parquet('Dataset/user_for_genre.parquet')
df_best_developer = pd.read_parquet('Dataset/developer_of_year.parquet')
df_developer_reviews = pd.read_parquet('Dataset/developer_review.parquet')
df_modelo_recomendacion = pd.read_parquet('Dataset/recomendar_juego.parquet')



def developer(desarrolladora):
    developer_filtrado = df_developer[df_developer['developer'] == desarrolladora]
    cantidad_anio = developer_filtrado.groupby('release_year')['item_id'].count()
    gratis_anio = (developer_filtrado[developer_filtrado['price'] == 0.0].groupby('release_year')['item_id'].count() / cantidad_anio * 100).fillna(0).astype(int)

    # Convertir los valores de las Series a listas
    cantidad_anio_list = cantidad_anio.tolist()
    gratis_anio_list = gratis_anio.tolist()

    # Convertir los índices a una lista
    anios_list = cantidad_anio.index.tolist()

    # Crear un diccionario con los resultados
    resultados = {
        'Año': anios_list,
        'Cantidad de juegos': cantidad_anio_list,
        '% juegos gratis': gratis_anio_list
    }

    return resultados



def user_data(usuario):
    user_filtrado = df_user_data_final[df_user_data_final['user_id'] == usuario]
    if not user_filtrado.empty:
        # Convertir los valores de NumPy a tipos nativos de Python usando int() y float()
        cantidad_dinero = int(user_filtrado['total_spent'].iloc[0])
        items_totales = int(user_filtrado['items_count'].iloc[0])
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
    df=pd.DataFrame(df_user_genre)
    
    # Filtrar por género
    df_genero = df[df['genres'] == genero]

    # Usuario con más horas jugadas por género
    usuario_mas_horas = df_genero.groupby('user_id')['playtime_forever'].sum().idxmax()
    usuario_mas_horas_df = df_genero[df_genero['user_id'] == usuario_mas_horas].iloc[0]

    # Filtrar por el usuario con más horas jugadas y calcular las horas jugadas por año de lanzamiento
    df_usuario_mas_horas = df_genero[df_genero['user_id'] == usuario_mas_horas]
    horas_por_anio = df_usuario_mas_horas.groupby('release_year')['playtime_forever'].sum().to_dict()

    return {"Usuario con más horas jugadas por género": usuario_mas_horas_df['user_id'], 
            "Género": usuario_mas_horas_df['genres'], 
            "Horas jugadas por año de lanzamiento" : horas_por_anio}



def best_developer_year(year):
    df = pd.DataFrame(df_best_developer)
    
    # Filtrar por año y recomendaciones True
    df_year = df[(df['release_year'] == year) & (df['recommend'] == True)]

    # Calcular la cantidad de recomendaciones por desarrollador
    developer_recommendations = df_year.groupby('developer')['recommend'].count().reset_index()

    # Ordenar en orden descendente y obtener el top 3
    top_developers = developer_recommendations.nlargest(3, 'recommend')

    # Crear la lista de resultados con los puestos y los desarrolladores
    resultado = [
        {"Puesto 1": top_developers.iloc[0]['developer'], "Recomendaciones": int(top_developers.iloc[0]['recommend'])},
        {"Puesto 2": top_developers.iloc[1]['developer'], "Recomendaciones": int(top_developers.iloc[1]['recommend'])},
        {"Puesto 3": top_developers.iloc[2]['developer'], "Recomendaciones": int(top_developers.iloc[2]['recommend'])},
    ]

    return resultado



def developer_reviews_analysis(developer):
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
    # Filtrar los juegos que coinciden con el nombre dado
    juego_filtrado = df_modelo_recomendacion[df_modelo_recomendacion['item_id'] == id_producto]

    # Obtener los géneros del juego dado
    genero_juego = set(juego_filtrado['genres'].str.split(',').explode())

    # Filtrar los juegos que tienen al menos 1 género en común con el juego dado
    juegos_recomendados = df_modelo_recomendacion[df_modelo_recomendacion['genres'].apply(lambda x: len(set(x.split(',')).intersection(genero_juego)) >= 1)]

    # Calcular la similitud del coseno entre los vectores de géneros de los juegos
    juegos_recomendados['genres_vector'] = juegos_recomendados['genres'].apply(lambda x: np.array([1 if genre in x else 0 for genre in genero_juego]))
    juego_filtrado['genres_vector'] = juego_filtrado['genres'].apply(lambda x: np.array([1 if genre in x else 0 for genre in genero_juego]))
    juegos_recomendados['similarity'] = juegos_recomendados.apply(lambda row: cosine_similarity([row['genres_vector']], [juego_filtrado['genres_vector'].iloc[0]])[0][0], axis=1)

    # Ordenar los juegos por similitud y recomendación en orden descendente
    juegos_recomendados = juegos_recomendados.sort_values(['similarity', 'recommend_y'], ascending=[False, False])

    # Seleccionar los 5 juegos con mayor similitud y recomendación
    top_juegos_recomendados = juegos_recomendados.head(5)

    # Obtener la lista de nombres de los juegos recomendados junto con el desarrollador
    juegos_recomendados_dict = {}
    juegos_recomendados_dict['Debido a que te gustó ' + juego_filtrado['title'].iloc[0] + ', también podría interesarte...'] = top_juegos_recomendados[['title']].to_dict(orient='records')

    return juegos_recomendados_dict


# Se instancia la aplicación
app = FastAPI()

# Funciones
@app.get(path="/", 
         response_class=HTMLResponse,
         tags=["Home"])
def home():
    return


@app.get(path = '/develop')
def develop(desarrollador: str):
    return developer(desarrollador)


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