import socket
import os
import time
from Funciones import*
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

host = 'localhost' # 127.0.0.1
port = 60000  # Puerto del Servidor principal
portKeys = 61000  # Puerto del servidor de licencias

def conectar_UA(client_socket):
    publica,privada = generar_claves()
    client_socket.send(str(publica).encode())
    clave_publica_UA = client_socket.recv(1024).decode()
    time.sleep(0.01)
    # Recibimos la clave y el IV para desencriptar.
    respuesta_encriptada_clave = client_socket.recv(1024).decode()
    time.sleep(0.01)
    respuesta_encriptada_iv = client_socket.recv(1024).decode()
    time.sleep(0.01)
    # Desciframos con RSA (clave privada), la clave y el IV
    clave = descifrar(eval(respuesta_encriptada_clave), privada)
    iv = descifrar(eval(respuesta_encriptada_iv), privada)
    print(clave,iv)
    archivo_cifrado = client_socket.recv(1024).decode()
    archivo = desencriptar_texto(eval(archivo_cifrado),clave.encode(),iv.encode())
    print(archivo)
    solicitud = preparar_peticion(archivo)
    solicitud_cifrada = encriptar_texto(solicitud,clave.encode(),iv.encode())
    client_socket.send(str(solicitud_cifrada).encode())
    time.sleep(0.01)
    claves = client_socket.recv(1024).decode()
    time.sleep(0.01)
    claveMain, ivMain = claves.split()
    #client_socket.close()
    return claveMain, ivMain
    
     

def preparar_peticion(archivo):
    clave_publica,clave_privada = generar_claves()
    firma_digital = cifrar(archivo, clave_privada)
    peticion = f"{archivo} {firma_digital} {clave_publica}"
    return peticion

def recibir_descarga(socket):
    # Nombre del nuevo archivo
    nombre = socket.recv(1026).decode()
    time.sleep(0.01)
    descarga = open(nombre,"wb")
    size_data = socket.recv(1026)
    time.sleep(0.01)
    # Recibimos el tamaño del archivo desde el servidor
    tam = int(size_data.decode())
    print(f"Datos recibidos: {tam}")
    cont=True  
    rec = 0
    # Comenzamos la descarga del archivo desde el servidor
    while cont:
        data = socket.recv(1026)
        rec += len(data)
        descarga.write(data)
        # Cuando el coincida con el tamaño el bucle para
        if rec == tam:
            cont=False
    descarga.close()
    
    tamaño_total = os.path.getsize(nombre)
    # Verificamos que el tamaño recibido coincide con el que tenemos
    print(f"Total recibidos: {tamaño_total}")
    clave,iv = conectar_UA(socket)
    # Desencriptar archivo con las claves recibidas.
    desencriptar_archivo(nombre, clave.encode(), iv.encode())
    #client_socket.close()

DCMsocket = socket(AF_INET, SOCK_STREAM)
DCM_sock = ('localhost', 62000)
print("conectando en {}, en el puerto {}".format(*DCM_sock))
DCMsocket.bind(DCM_sock)

DCMsocket.listen(5)

while True:
    print("Servidor esperando conexiones...")
    # Esperamos conexiones
    client_socket, client_address = DCMsocket.accept()
    print(f"Conexión establecida con {client_address}")
    recibir_descarga(client_socket)
    client_socket.close()
    
