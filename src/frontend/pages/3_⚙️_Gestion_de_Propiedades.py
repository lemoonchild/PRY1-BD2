import streamlit as st
import requests
from config import BASE_URL
import re
import ast


st.set_page_config(page_title="Gestión de Propiedades", page_icon="⚙️")
st.title("Gestión de Propiedades ⚙️")

AVAILABLE_LABELS = ["Review", "Component", "User", "Provider", "Category"]

def to_snake_case(text):
    return re.sub(r'(?<!^)(?=[A-Z])', '_', text).lower()

def get_identifier_key(label):
    return "title" if label == "Review" else "name"

# Función para intentar parsear una cadena que parezca lista
def parse_if_list(val):
    if isinstance(val, str) and val.startswith('[') and val.endswith(']'):
        try:
            parsed = ast.literal_eval(val)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            pass
    return val


# Agregar propiedades a 1 nodo
st.subheader("Agregar Propiedades a 1 Nodo")

label = st.selectbox("Selecciona el Label", AVAILABLE_LABELS)
identifier_key = get_identifier_key(label)
identifier_value = st.text_input(f"{identifier_key.capitalize()} del Nodo")

if "single_properties" not in st.session_state:
    st.session_state.single_properties = []

if st.button("Agregar nueva propiedad", key="add_single_property"):
    st.session_state.single_properties.append({"name": "", "type": "Texto", "value": ""})

for index, prop in enumerate(st.session_state.single_properties):
    cols = st.columns([3, 2, 3])
    prop["name"] = cols[0].text_input(f"Propiedad {index+1}", key=f"name_{index}")
    prop["type"] = cols[1].selectbox("Tipo", ["Texto", "Número", "Booleano", "Fecha", "Lista"], key=f"type_{index}")
    if prop["type"] == "Texto":
        prop["value"] = cols[2].text_input("Valor", key=f"value_{index}")
    elif prop["type"] == "Número":
        prop["value"] = cols[2].number_input("Valor", key=f"value_{index}")
    elif prop["type"] == "Booleano":
        prop["value"] = cols[2].checkbox("Valor", key=f"value_{index}")
    elif prop["type"] == "Fecha":
        prop["value"] = cols[2].date_input("Valor", key=f"value_{index}").isoformat()
    elif prop["type"] == "Lista":
        prop["value"] = cols[2].text_area("Valor (separado por comas)", key=f"value_{index}").split(',')

if st.button("Guardar Propiedades", key="save_single_properties"):
    properties = {to_snake_case(p["name"]): p["value"] for p in st.session_state.single_properties}
    payload = {
        "label": label,
        "identifier_key": identifier_key,
        "identifier_value": identifier_value,
        "properties": properties
    }
    print(payload)
    response = requests.patch(f"{BASE_URL}/nodes/add_properties", json=payload)
    st.write(response.json())




# Agregar propiedades a múltiples nodos
st.subheader("Agregar Propiedades a Múltiples Nodos")

label = st.selectbox("Selecciona el Label (Múltiples)", AVAILABLE_LABELS, key="multi_label")
identifier_key = get_identifier_key(label)
identifier_values = st.text_input("Nombres de los Nodos (separados por comas)", key="multi_identifier_add").split(',')

if "multi_properties" not in st.session_state:
    st.session_state.multi_properties = []

if st.button("Agregar nueva propiedad (Múltiples)", key="add_multi_property"):
    st.session_state.multi_properties.append({"name": "", "type": "Texto", "value": ""})

for index, prop in enumerate(st.session_state.multi_properties):
    cols = st.columns([3, 2, 3])
    prop["name"] = cols[0].text_input(f"Propiedad {index+1}", key=f"multi_name_{index}")
    prop["type"] = cols[1].selectbox("Tipo", ["Texto", "Número", "Booleano", "Fecha", "Lista"], key=f"multi_type_{index}")
    if prop["type"] == "Texto":
        prop["value"] = cols[2].text_input("Valor", key=f"multi_value_{index}")
    elif prop["type"] == "Número":
        prop["value"] = cols[2].number_input("Valor", key=f"multi_value_{index}")
    elif prop["type"] == "Booleano":
        prop["value"] = cols[2].checkbox("Valor", key=f"multi_value_{index}")
    elif prop["type"] == "Fecha":
        prop["value"] = cols[2].date_input("Valor", key=f"multi_value_{index}").isoformat()
    elif prop["type"] == "Lista":
        prop["value"] = cols[2].text_area("Valor (separado por comas)", key=f"multi_value_{index}").split(',')

if st.button("Guardar Propiedades (Múltiples)", key="save_multi_properties"):
    properties = {to_snake_case(p["name"]): p["value"] for p in st.session_state.multi_properties}
    payload = {
        "label": label,
        "identifier_key": identifier_key,
        "identifier_values": identifier_values,
        "properties": properties
    }
    response = requests.patch(f"{BASE_URL}/nodes/add_properties_multiple", json=payload)
    st.write(response.json())




