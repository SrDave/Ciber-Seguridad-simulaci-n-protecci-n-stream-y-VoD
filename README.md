# Ciber-Seguridad-simulación-protección-stream-y-VoD
Una simulación de ciberseguridad con AES CTR y RSA entre servidor de claves, cliente y CDM.


## INTRODUCCION. 

En el contexto actual, la salvaguarda de contenidos digitales se ha vuelto crucial. Este proyecto, se centra en la creación de un sistema robusto de protección, abordando los principios fundamentales compartidos por sistemas DRM como FairPlay, Widevine y PlayReady.

En este proyecto, nos enfocaremos en la programación en Python de elementos clave: una aplicación, un servidor de contenidos y un servidor de licencias. El objetivo principal es comprender y aplicar eficientemente los principios de funcionamiento de los sistemas DRM existentes.

El proyecto se divide en dos fases esenciales. La primera implica la interacción de la aplicación con el servidor de contenidos para adquirir recursos digitales. La segunda fase se adentra en la complejidad de la protección digital, con la aplicación enfrentándose a contenidos cifrados y buscando claves de descifrado gestionadas por el servidor de licencias.

En este proyecto la implementación no se limita a lo básico. Se debe incorporar marcas de agua en imágenes y firmas digitales en mensajes de solicitud de claves para una mayor seguridad.

En busca de la excelencia, la máxima calificación se logra mediante la segmentación de la aplicación de usuario en dos programas: una aplicación de usuario (UA) y un Content Decryption Module (CDM). Este enfoque especializado mejora la modularidad y eficiencia del sistema.

Este proyecto explora la criptografía, la seguridad de las comunicaciones y la gestión de derechos digitales, representando nuestro compromiso con la vanguardia de la tecnología digital. Bienvenidos a la era de la seguridad digital, donde nuestro sistema se erige como guardián de la integridad y los derechos en el mundo digital


## DESCRIPCIÓN.

En este apartado, detallaremos paso a paso el funcionamiento del proyecto. Lo primero de todo, hay que aclarar que en este proyecto no se ha usado la biblioteca cryptography para generar las claves RSA y AES CTR. Para generar las claves RSA hemos utilizado la función generar_claves() que se encarga de buscar números de 16 cifras primos para calcular (n,e),(n,d).

Para generar las claves AES CTR utilizamos claves que son ya strings, la única diferencia es que las generamos nosotros aleatoriamente y tenemos que enviarlas con encode() y recibirlas con decode(). Aquí la comparamos con OS:

Comencemos conectando el servidor principal, el servidor de claves y el CDM para que esperen una conexión. El servidor principal alberga 3 imágenes y dos videos, cifrados con AES en modo CTR, así como versiones sin cifrar. Al conectar la UA (cliente), esta se conecta inicialmente al servidor principal y espera uno de los dos comandos: 'LIST' o 'GET'. Con 'LIST ALL', se muestra el listado de nombres de los archivos en el servidor, permitiendo búsquedas más específicas como .jpg o .mp4. Por otro lado, el comando 'GET' inicia la descarga del archivo especificado.

A partir de este punto, se inicia un proceso lleno de solicitudes y cifrados. El servidor principal lee el archivo solicitado y verifica si es una imagen o no. En caso de ser una imagen, se verifica si está cifrada. En caso afirmativo, se establece conexión con la función conectar_claves_servidorRSA(), la cual implica un intercambio de claves públicas entre el servidor principal y el servidor de claves para comunicarse mediante cifrado RSA. El servidor principal envía el nombre del archivo cifrado con RSA y un certificado digital al servidor de claves. Este último valida el certificado y, si es correcto, genera una clave de cifrado y un vector de inicialización (IV) para el cifrado en modo CTR, enviándolos al servidor principal mediante RSA. El servidor principal recibe y descifra la clave y el IV mediante RSA.
El servidor de claves utiliza la función cargar_claves_desde_archivo() para descifrar un archivo de texto que almacena las claves de descifrado de los archivos. Extrae las claves del archivo solicitado, las encripta con la clave e IV creadas previamente y las envía al servidor principal. Este último recibe las claves cifradas en modo CTR, las descifra con la clave e IV recibidas anteriormente y desencripta la imagen solicitada por la UA.

