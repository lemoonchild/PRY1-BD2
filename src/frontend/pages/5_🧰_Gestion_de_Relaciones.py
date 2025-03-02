import streamlit as st
import requests
from config import BASE_URL
import re
from datetime import date

st.set_page_config(page_title="Gestion de Propiedades de Relaciones", page_icon="🔗")
st.title("Gestion de Propiedades de Relaciones 🔗")

AVAILABLE_LABELS = ["Review", "Component", "User", "Provider", "Category"]
RELATIONSHIP_TYPES = ["Purchased", "Categorized", "Supplies", "Reviews", "Promotes", 
                      "Associated_with", "Searched", "Wants", "Writes", "Complements"]

def to_snake_case(text):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()

def get_identifier_key(label):
    return "title" if label == "Review" else "name"

def get_property_input_ui(key_prefix):
    name = st.text_input(f"Nombre Propiedad", key=f"{key_prefix}_name")
    type_ = st.selectbox("Tipo", ["Texto", "Numero", "Booleano", "Fecha", "Lista"], key=f"{key_prefix}_type")

    if type_ == "Texto":
        value = st.text_input("Valor", key=f"{key_prefix}_value")
    elif type_ == "Numero":
        value = st.number_input("Valor", key=f"{key_prefix}_value")
    elif type_ == "Booleano":
        value = st.checkbox("Valor", key=f"{key_prefix}_value")
    elif type_ == "Fecha":
        value = st.date_input("Valor", value=date.today(), key=f"{key_prefix}_value").isoformat()
    elif type_ == "Lista":
        value = st.text_area("Valor (separado por comas)", key=f"{key_prefix}_value").split(',')
    
    return to_snake_case(name), value

def manage_single_relationship_properties(operation, endpoint):
    st.subheader(f"{operation} propiedades a 1 relación")

    from_label = st.selectbox("Label de origen", AVAILABLE_LABELS, key=f"{operation}_single_from_label")
    from_identifier = st.text_input(f"{get_identifier_key(from_label).capitalize()} del nodo origen", key=f"{operation}_single_from_id")
    to_label = st.selectbox("Label de destino", AVAILABLE_LABELS, key=f"{operation}_single_to_label")
    to_identifier = st.text_input(f"{get_identifier_key(to_label).capitalize()} del nodo destino", key=f"{operation}_single_to_id")
    relationship_type = st.selectbox("Tipo de Relación", RELATIONSHIP_TYPES, key=f"{operation}_single_relationship_type")

    if "single_relationship_properties" not in st.session_state:
        st.session_state.single_relationship_properties = []

    if st.button(f"Agregar nueva propiedad ({operation})", key=f"{operation}_add_single_property"):
        st.session_state.single_relationship_properties.append({})

    properties = {}
    for index, _ in enumerate(st.session_state.single_relationship_properties):
        name, value = get_property_input_ui(f"{operation}_single_{index}")
        properties[name] = value

    if st.button(f"{operation} propiedades", key=f"{operation}_submit_single"):
        payload = {
            "from_label": from_label,
            "to_label": to_label,
            "relationship_type": relationship_type.upper(),
            "from_identifier": from_identifier,
            "to_identifier": to_identifier,
            "properties": properties
        }
        response = requests.patch(f"{BASE_URL}/relationships/{endpoint}", json=payload)
        st.write(response.json())


