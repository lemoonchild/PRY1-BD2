from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.dbConnection import get_neo4j_driver

router = APIRouter()
driver = get_neo4j_driver()

class NodeWithProperties(BaseModel):
    label: str
    properties: dict  # Diccionario de propiedades clave-valor


# Endpoint para crear un nodo con solo una label
@router.post("/create-node", tags=["nodes"])
def create_node(label: str):
    """
    Crea un nodo en la base de datos con solo una etiqueta (sin propiedades).
    """
    query = f"CREATE (n:{label}) RETURN n"
    
    with driver.session() as session:
        result = session.run(query)
        record = result.single()
    
    if not record:
        raise HTTPException(status_code=500, detail="No se pudo crear el nodo.")
    
    return {"message": "Nodo creado exitosamente", "node": record["n"]}


# Endpoint para crear un nodo con 5+ propiedades
@router.post("/create-node-with-properties", tags=["nodes"])
def create_node_with_properties(node: NodeWithProperties):
    """
    Crea un nodo con una etiqueta y al menos 5 propiedades.
    """
    if len(node.properties) < 5:
        raise HTTPException(status_code=400, detail="Se requieren al menos 5 propiedades.")
    
    # Construcción dinámica de la consulta
    props_str = ", ".join([f"n.{k} = ${k}" for k in node.properties.keys()])
    query = f"CREATE (n:{node.label}) SET {props_str} RETURN n"

    with driver.session() as session:
        result = session.run(query, **node.properties)
        record = result.single()
    
    if not record:
        raise HTTPException(status_code=500, detail="No se pudo crear el nodo.")
    
    return {"message": "Nodo con propiedades creado exitosamente", "node": record["n"]}
