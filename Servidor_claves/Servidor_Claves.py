from socket import*
from Funciones import*
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

# Función para encriptar un archivo en modo CTR
def encriptar_archivo(archivo_entrada, archivo_salida, key, iv):
    cifrado = Cipher(algorithms.AES(key), modes.CTR(iv))
    encriptado = cifrado.encryptor()

    with open(archivo_entrada, 'rb') as entrada, open(archivo_salida, 'wb') as salida:
        
        for bloque in entrada:
            bloque_encriptado = encriptado.update(bloque)
            salida.write(bloque_encriptado)

# Función que maneja el encriptado de una cadena de texto en modo CTR, sin marcador.
def encriptar_texto(texto, key, iv):
    # Convertir la cadena de texto a bytes
    texto_bytes = texto.encode('utf-8')

    # Crear el objeto Cipher
    cifrado = Cipher(algorithms.AES(key), modes.CTR(iv))
    encriptado = cifrado.encryptor()

    # Encriptar la cadena de texto
    texto_encriptado = encriptado.update(texto_bytes)

    # Devolver el texto encriptado como bytes
    return texto_encriptado

# Función que maneja el desencriptado en modo CTR de un archivo   
def desencriptar_archivo(archivo_entrada, key, iv):
    cifrado = Cipher(algorithms.AES(key), modes.CTR(iv))
    desencriptado = cifrado.decryptor()

    with open(archivo_entrada, 'rb') as entrada:
        contenido_desencriptado = b''
        for bloque in entrada:
            bloque_desencriptado = desencriptado.update(bloque)
            contenido_desencriptado += bloque_desencriptado
    return contenido_desencriptado
            
# Función que desencripta modo CTR el archivo .txt y extrae las claves del archivo
def cargar_claves_desde_archivo(ruta_archivo,key,iv):
    claves = []
    desencriptado = desencriptar_archivo('licencias_cifradas.txt', key, iv).decode('latin-1')
    
    for linea in desencriptado.split('\n'):
        partes = linea.strip().split(';')
        nombre_archivo = partes[0].strip()
        clave = partes[1].strip()
        vi = partes[2].strip()
        if nombre_archivo == ruta_archivo:
            claves += clave, vi
    return ";".join(map(str, claves))

# Claves con la que está cifrado modo CTR el archivo .txt con las licencias de los archivos.
key = b'c'*16
iv = b'c'*16
#encriptar_archivo('licencias.txt', 'licencias_cifradas.txt', key, iv)

# Conexión TCP
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('localhost', 61000))
server_socket.listen(5)

while True:
    print("Servidor esperando conexiones...")
    # Esperamos conexiones
    client_socket, client_address = server_socket.accept()
    print(f"Conexión establecida con {client_address}")
    # Generamos clave pública y privada. Envia clave publica al cliente
    clave_publica, clave_privada = generar_claves()
    client_socket.send(str(clave_publica).encode())
    time.sleep(0.01)
    # Recibe clave publica RSA del cliente.
    cliente_clave_publica = eval(client_socket.recv(1024).decode())
    # Recibe el nombre de archivo cifrado con RSA, desciframos con clave privada
    recepcion = client_socket.recv(16024)
    datos_deco = recepcion.decode()
    
    descifrado = descifrar(eval(datos_deco),clave_privada)
    
    time.sleep(0.01)
    if any(caracter.isspace() for caracter in descifrado):        
        partes =  descifrado.rsplit('[', 1)
        
        archivo_original = partes[0].strip()
        
        lista_numeros_y_tupla = partes[1].rsplit(']', 1)
        archivo_firma = [int(numero) for numero in lista_numeros_y_tupla[0].split(',') if numero.strip()]
        
        tupla = [numero for numero in lista_numeros_y_tupla[1].strip(')').split(',')]
        publica_DCM = int(tupla[0][2:]),int(tupla[1])
      
        verificar_firma = descifrar(archivo_firma,publica_DCM)
 
        if archivo_original == verificar_firma:
            print("Firma digital confirmada")
            print(f'Petición claves de: {client_address}:\n')
            auxiliar = client_socket.recv(1024)
            time.sleep(0.01)
            # Genera claves aleatorias (clave e IV) para modo CTR
            numero_clave_cifrado = ''.join([chr(random.randint(48, 122)) for _ in range(16)])
            numero_iv_cifrado = ''.join([chr(random.randint(48, 122)) for _ in range(16)])
            # Cifra modo RSA con clave pública del cliente y lo envía
            cifrar_numero_clave = cifrar(numero_clave_cifrado, cliente_clave_publica)
            cifrar_numero_iv = cifrar(numero_iv_cifrado, cliente_clave_publica)
            client_socket.send(str(cifrar_numero_clave).encode())
            time.sleep(0.01)
            client_socket.send(str(cifrar_numero_iv).encode())
            time.sleep(0.01)
            # Saca las claves del archivo pedido de un archivo .txt encriptado
            claves = cargar_claves_desde_archivo(archivo_original,key,iv)
            # Encripta esas claves modoo CTR con la clave e IV generadas
            encriptar_claves = encriptar_texto(claves,numero_clave_cifrado.encode(),numero_iv_cifrado.encode())
            client_socket.send(encriptar_claves)
            print('Claves enviadas con exito')
            #client_socket.close()
        else:
            client_socket.send("Firma digital no confirmada").encode()
            client_socket.close()
        
    else:
        #Recepcion de firma digital
        recepcion_firma = client_socket.recv(1024)
        datos_deco_firma = recepcion_firma.decode()
        descifrado_firma = descifrar(eval(datos_deco_firma),cliente_clave_publica)
        print(f'Petición claves de: {client_address}:\n{descifrado}')
        time.sleep(0.01)
        if descifrado == descifrado_firma:
            print("Firma digital confirmada")
            print(f'Petición claves de: {client_address}:\n{descifrado}')
            # Genera claves aleatorias (clave e IV) para modo CTR
            numero_clave_cifrado = ''.join([chr(random.randint(48, 122)) for _ in range(16)])
            numero_iv_cifrado = ''.join([chr(random.randint(48, 122)) for _ in range(16)])
            # Cifra modo RSA con clave pública del cliente y lo envía
            cifrar_numero_clave = cifrar(numero_clave_cifrado, cliente_clave_publica)
            cifrar_numero_iv = cifrar(numero_iv_cifrado, cliente_clave_publica)
            client_socket.send(str(cifrar_numero_clave).encode())
            time.sleep(0.01)
            client_socket.send(str(cifrar_numero_iv).encode())
            time.sleep(0.01)
            # Saca las claves del archivo pedido de un archivo .txt encriptado
            claves = cargar_claves_desde_archivo(descifrado,key,iv)
            # Encripta esas claves modoo CTR con la clave e IV generadas
            encriptar_claves = encriptar_texto(claves,numero_clave_cifrado.encode(),numero_iv_cifrado.encode())
            client_socket.send(encriptar_claves)
            print('Claves enviadas con exito')
            #client_socket.close()
        else:
            client_socket.send("Firma digital no confirmada").encode()
            client_socket.close()

#client_socket.close()
