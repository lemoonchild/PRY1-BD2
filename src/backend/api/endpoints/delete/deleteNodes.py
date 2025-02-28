from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from utils.dbConnection import get_neo4j_driver

router = APIRouter()
driver = get_neo4j_driver()

class SingleNodeDelete(BaseModel):
    label: str
    identifier_value: str

class MultipleNodesDelete(BaseModel):
    label: str
    identifier_values: List[str]


def get_identifier_key(label: str) -> str:
    if label == "Review":
        return "title"
    else:
        return "name"


@router.delete("/delete_node", tags=["nodes"])
def delete_single_node(request: SingleNodeDelete):
    identifier_key = get_identifier_key(request.label)
    query = f"""
    MATCH (n:{request.label} {{{identifier_key}: $identifier_value}})
    DETACH DELETE n
    RETURN count(n) AS deleted_count
    """
    
    with driver.session() as session:
        result = session.run(query, identifier_value=request.identifier_value)
        deleted_count = result.single()["deleted_count"]
    
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Node not found")

    return {"message": f"{deleted_count} node(s) deleted successfully"}


@router.delete("/delete_nodes", tags=["nodes"])
def delete_multiple_nodes(request: MultipleNodesDelete):
    identifier_key = get_identifier_key(request.label)
    query = f"""
    MATCH (n:{request.label})
    WHERE n.{identifier_key} IN $identifier_values
    DETACH DELETE n
    RETURN count(n) AS deleted_count
    """
    
    with driver.session() as session:
        result = session.run(query, identifier_values=request.identifier_values)
        deleted_count = result.single()["deleted_count"]

    return {"message": f"{deleted_count} node(s) deleted successfully"}