def manage_multiple_relationships_properties(operation, endpoint):
    st.subheader(f"{operation} propiedades a múltiples relaciones")

    from_label = st.selectbox("Label de origen (Múltiples)", AVAILABLE_LABELS, key=f"{operation}_multi_from_label")
    to_label = st.selectbox("Label de destino (Múltiples)", AVAILABLE_LABELS, key=f"{operation}_multi_to_label")
    relationship_type = st.selectbox("Tipo de Relación", RELATIONSHIP_TYPES, key=f"{operation}_multi_relationship_type")

    pairs_text = st.text_area(f"Par de nodos (formato: nodo_origen,nodo_destino por línea)", key=f"{operation}_multi_pairs")
    pairs = [tuple(line.split(',')) for line in pairs_text.strip().split('\n') if line]

    if "multi_relationship_properties" not in st.session_state:
        st.session_state.multi_relationship_properties = []

    if st.button(f"Agregar nueva propiedad ({operation})", key=f"{operation}_add_multi_property"):
        st.session_state.multi_relationship_properties.append({})

    properties = {}
    for index, _ in enumerate(st.session_state.multi_relationship_properties):
        name, value = get_property_input_ui(f"{operation}_multi_{index}")
        properties[name] = value

    if st.button(f"{operation} propiedades", key=f"{operation}_submit_multi"):
        payload = {
            "from_label": from_label,
            "to_label": to_label,
            "relationship_type": relationship_type.upper(),
            "pairs": pairs,
            "properties": properties
        }
        print(payload)
        response = requests.patch(f"{BASE_URL}/relationships/{endpoint}", json=payload)
        st.write(response.json())



# Menú general
option = st.selectbox("¿Qué deseas hacer?", [
    "Agregar propiedades a 1 relación",
    "Agregar propiedades a múltiples relaciones",
    "Actualizar propiedades de 1 relación",
    "Actualizar propiedades de múltiples relaciones",
    "Eliminar propiedades de 1 relación",
    "Eliminar propiedades de múltiples relaciones"
])

if option == "Agregar propiedades a 1 relación":
    manage_single_relationship_properties("Agregar", "add_properties_to_relationship")

elif option == "Agregar propiedades a múltiples relaciones":
    manage_multiple_relationships_properties("Agregar", "add_properties_to_multiple_relationships")

elif option == "Actualizar propiedades de 1 relación":
    # =============== Actualizar propiedades de 1 relación ===============
    st.subheader("Actualizar Propiedades de 1 Relación")

    from_label = st.selectbox("Label de origen", AVAILABLE_LABELS, key="update_single_from_label")
    to_label = st.selectbox("Label de destino", AVAILABLE_LABELS, key="update_single_to_label")
    relationship_type = st.selectbox("Tipo de Relación", RELATIONSHIP_TYPES, key="update_single_relationship_type")

    from_identifier_key = get_identifier_key(from_label)
    to_identifier_key = get_identifier_key(to_label)

    from_identifier = st.text_input(f"{from_identifier_key.capitalize()} del nodo origen", key="update_single_from_id")
    to_identifier = st.text_input(f"{to_identifier_key.capitalize()} del nodo destino", key="update_single_to_id")

    if st.button("Cargar propiedades actuales", key="load_single_relationship_properties"):
        response = requests.get(
            f"{BASE_URL}/relationships/properties",
            params={
                "from_label": from_label,
                "to_label": to_label,
                "relationship_type": relationship_type.upper(),
                "from_value": from_identifier,
                "to_value": to_identifier
            }
        )

        if response.status_code == 200:
            st.session_state.current_relationship_properties = response.json()["properties"]
        else:
            st.error(f"Error {response.status_code}: {response.text}")

    if "current_relationship_properties" in st.session_state:
        current_properties = st.session_state.current_relationship_properties
        updated_properties = {}

        st.write("Modifica las propiedades:")

        for key, value in current_properties.items():
            if isinstance(value, bool):
                updated_properties[key] = st.checkbox(f"{key}:", value, key=f"update_single_checkbox_{key}")
            elif isinstance(value, (int, float)):
                updated_properties[key] = st.number_input(f"{key}:", value=value, key=f"update_single_number_{key}")
            elif isinstance(value, list):
                updated_properties[key] = st.text_area(f"{key} (separado por comas):", value=",".join(value), key=f"update_single_list_{key}").split(',')
            else:
                updated_properties[key] = st.text_input(f"{key}:", value=value, key=f"update_single_text_{key}")

        if st.button("Actualizar Propiedades", key="update_single_properties"):
            payload = {
                "from_label": from_label,
                "to_label": to_label,
                "relationship_type": relationship_type.upper(),
                "from_identifier": from_identifier,
                "to_identifier": to_identifier,
                "properties": updated_properties
            }
            res = requests.patch(f"{BASE_URL}/relationships/update_properties_in_relationship", json=payload)
            st.write(res.json())


