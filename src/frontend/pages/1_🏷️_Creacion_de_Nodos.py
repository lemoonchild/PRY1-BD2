import streamlit as st
import requests
from config import BASE_URL
import re
from datetime import date

st.set_page_config(page_title="Creación de Nodos", page_icon="🏷️")

st.title("Creación de Nodos 🏷️")

option = st.selectbox("¿Qué tipo de nodo quieres crear?", ["Con 1 Label", "Con Propiedades"])
label = st.selectbox("Selecciona un Label", ["Review", "Component", "Provider", "User", "Category"])

# Propiedades predefinidas por label
label_properties = {
    "Category": ["name", "popularity", "active", "featured", "last_update"],
    "Component": ["name", "model", "type", "price", "available", "specifications", "release_date", "main_market", "popularity"],
    "Provider": ["name", "rating", "warranty_offered", "products_offered", "avg_delivery_time"],
    "Review": ["title", "rating", "verified", "purchase_recommendation", "review_date"],
    "User": ["name", "budget", "looking_for_offers", "preferred_brands", "last_visit"]
}

category_groups = ["Gaming", "Audio", "Peripherals", "PC Components", "Networking", "Storage", "Cooling", "Power Supplies"]

subcategories = {
    "Gaming": ["Gaming Chair", "Gaming Mouse", "Gaming Keyboard", "Gaming Headset"],
    "Audio": ["Speakers", "Headphones", "Microphones", "Sound Cards"],
    "Peripherals": ["Mouse", "Keyboard", "Monitor", "Printer"],
    "PC Components": ["GPU", "CPU", "Motherboard", "RAM", "SSD", "HDD"],
    "Networking": ["Router", "Switch", "Network Card", "Modem"],
    "Storage": ["External HDD", "External SSD", "Flash Drive", "NAS"],
    "Cooling": ["CPU Cooler", "Case Fan", "Liquid Cooling", "Thermal Paste"],
    "Power Supplies": ["500W PSU", "750W PSU", "1000W PSU", "Modular PSU"]
}

# Función para convertir a snake_case
def to_snake_case(text):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()

# Crear nodo sin propiedades
if option == "Con 1 Label":
    if st.button("Crear Nodo"):
        response = requests.post(f"{BASE_URL}/nodes/create-node?label={label}")
        st.write(response.json())

# Crear nodo con propiedades (incluye dinámicas)
elif option == "Con Propiedades":
    properties = {}

    # Manejo especial para Component
    if label == "Component":
        st.subheader("Selecciona o crea Main Market y Type")

        option_main_market = st.radio(
            "¿Cómo deseas definir el mercado principal (Main Market)?",
            ["Seleccionar de la lista", "Ingresar manualmente"]
        )

        if option_main_market == "Seleccionar de la lista":
            main_market = st.selectbox("Selecciona el mercado principal", category_groups)
        else:
            main_market = st.text_input("Ingresa un nuevo mercado principal")

        # Ahora definimos "Type" dependiendo del Main Market
        if main_market in subcategories:
            type_option = st.radio(
                "¿Cómo deseas definir el tipo de componente (Type)?",
                ["Seleccionar de la lista", "Ingresar manualmente"]
            )
            if type_option == "Seleccionar de la lista":
                component_type = st.selectbox("Selecciona el tipo de componente", subcategories[main_market])
            else:
                component_type = st.text_input("Ingresa un nuevo tipo de componente")
        else:
            st.warning(f"Como '{main_market}' es nuevo, debes ingresar manualmente el tipo.")
            component_type = st.text_input("Ingresa un nuevo tipo de componente")

        properties["main_market"] = main_market
        properties["type"] = component_type


    # Manejo especial para User
    if label == "User":
        properties["preferred_brands"] = st.text_area(
            "Marcas Preferidas (separadas por comas)",
            placeholder="Ejemplo: Provider 1, Provider 2, Provider 3"
        ).split(',')

    # Recolectar propiedades predefinidas
    for prop in label_properties[label]:
        if prop in ["price", "popularity", "budget", "rating"]:
            properties[prop] = st.number_input(f"{prop.capitalize()}:", min_value=0.0)
        elif prop in ["available", "active", "featured", "verified", "looking_for_offers", "warranty_offered", "purchase_recommendation"]:
            properties[prop] = st.checkbox(f"{prop.capitalize()}:")
        elif prop in ["specifications", "products_offered"]:
            properties[prop] = st.text_area(f"{prop.capitalize()} (separadas por comas):").split(',')
        elif prop in ["release_date", "review_date", "last_update", "last_visit"]:
            properties[prop] = st.date_input(f"{prop.capitalize()}:", value=date.today()).isoformat()
        else:
            properties[prop] = st.text_input(f"{prop.capitalize()}:")

    st.divider()

    # Manejo de propiedades dinámicas
    st.subheader("Agregar nuevas propiedades dinámicas")

    if "dynamic_properties" not in st.session_state:
        st.session_state.dynamic_properties = []

    # Botón para agregar nueva propiedad dinámica
    if st.button("Agregar nueva propiedad"):
        st.session_state.dynamic_properties.append({
            "name": "",
            "type": "Texto",
            "value": ""
        })

    # Renderizar dinámicamente las propiedades adicionales
    for index, prop in enumerate(st.session_state.dynamic_properties):
        with st.expander(f"Propiedad dinámica {index + 1}", expanded=True):
            prop["name"] = st.text_input(f"Nombre de la Propiedad {index+1}", prop["name"], key=f"name_{index}")
            prop["type"] = st.selectbox(f"Tipo de Valor {index+1}", ["Texto", "Número", "Fecha", "Booleano", "Lista"], index=["Texto", "Número", "Fecha", "Booleano", "Lista"].index(prop["type"]), key=f"type_{index}")

            if prop["type"] == "Texto":
                prop["value"] = st.text_input(f"Valor (Texto) {index+1}", prop["value"], key=f"value_{index}")
            elif prop["type"] == "Número":
                prop["value"] = st.number_input(f"Valor (Número) {index+1}", value=float(prop["value"]) if prop["value"] else 0.0, key=f"value_{index}")
            elif prop["type"] == "Fecha":
                selected_date = st.date_input(f"Valor (Fecha) {index+1}", value=date.today(), key=f"value_{index}")
                prop["value"] = selected_date.isoformat()
            elif prop["type"] == "Booleano":
                prop["value"] = st.checkbox(f"Valor (Booleano) {index+1}", value=(prop["value"] == "True"), key=f"value_{index}")
            elif prop["type"] == "Lista":
                prop["value"] = st.text_area(f"Valor (Lista - separado por comas) {index+1}", prop["value"], key=f"value_{index}").split(',')

    # Convertir las propiedades dinámicas al diccionario final
    for prop in st.session_state.dynamic_properties:
        properties[to_snake_case(prop["name"])] = prop["value"]

    st.divider()

    # Botón para crear nodo con todas las propiedades
    if st.button("Crear Nodo"):
        response = requests.post(f"{BASE_URL}/nodes/create-node-with-properties", json={"label": label, "properties": properties})
        st.write(response.json())
