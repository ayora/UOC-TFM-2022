# APP

En esta carpeta contiene los ficheros de la aplicación web, desarrollada para mostrar una serie de indicadores. Estos indicadores se basan en la información extraida a partir de los tweets procesados en la parte de la ingesta:

- Top 10 de las cryptos más mencionadas y su polaridad.
- Top 10 de los hashtagas más usados y su polaridad.
- Top 10 de los usuarios de Twitter más activos con el número de seguidores.
- Nuevas cryptos aparecidas 

Todos estos indicadores se calculan a partir de un rango temporal que permite seleccionar la aplicación: 1 día, 7 días, 30 días, 1 año.


### Ejecución

Para desplegar la aplicación web, sería necesario crear un entorno virtual e instalar las librerías (fichero **dependencies.txt**).

```python
	python3 -m venv .venv
	
	source .venv/bin/activate

	pip install -r dependencies.txt
```

Un vez creado el entorno, en el fichero **cryptowebapp.cfg** se configura la conexión a la base de datos MongoDB y se levanta la aplicación con los siguientes comandos:

```python
	export FLASK_APP=home
	export FLASK_ENV=development

	flask run
```

El acceso a la aplicación se realizar mediante navegador en la url: <https://localhost:5000>