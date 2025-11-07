import json, random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

DB_FILE = "db.json"

def load_db() -> List[dict]:
    try:
        with open(DB_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    
class ItemBase(BaseModel):
    """Modelo base con campos comunes."""
    name: str

class Item(ItemBase):
    """Modelo para la lectura (salida/almacenamiento)."""
    id: int

app = FastAPI(
    title="Big Data Aplicado - Servicios",
    description="Crear un servicio con FastAPI que sea capaz de recoger un json con nombre de cliente y devuelva un id aleatorio",
    version="0.0.1"
)

db = load_db()

@app.get("/")
def read_root():
    return {"status": "API funcionando", "database_items": len(db)}

@app.get("/clients", response_model=List[ItemBase])
def read_items():
    return db

@app.post("/search/{name}", response_model=Item)
def search_client(name: str):
    client = next(
        filter(lambda x: x["name"].strip().lower() == name.strip().lower(), db),
        None
    )

    if client is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return {"name": client["name"], "id": random.randint(1, 1000)}