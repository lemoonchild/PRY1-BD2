import streamlit as st

st.set_page_config(
    page_title="Neo4j App",
    page_icon="🚀",
)

st.title("Bienvenido a la Gestión de Neo4j 📊")
st.sidebar.success("Selecciona una página arriba.")

st.write(
    """
    Esta aplicación permite gestionar nodos y relaciones en una base de datos Neo4j.
    Puedes:
    - Crear nodos y relaciones.
    - Visualizar información de nodos.
    - Modificar propiedades de nodos y relaciones.
    - Eliminar propiedades, nodos o relaciones.
    
    👈 Usa el menú lateral para navegar entre las secciones.
    """
)
