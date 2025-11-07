# BIG DATA APLICADO
## SERVICIOS
### 1. Creación box
1.1: Descargar ISO desde https://ubuntu.com/download/server/thank-you?version=25.10&architecture=amd64
1.2: Instalar imagen con Virtual Box.
1.3: Configurar hardware de la máquina virtual (cores, ram, adaptador de red, etc.)
1.4: Configurar parámetros necesarios dentro de la VM (permisos, actualizaciones, etc.).
1.5: Crear box en base a la VM que acabamos de configurar:
```powershell
    vagrant package --base "ubuntu-25.04-base" --output "ubuntu-25.04.box"
```
1.6: Añadir box al listado de Vagrant:
```powershell
    vagrant box add ubuntu/25.04 file:///C:/ruta/a/ubuntu-25.04.box
```
### 2. Crear Vagrantfile
2.1: Ejecutar el siguiente comando en una nueva carpeta:
```powershell
    vagrant init
```
2.2: Se generará un nuevo archivo llamado Vagrantfile y dentro de él escribimos el código necesario en lenguaje Ruby para indicarle todas las instrucciones que deberá ejecutar:
```python
Vagrant.configure("2") do |config|
    # --- Box base ---
    config.vm.box = "ubuntu_server_25_10"

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
    
    # --- Provisión ---
    config.vm.provision "shell", run: "once" do |s|
        s.inline = <<-SHELL
            apt-get update -y
            apt-get install -y python3 python3-pip

            # Crear el entorno virtual fuera del directorio compartido
            python3 -m venv /opt/venv
            /opt/venv/bin/pip install --upgrade pip
            /opt/venv/bin/pip install fastapi uvicorn
        SHELL
    end
end
```