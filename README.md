# Proyecto #1 - Base de Datos 2 - Motor de Recomendación

## Requerimientos:

Crea un venv con el comando: `python -m venv venv`

Luego lo activas: `.\venv\Scripts\Activate.ps1`

Deberás instalar:
- `streamlit`
- `requests`
- `python-dotenv`
- `neo4j==5.27.0`
- `uvicorn`
- `fastapi`
- `pandas`

Una vez instaladas las librerías deberás crear tu `.env` fuera de la carpeta `src`, con la siguiente estructura:

```
NEO4J_URI=neo4j+ssc://<URI>
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<NEO4J_PASSWORD>
AURA_INSTANCEID=<AURA_INSTANCE_ID>
AURA_INSTANCENAME=<INSTANCE_NAME>
API_BASE_URL=http://127.0.0.1
API_PORT=8000
```

## ¿Cómo utilizar?

Deberás levantar en 2 terminales el backend y el frontend:

### Frontend:
Ve a la carpeta de `src/frontend` y corre: `streamlit run .\1_🏠_Inicio.py`

### Backend:
Ve a la carpeta de `src/backend` y corre: `uvicorn main:app --reload`

## Funcionalidades:


1.  [Crear nodo con 1 label](https://youtu.be/hwBeFFI36cI)

2.  [Crear nodo con propiedades (>=5)](https://youtu.be/Trdw8MNSzEc)

3.  [Visualización de nodos](https://youtu.be/6WbkO4lNkxA)


4.  [Gestión de propiedades de nodos](https://youtu.be/Md7yQ2ka8yY)


5.  [Creación de relaciones](https://youtu.be/MoNS1u4rrAI)


6.  [Agrega 1 propiedad a una relación](https://youtu.be/iO2kJy-7Bms)


7.  [Agregar propiedades a multiples relaciones](https://youtu.be/cTPZDx5gZx8)


8.  [Actualizar 1 propiedad a una relación / multiples propiedades a multiples relaciones al mismo tiempo](https://youtu.be/Pje2TnIBvUo)


9.  [Elimina 1 propiedad a una relación / múltiples propiedades a múltiples relaciones al mismo tiempo](https://youtu.be/xOaRw7hMMcw)


10.  [Eliminación de 1 nodo / varios nodos](https://youtu.be/bDShYqDhr3E)


11.  [Eliminación de 1 relación / varias relaciones](https://youtu.be/0fZ-s50ppv8)

## Autores

- Madeline Nahomy Castro Morales, 22473
- Aroldo Xavier López Osoy, 22716
