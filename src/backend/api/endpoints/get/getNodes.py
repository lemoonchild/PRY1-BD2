from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from utils.dbConnection import get_neo4j_driver

router = APIRouter()
driver = get_neo4j_driver()

@router.get("/", tags=["nodes"])  
def get_nodes(
    label: Optional[str] = Query(None, description="Etiqueta del nodo, por ejemplo 'Component'"),
    prop: Optional[str] = Query(None, description="Nombre de la propiedad a filtrar, por ejemplo 'price'"),
    value: Optional[str] = Query(None, description="Valor de la propiedad para el filtro")
):
    """
    Retorna nodos filtrados:
      - Si se pasan parámetros (label, prop y value), retorna los nodos que cumplan el filtro.
      - Si no se pasan, retorna una vista general de todos los nodos (limitado a 100 por ejemplo).
    """
    if label:
        query = f"MATCH (n:{label})"
    else:
        query = "MATCH (n)"

    if prop and value:
        try:
            if "." in value: 
                value = float(value)
            else:  
                value = int(value)
        except ValueError:
            pass  

        query += f" WHERE n.{prop} = $value"
    
    query += " RETURN n LIMIT 100"

    with driver.session() as session:
        result = session.run(query, value=value)
        nodes = [record["n"] for record in result]

    return nodes


@router.get("/{name}", tags=["nodes"])
def get_node_by_name(name: str, label: Optional[str] = Query(None, description="Etiqueta del nodo, si se conoce")):
    """
    Retorna un nodo específico identificado por su nombre.
    Si se pasa el parámetro 'label', se restringe la búsqueda a esa etiqueta.
    """
    if label:
        query = f"MATCH (n:{label} {{name: $name}}) RETURN n"
    else:
        query = "MATCH (n {name: $name}) RETURN n"
    
    with driver.session() as session:
        result = session.run(query, name=name)
        record = result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Node not found")
        return record["n"]
    
@router.get("/aggregates", tags=["nodes"])
def get_node_aggregates(label: Optional[str] = None):
    """
    Retorna datos agregados de nodos, por ejemplo:
      - Conteo total de nodos.
      - Conteo de nodos por label.
      - Promedios o sumas de propiedades numéricas.
    """
    if label:
        query = f"MATCH (n:{label}) RETURN count(n) AS total"
    else:
        query = "MATCH (n) RETURN count(n) AS total"
    
    with driver.session() as session:
        result = session.run(query)
        total = result.single()["total"]
    
    return {"total_nodes": total}
