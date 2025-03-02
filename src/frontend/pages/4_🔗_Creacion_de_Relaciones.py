import streamlit as st
import requests
from config import BASE_URL
import re
from datetime import date

st.set_page_config(page_title="Creacion de Relaciones", page_icon="🔗")

st.title("Creacion de Relaciones 🔗")

AVAILABLE_LABELS = ["Review", "Component", "User", "Provider", "Category"]

# Relacion permitida: {Relacion: (Label Origen, Label Destino)}
VALID_RELATIONSHIPS = {
    "Purchased": ("User", "Component"),
    "Categorized": ("Component", "Category"),
    "Supplies": ("Provider", "Component"),
    "Reviews": ("Review", "Component"),
    "Promotes": ("Provider", "User"),
    "Associated_with": ("Provider", "Category"),
    "Searched": ("User", "Component"),
    "Wants": ("User", "Component"),
    "Writes": ("User", "Review"),
    "Complements": ("Component", "Component")
}

RELATION_PROPERTIES = {
    "Purchased": ["purchase_date", "quantity", "total_price", "payment_method"],
    "Categorized": ["assign_date", "relevance", "position"],
    "Supplies": ["shipping_mode", "payment_terms", "stock"],
    "Reviews": ["purchase_location", "satisfaction", "detail_level"],
    "Promotes": ["discount_percentage", "promotion_date", "promotion_type"],
    "Associated_with": ["association_level", "start_date", "association_terms"],
    "Searched": ["keyword", "search_date", "result_count"],
    "Wants": ["added_date", "priority", "reason"],
    "Writes": ["trust_index", "verified_purchase", "review_type"],
    "Complements": ["compatibility_level", "compatibility_reason", "relation_date"]
}

def to_snake_case(text):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()

def get_identifier_key(label):
    return "title" if label == "Review" else "name"

# Formulario para la relacion
st.subheader("Definir Relacion")

from_label = st.selectbox("Label de origen", AVAILABLE_LABELS, key="from_label")
from_identifier_key = get_identifier_key(from_label)
from_identifier_value = st.text_input(f"{from_identifier_key.capitalize()} del nodo origen", key="from_identifier")

to_label = st.selectbox("Label de destino", AVAILABLE_LABELS, key="to_label")
to_identifier_key = get_identifier_key(to_label)
to_identifier_value = st.text_input(f"{to_identifier_key.capitalize()} del nodo destino", key="to_identifier")

relationship_type = st.selectbox("Tipo de Relacion", list(VALID_RELATIONSHIPS.keys()))

# Validacion defensiva
if (from_label, to_label) != VALID_RELATIONSHIPS[relationship_type]:
    st.error(f"⚠️ Relacion invalida: '{relationship_type}' solo puede existir entre '{VALID_RELATIONSHIPS[relationship_type][0]}' y '{VALID_RELATIONSHIPS[relationship_type][1]}'")
    st.stop()

# Propiedades predefinidas
st.subheader("Propiedades predefinidas de la relacion")

properties = {}
for prop in RELATION_PROPERTIES[relationship_type]:
    if "fecha" in prop:
        properties[prop] = st.date_input(f"{prop.replace('_', ' ').capitalize()}", value=date.today()).isoformat()
    elif "cantidad" in prop or "nivel" in prop or "posicion" in prop or "grado" in prop or "indice" in prop or "prioridad" in prop or "stock" in prop:
        properties[prop] = st.number_input(f"{prop.replace('_', ' ').capitalize()}", min_value=0)
    elif "precio" in prop or "porcentaje" in prop:
        properties[prop] = st.number_input(f"{prop.replace('_', ' ').capitalize()}", min_value=0.0)
    elif "verificada" in prop:
        properties[prop] = st.checkbox(f"{prop.replace('_', ' ').capitalize()}")
    else:
        properties[prop] = st.text_input(f"{prop.replace('_', ' ').capitalize()}")

st.divider()

# Propiedades dinamicas
st.subheader("Agregar propiedades dinamicas adicionales")

if "dynamic_relationship_properties" not in st.session_state:
    st.session_state.dynamic_relationship_properties = []

if st.button("Agregar nueva propiedad dinamica"):
    st.session_state.dynamic_relationship_properties.append({
        "name": "",
        "type": "Texto",
        "value": ""
    })

for index, prop in enumerate(st.session_state.dynamic_relationship_properties):
    cols = st.columns([3, 2, 3])
    prop["name"] = cols[0].text_input(f"Nombre Propiedad {index+1}", prop["name"], key=f"rel_name_{index}")
    prop["type"] = cols[1].selectbox(f"Tipo {index+1}", ["Texto", "Numero", "Booleano", "Fecha", "Lista"], index=["Texto", "Numero", "Booleano", "Fecha", "Lista"].index(prop["type"]), key=f"rel_type_{index}")

    if prop["type"] == "Texto":
        prop["value"] = cols[2].text_input(f"Valor (Texto) {index+1}", prop["value"], key=f"rel_value_{index}")
    elif prop["type"] == "Numero":
        prop["value"] = cols[2].number_input(f"Valor (Numero) {index+1}", value=float(prop["value"]) if prop["value"] else 0.0, key=f"rel_value_{index}")
    elif prop["type"] == "Booleano":
        prop["value"] = cols[2].checkbox(f"Valor (Booleano) {index+1}", value=(prop["value"] == "True"), key=f"rel_value_{index}")
    elif prop["type"] == "Fecha":
        selected_date = cols[2].date_input(f"Valor (Fecha) {index+1}", value=date.today(), key=f"rel_value_{index}")
        prop["value"] = selected_date.isoformat()
    elif prop["type"] == "Lista":
        prop["value"] = cols[2].text_area(f"Valor (Lista, separado por comas) {index+1}", prop["value"], key=f"rel_value_{index}").split(',')

for prop in st.session_state.dynamic_relationship_properties:
    properties[to_snake_case(prop["name"])] = prop["value"]

# Boton para crear relacion
if st.button("Crear Relacion"):
    payload = {
        "from_label": from_label,
        "from_value": from_identifier_value,
        "to_label": to_label,
        "to_value": to_identifier_value,
        "relation_type": relationship_type.upper(),
        "properties": properties
    }

    response = requests.post(f"{BASE_URL}/relationships/create-relationship", json=payload)

    if response.status_code == 200:
        st.success("Relacion creada exitosamente")
        st.json(response.json())
    else:
        st.error(f"Error {response.status_code}: {response.text}")
