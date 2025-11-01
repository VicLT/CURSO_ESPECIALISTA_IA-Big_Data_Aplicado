# --------------------------- MÓDULO 2: INTRODUCCIÓN ---------------------------

# from fastapi import FastAPI

# 2. Crear una instancia de FastAPI
# app = FastAPI(
    # title="API del curso",
    # description="Esta es una API de prueba para el curso de FastAPI.",
    # version="0.1.0"
# )

# 3. Definir el "decorador" de la operación de ruta
# @app: Se refiere a nuestra instancia
# .get: Es el método HTTP (el "verbo" REST)
# ("/"): Es la URI (la "ruta" o "path")
# @app.get("/")
# def read_root():
    # Endpoint raíz de la API.
    # 4. La función que se ejecuta
    # FastAPI convertirá automáticamente este diccionario de Python en una respuesta JSON
    # return {"Hello": "World", "message": "Bienvenido a nuestra API"}

# @app.get("/items/{item_id}")
# def read_item(item_id):
    # FastAPI pasa el valor de la URL como argumento con el nombre en la ruta
    # El nombre del argumento DEBE coincidir con el nombre en la ruta
    # return {"item_id_recibido": item_id}

# @app.get("/items/{item_id}")
# def read_item(item_id: int): # <--- ¡HEMOS AÑADIDO: 'int'!
    # Ahora, FastAPI solo pasa el valor, sino que
    # 1. VALIDA que sea un entero.\
    # 2. CONVIERTE el string "5" al entero "5"
    # return {"item_id_recibido": item_id, "es_entero": isinstance(item_id, int)}

# @app.get("/items/{item_id}")
# def read_item(item_id: int):
    # Endpoint para leer un ítem por su ID (debe ser un entero).
    # - **item_id**: El ID del ítem a recuperar (obligatorio).
    # return {"item_id": item_id, "tipo_dato": str(type(item_id))}

# @app.get("/users/{user_name}")
# def read_user(user_name: str):
    # Endpoint para leer un usuario por su nombre.
    # - **user_name**: El nombre del usuario (obligatorio).
    # return {"user_name": user_name, "tipo_dato": str(type(user_name))}

# ----------------------------- MÓDULO 3: PYDANTIC -----------------------------

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# 1. Definimos nuestro "schema" como una clase
class ItemBase(BaseModel):
    # Modelo base con campos comunes
    name: str
    description: str | None = None # Python 3.10+ (o Optional[str] = None)
    price: float
    tax: float | None = None

# 2. Crear el modelo de entrada (ItemCreate)
class ItemCreate(ItemBase):
    # Por ahora no tiene campos extra.
    # Es exactamente lo que el cliente debe proveer.
    pass

# Paso 3: Crear el modelo de salida/almacenamiento (item)
class Item(ItemBase):
    id: int
    # Podríamos tener otros campos generador por el servidor como owner_id, created_at, etc.

# Instancia de la app y BBDD (simulada)
app = FastAPI(
    title="API Módulo 3",
    description="API con validación de Pydantic",
    version="0.3.0"
)

# Simulación de nuestra BBDD
db_items = {}

# --- Endpoints ---
@app.get("/")
def read_root():
    return {"status": "API funcionando"}

@app.post("/items/", response_model=Item)
def create_item(item: ItemCreate):
    # 1. FastAPI recibe el JSON del body.
    # 2. Intenta validarlo contra el modelo 'ItemCreate'.
    # 3. Si falla -> Devuelve un error 422 automático.
    # 4. Si tiene éxito -> 'item' es una instancia de Pydantic 'ItemCreate'.

    # Ahora podemos trabajar con 'item' como un objeto de Python
    print(f"Creando ítem: {item.name}")
    print(f"Precio: {item.price}")

    # Lógica para "guardarlo" (simulación)
    new_id = len(db_items) + 1

    # Convertimos el modelo Pydantic a un dict para guardarlo
    # .model_dump() es el reemplazo moderno de .dict()
    db_item_data = item.model_dump()
    db_item_data["id"] = new_id # Le asignamos el ID

    # "Guardamos" en la BBDD
    db_items[new_id] = db_item_data

    # FastAPI validará este dict contra 'response_model=Item'
    return db_item_data

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    """
    Lee un ítem por su ID.
    (Aún no maneja errores 404, eso es en módulo 4)
    """
    if item_id in db_items:
        return db_items[item_id]
    
    # Temporal (en el módulo 4 usaremos HTTPException)
    return {"error": "Item not found"}

# ------------------------------- MÓDULO 4: CRUD -------------------------------

from fastapi import Query

# GET/items/ (Leer todos)
@app.get("/items/", response_model=list[Item])
def read_items(max_price: float | None = Query(None, gt=0)):
    """
    Lee todos los ítems de la base de datos.
    - **max_price** (opcional): Filtra ítems con un precio menor o igual.
    """
    if max_price:
        # ¡List comprehension!
        # Filtramos la BBDD en memoria.
        filtered_items = [
            item
            for item in db
            if item["price"] <= max_price
        ]
        return filtered_items
    
# GET/items/{item_id} (Leer uno)
@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    # Usamos filter() y una lambda. filter() devuelve un iterador.
    # next(..., None) toma el primer resultad o devuelve None si no hay.
    item = next(filter(lambda x: x["id"] == item_id, db), None)

    if item is None:
        raise HTTPException(status_code=404, detail="Item no encontrado")
    
# POST /items/
@app.post("/items/", response_model=Item, status_code=201) # Una creación exitosa debe devolver 201 Created. 
def create_item(item: ItemCreate):
    """
    Crea un nuevo ítem.
    """
    # Lógica para generar un nuevo ID
    # Usamos max() con una list comprehension y un key lambda (o un generador)
    last_id = max((i["id"] for i in db), default=0)
    new_id = last_id + 1

    new_item_data = item.model_dump()
    new_item_data["id"] = new_id

    # "Guardamos" en la BBDD en memoria
    db.append(new_item_data)

    # Guardamos en el archivo JSON
    save_db(db)

    return new_item_data