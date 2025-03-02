from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Tuple, Any
from utils.dbConnection import get_neo4j_driver

router = APIRouter()
driver = get_neo4j_driver()

class UpdateSingleRelationshipProperties(BaseModel):
    from_label: str
    to_label: str
    relationship_type: str
    from_identifier: str
    to_identifier: str
    properties: Dict[str, Any]

class UpdateMultipleRelationshipsProperties(BaseModel):
    from_label: str
    to_label: str
    relationship_type: str
    pairs: List[Tuple[str, str]]  # Cada tupla es (from_identifier, to_identifier)
    properties: Dict[str, Any]

def get_identifier_key(label: str) -> str:
    return "title" if label == "Review" else "name"

# Actualizar propiedades de UNA relación
@router.patch("/update_properties_in_relationship", tags=["relationships"])
def update_properties_in_relationship(request: UpdateSingleRelationshipProperties):
    from_key = get_identifier_key(request.from_label)
    to_key = get_identifier_key(request.to_label)

    set_statements = ", ".join([f"r.{k} = $prop_{k}" for k in request.properties])

    query = f"""
    MATCH (a:{request.from_label})-[r:{request.relationship_type}]->(b:{request.to_label})
    WHERE a.{from_key} = $from_identifier AND b.{to_key} = $to_identifier
    SET {set_statements}
    RETURN r
    """

    parameters = {
        "from_identifier": request.from_identifier,
        "to_identifier": request.to_identifier,
    }

    for k, v in request.properties.items():
        parameters[f"prop_{k}"] = v

    with driver.session() as session:
        result = session.run(query, **parameters)
        record = result.single()

    if not record:
        raise HTTPException(status_code=404, detail="Relationship not found")

    return {"message": "Properties updated successfully", "updated_relationship": record["r"]}


# Actualizar propiedades de MÚLTIPLES relaciones
@router.patch("/update_properties_in_multiple_relationships", tags=["relationships"])
def update_properties_in_multiple_relationships(request: UpdateMultipleRelationshipsProperties):
    from_key = get_identifier_key(request.from_label)
    to_key = get_identifier_key(request.to_label)

    set_statements = ", ".join([f"r.{k} = $prop_{k}" for k in request.properties])

    query = f"""
    UNWIND $pairs AS pair
    MATCH (a:{request.from_label})-[r:{request.relationship_type}]->(b:{request.to_label})
    WHERE a.{from_key} = pair[0] AND b.{to_key} = pair[1]
    SET {set_statements}
    RETURN count(r) AS updated_count
    """

    parameters = {
        "pairs": request.pairs,
    }

    for k, v in request.properties.items():
        parameters[f"prop_{k}"] = v

    with driver.session() as session:
        result = session.run(query, **parameters)
        updated_count = result.single()["updated_count"]

    return {"message": f"{updated_count} relationship(s) updated successfully"}
