from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Union
from utils.dbConnection import get_neo4j_driver

router = APIRouter()
driver = get_neo4j_driver()

# Modelo para recibir las actualizaciones
class UpdateNodeProperties(BaseModel):
    label: str
    identifier_key: str
    identifier_value: str
    properties: Dict[str, Union[str, int, float, bool]]

class UpdateMultipleNodesProperties(BaseModel):
    label: str
    identifier_key: str
    identifier_values: List[str]
    properties: Dict[str, Union[str, int, float, bool]]

class DeleteNodeProperties(BaseModel):
    label: str
    identifier_key: str
    identifier_value: str
    properties: List[str]

class DeleteMultipleNodesProperties(BaseModel):
    label: str
    identifier_key: str
    identifier_values: List[str]
    properties: List[str]


# Agregar propiedades a un nodo
@router.patch("/add_properties", tags=["nodes"])
def add_properties_to_node(request: UpdateNodeProperties):
    """
    Agrega una o más propiedades a un nodo específico.
    """
    query = f"""
    MATCH (n:{request.label} {{{request.identifier_key}: $identifier_value}})
    SET n += $properties
    RETURN n
    """
    
    with driver.session() as session:
        result = session.run(query, identifier_value=request.identifier_value, properties=request.properties)
        node = result.single()
        
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
    
    return {"message": "Properties added successfully", "updated_node": node["n"]}


# Agregar propiedades a múltiples nodos
@router.patch("/add_properties_multiple", tags=["nodes"])
def add_properties_to_multiple_nodes(request: UpdateMultipleNodesProperties):
    """
    Agrega una o más propiedades a múltiples nodos.
    """
    query = f"""
    MATCH (n:{request.label})
    WHERE n.{request.identifier_key} IN $identifier_values
    SET n += $properties
    RETURN count(n) AS updated_count
    """
    
    with driver.session() as session:
        result = session.run(query, identifier_values=request.identifier_values, properties=request.properties)
        updated_count = result.single()["updated_count"]
    
    return {"message": "Properties added successfully", "nodes_updated": updated_count}


# Actualizar propiedades de un nodo
@router.patch("/update_properties", tags=["nodes"])
def update_properties_of_node(request: UpdateNodeProperties):
    """
    Actualiza una o más propiedades de un nodo específico.
    """
    query = f"""
    MATCH (n:{request.label} {{{request.identifier_key}: $identifier_value}})
    SET n += $properties
    RETURN n
    """
    
    with driver.session() as session:
        result = session.run(query, identifier_value=request.identifier_value, properties=request.properties)
        node = result.single()
        
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
    
    return {"message": "Properties updated successfully", "updated_node": node["n"]}


# Actualizar propiedades de múltiples nodos
@router.patch("/update_properties_multiple", tags=["nodes"])
def update_properties_of_multiple_nodes(request: UpdateMultipleNodesProperties):
    """
    Actualiza una o más propiedades en múltiples nodos.
    """
    query = f"""
    MATCH (n:{request.label})
    WHERE n.{request.identifier_key} IN $identifier_values
    SET n += $properties
    RETURN count(n) AS updated_count
    """
    
    with driver.session() as session:
        result = session.run(query, identifier_values=request.identifier_values, properties=request.properties)
        updated_count = result.single()["updated_count"]
    
    return {"message": "Properties updated successfully", "nodes_updated": updated_count}


# Eliminar propiedades de un nodo
@router.patch("/remove_properties", tags=["nodes"])
def remove_properties_from_node(request: DeleteNodeProperties):
    """
    Elimina una o más propiedades de un nodo.
    """
    remove_statements = ", ".join([f"n.{prop}" for prop in request.properties])
    query = f"""
    MATCH (n:{request.label} {{{request.identifier_key}: $identifier_value}})
    REMOVE {remove_statements}
    RETURN n
    """
    
    with driver.session() as session:
        result = session.run(query, identifier_value=request.identifier_value)
        node = result.single()
        
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
    
    return {"message": "Properties removed successfully", "updated_node": node["n"]}


# Eliminar propiedades de múltiples nodos
@router.patch("/remove_properties_multiple", tags=["nodes"])
def remove_properties_from_multiple_nodes(request: DeleteMultipleNodesProperties):
    """
    Elimina una o más propiedades de múltiples nodos.
    """
    remove_statements = ", ".join([f"n.{prop}" for prop in request.properties])
    query = f"""
    MATCH (n:{request.label})
    WHERE n.{request.identifier_key} IN $identifier_values
    REMOVE {remove_statements}
    RETURN count(n) AS updated_count
    """
    
    with driver.session() as session:
        result = session.run(query, identifier_values=request.identifier_values)
        updated_count = result.single()["updated_count"]
    
    return {"message": "Properties removed successfully", "nodes_updated": updated_count}
