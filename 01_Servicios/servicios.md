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
1.7: Comprobar importación de la box:
```powershell
    vagrant box list
```
### 2. Crear Vagrantfile
2.1: Abrimos CMD y generamos un Vagrantfile vacío:
```powershell
    vagrant init
```
2.2: Abrimos Vagrantfile y escribimos el código necesario (en lenguaje Ruby) para indicarle todas las instrucciones que deberá ejecutar:
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
        #config.ssh.insert_key = false
        #config.ssh.private_key_path = [File.expand_path("~/.ssh/id_rsa")]

        # --- Provisiones ---
        config.vm.provision "shell",
            path: "create_user.sh",
            args: [NEW_USERNAME, NEW_PASSWORD]

        # Clave pública en la VM (file + shell):
        #config.vm.provision "file",
            #source: File.expand_path("~/.ssh/id_rsa.pub"),
            #destination: "/tmp/id_rsa.pub"

        #config.vm.provision "shell", inline: <<-SHELL
        #    mkdir -p /home/vagrant/.ssh
        #    chmod 700 /home/vagrant/.ssh
        #    cat /tmp/id_rsa.pub >> /home/vagrant/.ssh/authorized_keys
        #    chmod 600 /home/vagrant/.ssh/authorized_keys
        #    chown -R vagrant:vagrant /home/vagrant/.ssh
        #
        #    mkdir -p /home/#{NEW_USERNAME}/.ssh
        #    chmod 700 /home/#{NEW_USERNAME}/.ssh
        #    cat /tmp/id_rsa.pub >> /home/#{NEW_USERNAME}/.ssh/authorized_keys
        #    chmod 600 /home/#{NEW_USERNAME}/.ssh/authorized_keys
        #    chown -R #{NEW_USERNAME}:#{NEW_USERNAME} /home/#{NEW_USERNAME}/.ssh
        #SHELL

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
Primero activamos el entorno virtual:
```bash
    source /opt/venv/bin/activate
```
```bash
    # uvicorn [nombre_archivo_compartido(sin .py)]:[nombre_application] --host 0.0.0.0 --port 8000
    uvicorn main:FastAPI --host 0.0.0.0 --port 8000
```
### RESOLUCIÓN DE PROBLEMAS
#### 1. Error a la hora de crear una nueva VM y no coincide la private key:
Borramos el contenido de los siguientes directorios:
- Carpeta ```.vagrant``` creada cuando se ejecutó ```vagrant up```.
```powershell
    vagrant destroy -f
```
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