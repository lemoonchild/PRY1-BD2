import streamlit as st
import requests
from config import BASE_URL

st.set_page_config(page_title="Visualizacion de Nodos", page_icon="📊")

st.title("📊 Visualizacion de Nodos")

AVAILABLE_LABELS = ["Review", "Component", "User", "Provider", "Category"]

def get_identifier_key(label: str) -> str:
    return "title" if label == "Review" else "name"

st.subheader("Consultar Nodos por Filtro")

label = st.selectbox("Selecciona un Label (opcional)", [""] + AVAILABLE_LABELS, key="filter_label")
prop = st.text_input("Propiedad (opcional)", key="filter_prop")
value = st.text_input("Valor (opcional)", key="filter_value")

if st.button("Consultar Nodos con Filtro", key="btn_filter"):
    params = {}
    if label:
        params["label"] = label
    if prop:
        params["prop"] = prop
    if value:
        params["value"] = value

    response = requests.get(f"{BASE_URL}/nodes", params=params)

    if response.status_code == 200:
        nodes = response.json()
        if nodes:
            st.write(f"Se encontraron {len(nodes)} nodo(s)")
            st.json(nodes)
        else:
            st.warning("No se encontraron nodos con los filtros aplicados.")
    else:
        st.error(f"Error {response.status_code}: {response.text}")

st.subheader("Consultar 1 o Más Nodos por Nombre")

label_specific = st.selectbox("Selecciona el Label", AVAILABLE_LABELS, key="specific_label")
names_input = st.text_area("Nombres de los nodos (separados por coma)", key="specific_names")
names_list = [name.strip() for name in names_input.split(",") if name.strip()]

if st.button("Buscar Nodo(s)", key="btn_specific_nodes"):
    if not names_list:
        st.warning("Debes ingresar al menos un nombre.")
    else:
        identifier_key = get_identifier_key(label_specific)

        # ✅ Hacer un solo request al nuevo endpoint /batch
        response = requests.get(f"{BASE_URL}/nodes/batch", params={
            "label": label_specific,
            "prop": identifier_key,
            "values": names_list
        }, timeout=30)

        if response.status_code == 200:
            nodes = response.json()
            if nodes:
                st.success(f"Se encontraron {len(nodes)} nodo(s):")
                st.json(nodes)
            else:
                st.warning("No se encontraron nodos con los nombres indicados.")
        else:
            st.error(f"Error {response.status_code}: {response.text}")

st.subheader("Consulta Agregada")

label_agg = st.selectbox("Selecciona el Label para consulta agregada", [""] + AVAILABLE_LABELS, key="agg_label")

if st.button("Consultar Agregados", key="btn_aggregates"):
    params = {}
    if label_agg:
        params["label"] = label_agg

    response = requests.get(f"{BASE_URL}/nodes/aggregates", params=params)

    if response.status_code == 200:
        st.json(response.json())
    else:
        st.error(f"Error {response.status_code}: {response.text}")
