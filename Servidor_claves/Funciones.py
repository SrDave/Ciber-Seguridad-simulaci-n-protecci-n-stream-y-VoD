import random
import math

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

