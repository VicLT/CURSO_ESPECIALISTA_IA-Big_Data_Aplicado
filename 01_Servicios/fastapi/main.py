import random
from fastapi import FastAPI
from pydantic import BaseModel

class ClientRequest(BaseModel):
    name: str

class ClientResponse(BaseModel):
    id: int
    name: str

app = FastAPI(
    title="Big Data Aplicado - Servicios",
    description="Crear un servicio con FastAPI que sea capaz de recoger un json con nombre de cliente y devuelva un id aleatorio",
    version="0.0.1"
)

@app.post("/generate-id", response_model=ClientResponse)
def generate_client_id(client: ClientRequest):
    return {"id": random.randint(1, 1000), "name": client.name}

@app.post("/generate-id/{name}", response_model=ClientResponse)
def generate_client_id(name: str):
    return {"id": random.randint(1, 1000), "name": name}

#import json, random
#from fastapi import FastAPI, HTTPException
#from pydantic import BaseModel
#from typing import List
#
#DB_FILE = "db.json"
#
#def load_db() -> List[dict]:
#    try:
#        with open(DB_FILE, 'r') as file:
#            return json.load(file)
#    except FileNotFoundError:
#        return []
#    
#class ClientRequest(BaseModel):
#    name: str # JSON que recibimos del cliente
#
#class ClientResponse(BaseModel):
#    """Modelo para la lectura (salida/almacenamiento)."""
#    id: int # ID aleatorio que vamos a devolver
#    name: str # Nombre recibido
#
#app = FastAPI(
#    title="Big Data Aplicado - Servicios",
#    description="Crear un servicio con FastAPI que sea capaz de recoger un json con nombre de #cliente y devuelva un id aleatorio",
#    version="0.0.1"
#)
#
#db = load_db()
#
#@app.get("/")
#def read_root():
#    return {"status": "API funcionando", "database_items": len(db)}
#
#@app.get("/clients", response_model=List[ClientRequest])
#def read_items():
#    return db
#
#@app.post("/generate-id", response_model=ClientResponse)
#def generate_client_id(client: ClientRequest):
#    # Recibe un JSON con el nombre del cliente y devuelve un ID aleatorio
#    random_id = random.randint(1, 1000) # Genera un ID aleatorio
#    return {"id": random_id, "name": client.name}
#
#@app.post("/search/{name}", response_model=ClientRequest)
#def search_client(name: str):
#    client = next(
#        filter(lambda x: x["name"].strip().lower() == name.strip().lower(), db),
#        None
#    )
#
#    if client is None:
#        raise HTTPException(status_code=404, detail="Cliente no encontrado")
#    
#    return {"name": client["name"], "id": random.randint(1, 1000)}