elif option == "Actualizar propiedades de múltiples relaciones":
    st.subheader("Actualizar Propiedades de Múltiples Relaciones")

    from_label = st.selectbox("Label de origen (Múltiples)", AVAILABLE_LABELS, key="update_multi_from_label")
    to_label = st.selectbox("Label de destino (Múltiples)", AVAILABLE_LABELS, key="update_multi_to_label")
    relationship_type = st.selectbox("Tipo de Relación", RELATIONSHIP_TYPES, key="update_multi_relationship_type")

    pairs_text = st.text_area("Par de nodos (formato: nodo_origen,nodo_destino por línea)", key="update_multi_pairs")
    pairs = [tuple(line.strip().split(',')) for line in pairs_text.strip().split('\n') if line]

    if st.button("Cargar propiedades comunes", key="load_multi_relationship_properties"):
        properties_list = []

        for from_value, to_value in pairs:
            response = requests.get(
                f"{BASE_URL}/relationships/properties",
                params={
                    "from_label": from_label,
                    "to_label": to_label,
                    "relationship_type": relationship_type.upper(),
                    "from_value": from_value.strip(),
                    "to_value": to_value.strip()
                }
            )
            if response.status_code == 200:
                properties_list.append(response.json()["properties"])
            else:
                st.error(f"Relación {from_value} -> {to_value} no encontrada")

        if properties_list:
            common_properties = set(properties_list[0].keys())
            for props in properties_list[1:]:
                common_properties.intersection_update(props.keys())

            st.session_state.common_relationship_properties = list(common_properties)
            st.session_state.sample_properties = properties_list[0]
        else:
            st.error("No se encontraron propiedades comunes")

    if "common_relationship_properties" in st.session_state:
        common_properties = st.session_state.common_relationship_properties
        sample_properties = st.session_state.sample_properties
        updated_properties = {}

        st.write("Modifica las propiedades comunes:")

        for key in common_properties:
            value = sample_properties[key]

            if isinstance(value, bool):
                updated_properties[key] = st.checkbox(f"{key}:", value, key=f"update_multi_checkbox_{key}")
            elif isinstance(value, (int, float)):
                updated_properties[key] = st.number_input(f"{key}:", value=value, key=f"update_multi_number_{key}")
            elif isinstance(value, list):
                updated_properties[key] = st.text_area(f"{key} (separado por comas):", value=",".join(value), key=f"update_multi_list_{key}").split(',')
            else:
                updated_properties[key] = st.text_input(f"{key}:", value=value, key=f"update_multi_text_{key}")

        if st.button("Actualizar Propiedades (Múltiples)", key="update_multi_properties"):
            payload = {
                "from_label": from_label,
                "to_label": to_label,
                "relationship_type": relationship_type.upper(),
                "pairs": pairs,
                "properties": updated_properties
            }
            res = requests.patch(f"{BASE_URL}/relationships/update_properties_in_multiple_relationships", json=payload)
            st.write(res.json())
