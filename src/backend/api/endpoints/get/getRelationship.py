from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from utils.dbConnection import get_neo4j_driver

router = APIRouter()
driver = get_neo4j_driver()

def get_identifier_key(label: str) -> str:
    """
    Devuelve la key de identificador según el label.
    - Reviews usan `title`
    - Los demás usan `name`
    """
    return "title" if label == "Review" else "name"


@router.get("/properties", tags=["relationships"])
def get_relationship_properties(
    from_label: str = Query(..., description="Label del nodo origen"),
    to_label: str = Query(..., description="Label del nodo destino"),
    relationship_type: str = Query(..., description="Tipo de relación (en mayúsculas)"),
    from_value: str = Query(..., description="Identificador (name/title) del nodo origen"),
    to_value: str = Query(..., description="Identificador (name/title) del nodo destino")
):
    """
    Obtiene las propiedades de una relación específica entre dos nodos.
    """

    from_key = get_identifier_key(from_label)
    to_key = get_identifier_key(to_label)

    query = f"""
    MATCH (a:{from_label})-[r:{relationship_type}]->(b:{to_label})
    WHERE a.{from_key} = $from_value AND b.{to_key} = $to_value
    RETURN properties(r) AS properties
    """

    with driver.session() as session:
        result = session.run(query, from_value=from_value, to_value=to_value)
        record = result.single()

    if not record:
        raise HTTPException(status_code=404, detail=f"No se encontró la relación {relationship_type} entre {from_label} '{from_value}' y {to_label} '{to_value}'.")

    properties = record.get("properties", {})

    return {"properties": properties}
