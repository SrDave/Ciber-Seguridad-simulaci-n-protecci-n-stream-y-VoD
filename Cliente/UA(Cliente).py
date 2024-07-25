import socket
import os
import time
from Funciones import*
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


host = 'localhost' # 127.0.0.1
port = 60000  # Puerto del Servidor principal
portKeys = 61000  # Puerto del servidor de licencias
portDCM = 62000  # Puerto del DCM

#socket TCP
client_socket = socket(AF_INET, SOCK_STREAM)

client_socket.connect((host, port))
print(f"Conectado al servidor en {host}:{port}")

# Función para desencriptar un archivo en modo CTR
def desencriptar_archivo(archivo_entrada, key, iv):
    cifrado = Cipher(algorithms.AES(key), modes.CTR(iv))
    desencriptado = cifrado.decryptor()
    with open(archivo_entrada, 'rb') as entrada:
        contenido_cifrado = entrada.read()
        contenido_cifrado = contenido_cifrado[:-7]
        contenido_desencriptado = desencriptado.update(contenido_cifrado)

    with open(archivo_entrada, 'wb') as sobrescribir:
        sobrescribir.write(contenido_desencriptado)

# Función para desencriptar na cadena de texto en modo CTR
def desencriptar_texto(texto_encriptado, key, iv):
    # Crear el objeto Cipher
    cifrado = Cipher(algorithms.AES(key), modes.CTR(iv))
    desencriptado = cifrado.decryptor()

    # Desencriptar el texto
    texto_desencriptado_bytes = desencriptado.update(texto_encriptado)

    # Convertir los bytes desencriptados a una cadena de texto
    texto_desencriptado = texto_desencriptado_bytes.decode('utf-8')

    # Devolver la cadena de texto desencriptada
    return texto_desencriptado

# Función para manejar la recepción de mensajes que no tengan que ver con 'LIST' O 'GET'
def recibir_mensajes():
    while True:
        try:
            data = client_socket.recv(1024)
            if data:
                print(f"\nMensaje recibido: {data.decode('utf-8')}")
                break
            else:
                print("El servidor ha cerrado la conexión.")
                break
        except Exception as e:
            print(f"Error al recibir mensajes: {e}")
            break

def conectar_DCM(archivo,client_socket_DCM):

    # Recibimos clave publica RSA del servidor de licencias
    DCM_clave_publica = eval(client_socket_DCM.recv(1024).decode())

    # Generar clave publica y privada
    clave_publica, clave_privada = generar_claves()
    client_socket_DCM.send(str(clave_publica).encode())
    time.sleep(0.01)
    # Genera claves aleatorias (clave e IV) para modo CTR ''.join([chr(random.randint(48, 122)) for _ in range(16)])
    numero_clave_cifrado = ''.join([chr(random.randint(48, 122)) for _ in range(16)])
    numero_iv_cifrado = ''.join([chr(random.randint(48, 122)) for _ in range(16)])
    # Cifra modo RSA con clave pública del cliente y lo envía
    cifrar_numero_clave = cifrar(numero_clave_cifrado, DCM_clave_publica)
    cifrar_numero_iv = cifrar(numero_iv_cifrado, DCM_clave_publica)
    client_socket_DCM.send(str(cifrar_numero_clave).encode())
    time.sleep(0.01)
    client_socket_DCM.send(str(cifrar_numero_iv).encode())
    time.sleep(0.01)
 
    archivo_cifrado = encriptar_texto(archivo[3:],numero_clave_cifrado.encode(),numero_iv_cifrado.encode())
    client_socket_DCM.send(str(archivo_cifrado).encode())
    time.sleep(0.01)

    peticion = client_socket_DCM.recv(2024).decode()
    time.sleep(0.01)
    peticion_desencriptada = desencriptar_texto(eval(peticion),numero_clave_cifrado.encode(),numero_iv_cifrado.encode())

    clave, iv = conectar_claves_servidorRSA(peticion_desencriptada)
    claves = f"{clave} {iv}"

    client_socket_DCM.send(str(claves).encode())
    time.sleep(0.01)
    #client_socket_DCM.close()
    

def enviar_descarga(nombre):
    client_socket_DCM = socket(AF_INET, SOCK_STREAM)
    client_socket_DCM.connect((host, portDCM))
    archivo_read = open(nombre,"rb")      
    ArchivoEncode = archivo_read.read()
    tamaño_total = os.path.getsize(nombre)
    client_socket_DCM.sendall(str(nombre).encode())
    time.sleep(0.01)
    client_socket_DCM.sendall(str(tamaño_total).encode())
    time.sleep(0.01)
    client_socket_DCM.sendall(ArchivoEncode)
    print(f"Enviado a DCM {len(ArchivoEncode)} bytes")
    #client_socket_DCM.close()
    conectar_DCM(nombre,client_socket_DCM)
    #client_socket_DCM.close()

# Función para manejar la recepción de la descarga
def recibir_descarga(mensaje,socket):
    # Nombre del nuevo archivo
    nombre = "NEW"+mensaje[4:]
    descarga = open(nombre,"wb")
    size_data = socket.recv(1026)
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
    # Comprobamos si está cifrado o no
    if verificar_marcador(nombre):
        print("Archivo cifrado")
        enviar_descarga(nombre)
        
    else:
        print("Archivo no cifrado")

# Bucle principal para enviar mensajes
while True:
    message = input("Ingrese un mensaje ('QUIT' para salir, 'GET' para descargar, 'LIST ALL' para listado ): ")
    client_socket.sendall(message.encode())
    peticion =  client_socket.recv(1024);peti_deco = peticion.decode()
    if peti_deco.startswith('202'):
        try:
            recibir_descarga(message,client_socket)
        except Exception as e:
            print(f"Error al recibir el archivo: {e}")
    
    elif message.upper() == 'QUIT':
        break

    elif peti_deco.startswith('200'):
        recibir_mensajes()
       
    else:
        print("El servidor denegó tu petición.\n")
            

# Cerrar el socket
#client_socket.close()

