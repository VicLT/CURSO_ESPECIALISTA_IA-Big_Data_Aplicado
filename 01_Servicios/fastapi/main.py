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