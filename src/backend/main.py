from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.endpoints.get import getNodes
from api.endpoints.get import getRelationship
from api.endpoints.post import createNodes, createRelationships
from api.endpoints.patch import patchNodes, putPropRelationship, updatePropRelationship
from api.endpoints.delete import deleteNodes, deleteRelations, deletePropRelationship

import uvicorn

app = FastAPI(title="Neo4j API", description="API para gestionar nodos y relaciones en Neo4j.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(getNodes.router, prefix="/nodes", tags=["Nodes"])

app.include_router(getRelationship.router, prefix="/relationships", tags=["Relationships"])

app.include_router(createNodes.router, prefix="/nodes", tags=["Nodes"])

app.include_router(createRelationships.router, prefix="/relationships", tags=["Relationships"])

app.include_router(patchNodes.router, prefix="/nodes", tags=["Nodes"])

app.include_router(putPropRelationship.router, prefix="/relationships", tags=["Relationships"])  

app.include_router(updatePropRelationship.router, prefix="/relationships", tags=["Relationships"])  

app.include_router(deleteNodes.router, prefix="/nodes", tags=["Nodes"])

app.include_router(deleteRelations.router, prefix="/relationships", tags=["Relationships"])

app.include_router(deletePropRelationship.router, prefix="/relationships", tags=["Relationships"])

@app.get("/")
def read_root():
    return {"message": "Bienvenido a la API de Neo4j"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