Posteriormente, el servidor principal emplea la función agregar_marca_agua() para crear una copia de la imagen solicitada con una marca de agua visible, que contiene la IP y el puerto de la UA. Luego, cifra nuevamente los archivos en modo CTR y envía la imagen cifrada con la marca de agua a la UA. Si la imagen no está cifrada, se le añade una marca de agua y se envía directamente a la UA. En caso de ser un video, se repite el proceso, pero sin agregar una marca de agua.

Cuando la UA recibe la descarga de un archivo, verifica si está cifrado. En caso afirmativo, se conecta con el CDM mediante la función enviar_descarga(), que envía el archivo como se describió anteriormente. La UA y el CDM inician una conversación RSA similar a la descrita anteriormente, con comunicación simétrica y asimétrica. La diferencia radica en que el CDM prepara una petición para el servidor de claves utilizando la función preparar_peticion(), que consiste en enviar tres valores, el nombre del archivo, la firma digital de este, y la clave pública para descifrar la firma digital. Esta petición se cifra en modo CTR y se envía a la UA, quien la transmite al servidor de claves mediante la función conectar_servidor_clavesRSA().

El servidor de claves recibe e identifica la petición, comprueba si es una petición mediante los espacios. Separa las variables, la descifra y verifica la firma digital. Si es válida, sigue con el protocolo estándar enviando las claves a la UA. La UA recibe las claves, las envía cifradas al CDM, y finalmente, el CDM las recibe y desencripta con éxito el archivo cifrado, almacenándolo en su directorio.
Si los archivos no están cifrados, la UA los recibe directamente del servidor principal en su directorio, marcando el fin de este proceso.

## CONCLUSIONES.
En el transcurso de la implementación del proyecto "Seguridad y Gestión de Derechos Digitales", se ha logrado abordar de manera integral los desafíos contemporáneos relacionados con la protección de contenidos digitales. Las conclusiones extraídas de esta experiencia son las siguientes:

Comprensión Profunda de Sistemas DRM Actuales: Se ha consolidado un conocimiento sólido sobre los sistemas DRM más utilizados en la actualidad, como FairPlay, Widevine y PlayReady. Este entendimiento fue esencial para identificar los principios fundamentales compartidos que guiaron el diseño de nuestro propio sistema.

Dominio en Criptografía y Seguridad Digital: La implementación del proyecto permitió adquirir habilidades avanzadas en criptografía simétrica y asimétrica, así como en la aplicación de firmas digitales. La elección de algoritmos robustos, como AES para cifrado simétrico y RSA para cifrado asimétrico, demostró la capacidad para tomar decisiones informadas en la protección de datos sensibles.

Modularidad y Eficiencia con Segmentación de Aplicación: La segmentación de la aplicación de usuario en dos programas distintos (UA y CDM) no solo cumplió con los requisitos para la máxima calificación, sino que también demostró ser una estrategia efectiva para mejorar la modularidad y la eficiencia del sistema. Esta aproximación ofrece flexibilidad y facilita el mantenimiento futuro.

Implementación de Funcionalidades Adicionales para Destacar: La incorporación de características adicionales, como marcas de agua en imágenes y firmas digitales en mensajes de solicitud de claves, refleja un compromiso con la excelencia y la búsqueda constante de mejorar la seguridad del sistema.

Enfrentamiento de Desafíos Técnicos y de Seguridad: A lo largo del proyecto, se han enfrentado y superado diversos desafíos técnicos y de seguridad. La comunicación cifrada entre componentes, la gestión de claves de cifrado y la firma digital de mensajes fueron áreas críticas que requirieron atención meticulosa y soluciones efectivas.

Contribución a la Seguridad Digital: El proyecto contribuye al campo de la seguridad digital al ofrecer un sistema de protección de contenidos digitales que integra principios fundamentales de sistemas DRM existentes. Esta contribución es especialmente relevante en un entorno digital en constante evolución y creciente amenaza cibernética.

En resumen, el proyecto ha sido una oportunidad valiosa para aplicar conocimientos teóricos a situaciones prácticas, desarrollando habilidades técnicas y estratégicas esenciales en el campo de la seguridad digital y la gestión de derechos en entornos digitales







