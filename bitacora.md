# Bitácora

Miniproyecto 2 · Catálogo consultable de producción científica

Equipo: Diaz Bello Israel Jaziz · Flores Canaán Raúl Hased · Miranda Chávez Gabriela

## Cómo se repartió el trabajo

| Integrante | De qué se encargó |
|---|---|
| Diaz Bello Israel Jaziz | El AVL (altura, factor de balance, las cuatro rotaciones, inserción y eliminación con rebalanceo, verificador), el montículo (flotar, hundir, extraer mínimo, decrementar clave, cola de revisión y top-k) y el catálogo con la carga del CSV y los cinco problemas. Sus archivos son avl_monticulo.py y catalogo.py. |
| Miranda Chávez Gabriela | Las búsquedas en Crossref y la descarga de los datos, la revisión del subconjunto y el ABB (inserción, búsqueda, mínimo, máximo, sucesor, eliminación, recorridos y verificador). Sus archivos son descargar_datos.py, articulos.csv y abb.py. |
| Flores Canaán Raúl Hased | Las mediciones (ABB contra AVL y contra las estructuras de Python), las pruebas, el menú del programa y las instrucciones de ejecución del README. Sus archivos son main.py y README.md. |

## Lo que se decidió

| Fecha | Qué hicimos o decidimos                                                                                                                                                                                             | Por qué |
|---|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---|
| 04/11/2026 | Se nos asignó el área de ciencia de datos con 12,000 registros, Gabriela hizo la primera búsqueda en Crossref con "data science", solo artículos de revista.                                                        | Era lo más directo para el área que nos tocó. |
| 04/11/2026 | Decidimos quitar los registros que no tuvieran DOI o fecha, y los DOI repetidos. Si un artículo solo trae año y mes, le ponemos día 01.                                                                             | Sin DOI no podemos buscar el artículo y sin fecha no lo podemos ordenar. |
| 04/11/2026 | Guardamos los DOI en minúsculas.                                                                                                                                                                                    | Crossref no distingue mayúsculas en los DOI, y así una búsqueda no falla por cómo se escribió. |
| 08/11/2026 | La primera descarga dio 12,000 registros, pero eran de 1952 a 2002 y muchos de medicina y química. Al revisarlos vimos que en el título solo decían "data", no "data science".                                      | Crossref buscó las palabras "data" y "science" por separado y no la frase completa. |
| 08/11/2026 | Elegimos las claves: el DOI para localizar un artículo, (fecha, DOI) para el orden cronológico y (−citas, DOI) para la cola de revisión.                                                                            | Está explicado en el reporte, en la justificación de la clave. |
| 08/11/2026 | Decidimos rechazar los DOI repetidos en las tres estructuras.                                                                                                                                                       | Un DOI es de un solo artículo, así que si se repite es un error. |
| 08/11/2026 | Usamos dos árboles de cada tipo, uno por DOI y otro por fecha, y cuando damos de baja un artículo lo quitamos de todos.                                                                                             | Un mismo árbol no puede estar ordenado por DOI y por fecha a la vez. |
| 08/11/2026 | El AVL hereda del ABB buscar, mínimo, máximo, sucesor, transplant y los recorridos, y solo cambia insertar y eliminar.                                                                                              | Esas partes son iguales en los dos árboles y no queríamos repetir código. |
| 08/11/2026 | Subimos el límite de recursión de Python a 50,000.                                                                                                                                                                  | Con datos en orden el ABB llega a altura n − 1 y los recorridos recursivos pasaban el límite normal de 1,000. |
| 08/11/2026 | Para decrementar clave en la cola, primero buscamos la posición del DOI recorriendo el arreglo, O(n).                                                                                                               | Para hacerlo en O(1) necesitaríamos un dict, y el enunciado solo lo deja usar para comparar. |
| 08/11/2026 | Para dar de baja un artículo de la cola, le bajamos la clave a −infinito para que suba a la raíz y luego lo extraemos.                                                                                              | Así usamos las mismas operaciones del montículo. |
| 08/11/2026 | En las mediciones con datos en orden usamos n = 1,000, 2,000 y 4,000.                                                                                                                                               | Construir el ABB con datos en orden cuesta O(n²) y con más datos tardaba demasiado. |
| 08/11/2026 | Con la primera descarga notamos que los DOI venían casi en orden (94% de los pares seguidos), y el ABB por DOI quedó con altura 284 contra 15 del AVL.                                                              | Nos sirvió para ver que el orden del cursor puede degenerar el ABB (problema 3). |
| 09/11/2026 | Gabriela volvió a hacer la búsqueda pidiendo los resultados por relevancia y quedándose solo con los artículos que dicen "data science" en el título.                                                               | Así todo el subconjunto es de verdad de ciencia de datos. |
| 09/11/2026 | Con esa búsqueda solo salieron 4,967 artículos, porque Crossref ya no tiene más con esa frase. Gabriela agregó la búsqueda de "big data" (y "data mining" por si faltaban) para completar los 12,000.               | Son términos del área y así llegamos a los 12,000 que nos pidieron. |
| 09/11/2026 | La descarga final quedó con 12,000 artículos sin DOI repetidos: 5,025 de "data science" y 6,975 de "big data". No hizo falta "data mining". Casi todos son de 2014 en adelante.                                     | Es el articulos.csv que está en el repositorio. |
| 10/11/2026 | Gabriela le preguntó al doctor si usábamos solo los 4,967 de "data science" o los 12,000 combinados, y nos dijo que usáramos los 12,000 combinados: todos los de "data science" y los de "big data" para completar. | Lo confirmamos con él para que nuestros resultados coincidan con sus valores de control. |
| 11/11/2026 | Israel se quedó con el catálogo, además del AVL y el montículo.                                                                                                                                                     | Los problemas 3, 4 y 5 se resuelven con el AVL y el montículo, que él implementó, así que él sabe mejor cómo conectarlos. |
| 11/11/2026 | Raúl se encargó de las instrucciones del README.                                                                                                                                                                    | El README explica cómo correr main.py y usar el menú, que son de Raúl. |

