from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
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


def get_numeric_properties(label: str) -> list:
    """
    Extrae propiedades numéricas reales (int o float) de un nodo de prueba.
    Si un label no tiene nodos, lanza un error 404.
    """
    query = f"MATCH (n:{label}) RETURN n LIMIT 1"

    with driver.session() as session:
        result = session.run(query)
        record = result.single()

        if not record:
            raise HTTPException(status_code=404, detail=f"No hay nodos con label '{label}'")

        node = record["n"]
        numeric_props = []

        for key, value in dict(node).items():
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                numeric_props.append(key)

        return numeric_props


@router.get("/aggregates", tags=["nodes"])
def get_node_aggregates(label: Optional[str] = None) -> Dict[str, Any]:
    """
    Devuelve:
    - Total de nodos.
    - Si hay label, devuelve promedio (avg), media (median) y moda (mode) de propiedades numéricas.
    """

    if label:
        numeric_props = get_numeric_properties(label)

        if not numeric_props:
            return {"total_nodes": 0, "message": "No hay propiedades numéricas en este tipo de nodo."}

        # Bloques dinámicos para cada métrica
        avg_part = ", ".join([f"avg(n.{prop}) AS avg_{prop}" for prop in numeric_props])
        median_part = ", ".join([f"percentileCont(n.{prop}, 0.5) AS median_{prop}" for prop in numeric_props])

        # Para moda, hacemos un truco: Contamos frecuencia y seleccionamos el más común
        mode_part_list = []
        for prop in numeric_props:
            mode_query = f"""
            OPTIONAL MATCH (n:{label})
            WITH n.{prop} AS value
            WHERE value IS NOT NULL
            RETURN value, count(*) AS frequency
            ORDER BY frequency DESC
            LIMIT 1
            """
            mode_part_list.append((prop, mode_query))

        # Consulta principal para count, avg y median
        query = f"""
        MATCH (n:{label})
        RETURN count(n) AS total, {avg_part}, {median_part}
        """

        response = {}

        with driver.session() as session:
            result = session.run(query)
            record = result.single()

            response["total_nodes"] = record["total"]
            for prop in numeric_props:
                response[f"avg_{prop}"] = record[f"avg_{prop}"]
                response[f"median_{prop}"] = record[f"median_{prop}"]

            # Ejecutamos cada consulta de moda individualmente
            for prop, mode_query in mode_part_list:
                mode_result = session.run(mode_query)
                mode_record = mode_result.single()
                response[f"mode_{prop}"] = mode_record["value"] if mode_record else None

        return response

    else:
        query = "MATCH (n) RETURN count(n) AS total"
        with driver.session() as session:
            result = session.run(query)
            record = result.single()
            return {"total_nodes": record["total"]}

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
    
