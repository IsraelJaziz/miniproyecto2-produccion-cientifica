# Miniproyecto 2 · Catálogo consultable de producción científica

**TecNM / Instituto Tecnológico de Orizaba**  
Ingeniería en Ciencia de Datos · Estructuras de Datos  
Catedrático: Dr. Ulises Juárez Martínez  

**Equipo:** Diaz Bello Israel Jaziz · Flores Canaán Raúl Hased · Miranda Chávez Gabriela

## 1. Contenido del proyecto

| Archivo | Función |
|---|---|
| `abb.py` | Árbol binario de búsqueda (ABB): búsqueda, inserción, eliminación, mínimo, máximo, sucesor y recorridos. |
| `avl_monticulo.py` | Árbol AVL con cuatro rotaciones; montículo mínimo, cola de revisión y operación top-k. |
| `catalogo.py` | Carga de los registros CSV e integración de las estructuras para resolver las consultas del catálogo. |
| `main.py` | Menú, batería de 23 pruebas y experimentos de medición. |
| `articulos.csv` | Subconjunto de 12,000 artículos de Crossref para el área de ciencia de datos. |
| `descargar_datos.py` | Script utilizado para obtener el subconjunto desde Crossref. No es necesario ejecutarlo para usar el proyecto. |
| `bitacora.md` | Distribución del trabajo, decisiones de diseño, avances y uso de herramientas de IA. |
| `resultados_subconjunto.txt` | Salida de referencia de la opción 1 del menú. |
| `mediciones.txt` | Salida de referencia de la opción 3 del menú en el equipo donde se ejecutó. |

## 2. Requisitos

- Python 3.10 o posterior.
- No se requieren paquetes externos.
- Todos los archivos `.py` y `articulos.csv` deben permanecer en la misma carpeta.

## 3. Cómo ejecutar

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
python main.py
```

El programa presenta estas opciones:

1. **Resultados del subconjunto:** muestra los resultados de las consultas del catálogo (problemas 1 a 5).
2. **Pruebas:** ejecuta la batería automatizada; deben aprobarse las 23 pruebas.
3. **Mediciones:** compara alturas y tiempos del ABB y AVL, y contrasta las estructuras propias con `dict`, `sorted` y `heapq`.

## 4. Resultados de validación

En la ejecución de validación del 13 de noviembre de 2026:

- Las **23 de 23 pruebas** terminaron correctamente.
- Se cargaron **12,000 artículos** y se rechazaron **0 DOI duplicados**.
- Altura del ABB por DOI: **41**; altura del AVL por DOI: **15**.
- Altura del ABB por fecha: **32**; altura del AVL por fecha: **15**.
- La consulta de artículos de 2018 a 2020 devolvió **2,651 registros**.
- Los resultados de `top_k` coincidieron con `heapq`.

Las salidas completas de las opciones 1 y 3 se guardan en `resultados_subconjunto.txt` y `mediciones.txt`.

## 5. Cómo interpretar las mediciones

El experimento ABB-AVL utiliza tamaños de 1,000, 2,000 y 4,000 claves, con inserción ordenada y aleatoria. La búsqueda se mide con 100 claves y 30 repeticiones; se informa la mediana del tiempo por búsqueda. La inserción ordenada produce un ABB degenerado con altura `n - 1`, mientras que el AVL conserva una altura logarítmica.

El segundo experimento utiliza los 12,000 DOI en el orden del archivo y compara búsqueda, recorrido ordenado, atención completa de la cola y top-10. Los tiempos están expresados en nanosegundos y dependen del hardware, del sistema operativo y de la carga de la computadora; por ello son evidencia experimental del equipo donde se ejecutó, no constantes universales.

## 6. Datos

El subconjunto se obtuvo de la API REST de Crossref (`https://api.crossref.org/works`) con los términos `data science` y `big data`, filtrando artículos de revista y conservando registros con DOI, título y fecha. El archivo CSV incluido permite ejecutar el catálogo sin conexión a internet. Para volver a generar los datos (opcional), ejecuta:

```bash
python descargar_datos.py
```

Una descarga posterior puede producir metadatos o conteos de citas distintos, ya que Crossref actualiza su información.