# Actualizar propiedades de 1 nodo
st.subheader("Actualizar Propiedades de 1 Nodo")

label = st.selectbox("Selecciona el Label (Actualizar)", AVAILABLE_LABELS, key="update_single_label")
identifier_key = get_identifier_key(label)
identifier_value = st.text_input(f"{identifier_key.capitalize()} del Nodo a actualizar")

if st.button("Cargar propiedades actuales", key="load_current_properties"):
    response = requests.get(f"{BASE_URL}/nodes?label={label}&prop={identifier_key}&value={identifier_value}")
    if response.status_code == 200:
        current_properties = response.json()
        st.session_state.current_properties = current_properties
    else:
        st.error(f"Error {response.status_code}: {response.text}")

if "current_properties" in st.session_state:
    current_properties = st.session_state.current_properties
    updated_properties = {}

    st.write("Modifica las propiedades:")
    for prop in current_properties:
        for key, value in prop.items():
            if isinstance(value, bool):
                updated_properties[key] = st.checkbox(f"{key}:", value, key=f"update_single_checkbox_{key}")
            elif isinstance(value, (int, float)):
                updated_properties[key] = st.number_input(f"{key}:", value=value, key=f"update_single_number_{key}")
            elif isinstance(value, list):
                updated_properties[key] = st.text_area(f"{key} (separado por comas):", value=",".join(value)).split(',')
            else:
                updated_properties[key] = st.text_input(f"{key}:", value=value, key=f"update_single_text_{key}")

    if st.button("Actualizar Propiedades", key="update_single_properties"):
        payload = {
            "label": label,
            "identifier_key": identifier_key,
            "identifier_value": identifier_value,
            "properties": updated_properties
        }
        res = requests.patch(f"{BASE_URL}/nodes/update_properties", json=payload)
        st.write(res.json())




# Actualizar propiedades de múltiples nodos
st.subheader("Actualizar Propiedades de Múltiples Nodos")

label = st.selectbox("Selecciona el Label (Actualizar Múltiples)", AVAILABLE_LABELS, key="update_multi_label")
identifier_key = get_identifier_key(label)
identifier_values = [node.strip() for node in st.text_input("Nombres de los Nodos (separados por comas)", key="multi_identifier_update").split(',') if node.strip()]

if "update_multi_last_nodes" not in st.session_state:
    st.session_state.update_multi_last_nodes = []

def convert_value(value, expected_type):
    try:
        if expected_type is bool:
            if isinstance(value, bool):
                return value
            val_lower = str(value).lower()
            if val_lower in ["true", "1", "yes"]:
                return True
            elif val_lower in ["false", "0", "no"]:
                return False
            else:
                raise ValueError("Input should be a valid boolean")
        elif expected_type is int:
            return int(value)
        elif expected_type is float:
            return float(value)
        elif expected_type is list:
            return value if isinstance(value, list) else parse_if_list(value)
        else:
            return str(value)
    except:
        raise ValueError(f"Cannot parse '{value}' as {expected_type.__name__}")

if st.button("Cargar propiedades comunes", key="load_common_properties_update"):
    st.session_state.update_multi_nodes = identifier_values.copy()
    properties_list = []
    for node in identifier_values:
        response = requests.get(f"{BASE_URL}/nodes?label={label}&prop={identifier_key}&value={node}")
        if response.status_code == 200 and response.json():
            properties_list.append(response.json()[0])
        else:
            st.error(f"Nodo '{node}' no encontrado o sin datos.")

    if properties_list:
        all_properties = [set(n.keys()) for n in properties_list]
        common_properties = set.intersection(*all_properties).difference({"name", "title"})
        st.session_state.update_multi_common_properties = list(common_properties)

        sample_values = {}
        property_types = {}
        for prop in common_properties:
            values = [node[prop] for node in properties_list]
            first_val = parse_if_list(values[0])
            property_types[prop] = type(first_val)
            sample_values[prop] = first_val if all(v == values[0] for v in values) else ""
        st.session_state.update_multi_current_values = sample_values
        st.session_state.update_multi_property_types = property_types
    else:
        st.error("No se encontraron nodos con esas etiquetas y nombres.")

