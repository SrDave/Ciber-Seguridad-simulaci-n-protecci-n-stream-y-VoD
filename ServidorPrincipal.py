from socket import*
from Funciones import*
import os
import time
from PIL import Image, ImageDraw, ImageFont
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

host = 'localhost' # 127.0.0.1
port = 60000  # Puerto del Servidor principal
portKeys = 61000  # Puerto del servidor de licencias


def agregar_marca_agua(ima, usuario_id):
    # Cargar la imagen
    imagen = Image.open(ima)
    # Crear un objeto ImageDraw para dibujar en la imagen
    draw = ImageDraw.Draw(imagen)
    # Configurar la fuente y el tamaño para la marca de agua
    font = ImageFont.load_default()
    # Configurar el contenido de la marca de agua (puedes personalizar esto según tus necesidades)
    marca_de_agua = f"Marca de agua, Usuario:{usuario_id}"
    # Obtener las dimensiones de la imagen
    width, height = imagen.size
    # Calcular la posición para la marca de agua (puedes personalizar la posición)
    x = width - 265
    y = height - 50
    # Agregar la marca de agua a la imagen
    draw.text((x, y), marca_de_agua, font=font, fill=(255, 255, 255, 128))
    # Guardar la imagen con la marca de agua
    imagen_con_marca = f"con_marca{ima}"
    imagen.save(imagen_con_marca)

    return imagen_con_marca

def LIST(e):
    lista = os.listdir();lis=[]
    for i in lista:
        if i.endswith(str(e[-3:])):
            lis.append(i)
    return lis


def descarga(n, conexion, usuario_id):
    try:
        nombre = n[4:]
        archivo_read = open(nombre,"rb")      
        ArchivoEncode = archivo_read.read()
        
        if nombre.endswith(('jpg','jpeg','png','bmp')):

            if verificar_marcador(nombre):
                print("Archivo cifrado, solicitando claves")
                # Petición de claves al servidor de licencias via RSA
                clave,iv = conectar_claves_servidorRSA(nombre)
                # Desencriptar archivo con las claves recibidas.               
                desencriptar_archivo(nombre, clave.encode(), iv.encode())
                agregar_marca_agua(nombre, usuario_id)
                encriptar_archivo("con_marca"+nombre,"con_marca"+nombre, clave.encode(), iv.encode())
                encriptar_archivo(nombre, nombre, clave.encode(), iv.encode())
                
                read_con_marca = open("con_marca"+nombre,"rb")
                tamaño_marca = os.path.getsize("con_marca"+nombre)
                #Enviar tamaño del archivo
                conexion.sendall(str(tamaño_marca).encode())
                time.sleep(0.01)
                Archivo_con_marca = read_con_marca.read()
                conexion.sendall(Archivo_con_marca)
                print(f"Enviado {len(Archivo_con_marca)} bytes")
                # Cerrar y eliminar el archivo con la marca de agua después de enviarlo
                read_con_marca.close()
                os.remove("con_marca" + nombre)
            else:
                agregar_marca_agua(nombre, usuario_id)
                read_con_marca = open("con_marca"+nombre,"rb")
                tamaño_marca = os.path.getsize("con_marca"+nombre)
                conexion.sendall(str(tamaño_marca).encode())
                time.sleep(0.01)
                Archivo_con_marca = read_con_marca.read()
                conexion.sendall(Archivo_con_marca)
                print(f"Enviado {len(Archivo_con_marca)} bytes")
                # Cerrar y eliminar el archivo con la marca de agua después de enviarlo
                read_con_marca.close()
                os.remove("con_marca" + nombre)
        else:
            tamaño_total = os.path.getsize(nombre)
            conexion.sendall(str(tamaño_total).encode())
            time.sleep(0.01)
            conexion.sendall(ArchivoEncode)
            print(f"Enviado {len(ArchivoEncode)} bytes")
    except FileNotFoundError:
        conexion.sendall("401 FICHERO NO ENCONTRADO.".encode())
    finally:
        archivo_read.close()
        
    
def tamaño(p):
    size = os.path.getsize(p[4:])
    return size


serversocket = socket(AF_INET, SOCK_STREAM)
TCPserver = ('localhost', 60000)
print("conectando en {}, en el puerto {}".format(*TCPserver))
serversocket.bind(TCPserver)

serversocket.listen(5)

while True:
    sock,client_address = serversocket.accept()
    print(f"Nueva conexión establecida...{client_address}")
    while True:
        listado = os.listdir();listado_conv= tuple(listado)    
        peticion = sock.recv(1024)
        start= peticion.decode();concreto = LIST(start)
                        
        if (start.startswith("LIST") == True) or (start.startswith("GET") == True) or (start == "QUIT"):
            if (start.startswith("LIST") == True):            
                if start.endswith(" ALL"):
                    sock.send(("200 INICIO DE ENVIO LISTADO..."+"\n").encode())                            
                    sock.send(str(listado_conv).encode())

                elif concreto == []:
                    sock.send("201 NO HAY FICHEROS.".encode())
                else:
                    sock.send(("200 INICIO DE ENVIO LISTADO..."+"\n").encode())
                    sock.send(str(concreto).encode())
                        
            elif (start.startswith("GET") == True):
                try:
                    ok=("202 LONGITUD DEL CONTENIDO:"+str(tamaño(start))+" bytes"+"\n")
                    sock.send(ok.encode())
                    descarga(start,sock,client_address)
                except:
                    sock.send("401 FICHERO NO ENCONTRADO.".encode())           

            elif (start.startswith("QUIT") == True):
                sock.send("Gracias por usar este programa.".encode())
                sock.close()
        

        else:
            nook=("400 ERROR. MENSAJE NO IDENTIFICADO"+"\n")
            sock.send(nook.encode())
            
        print(f"{client_address} dice: ",start)   
#sock.close()
