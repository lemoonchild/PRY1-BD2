import streamlit as st
import requests
from config import BASE_URL
import re

st.set_page_config(page_title="Eliminacion de Nodos y Relaciones", page_icon="🗑️")
st.title("🗑️ Eliminacion de Nodos y Relaciones")

AVAILABLE_LABELS = ["Review", "Component", "User", "Provider", "Category"]
RELATIONSHIP_TYPES = ["Purchased", "Categorized", "Supplies", "Reviews", "Promotes",
                      "Associated_with", "Searched", "Wants", "Writes", "Complements"]

def get_identifier_key(label: str) -> str:
    return "title" if label == "Review" else "name"

def handle_response(response, success_message, not_found_message):
    if response.status_code == 200:
        st.success(success_message)
    elif response.status_code == 404:
        st.warning(not_found_message)
    else:
        st.error(f"Error {response.status_code}: {response.text}")

# Elección principal: ¿Qué deseas eliminar?
delete_type = st.selectbox("¿Qué deseas eliminar?", ["Nodos", "Relaciones"])

if delete_type == "Nodos":
    st.subheader("Eliminar Nodos")

    delete_mode = st.radio("Eliminar:", ["Un nodo", "Múltiples nodos"])

    if delete_mode == "Un nodo":
        label = st.selectbox("Selecciona el Label", AVAILABLE_LABELS, key="delete_single_label")
        identifier_key = get_identifier_key(label)
        identifier_value = st.text_input(f"{identifier_key.capitalize()} del nodo a eliminar", key="delete_single_value")

        if st.button("Eliminar Nodo"):
            payload = {
                "label": label,
                "identifier_value": identifier_value
            }
            response = requests.delete(f"{BASE_URL}/nodes/delete_node", json=payload)

            handle_response(
                response,
                success_message=f"✅ Nodo '{identifier_value}' eliminado correctamente.",
                not_found_message=f"⚠️ El nodo '{identifier_value}' no fue encontrado."
            )

    elif delete_mode == "Múltiples nodos":
        label = st.selectbox("Selecciona el Label", AVAILABLE_LABELS, key="delete_multiple_label")
        identifier_key = get_identifier_key(label)
        identifier_values = st.text_area(f"{identifier_key.capitalize()} de los nodos (separados por coma)").split(',')

        if st.button("Eliminar Nodos"):
            cleaned_identifiers = [val.strip() for val in identifier_values if val.strip()]

            found = []
            not_found = []

            for identifier in cleaned_identifiers:
                payload = {
                    "label": label,
                    "identifier_value": identifier
                }
                response = requests.delete(f"{BASE_URL}/nodes/delete_node", json=payload)

                if response.status_code == 200:
                    found.append(identifier)
                elif response.status_code == 404:
                    not_found.append(identifier)
                else:
                    st.error(f"Error {response.status_code} al eliminar '{identifier}': {response.text}")

            if found:
                st.success(f"✅ Se eliminaron los siguientes nodos: {', '.join(found)}")
            if not_found:
                st.warning(f"⚠️ No se encontraron los siguientes nodos: {', '.join(not_found)}")

elif delete_type == "Relaciones":
    st.subheader("Eliminar Relaciones")

    delete_mode = st.radio("Eliminar:", ["Una relación", "Múltiples relaciones"])

    if delete_mode == "Una relación":
        from_label = st.selectbox("Label de origen", AVAILABLE_LABELS, key="delete_single_from_label")
        to_label = st.selectbox("Label de destino", AVAILABLE_LABELS, key="delete_single_to_label")
        relationship_type = st.selectbox("Tipo de Relación", RELATIONSHIP_TYPES, key="delete_single_relationship_type")

        from_identifier_key = get_identifier_key(from_label)
        to_identifier_key = get_identifier_key(to_label)

        from_identifier = st.text_input(f"{from_identifier_key.capitalize()} del nodo origen", key="delete_single_from_value")
        to_identifier = st.text_input(f"{to_identifier_key.capitalize()} del nodo destino", key="delete_single_to_value")

        if st.button("Eliminar Relación"):
            payload = {
                "from_label": from_label,
                "to_label": to_label,
                "relationship_type": relationship_type.upper(),
                "from_identifier": from_identifier,
                "to_identifier": to_identifier
            }
            response = requests.delete(f"{BASE_URL}/relationships/delete_relationship", json=payload)

            handle_response(
                response,
                success_message=f"✅ Relación {relationship_type.upper()} entre '{from_identifier}' y '{to_identifier}' eliminada correctamente.",
                not_found_message=f"⚠️ No se encontró la relación {relationship_type.upper()} entre '{from_identifier}' y '{to_identifier}'."
            )

    elif delete_mode == "Múltiples relaciones":
        from_label = st.selectbox("Label de origen", AVAILABLE_LABELS, key="delete_multiple_from_label")
        to_label = st.selectbox("Label de destino", AVAILABLE_LABELS, key="delete_multiple_to_label")
        relationship_type = st.selectbox("Tipo de Relación", RELATIONSHIP_TYPES, key="delete_multiple_relationship_type")

        pairs_text = st.text_area("Par de nodos (formato: nodo_origen,nodo_destino por línea)", key="delete_multiple_pairs")
        pairs = [
            [part.strip() for part in line.split(',')]
            for line in pairs_text.split('\n')
            if line.strip()
        ]

        if st.button("Eliminar Relaciones"):
            found = []
            not_found = []

            for from_id, to_id in pairs:
                payload = {
                    "from_label": from_label,
                    "to_label": to_label,
                    "relationship_type": relationship_type.upper(),
                    "from_identifier": from_id,
                    "to_identifier": to_id
                }
                response = requests.delete(f"{BASE_URL}/relationships/delete_relationship", json=payload)

                if response.status_code == 200:
                    found.append(f"({from_id} -> {to_id})")
                elif response.status_code == 404:
                    not_found.append(f"({from_id} -> {to_id})")
                else:
                    st.error(f"Error {response.status_code} al eliminar la relación {from_id} -> {to_id}: {response.text}")

            if found:
                st.success(f"✅ Se eliminaron las siguientes relaciones: {', '.join(found)}")
            if not_found:
                st.warning(f"⚠️ No se encontraron las siguientes relaciones: {', '.join(not_found)}")
