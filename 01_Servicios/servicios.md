# BIG DATA APLICADO
## SERVICIOS
### 1. Crear, instalar y configurar VM
1.1: Descargar ISO Ubuntu Server 25.10 desde https://ubuntu.com/download/server/thank-you?version=25.10&architecture=amd64.
1.2: Crear VM en VirtualBox e instalar el sistema operativo.
1.3: Ingresar en la VM y ejecutar los siguientes parámetros:
```powershell
# Sudo sin contraseña para vagrant
echo "vagrant ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/vagrant
```
```powershell
# Instalar clave pública "insegura" de Vagrant
sudo mkdir -p /home/vagrant/.ssh
sudo chmod 0700 /home/vagrant/.ssh
sudo wget --no-check-certificate https://raw.githubusercontent.com/hashicorp/vagrant/mainkeys/vagrant.pub -O /home/vagrant/.ssh/authorized_keys
sudo chmod 0600 /home/vagrant/.ssh/authorized_keys
sudo chown -R vagrant:vagrant /home/vagrant/.ssh
```
```powershell
# Instalar Guest Additions (para synced folders, vboxsf)
sudo apt-get update
sudo apt-get install -y build-essential dkms linux-headers-$(uname -r)
# desde la GUI de VirtualBox: Devices → Insert Guest Additions CD
sudo mount /dev/cdrom /mnt
sudo /mnt/VBoxLinuxAdditions.run
sudo reboot
```
```powershell
# Limpiar y compactar disco antes de empaquetar
sudo apt-get clean
sudo dd if=/dev/zero of=/EMPTY bs=1M || true
sudo rm -f /EMPTY
sudo shutdown -h now
```
### 2. Crear box
2.1: Empaquetar VM a .box:
```powershell
vagrant package --base "[nombre_vm_virtualbox]" --output "[nombre_nueva_box].box"
```
2.2: Añadir box al inventario local de Vagrant:
```powershell
vagrant box add "[nombre_box]" file:///[ruta_absoluta_ubicacion.box]
# o si tienes problemas con la ruta en windows
vagrant box add "[nombre_box]" "[ruta_absoluta_ubicacion.box]"
```
2.3: Comprobar importación de la box:
```powershell
vagrant box list
```
### 3. Preparar la API
3.1: Crear ```main.py``` con FastAPI:
```python
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
    
class ClientRequest(BaseModel):
    name: str # JSON que recibimos del cliente

class ClientResponse(BaseModel):
    """Modelo para la lectura (salida/almacenamiento)."""
    id: int # ID aleatorio que vamos a devolver
    name: str # Nombre recibido

app = FastAPI(
    title="Big Data Aplicado - Servicios",
    description="Crear un servicio con FastAPI que sea capaz de recoger un json con nombre de cliente y devuelva un id aleatorio",
    version="0.0.1"
)

db = load_db()

@app.get("/")
def read_root():
    return {"status": "API funcionando", "database_items": len(db)}

@app.get("/clients", response_model=List[ClientRequest])
def read_items():
    return db

@app.post("/generate-id", response_model=ClientResponse)
def generate_client_id(client: ClientRequest):
    # Recibe un JSON con el nombre del cliente y devuelve un ID aleatorio
    random_id = random.randint(1, 1000) # Genera un ID aleatorio
    return {"id": random_id, "name": client.name}

@app.post("/search/{name}", response_model=ClientRequest)
def search_client(name: str):
    client = next(
        filter(lambda x: x["name"].strip().lower() == name.strip().lower(), db),
        None
    )

    if client is None:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    
    return {"name": client["name"], "id": random.randint(1, 1000)}
```
3.2: Crear JSON vacío que hará las veces de BD para persistencia de datos:
```json
[]
```
### 4. Crear Vagrantfile
4.1: Abrimos CMD y generamos un Vagrantfile vacío:
```powershell
vagrant init
```
4.2: Abrimos Vagrantfile y escribimos el código necesario (en lenguaje Ruby) para indicarle todas las instrucciones que deberá ejecutar:
```ruby
NEW_USERNAME = "victorlt"
NEW_PASSWORD = "victorlt"

Vagrant.configure("2") do |config|
    # --- Box base ---
    config.vm.box = "ubuntu_server_25_10_configurada"

    # --- Red ---
    config.vm.network "private_network", ip: "192.168.56.2"
    config.vm.network "forwarded_port", guest: 80, host: 8080

    # --- Carpeta compartida ---
    config.vm.synced_folder "./fastapi", "/home/vagrant"
    
    # --- Hardware ---
    config.vm.provider "virtualbox" do |vb|
        vb.name = "ubuntu_server_vagrant_01"
        vb.memory = "2048"
        vb.cpus = 2
    end

    # --- Usuario ---
    #config.ssh.username = "vagrant"
    #config.ssh.password = "vagrant"

    # --- Deshabilitar la inserción de clave y apuntar a tu privada ---
    #config.ssh.insert_key = true
    #config.ssh.private_key_path = [File.expand_path("~/.ssh/id_rsa")]

    # --- Provisiones ---
    config.vm.provision "shell",
        path: "create_user.sh",
        args: [NEW_USERNAME, NEW_PASSWORD]

    # Clave pública en la VM (file + shell):
    config.vm.provision "file",
    source: File.expand_path("~/.ssh/id_rsa.pub"),
    destination: "/tmp/id_rsa.pub"

    #config.vm.provision "shell", inline: <<-SHELL
        #mkdir -p /home/vagrant/.ssh
        #chmod 700 /home/vagrant/.ssh
        #cat /tmp/id_rsa.pub >> /home/vagrant/.ssh/authorized_keys
        #chmod 600 /home/vagrant/.ssh/authorized_keys
        #chown -R vagrant:vagrant /home/vagrant/.ssh
    #SHELL
    
    config.vm.provision "shell", inline: <<-SHELL
        mkdir -p /home/#{NEW_USERNAME}/.ssh
        chmod 700 /home/#{NEW_USERNAME}/.ssh
        cat /tmp/id_rsa.pub >> /home/#{NEW_USERNAME}/.ssh/authorized_keys
        chmod 600 /home/#{NEW_USERNAME}/.ssh/authorized_keys
        chown -R #{NEW_USERNAME}:#{NEW_USERNAME} /home/#{NEW_USERNAME}/.ssh
    SHELL

    # Solo en la primera ejecución
    config.vm.provision "shell", run: "once" do |s|
        s.inline = <<-SHELL
            sudo add-apt-repository universe
            sudo apt update -y
            sudo apt install -y python3.13 python3.13-venv python3-pip

            # Crear el entorno virtual fuera del directorio compartido
            sudo python3.13 -m venv /opt/venv --without-pip
            sudo /opt/venv/bin/python3 -m ensurepip --upgrade
            sudo /opt/venv/bin/python3 -m pip install --upgrade pip
            sudo /opt/venv/bin/python3 -m pip install fastapi uvicorn
        SHELL
    end
end
```
### 5. Ejecutar Vagrantfile
Abrimos CMD en la misma ruta donde esté ubicado el Vagrantfile e introducimos el siguiente comando para que se lleve a cabo la instalación automatizada:
```powershell
vagrant up
```
### 6. Conectarnos a la VM
En la misma consola abierta que hemos usado en el paso anterior:
```powershell
vagrant ssh
```
### 7. Levantar el servicio
Primero activamos el entorno virtual:
```bash
source /opt/venv/bin/activate
```
Ahora ya podemos levantar el servidor:
```bash
# uvicorn [nombre_archivo_compartido(sin .py)]:[nombre_application] --host 0.0.0.0 --port 8000
uvicorn main:app --host 0.0.0.0 --port 8000
```
### RESOLUCIÓN DE PROBLEMAS
#### 1. Error a la hora de crear una nueva VM y no coincide la private key:
- Eliminar máquina virtual:
```powershell
vagrant destroy -f
    
# Asegúrate de que se ha eliminado correctamente en:
C:\Users\[tu_nombre_de_usuario]\VirtualBox VMs\
```
- Eliminar carpeta ```.vagrant``` que se ha creado en el mismo directorio donde hicimos ```vagrant up```:
- Eliminar contenido de la carpeta ```.ssh```:
```powershell
C:\Users\[tu_nombre_de_usuario]\.ssh

# Si deseas regenerar la clave:
ssh-keygen -t rsa -b 4096
```
- Eliminar claves privadas almacenadas:
```powershell
C:\Users\[tu_nombre_de_usuario]\.vagrant.d\insecure_private_keys
```