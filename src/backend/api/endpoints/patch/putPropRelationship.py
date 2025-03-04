from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Tuple, Any
from utils.dbConnection import get_neo4j_driver

router = APIRouter()
driver = get_neo4j_driver()

class PutSingleRelationshipProperties(BaseModel):
    from_label: str
    to_label: str
    relationship_type: str
    from_identifier: str
    to_identifier: str
    properties: Dict[str, Any]

class PutMultipleRelationshipsProperties(BaseModel):
    from_label: str
    to_label: str
    relationship_type: str
    pairs: List[Tuple[str, str]]
    properties: Dict[str, Any]

def get_identifier_key(label: str) -> str:
    return "title" if label == "Review" else "name"

@router.patch("/add_properties_to_relationship", tags=["relationships"])
def add_properties_to_relationship(request: PutSingleRelationshipProperties):
    from_key = get_identifier_key(request.from_label)
    to_key = get_identifier_key(request.to_label)

    query = f"""
    MATCH (a:{request.from_label})-[r:{request.relationship_type}]->(b:{request.to_label})
    WHERE a.{from_key} = $from_identifier AND b.{to_key} = $to_identifier
    SET r += $properties
    RETURN r
    """
    with driver.session() as session:
        result = session.run(query, from_identifier=request.from_identifier, to_identifier=request.to_identifier, properties=request.properties)
        record = result.single()

    if not record:
        raise HTTPException(status_code=404, detail="Relationship not found")

    return {"message": "Properties added successfully", "updated_relationship": record["r"]}


@router.patch("/add_properties_to_multiple_relationships", tags=["relationships"])
def add_properties_to_multiple_relationships(request: PutMultipleRelationshipsProperties):
    from_key = get_identifier_key(request.from_label)
    to_key = get_identifier_key(request.to_label)

    query = f"""
    UNWIND $pairs AS pair
    MATCH (a:{request.from_label})-[r:{request.relationship_type}]->(b:{request.to_label})
    WHERE a.{from_key} = pair[0] AND b.{to_key} = pair[1]
    SET r += $properties
    RETURN count(r) AS updated_count
    """

    with driver.session() as session:
        result = session.run(query, pairs=request.pairs, properties=request.properties)
        updated_count = result.single()["updated_count"]

    return {"message": f"{updated_count} relationship(s) updated successfully"}
