import random
import math
import time
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from socket import*

host = 'localhost' # 127.0.0.1
port = 60000  # Puerto del Servidor principal
portKeys = 61000  # Puerto del servidor de licencias

def generar_claves():
    #Genera dos númeos primos aleatorios
    p = generar_primo()
    q = generar_primo()
    
    #Calcular el módulo n y la función de Euler phi
    n = p * q
    phi = (p - 1) * (q -1)
    
    #Elegir una clave pública y que sea coprima con phi
    e = clave_publica(phi)
    
    #Calcular la clave privada
    d = modinv(e,phi)
    # Imprimir las claves generadas
    return ((n,e),(n,d))

def generar_primo():
    #Generar un número primo aleatorio
    while True:
        num = random.randint(2**25,2**26-1)
        if primo(num):
            return num

def primo(numero):
    #Verificar si es un número primo
    for i in range(2, int(math.sqrt(numero))+1):
        if numero % i == 0:
            return False
    return True

def clave_publica(phi):
    #Elegir una clave publica y que sea coprima con phi
    while True:
        e = random.randint(2,phi-1)
        if math.gcd(e,phi) == 1:
            return e

def modinv(a,m):
    #Calcular el inverso modular usando el algoritmo extendido de Euclides
    mO, xO, x1 = m,0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        xO, x1 = x1 - q * xO, xO
    return x1 + mO if x1 < 0 else x1

def cifrar(mensaje, clave_publica):
    # Cifrar el mensaje usando la clave publica (n, e)
    n, e = clave_publica
    # Convertir el texto a una lista de números representando los caracteres
    mensaje_numerico = [ord(char) for char in mensaje]
    # Cifrar cada número por separado
    mensaje_cifrado_numerico = [pow(char, e, n) for char in mensaje_numerico]
    return mensaje_cifrado_numerico

def descifrar(mensaje_cifrado, clave_privada):
    # Descifrar un mensaje cifrado usando la clave privada (n, d)
    n, d = clave_privada
    # Descifrar cada número por separado
    mensaje_descifrado_numerico = [pow(char, d, n) for char in mensaje_cifrado]
    # Convertir los números a caracteres y unirlos en un solo texto
    mensaje_descifrado_texto = ''.join([chr(char) for char in mensaje_descifrado_numerico])
    return mensaje_descifrado_texto

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

# Función para encriptar un archivo en modo CTR
def encriptar_archivo(archivo_entrada, archivo_salida, key, iv):
    cifrado = Cipher(algorithms.AES(key), modes.CTR(iv))
    encriptado = cifrado.encryptor()

    with open(archivo_entrada, 'rb') as entrada:
        bloque_encriptado = entrada.read()
        bloque_encriptado = encriptado.update(bloque_encriptado)
    with open(archivo_salida, 'wb') as salida:
        salida.write(bloque_encriptado)
        salida.write(b'cifrado')

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


# Función que conecta con el servidor de licencias via RSA
def conectar_claves_servidorRSA(archivo):
    client_socket_licencia = socket(AF_INET, SOCK_STREAM)
    client_socket_licencia.connect((host, portKeys))
    # Recibimos clave publica RSA del servidor de licencias
    servidor_clave_publica = eval(client_socket_licencia.recv(1024).decode())
    # Generar clave publica y privada
    clave_publica, clave_privada = generar_claves()
    client_socket_licencia.send(str(clave_publica).encode())
    time.sleep(0.01)
    # Cifrar el nombre de archivo con la clave pública del servidor
    cifrar_archivo = cifrar(archivo, servidor_clave_publica)
    client_socket_licencia.sendall(str(cifrar_archivo).encode())
    time.sleep(0.01)
    #Firma digital
    firmar_archivo = cifrar(archivo,clave_privada)
    client_socket_licencia.sendall(str(firmar_archivo).encode())
    time.sleep(0.01)
    # Recibimos la clave y el IV para desencriptar.
    respuesta_encriptada_clave = client_socket_licencia.recv(1024).decode()
    time.sleep(0.01)
    respuesta_encriptada_iv = client_socket_licencia.recv(1024).decode()
    time.sleep(0.01)
    # Desciframos con RSA (clave privada), la clave y el IV
    clave_descifrada = descifrar(eval(respuesta_encriptada_clave), clave_privada)
    iv_descifrada = descifrar(eval(respuesta_encriptada_iv), clave_privada)
    data = client_socket_licencia.recv(1024)
    print('Claves recibidas del servidor de claves.\nDesencriptando archivo...')
    # Desencriptamos las claves que nos mandan en modo CTR
    lista = desencriptar_texto(data,clave_descifrada.encode(),iv_descifrada.encode())
    lista = lista.split(";")
    print("¡Archivo desencriptado con exito!")
    #client_socket_licencia.close()
    return lista

 # Función para verificar si un archivo esta encriptado o no   
def verificar_marcador(archivo):
    with open(archivo, 'rb') as entrada:
        entrada.seek(-7, 2)
        marcador = entrada.read()
        return marcador == b'cifrado'
# archivo='cifrado_pinkpanter.jpeg'
#print(conectar_claves_servidorRSA(archivo))
# Ejemplo de uso
# Genera clave publica y privada
# publica, privada = generar_claves()
# 
# # Mensaje de ejemplo
# mensaje_original = "Hola, esto es un mensaje secreto."
# 
# # Cifrar el mensaje
# mensaje_cifrado = cifrar(mensaje_original, publica)
# 
# # Descifrar el mensaje cifrado
# mensaje_descifrado = descifrar(mensaje_cifrado, privada)
# 
# print("Mensaje original:", mensaje_original)
# print("Mensaje cifrado:", mensaje_cifrado)
# print("Mensaje descifrado:", mensaje_descifrado)

