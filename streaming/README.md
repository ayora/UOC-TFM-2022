# STREAMING

En esta carpeta se encuentran los scripts desarrollados para la ingesta de tweets desde la API de Twitter a la base de datos MongoDB. 

- **tweepy_to_mongo_extract.py**:

- **tweepy_to_mongo_transform.py**:

- **stream.cfg**: fichero de configuración con los parámetros necesario para las conexiones, tanto del API de Twitter como de la base de datos MongoDB.

- **dependencies.txt**: contiene el listado de las dependencias para instalar en un virtualenv y ejecutar los scripts.

### Ejecución

Para llevar a cabo la ingesta de tweets será necesario ejecutar los dos scripts:

```python
	python3 -m venv .venv
	
	source .venv/bin/activate

	pip install -r dependencies.txt
```

```python
	python tweepy_to_mongo_extract.py

	python tweepy_to_mongo_transform.py
```

El primero leerá 3.000 tweets relacionados con la criptomoneda Bitcoin ($BTC) a través de la librería **Tweepy**, quedándose con aquellos campos de cada tweet que se consideran indispensables (fecha de creación, usuario, seguidores, texto del tweet, etc.), para posteriormente guardarlos en una colección en MongoDB.

El segundo script procesará los tweets almacenados, realizando sobre cada uno de ellos una serie de transformaciones:

- Extracción de los hashtags
- Extracción de las criptos mencionadas
- Limpieza del texto y aplicación de análisis de sentimientos mediante la librería **TextBlob**