elif option == "Eliminar propiedades de 1 relación":
    st.subheader("Eliminar Propiedades de 1 Relación")
    from_label = st.selectbox("Label de origen", AVAILABLE_LABELS, key="remove_single_from_label")
    to_label = st.selectbox("Label de destino", AVAILABLE_LABELS, key="remove_single_to_label")
    relationship_type = st.selectbox("Tipo de Relación", RELATIONSHIP_TYPES, key="remove_single_relationship_type")

    from_identifier = st.text_input(f"{get_identifier_key(from_label).capitalize()} del nodo origen", key="remove_single_from_id")
    to_identifier = st.text_input(f"{get_identifier_key(to_label).capitalize()} del nodo destino", key="remove_single_to_id")

    # Botón para cargar las propiedades de la relación
    if st.button("Cargar Propiedades", key="load_properties_single_relationship"):
        response = requests.get(
            f"{BASE_URL}/relationships/properties",
            params={
                "from_label": from_label,
                "to_label": to_label,
                "relationship_type": relationship_type.upper(),
                "from_value": from_identifier,
                "to_value": to_identifier
            }
        )

        if response.status_code == 200:
            st.session_state.single_relationship_properties = list(response.json()["properties"].keys())
        else:
            st.error(f"Error {response.status_code}: {response.text}")

    # Mostrar multiselect para elegir propiedades a eliminar (solo si ya se cargaron)
    if "single_relationship_properties" in st.session_state:
        properties_to_remove = st.multiselect(
            "Selecciona las propiedades a eliminar",
            st.session_state.single_relationship_properties,
            key="remove_single_relationship_properties_list"
        )

        if st.button("Eliminar Propiedades", key="delete_single_relationship_properties"):
            payload = {
                "from_label": from_label,
                "to_label": to_label,
                "relationship_type": relationship_type.upper(),
                "from_identifier": from_identifier,
                "to_identifier": to_identifier,
                "properties": properties_to_remove
            }
            response = requests.delete(f"{BASE_URL}/relationships/remove_properties_from_relationship", json=payload)
            st.write(response.json())

elif option == "Eliminar propiedades de múltiples relaciones":
    st.subheader("Eliminar Propiedades de Múltiples Relaciones")

    from_label = st.selectbox("Label de origen (Múltiples)", AVAILABLE_LABELS, key="remove_multi_from_label")
    to_label = st.selectbox("Label de destino (Múltiples)", AVAILABLE_LABELS, key="remove_multi_to_label")
    relationship_type = st.selectbox("Tipo de Relación", RELATIONSHIP_TYPES, key="remove_multi_relationship_type")

    pairs_text = st.text_area("Par de nodos (formato: nodo_origen,nodo_destino por línea)", key="multi_relationship_pairs")
    pairs = [tuple(line.strip().split(',')) for line in pairs_text.strip().split('\n') if line.strip()]

    # Botón para cargar propiedades comunes de las relaciones
    if st.button("Cargar Propiedades Comunes", key="load_common_properties_multi_relationships"):
        properties_list = []

        for from_value, to_value in pairs:
            response = requests.get(
                f"{BASE_URL}/relationships/properties",
                params={
                    "from_label": from_label,
                    "to_label": to_label,
                    "relationship_type": relationship_type.upper(),
                    "from_value": from_value.strip(),
                    "to_value": to_value.strip()
                }
            )
            if response.status_code == 200:
                properties = response.json()["properties"]
                properties_list.append(set(properties.keys()))
            else:
                st.error(f"No se encontraron propiedades para la relación entre {from_value} y {to_value}")

        # Si hay al menos una relación válida
        if properties_list:
            common_properties = set.intersection(*properties_list)
            if common_properties:
                st.session_state.multi_relationship_common_properties = list(common_properties)
            else:
                st.error("No hay propiedades comunes entre las relaciones seleccionadas.")
        else:
            st.error("No se pudieron cargar propiedades de las relaciones proporcionadas.")

    # Mostrar multiselect de propiedades comunes (si ya se cargaron)
    if "multi_relationship_common_properties" in st.session_state:
        properties_to_remove = st.multiselect(
            "Selecciona las propiedades a eliminar (Múltiples)",
            st.session_state.multi_relationship_common_properties,
            key="remove_multi_relationship_properties_list"
        )

        if st.button("Eliminar Propiedades (Múltiples)", key="delete_multi_relationship_properties"):
            payload = {
                "from_label": from_label,
                "to_label": to_label,
                "relationship_type": relationship_type.upper(),
                "pairs": pairs,
                "properties": properties_to_remove
            }
            response = requests.delete(f"{BASE_URL}/relationships/remove_properties_from_multiple_relationships", json=payload)
            st.write(response.json())

