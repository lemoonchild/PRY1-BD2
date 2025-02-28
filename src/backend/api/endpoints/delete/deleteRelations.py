from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Tuple
from utils.dbConnection import get_neo4j_driver

router = APIRouter()
driver = get_neo4j_driver()

class SingleRelationshipDelete(BaseModel):
    from_label: str
    to_label: str
    relationship_type: str
    from_identifier: str
    to_identifier: str

class MultipleRelationshipsDelete(BaseModel):
    from_label: str
    to_label: str
    relationship_type: str
    pairs: List[Tuple[str, str]]  # Lista de (from_identifier, to_identifier)


def get_identifier_key(label: str) -> str:
    return "title" if label == "Review" else "name"


@router.delete("/delete_relationship", tags=["relationships"])
def delete_single_relationship(request: SingleRelationshipDelete):
    from_key = get_identifier_key(request.from_label)
    to_key = get_identifier_key(request.to_label)

    query = f"""
    MATCH (a:{request.from_label})-[r:{request.relationship_type}]->(b:{request.to_label})
    WHERE a.{from_key} = $from_identifier AND b.{to_key} = $to_identifier
    DELETE r
    RETURN count(r) AS deleted_count
    """

    with driver.session() as session:
        result = session.run(query, from_identifier=request.from_identifier, to_identifier=request.to_identifier)
        deleted_count = result.single()["deleted_count"]

    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Relationship not found")

    return {"message": f"{deleted_count} relationship(s) deleted successfully"}


@router.delete("/delete_relationships", tags=["relationships"])
def delete_multiple_relationships(request: MultipleRelationshipsDelete):
    from_key = get_identifier_key(request.from_label)
    to_key = get_identifier_key(request.to_label)

    query = f"""
    UNWIND $pairs AS pair
    MATCH (a:{request.from_label})-[r:{request.relationship_type}]->(b:{request.to_label})
    WHERE a.{from_key} = pair[0] AND b.{to_key} = pair[1]
    DELETE r
    RETURN count(r) AS deleted_count
    """

    with driver.session() as session:
        result = session.run(query, pairs=request.pairs)
        deleted_count = result.single()["deleted_count"]

    return {"message": f"{deleted_count} relationship(s) deleted successfully"}
