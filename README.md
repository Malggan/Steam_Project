
# Proyecto Steam Project 


<br>

## Índice

* [Propuesta y Objetivos](#propuesta-y-objetivos)

* [Datos](#datos)

* [ETL](#etl)

* [Feature engineering](#feature-engineering)

* [EDA](#bar_chart-eda)

* [Modelo de Recomendación](#robot-modelo-de-recomendación)

* [Desarrollo de API](#desarrollo-de-api)

* [Deployment](#deployment)


<br>

## Propuesta y Objetivos

Objetivos del Proyecto:
* Desarrollar un sistema de recomendación de videojuegos altamente efectivo para los usuarios de Steam.

* Evaluar la calidad y madurez de los datos disponibles, identificando áreas de mejora y definición de estrategias para su enriquecimiento.
* Diseñar y construir pipelines de datos robustos que permitan la extracción, transformación y carga eficiente de datos.
* Colaborar estrechamente con el equipo de Data Science en la implementación de modelos de Machine Learning para la recomendación de videojuegos.
Entregar un MVP funcional y escalable dentro de los plazos establecidos, demostrando el valor de la solución propuesta.

<br>

## Datos

Los 3 DataSets proporcionados son:

* **steam_games.json** 

* **australian_user_reviews.json** 

* **australian_users_items.json** 


La información detallada se encuentra en el [Diccionario de datos](https://github.com/Malggan/Steam_Project/blob/8895e9e858d85441a3e4bc8c1f916398ee175b0f/Diccionario%20de%20Datos%20STEAM.xlsx).

<br>

## ETL

Se realizó la extracción, transformación y carga (ETL) de los tres conjuntos de datos entregados. Dos de los conjuntos de datos se encontraban anidados, es decir había columnas con diccionarios o listas de diccionarios, por lo que aplicaron distintas estrategias para transformar las claves de esos diccionarios en columnas. Luego se rellenaron algunos nulos de variables necesarias para el proyecto, se borraron columnas con muchos nulos o que no eran necesarias para el proyecto, para optimizar el rendimiento de la API y teneniendo en cuenta las limitaciones de almacenamiento del deploy.

Los detalles del ETL se puede ver en: 
+ [ETL steam_games](https://github.com/Malggan/Steam_Project/blob/8895e9e858d85441a3e4bc8c1f916398ee175b0f/ETL/Steam_games_ETL.ipynb) 
+ [ETL australian_users_items](https://github.com/Malggan/Steam_Project/blob/8895e9e858d85441a3e4bc8c1f916398ee175b0f/ETL/users_items_ETL.ipynb)  
+ [ETL australian_user_reviews](https://github.com/Malggan/Steam_Project/blob/8895e9e858d85441a3e4bc8c1f916398ee175b0f/ETL/user_reviews_ETL.ipynb).

<br>

## Feature engineering

Uno de los requisitos para este proyecto fue aplicar un análisis de sentimiento a los reviews de los usuarios. Para ello se creó una nueva columna llamada 'sentiment_analysis' que reemplaza a la columna que contiene los reviews donde clasifica los sentimientos de los comentarios con la siguiente escala:

* 0  malo,
* 1  neutral o está sin review
* 2  positivo.


<br>

## :bar_chart: EDA

Se realizó el EDA a los tres conjuntos de datos sometidos a ETL con el objetivo de identificar las variables que se pueden utilizar en la creación del modelo de recmendación. Para ello se utilizó la librería Pandas para la manipulación de los datos y las librerías Matplotlib y Seaborn para la visualización de los graficos.

<br>

<p align="center">
<img src="https://github.com/Malggan/Steam_Project/blob/3bdfc2420404727a2847f64531ea3178917e22c1/images/Juegos%20x%20genero.jpg" alt="imagen de gráfico" width="800" height="400">
</p>
<p align="center">
<i>Gráfico de barras cantidad de juegos por género.</i>
</p>

<br>

En particular para el modelo de recomendación, se terminó eligiendo construir un dataframe específico con el id del usuario que realizaron reviews y los nombres de los juegos a los cuales se le realizaron comentarios.

El desarrollo de este análisis se encuentra en: 
+ [EDA](https://github.com/Malggan/Steam_Project/blob/3bdfc2420404727a2847f64531ea3178917e22c1/EDA.ipynb)

<br>

## :robot: Modelo de recomendación

Se creaó el modelo de recomendación, que generan una lista de 5 juegos ingresando el id_producto.

El modelo tiene una relación ítem-ítem. Se toma un juego y en base a que tan similar es ese juego con el resto de los juegos se recomiendan similares. Para ello, se aplicaron filtro previos a aplicar la **similitud del coseno**, tales como que los juegos potencialmente recomendados debían compartir al menos una categoría de genero con el item_id ingresado para la consulta. Esto generaba una lista de 10 productos recomendados, luego de aplicar el filtro de género y la similitud del coseno, lista de la cual se seleccionaban los 5 juegos con mayor porcentaje de recomendación por el usuario.

<br>

<p align="center">
<img src="https://github.com/Malggan/Steam_Project/blob/3bdfc2420404727a2847f64531ea3178917e22c1/images/recomend.jpg?raw=true" alt="imagen modelo de recomendacón" width="1000" height="300">
</p>
<p align="center">
<i>Función de modelo de recomendación.</i>
</p>

<br>

La **similitud del coseno** que es una medida comúnmente utilizada para evaluar la similitud entre dos vectores en un espacio multidimensional. En el contexto de sistemas de recomendación y análisis de datos, la similitud del coseno se utiliza para determinar cuán similares son dos conjuntos de datos o elementos, y se calcula utilizando el coseno del ángulo entre los vectores que representan esos datos o elementos.

<br>

## Desarrollo de API

Para el desarrolo de la API se decidió utilizar el framework FastAPI, creando las siguientes funciones:

* **developer**: Esta función recibe como parámetro 'developer', que es la empresa desarrolladora del juego, y devuelve la cantidad de items que desarrolla dicha empresa y el porcentaje de contenido Free por año por sobre el total que desarrolla.

* **user_data**: Esta función tiene por parámentro 'user_id' y devulve la cantidad de dinero gastado por el usuario, el porcentaje de recomendaciones que realizó sobre la cantidad de reviews que se analizan y la cantidad de items que posee en su biblioteca de juegos.

* **user_for_genre**: Esta función recibe como parámetro el género de un videojuego y devuelve el usuario con más horas de juego en el género ingresado, y una lista de acumulación de horas jugadas por año.

* **best_developer_year**: En esta función se ingresa un año como parámetro y devuelve el top 3 de desarrolladoras con mas recomendaciones positivas por usuarios, para ese año dado.

* **developer_review_analysis**: Esta función recibe como parámetro una desarrolladora y devuelve un diccionario con la cantidad de reviews positivas y reviews negativas hechas por los usuarios, para esa desarrolladora.

* **recomendacion_juego**: Esta función recibe como parámetro el id de un juego y devuelve una lista con 5 juegos recomendados similares al ingresado.

<br>

<p align="center">
<img src="https://github.com/Malggan/Steam_Project/blob/3bdfc2420404727a2847f64531ea3178917e22c1/images/Fastapi.jpg?raw=true" alt="fastapi" width="700" height="380">
</p>
<p align="center">
<i>Funciones en fastAPI en Render</i>
</p>

<br>

El desarrollo de las funciones de consultas generales se puede ver en: [main.py](https://github.com/Malggan/Steam_Project/blob/3bdfc2420404727a2847f64531ea3178917e22c1/main.py).

<br>

## Deployment

Para el deploy de la API se decidió crear un nuevo repositorio [repo_render](https://github.com/SebitaElGordito/PI_render). que contara solo con las funciones a consumir en la API, liberandonos de las carpetas o jupiters notebooks innecesarios y desplegandolo a partir de nuestro repositorio en GitHub. 
- Se generó un servicio nuevo  en `render.com`, conectado al presente repositorio.
- El servicio queda corriendo en [https://steam-project-p66a.onrender.com](https://steam-project-p66a.onrender.com/docs).
