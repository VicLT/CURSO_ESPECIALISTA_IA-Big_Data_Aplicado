from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel
from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Dict
from pathlib import Path
import json

# ------------------------------ Modelos Pydantic ------------------------------

class ItemBase(BaseModel):
    """Modelo base con los campos comunes de un ítem."""
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


class ItemCreate(ItemBase):
    """Modelo que se usa para crear o actualizar ítems (sin ID)."""
    pass


class Item(ItemBase):
    """Modelo de salida, incluye el ID asignado por el servidor."""
    id: int


# ---------------------------- Funciones auxiliares ----------------------------

def get_db_path() -> Path:
    """Devuelve la ruta absoluta del archivo JSON que simula la base de datos."""
    return Path(__file__).parent / "database.json"


def load_db() -> List[Dict]:
    """
    Carga los datos desde 'database.json' si existe,
    o devuelve una lista vacía si no existe o está vacío.
    """
    json_path = get_db_path()
    if not json_path.exists() or json_path.stat().st_size == 0:
        print("'database.json' no existe o está vacío. Iniciando con lista vacía.")
        return []
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Error: 'database.json' no contiene JSON válido.")
        return []


def save_db(data: List[Dict]) -> None:
    """Guarda los datos actuales en 'database.json' con formato legible."""
    json_path = get_db_path()
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# ---------------------------------- Lifespan ----------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Carga la base de datos al iniciar y la deja disponible en app.state."""
    app.state.db = load_db()
    print(f"Base de datos cargada: {len(app.state.db)} elementos")
    yield
    print("Cerrando aplicación...")


# ------------------------------- Inicialización -------------------------------

app = FastAPI(
    title="API con Lifespan y CRUD",
    description="Gestión de ítems con FastAPI y almacenamiento en JSON.",
    version="1.0.0",
    lifespan=lifespan,
)

# --------------------------------- Endpoints ---------------------------------

@app.get("/")
def read_root():
    """Endpoint raíz de prueba."""
    return {"status": "API funcionando correctamente"}


@app.get("/items/", response_model=List[Item])
def read_items(request: Request, max_price: float | None = Query(None, gt=0)):
    """Devuelve todos los ítems, o filtra por precio máximo si se indica."""
    db = request.app.state.db
    if max_price is not None:
        return [item for item in db if item["price"] <= max_price]
    return db


@app.get("/items/{item_id}", response_model=Item)
def read_item(request: Request, item_id: int):
    """Devuelve un ítem por su ID."""
    db = request.app.state.db
    item = next((x for x in db if x["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    return item


@app.post("/items/", response_model=Item, status_code=201)
def create_item(request: Request, item: ItemCreate):
    """Crea un nuevo ítem y lo guarda en el JSON."""
    db = request.app.state.db
    new_id = max((i["id"] for i in db), default=0) + 1
    new_item = item.model_dump()
    new_item["id"] = new_id
    db.append(new_item)
    save_db(db)
    return new_item


@app.put("/items/{item_id}", response_model=Item)
def update_item(request: Request, item_id: int, item_update: ItemCreate):
    """Actualiza (reemplaza) un ítem por su ID."""
    db = request.app.state.db

    # Buscar índice del ítem
    index = next((i for i, item in enumerate(db)
                  if item["id"] == item_id), None)
    if index is None:
        raise HTTPException(status_code=404, detail="Item no encontrado")

    # Crear nuevo objeto preservando el ID
    updated_item = item_update.model_dump()
    updated_item["id"] = item_id

    # Reemplazar en la lista
    db[index] = updated_item
    save_db(db)

    return updated_item


@app.delete("/items/{item_id}", status_code=200)
def delete_item(request: Request, item_id: int):
    """Elimina un ítem por su ID."""
    db = request.app.state.db

    # Verificar existencia
    if not any(item["id"] == item_id for item in db):
        raise HTTPException(status_code=404, detail="Item no encontrado")

    # Filtrar lista y sobrescribir
    new_db = [item for item in db if item["id"] != item_id]
    request.app.state.db = new_db
    save_db(new_db)

    return {"detail": f"Item con ID {item_id} eliminado correctamente"}