## Avance en el repositorio

| Fecha | Quién | Qué subió |
|---|---|---|
| 10/11/2026 | Miranda Chávez Gabriela | El script de descarga (descargar_datos.py), articulos.csv y abb.py. |
| 11/11/2026 | Diaz Bello Israel Jaziz | avl_monticulo.py, con el AVL y el montículo. |
| 12/11/2026 | Diaz Bello Israel Jaziz | catalogo.py, con la carga de los datos y los cinco problemas. |
| 12/11/2026 | Flores Canaán Raúl Hased | main.py, con las mediciones, las pruebas y el menú. Ya con todos los archivos corrimos las pruebas y pasaron las 23. |
| 12/11/2026 | Flores Canaán Raúl Hased | El README.md con las instrucciones para ejecutar el proyecto. |
| 12/11/2026 | Flores Canaán Raúl Hased | El archivo bitacora.md. |
| 13/11/2026 | Miranda Chávez Gabriela | El reporte técnico en PDF. |

## Uso de LLM

Usamos Claude durante todo el proyecto y aquí anotamos qué le pedimos, qué aceptamos y qué corregimos.

| Fecha | Qué le pedimos | Qué aceptamos | Qué corregimos |
|---|---|---|---|
| 04/11/2026 | Un script para descargar los datos de Crossref. | El script descargar_datos.py. | No hizo falta corregir nada. |
| 08/11/2026 | Que revisara el CSV de la primera descarga. | Su revisión: 12,000 registros sin duplicados y casi en orden de DOI. | Nos avisó que muchos artículos no eran de ciencia de datos, y por eso decidimos volver a buscar. |
| 08/11/2026 | El código del ABB, AVL, montículo, catálogo, mediciones y pruebas, y la especificación de los TDA, a nivel principiante. | El código y los documentos. | No hizo falta corregir nada. |
| 09/11/2026 | Corregir la búsqueda para que solo trajera artículos con "data science" en el título. | La nueva versión del script, con orden por relevancia y el filtro por título. | No hizo falta corregir nada. |
| 09/11/2026 | Completar los 12,000 registros, porque con "data science" solo salieron 4,967. | Agregar "big data" a la búsqueda, en ese orden. | No hizo falta corregir nada. |
| 10/11/2026 | Revisar que la entrega tenga solo lo que pide el enunciado. | Dejar el README solo con las instrucciones y la especificación de los TDA dentro del reporte. | No hizo falta corregir nada. |
| 10/11/2026 | Organizar el código en un archivo por parte. | El código quedó en abb.py, avl_monticulo.py, catalogo.py y main.py. | No hizo falta corregir nada. |
## Validación final y evidencia experimental (13/11/2026)

| Fecha | Quién | Qué se realizó | Resultado |
|---|---|---|---|
| 13/11/2026 | Flores Canaán Raúl Hased | Se ejecutó `python main.py` y se eligió la opción 2 para correr la batería completa. | Pasaron las 23 pruebas: ABB, cuatro rotaciones AVL, inserción y eliminación AVL, montículo, cola de revisión, top-k y catálogo integrado. |
| 13/11/2026 | Flores Canaán Raúl Hased | Se ejecutó la opción 1 para comprobar los resultados del subconjunto real. | 12,000 artículos cargados; 0 DOI duplicados rechazados; alturas ABB/AVL por DOI de 41/15 y por fecha de 32/15; 2,651 artículos entre 2018 y 2020. |
| 13/11/2026 | Flores Canaán Raúl Hased | Se ejecutó la opción 3 para obtener las mediciones experimentales y se guardó la salida en `mediciones.txt`. | Con inserción ordenada, el ABB alcanzó alturas 999, 1,999 y 3,999 para n=1,000, 2,000 y 4,000; el AVL alcanzó 9, 10 y 11. En inserción aleatoria, las alturas ABB fueron 25, 24 y 26, frente a 11, 12 y 13 del AVL. |
| 13/11/2026 | Flores Canaán Raúl Hased | Se actualizó este README con requisitos, instrucciones, resultados de validación y explicación de las mediciones. | Se documentó cómo reproducir las tres opciones del menú y dónde consultar las salidas. |
| 13/11/2026 | Flores Canaán Raúl Hased | Se utilizó ChatGPT para revisar los archivos entregados, ejecutar las pruebas y mediciones, y redactar documentación de ejecución a partir de los resultados reales. | Se conservaron las pruebas y el código del equipo; se añadieron los resultados observados y se identificó que el PDF disponible en la carpeta corresponde al enunciado, no al reporte técnico final. |

### Resultados de medición registrados

Los tiempos medidos en esta ejecución se encuentran en `mediciones.txt`. Para el subconjunto de 12,000 registros, los tiempos por búsqueda fueron: ABB 1,017 ns, AVL 629 ns y `dict` 24 ns. El recorrido completo por inorden tomó 986,536 ns en ABB y 933,524 ns en AVL; `sorted` tomó 1,737,611 ns. La construcción y atención completa de la cola tomó 62,514,207 ns con el montículo propio y 9,924,327 ns con `heapq`. El top-10 tomó 7,647,161 ns con la implementación propia y 490,744 ns con `heapq`; ambos métodos produjeron el mismo resultado.

**Nota:** los tiempos dependen del equipo y de las condiciones de ejecución. Deben citarse como resultados de esta corrida, no como valores fijos del algoritmo.
