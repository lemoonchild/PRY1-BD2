from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from utils.dbConnection import get_neo4j_driver

router = APIRouter()
driver = get_neo4j_driver()

class RemovePropertiesFromSingleRelationship(BaseModel):
    from_label: str
    to_label: str
    relationship_type: str
    from_identifier: str
    to_identifier: str
    properties: List[str]

class RemovePropertiesFromMultipleRelationships(BaseModel):
    from_label: str
    to_label: str
    relationship_type: str
    pairs: List[List[str]]  # Cada sublista es ["from_identifier", "to_identifier"]
    properties: List[str]

def get_identifier_key(label: str) -> str:
    return "title" if label == "Review" else "name"

@router.delete("/remove_properties_from_relationship", tags=["relationships"])
def remove_properties_from_relationship(request: RemovePropertiesFromSingleRelationship):
    from_key = get_identifier_key(request.from_label)
    to_key = get_identifier_key(request.to_label)

    remove_statements = " ".join([f"REMOVE r.{prop}" for prop in request.properties])

    query = f"""
    MATCH (a:{request.from_label})-[r:{request.relationship_type}]->(b:{request.to_label})
    WHERE a.{from_key} = $from_identifier AND b.{to_key} = $to_identifier
    {remove_statements}
    RETURN r
    """

    with driver.session() as session:
        result = session.run(query, from_identifier=request.from_identifier, to_identifier=request.to_identifier)
        record = result.single()

    if not record:
        raise HTTPException(status_code=404, detail="Relationship not found")

    return {"message": "Properties removed successfully", "updated_relationship": record["r"]}

@router.delete("/remove_properties_from_multiple_relationships", tags=["relationships"])
def remove_properties_from_multiple_relationships(request: RemovePropertiesFromMultipleRelationships):
    from_key = get_identifier_key(request.from_label)
    to_key = get_identifier_key(request.to_label)

    remove_statements = " ".join([f"REMOVE r.{prop}" for prop in request.properties])

    query = f"""
    UNWIND $pairs AS pair
    MATCH (a:{request.from_label})-[r:{request.relationship_type}]->(b:{request.to_label})
    WHERE a.{from_key} = pair[0] AND b.{to_key} = pair[1]
    {remove_statements}
    RETURN count(r) AS updated_count
    """

    with driver.session() as session:
        result = session.run(query, pairs=request.pairs)
        updated_count = result.single()["updated_count"]

    return {"message": f"{updated_count} relationship(s) updated successfully"}