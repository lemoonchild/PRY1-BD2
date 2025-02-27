from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from utils.dbConnection import get_neo4j_driver

router = APIRouter()
driver = get_neo4j_driver()

# Definir los labels y las claves asociadas
LABEL_KEY_MAP = {
    "Component": "name",
    "Category": "name",
    "Provider": "name",
    "User": "name",
    "Review": "title"  # Solo los nodos de Review usan 'title' en vez de 'name'
}

# 📌 Modelo Pydantic para la creación de relaciones con propiedades
class RelationshipWithProperties(BaseModel):
    from_label: str  # Label del nodo origen
    from_value: str  # Valor de la clave del nodo origen

    to_label: str  # Label del nodo destino
    to_value: str  # Valor de la clave del nodo destino

    relation_type: str  # Tipo de relación
    properties: dict  # Propiedades de la relación

# Endpoint para crear una relación con al menos 3 propiedades
@router.post("/create-relationship", tags=["relationships"])
def create_relationship(rel: RelationshipWithProperties):
    """
    Crea una relación entre dos nodos existentes con la clave correcta.
    - Busca nodos por 'name' si son Component, Category, Provider, User.
    - Busca nodos por 'title' si son Review.
    - Crea la relación solo si se encuentran ambos nodos.
    - La relación debe incluir al menos 3 propiedades.
    """
    if rel.from_label not in LABEL_KEY_MAP or rel.to_label not in LABEL_KEY_MAP:
        raise HTTPException(status_code=400, detail="Label inválido. Debe ser Component, Category, Provider, User o Review.")

    from_key = LABEL_KEY_MAP[rel.from_label]
    to_key = LABEL_KEY_MAP[rel.to_label]

    if len(rel.properties) < 3:
        raise HTTPException(status_code=400, detail="Se requieren al menos 3 propiedades para la relación.")

    # Construcción dinámica de la consulta
    props_str = ", ".join([f"r.{k} = ${k}" for k in rel.properties.keys()])

    query = f"""
    MATCH (a:{rel.from_label} {{{from_key}: $from_value}}), 
          (b:{rel.to_label} {{{to_key}: $to_value}})
    CREATE (a)-[r:{rel.relation_type}]->(b)
    SET {props_str}
    RETURN r
    """

    with driver.session() as session:
        result = session.run(query, from_value=rel.from_value, to_value=rel.to_value, **rel.properties)
        record = result.single()

    if not record:
        raise HTTPException(status_code=404, detail="No se pudieron encontrar los nodos o crear la relación.")

    return {"message": "Relación creada exitosamente", "relationship": record["r"]}
