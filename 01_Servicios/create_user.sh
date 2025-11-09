#!/bin/bash
USERNAME=$1
PASSWORD=$2

if id -u "$USERNAME" >/dev/null 2>&1; then
  echo "El usuario '$USERNAME' ya existe. Omitiendo la creación."
else
  sudo useradd -m -s /bin/bash "$USERNAME"
  echo "${USERNAME}:${PASSWORD}" | sudo chpasswd
  sudo usermod -aG sudo "$USERNAME"
  echo "Usuario '$USERNAME' creado con éxito."
fi