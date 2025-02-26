from neo4j import GraphDatabase
from dotenv import load_dotenv
import pandas as pd
import os

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# Conexión a Neo4j
def get_neo4j_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

driver = get_neo4j_driver()

# Diccionario para almacenar logs
load_report = {"nodes": {}, "relationships": {}}

def load_nodes_from_csv(file_path, node_label):
    df = pd.read_csv(file_path)

    primary_key = "name"
    if node_label == "Review":
        primary_key = "title"

    query = f"""
    UNWIND $data AS row
    MERGE (n:{node_label} {{{primary_key}: row.{primary_key}}})
    SET n += row
    """

    with driver.session() as session:
        session.run(query, data=df.to_dict(orient="records"))

    loaded_count = len(df)
    load_report["nodes"][node_label] = loaded_count
    print(f"✅ {loaded_count} nodos de {node_label} cargados correctamente.")

def load_relationships_from_csv(file_path, relation_type, from_label, to_label, from_key, to_key):
    df = pd.read_csv(file_path)
    
    # Filtrar filas inválidas (source o target vacíos)
    df = df.dropna(subset=[df.columns[0], df.columns[1]])

    query = f"""
    UNWIND $data AS row
    MATCH (a:{from_label} {{{from_key}: row.source}})
    MATCH (b:{to_label} {{{to_key}: row.target}})
    WHERE a IS NOT NULL AND b IS NOT NULL
    MERGE (a)-[r:{relation_type}]->(b)
    SET r += row.properties
    """

    successful_loads = 0

    with driver.session() as session:
        for _, row in df.iterrows():
            result = session.run(query, data={
                "source": row[df.columns[0]],
                "target": row[df.columns[1]],
                "properties": row[2:].to_dict()
            })
            if result.consume().counters.relationships_created > 0:
                successful_loads += 1

    load_report["relationships"][relation_type] = successful_loads
    print(f"✅ {successful_loads} relaciones {relation_type} cargadas correctamente.")

def load_all_nodes():
    base_path = "src/csvData"
    node_files = {
        "components.csv": "Component",
        "categories.csv": "Category",
        "users.csv": "User",
        "reviews.csv": "Review",
        "providers.csv": "Provider"
    }

    for file, label in node_files.items():
        file_path = os.path.join(base_path, file)
        if os.path.exists(file_path):
            load_nodes_from_csv(file_path, label)
        else:
            load_report["nodes"][label] = "❌ No encontrado"
            print(f"⚠️ El archivo {file} no existe.")

def load_all_relationships():
    base_path = "src/csvData"
    relation_files = {
        "relations_purchase.csv": ("User", "Component", "PURCHASED", "name", "name"),
        "relations_categorize.csv": ("Component", "Category", "CATEGORIZED", "name", "name"),
        "relations_supply.csv": ("Provider", "Component", "SUPPLIES", "name", "name"),
        "relations_review.csv": ("Review", "Component", "REVIEWS", "title", "name"),
        "relations_promote.csv": ("Provider", "User", "PROMOTES", "name", "name"),
        "relations_associate.csv": ("Provider", "Category", "ASSOCIATED_WITH", "name", "name"),
        "relations_search.csv": ("User", "Component", "SEARCHED", "name", "name"),
        "relations_wishlist.csv": ("User", "Component", "WANTS", "name", "name"),
        "relations_write.csv": ("User", "Review", "WRITES", "name", "title"),
        "relations_complement.csv": ("Component", "Component", "COMPLEMENTS", "name", "name")
    }

    for file, (from_label, to_label, relation_type, from_key, to_key) in relation_files.items():
        file_path = os.path.join(base_path, file)
        if os.path.exists(file_path):
            load_relationships_from_csv(file_path, relation_type, from_label, to_label, from_key, to_key)
        else:
            load_report["relationships"][relation_type] = "❌ No encontrado"
            print(f"⚠️ Archivo {file} no encontrado.")

if __name__ == "__main__":
    print("Cargando nodos...")
    load_all_nodes()
    print("\nCargando relaciones...")
    load_all_relationships()
    
    print("\n**Reporte de Carga**")
    print("**NODOS:**")
    for node, count in load_report["nodes"].items():
        print(f"  - {node}: {count}")

    print("\n**RELACIONES:**")
    for relation, count in load_report["relationships"].items():
        print(f"  - {relation}: {count}")

    print("\n✅ Carga de datos completada")