if ("update_multi_common_properties" in st.session_state and 
    set(st.session_state.update_multi_nodes) == set(identifier_values)):

    st.write("Modifica las propiedades comunes:")
    updated_properties = {}

    for prop in st.session_state.update_multi_common_properties:
        valor_referencia = st.session_state.update_multi_current_values.get(prop, "")
        prop_type = st.session_state.update_multi_property_types.get(prop, str)
        if prop_type is bool:
            updated_properties[prop] = st.checkbox(f"{prop}:", value=valor_referencia, key=f"update_multi_checkbox_{prop}")
        elif prop_type in [int, float]:
            default_value = valor_referencia if isinstance(valor_referencia, (int, float)) else 0.0
            updated_properties[prop] = st.number_input(f"{prop}:", value=default_value, key=f"update_multi_number_{prop}")
        elif prop_type is list:
            valor_str = ",".join(valor_referencia) if valor_referencia else ""
            input_list = st.text_area(f"{prop} (separado por comas):", value="", placeholder=valor_str, key=f"update_multi_list_{prop}")
            updated_properties[prop] = valor_referencia if input_list.strip() == "" else [elem.strip() for elem in input_list.split(',') if elem.strip()]
        else:
            updated_properties[prop] = st.text_input(f"{prop}:", value="", placeholder=str(valor_referencia), key=f"update_multi_text_{prop}")

    if st.button("Actualizar Propiedades (Múltiples)", key="update_multi_properties"):
        valid = True
        for prop, val in updated_properties.items():
            try:
                converted_val = convert_value(val, st.session_state.update_multi_property_types.get(prop, str))
                if isinstance(converted_val, list):
                    converted_val = ",".join(map(str, converted_val))
                updated_properties[prop] = converted_val
            except ValueError as e:
                st.error(f"Error en '{prop}': {e}")
                valid = False
        
        if valid:
            payload = {
                "label": label,
                "identifier_key": identifier_key,
                "identifier_values": identifier_values,
                "properties": updated_properties
            }
            print(payload)
            res = requests.patch(f"{BASE_URL}/nodes/update_properties_multiple", json=payload)
            try:
                json_response = res.json()
            except:
                json_response = res.text
            st.write(json_response)




# Eliminar propiedades de 1 nodo
st.subheader("Eliminar Propiedades de 1 Nodo")

label = st.selectbox("Selecciona el Label (Eliminar)", AVAILABLE_LABELS, key="del_single_label")
identifier_key = get_identifier_key(label)
identifier_value = st.text_input(f"{identifier_key.capitalize()} del Nodo a eliminar propiedades")

if st.button("Cargar propiedades", key="load_properties_delete_single"):
    response = requests.get(f"{BASE_URL}/nodes/{identifier_value}?label={label}")
    if response.status_code == 200:
        # Guarda la lista de propiedades en session_state
        st.session_state.del_single_properties = list(response.json().keys())

# Solo muestra el multiselect si hay propiedades en session_state
if "del_single_properties" in st.session_state:
    to_remove = st.multiselect("Selecciona las propiedades a eliminar", st.session_state.del_single_properties)

    if st.button("Eliminar Propiedades", key="delete_single_properties"):
        payload = {
            "label": label,
            "identifier_key": identifier_key,
            "identifier_value": identifier_value,
            "properties": to_remove
        }
        res = requests.patch(f"{BASE_URL}/nodes/remove_properties", json=payload)
        st.write(res.json())




# Eliminar propiedades de múltiples nodos
st.subheader("Eliminar Propiedades de Múltiples Nodos")

# Guarda la selección del label en session_state
if "delete_multi_label" not in st.session_state:
    st.session_state.delete_multi_label = AVAILABLE_LABELS[0]

label = st.selectbox(
    "Selecciona el Label (Eliminar Múltiples)",
    AVAILABLE_LABELS,
    key="delete_multi_label"
)
identifier_key = get_identifier_key(label)
identifier_values = st.text_input("Nombres de los Nodos (separados por comas)", key="multi_identifier_delete").split(',')

# Cargar y guardar propiedades comunes en session_state
if st.button("Cargar propiedades comunes", key="load_common_properties_delete_multi"):
    properties_list = []

    for node in identifier_values:
        response = requests.get(f"{BASE_URL}/nodes?label={label}&prop={identifier_key}&value={node.strip()}")
        if response.status_code == 200:
            data = response.json()
            if data:
                properties_list.append(data[0])
            else:
                st.error(f"No se encontraron propiedades para el nodo '{node}'.")
    if properties_list:
        common_properties = set(properties_list[0].keys())
        for props in properties_list:
            common_properties.intersection_update(props.keys())
        if common_properties:
            st.session_state.common_properties = list(common_properties)
        else:
            st.error("No hay propiedades comunes entre los nodos seleccionados.")
    else:
        st.error("No se encontraron nodos con las etiquetas proporcionadas.")

# Desplegar el multiselect si ya se han cargado propiedades comunes
if "common_properties" in st.session_state:
    to_remove = st.multiselect("Selecciona las propiedades a eliminar", st.session_state.common_properties, key="delete_multi_properties_list")
    if st.button("Eliminar Propiedades (Múltiples)", key="delete_multi_properties"):
        payload = {
            "label": label,
            "identifier_key": identifier_key,
            "identifier_values": identifier_values,
            "properties": to_remove
        }
        res = requests.patch(f"{BASE_URL}/nodes/remove_properties_multiple", json=payload)
        st.write(res.json())
