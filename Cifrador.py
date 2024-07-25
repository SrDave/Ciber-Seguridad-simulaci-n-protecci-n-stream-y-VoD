from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def encriptar_archivo(archivo_entrada, archivo_salida, key, iv):
    cifrado = Cipher(algorithms.AES(key), modes.CTR(iv))
    encriptado = cifrado.encryptor()

    with open(archivo_entrada, 'rb') as entrada, open(archivo_salida, 'wb') as salida:
        
        for bloque in entrada:
            bloque_encriptado = encriptado.update(bloque)
            salida.write(bloque_encriptado)
        salida.write(b'cifrado')

    
def desencriptar_archivo(archivo_entrada, archivo_salida, key, iv):
    cifrado = Cipher(algorithms.AES(key), modes.CTR(iv))
    desencriptado = cifrado.decryptor()

    with open(archivo_entrada, 'rb') as entrada, open(archivo_salida, 'wb') as salida:
        for bloque in entrada:
            bloque_desencriptado = desencriptado.update(bloque)
            salida.write(bloque_desencriptado)

# Generar clave y IV deseados
key_pinkpanter = b'd'*16
iv_pinkpanter = b'd'*16

# Rutas de archivo de entrada y salida
archivo = 'Las_urracas_parlanchinas.jpg'
archivo_encriptado = 'cifrado_las_urracas_parlanchinas.jpg'
archivo_desencriptado = 'desencriptado_TouchOSC_soundcool_.jpeg'

# Encriptar el archivo
encriptar_archivo(archivo, archivo_encriptado, key_pinkpanter, iv_pinkpanter)

print(f"Archivo encriptado con clave: {key_pinkpanter.hex()} e IV: {iv_pinkpanter.hex()}")

# Desencriptar el archivo
desencriptar_archivo(archivo_encriptado, archivo_desencriptado, key_pinkpanter, iv_pinkpanter)
print("Archivo desencriptado")

def verificar_marcador(archivo):
    with open(archivo, 'rb') as entrada:
        entrada.seek(-7, 2)
        marcador = entrada.read()
        return marcador == b'cifrado'

# Verificar marcador
if verificar_marcador(archivo_encriptado):
    print('Marcador presente en el archivo encriptado')
else:
    print('Marcador no presente en el archivo encriptado')
    
