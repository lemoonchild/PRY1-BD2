import streamlit as st
import requests
from config import BASE_URL

st.set_page_config(page_title="Visualización de Nodos", page_icon="📊")

st.title("Visualización de Nodos 📊")

# Lista de labels disponibles (centralizado para reuso)
AVAILABLE_LABELS = ["Review", "Component", "User", "Provider", "Category"]

st.subheader("Consultar Nodos")
label = st.selectbox("Selecciona un Label (opcional)", [""] + AVAILABLE_LABELS)
prop = st.text_input("Propiedad (opcional)")
value = st.text_input("Valor (opcional)")

if st.button("Consultar"):
    params = {}
    if label:
        params["label"] = label
    if prop:
        params["prop"] = prop
    if value:
        params["value"] = value

    response = requests.get(f"{BASE_URL}/nodes", params=params)

    if response.status_code == 200:
        st.json(response.json())
    else:
        st.error(f"Error {response.status_code}: {response.text}")


st.subheader("Consultar Nodo por Nombre")
name = st.text_input("Nombre del Nodo")
label = st.selectbox("Selecciona el Label del Nodo", AVAILABLE_LABELS)

if st.button("Buscar Nodo"):
    params = {"label": label}
    response = requests.get(f"{BASE_URL}/nodes/{name}", params=params)

    if response.status_code == 200:
        st.json(response.json())
    else:
        st.error(f"Error {response.status_code}: {response.text}")


st.subheader("Consulta Agregada")
label_agg = st.selectbox("Selecciona el Label para consulta agregada", [""] + AVAILABLE_LABELS)

if st.button("Consulta Agregada"):
    params = {}
    if label_agg:
        params["label"] = label_agg

    print(label_agg)
    print(params)


    response = requests.get(f"{BASE_URL}/nodes/aggregates", params=params)
    print(f"{BASE_URL}/nodes/aggregates")

    if response.status_code == 200:
        st.json(response.json())
    else:
        st.error(f"Error {response.status_code}: {response.text}")
