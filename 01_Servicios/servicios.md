# BIG DATA APLICADO
## SERVICIOS
### 1. Crear box
1.1: Descargar ISO Ubuntu Server 25.10 desde https://ubuntu.com/download/server/thank-you?version=25.10&architecture=amd64.
1.2: Crear VM en VirtualBox.
1.3: Instalar ISO.
1.4: Configurar parámetros necesarios dentro de la VM (permisos, actualizaciones, guest additions, etc.).
1.5: Empaquetar VM a .box:
```powershell
    vagrant package --base "[nombre_vm_virtualbox]" --output "[nombre_nueva_box].box"
```
1.6: Añadir box al inventario local de Vagrant:
```powershell
    vagrant box add "[nombre_box]" file:///[ruta_absoluta_ubicacion.box]
    # o si tienes problemas con la ruta en windows
    vagrant box add "[nombre_box]" "[ruta_absoluta_ubicacion.box]"
```
### 2. Crear Vagrantfile
2.1: Ejecutar el siguiente comando:
```powershell
    vagrant init
```
2.2: Se generará un nuevo archivo llamado Vagrantfile y dentro de él escribimos el código necesario en lenguaje Ruby para indicarle todas las instrucciones que deberá ejecutar:
```ruby
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

        # --- Desactivar inserción de nueva llave ---
        # config.ssh.insert_key = false
        
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
### 3. Ejecutar Vagrantfile
Abrimos CMD en la misma ruta donde esté ubicado el Vagrantfile e introducimos el siguiente comando para que se lleve a cabo la instalación automatizada:
```powershell
    vagrant up
```
### 4. Conectarnos a la VM
En la misma consola abierta que hemos usado en el paso anterior:
```powershell
    vagrant ssh
```
### 5. Levantar el servicio
Una vez conectados a la VM, en la misma consola:
```powershell
    uvicorn
```
### RESOLUCIÓN DE PROBLEMAS
#### 1. Error a la hora de crear una nueva VM y no coincide la private key:
Borramos el contenido de los siguientes directorios:
- Carpeta ```.vagrant``` creada cuando se ejecutó ```vagrant up```.
- Contenido de la carpeta ```.ssh```:
```powershell
C:\Users\[tu_nombre_de_usuario]\.ssh
```
- Máquina virtual que se creó cuando se ejecutó ```vagrant up```:
```powershell
C:\Users\[tu_nombre_de_usuario]\VirtualBox VMs\[nombre_vm]
```
- Claves privadas almacenadas relacionadas (ojo con lo que eliminas):
```powershell
C:\Users\[tu_nombre_de_usuario]\.vagrant.d\insecure_private_keys
```