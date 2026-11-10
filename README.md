# Miniproyecto 2 · Catálogo consultable de producción científica

Estructuras de Datos · TecNM / Instituto Tecnológico de Orizaba · Dr. Ulises Juárez Martínez

Equipo: Diaz Bello Israel Jaziz · Raúl · Miranda Chávez Gabriela

## Archivos

| Archivo | Qué es |
|---|---|
| `proyecto.py` | Todo el proyecto: ABB, AVL, montículo, catálogo (problemas 1 a 5), mediciones y pruebas. |
| `articulos.csv` | Subconjunto asignado: 12,000 artículos de Crossref, área ciencia de datos. |
| `descargar_datos.py` | Script que generó `articulos.csv`. Ya no hace falta correrlo. |
| `README.md` | Este archivo: instrucciones, especificación de los TDA y bitácora. |

## Cómo ejecutarlo

- **Requisitos:** Python 3.10 o más reciente. No hace falta instalar nada.
- Desde la carpeta del proyecto, con `articulos.csv` en ella:

```
python proyecto.py
```

El programa muestra un menú:

1. **Resultados del subconjunto:** los problemas 1 a 5, para contrastar con los valores de control.
2. **Pruebas:** deben pasar las 23.
3. **Mediciones:** ABB frente a AVL y frente a las estructuras nativas. Tardan unos segundos.

**Volver a descargar los datos** (opcional, necesita internet): `python descargar_datos.py`. Crossref actualiza las citas, así que una descarga nueva puede dar resultados distintos.

**Subconjunto:**
- Crossref REST API, `https://api.crossref.org/works`.
- Parámetros de la búsqueda: `query.bibliographic="data science"` y `filter=type:journal-article`.
- Paginación por cursor, de 1,000 en 1,000.
- Se tomaron los primeros 12,000 registros con DOI y fecha.

## Especificación de los TDA

Notación: *n* = número de artículos guardados; *h* = altura del árbol; *m* = número de resultados de una consulta.

---

### 1. Elemento del dominio: Artículo

Un artículo es un registro con estos campos, tomados de la Crossref REST API:

| Campo | Tipo | Ejemplo |
|---|---|---|
| doi | texto en minúsculas | `10.1067/mje.2000.104899` |
| titulo | texto | Optimal Rotational Interval for… |
| fecha | texto `AAAA-MM-DD` | `2000-08-01` |
| anio | entero | 2000 |
| autores | texto, separados por `;` | Youssef F.M. Nosir; … |
| revista | texto | Journal of the American Society of Echocardiography |
| citas | entero ≥ 0 (`is-referenced-by-count`) | 9 |

Si Crossref solo da año y mes, o solo año, el día y el mes faltantes se toman como 01.

---

### 2. TDA Diccionario ordenado

Guarda parejas (clave, valor) con claves únicas y comparables, y permite recorrerlas en orden de clave.

**Implementaciones:** `ABB` y `AVL` (partes 1 y 2 de proyecto.py).

**Invariante:**
- Todo nodo del subárbol izquierdo tiene clave menor que la del nodo, y todo nodo del subárbol derecho tiene clave mayor.
- Cada hijo apunta a su padre.
- En el AVL, además, cada nodo guarda su altura correcta y su factor de balance está en {-1, 0, 1}.

| Operación | Precondición | Poscondición | ABB | AVL |
|---|---|---|---|---|
| `insertar(clave, valor)` | `clave` es comparable con las demás | Si la clave no existía, queda guardada, el tamaño aumenta en 1 y regresa True. Si ya existía, el diccionario no cambia y regresa False. | O(h); peor caso O(n) | O(log n) |
| `buscar(clave)` | ninguna | Regresa el valor asociado, o None si no existe. No modifica nada. | O(h) | O(log n) |
| `eliminar(clave)` | ninguna | Si existía, se quita, el tamaño disminuye en 1, se conserva el invariante y regresa True. Si no existía, regresa False. | O(h) | O(log n) |
| `minimo()` / `maximo()` | ninguna | Regresa el nodo con la menor / mayor clave, o None si está vacío. | O(h) | O(log n) |
| `sucesor(clave)` | ninguna | Regresa el nodo con la menor clave mayor que `clave`, o None si es el máximo o `clave` no existe. | O(h) | O(log n) |
| `inorden()` | ninguna | Regresa los valores ordenados por clave. | O(n) | O(n) |
| `preorden()` | ninguna | Regresa las claves en orden raíz-izquierdo-derecho; insertarlas en ese orden reconstruye la misma forma. | O(n) | O(n) |
| `postorden()` | ninguna | Regresa las claves en orden izquierdo-derecho-raíz. | O(n) | O(n) |
| `rango(bajo, alto)` | `bajo <= alto` | Regresa en orden los valores con `bajo <= clave <= alto`. | — | O(log n + m) |
| `altura()` | ninguna | Regresa la altura (vacío = -1, una hoja = 0). | O(n) | O(1) |
| `verificar()` | ninguna | Regresa True si se cumple el invariante; si no, lanza AssertionError con el nodo que falla. | O(n) | O(n) |

---

### 3. TDA Cola de prioridad

Guarda parejas (clave, valor) y siempre entrega primero la de clave mínima.

**Implementación:** `MinHeap` (parte 3 de proyecto.py), sobre un arreglo. En el dominio se usa a través de `ColaRevision`.

**Invariante (min-heap):**
- Para toda posición i > 0, la clave en i es mayor o igual que la clave de su padre, en la posición (i - 1) // 2.
- El arreglo no tiene huecos.

| Operación | Precondición | Poscondición | Costo |
|---|---|---|---|
| `insertar(clave, valor)` | `clave` es comparable | La pareja queda en la cola y se conserva el invariante. | O(log n) |
| `ver_minimo()` | ninguna | Regresa la pareja de clave mínima sin quitarla, o None si está vacía. | O(1) |
| `extraer_minimo()` | ninguna | Quita y regresa la pareja de clave mínima, o None si está vacía. Se conserva el invariante. | O(log n) |
| `decrementar_clave(i, nueva)` | `0 <= i < n` y `nueva <= clave actual` | El elemento en i tiene la nueva clave y se conserva el invariante. Si `nueva` es mayor, lanza ValueError. | O(log n) |
| `construir(parejas)` | ninguna | La cola contiene exactamente esas parejas y cumple el invariante. | O(n) |
| `esta_vacio()` / `tamanio()` | ninguna | Regresa si está vacía / cuántos elementos tiene. | O(1) |
| `verificar()` | ninguna | Regresa True si se cumple el invariante; si no, lanza AssertionError. | O(n) |

**Operaciones del dominio (ColaRevision):**
- `agregar` y `atender` usan `insertar` y `extraer_minimo`.
- `actualizar_citas(doi, nuevas)` y `retirar(doi)` primero buscan la posición del DOI en el arreglo, O(n), y luego usan `decrementar_clave`, O(log n).
- `top_k(articulos, k)` usa `construir` y luego extrae k veces: O(n + k log n), sin ordenar toda la colección.

---

### 4. Justificación de las claves

| Estructura | Clave | Por qué |
|---|---|---|
| ABB / AVL por DOI | `doi` | El problema 1 pide localizar *por DOI*. El DOI es único por artículo y no cambia con el tiempo, a diferencia de las citas. |
| ABB / AVL por fecha | `(fecha, doi)` | Los problemas 1 y 4 piden orden cronológico, rango de años, más antiguo, más reciente y siguiente. Con la fecha como clave, el inorden ya es cronológico y el rango es una consulta de intervalo. La fecha sola se repite mucho (en el subconjunto hay 590 fechas distintas para 12,000 artículos), así que se agrega el DOI para desempatar y que la clave sea única. |
| Montículo | `(-citas, doi)` | El problema 5 pide atender primero al *más citado*. Como el montículo es de mínimos, se niegan las citas. El DOI desempata artículos con las mismas citas, así el orden de atención no depende del orden de llegada. |

**Respuesta a la pregunta guía.**
- **DOI:** sirve para *identificar* un artículo, porque es único y estable. No dice nada del orden temporal ni de la importancia del artículo.
- **Año o fecha de publicación:** sirve para *ordenar y consultar por intervalos*, y por eso se usa en los árboles. No sirve sola como identificador.
- **Conteo de citas:** sirve para *priorizar*. Solo importa saber cuál es el máximo y extraerlo, no el orden total, y eso es lo que hace un montículo en O(log n). Además, las citas cambian con el tiempo, así que no sirven como clave de un árbol de búsqueda.

**Por qué AVL y no solo ABB (problema 3).** El cursor de Crossref entrega los registros en un orden fijo. En nuestro subconjunto, el 94% de los registros consecutivos ya vienen en orden de DOI. Insertados así, el ABB por DOI queda con altura 284, cuando lo ideal ronda 13. Con datos totalmente ordenados el ABB llega a altura n - 1. El AVL se mantiene en 15 con los mismos datos.

---

### 5. Política de claves duplicadas

**Se rechazan**, de la misma forma en las tres estructuras:
- `ABB.insertar` y `AVL.insertar` regresan False y no modifican el árbol.
- El catálogo inserta primero en el AVL por DOI. Si lo rechaza, el artículo no entra a ninguna otra estructura (tampoco al montículo) y se cuenta en `rechazados`.
- En la cola, un cambio de citas se hace con `actualizar_citas` (decrementar clave), nunca insertando el artículo otra vez.

**Motivo:** un DOI identifica a un solo artículo, así que un DOI repetido es un error de datos o un duplicado, que el problema 2 pide dar de baja. No es un artículo nuevo.

## Bitácora

### Decisiones de diseño

| Fecha | Decisión | Motivo |
|---|---|---|
| 04/11/2026 | Subconjunto: búsqueda "data science" en Crossref, solo artículos de revista, primeros 12,000 en orden del cursor. | El docente asignó el área de ciencia de datos con 12,000 registros, sin ficha con filtro exacto. |
| 04/11/2026 | Se descartan los registros sin DOI o sin fecha y los DOI repetidos. Si falta el día o el mes, se usa 01. | El DOI es la clave de búsqueda y la fecha la del orden cronológico; sin ellas el registro no se puede ubicar. |
| 04/11/2026 | Los DOI se guardan en minúsculas. | Crossref no distingue mayúsculas en los DOI; así una búsqueda no falla por cómo se escribió. |
| 08/11/2026 | Descarga del subconjunto: 12,000 registros, 0 duplicados. Años de 1952 a 2002. | Se guardó en `articulos.csv`. |
| 08/11/2026 | Claves: DOI para localizar, (fecha, DOI) para el orden cronológico y (-citas, DOI) para la cola de revisión. | Ver la sección Especificación de los TDA de este archivo. |
| 08/11/2026 | Política de duplicados: rechazarlos en las tres estructuras. | Un DOI identifica a un solo artículo. |
| 08/11/2026 | Se usan dos árboles por estructura (uno por DOI y otro por fecha), y la baja se hace en todos. | Un solo árbol no puede estar ordenado por DOI y por fecha a la vez. |
| 08/11/2026 | El AVL hereda del ABB buscar, mínimo, máximo, sucesor, transplant y recorridos; redefine insertar y eliminar. | No se repite código que es idéntico. |
| 08/11/2026 | Se sube el límite de recursión de Python a 50,000. | Con inserción ordenada el ABB llega a altura n - 1 y los recorridos recursivos superan el límite de 1,000. |
| 08/11/2026 | Para decrementar clave en la cola se busca la posición del DOI recorriendo el arreglo, O(n). | Mantener un índice de posiciones requeriría un dict, que el enunciado solo permite como referencia. |
| 08/11/2026 | La baja en la cola se hace con decrementar clave a -infinito y luego extraer el mínimo. | Así se reutilizan las operaciones del montículo. |
| 08/11/2026 | En las mediciones con inserción ordenada se usan n = 1,000, 2,000 y 4,000. | El ABB en orden cuesta O(n²) al construirse. |
| 08/11/2026 | Hallazgo: el CSV viene casi ordenado por DOI (94% de pares consecutivos en orden). El ABB por DOI quedó con altura 284 y el AVL con 15. | Es la evidencia que justifica el AVL (problema 3). |

### Uso de LLM

Herramienta: Claude (Anthropic).

| Fecha | Qué se pidió | Qué se aceptó | Qué se corrigió |
|---|---|---|---|
| 04/11/2026 | Script para descargar el subconjunto de Crossref. | `descargar_datos.py` completo. | — |
| 08/11/2026 | Revisión del CSV descargado. | Diagnóstico: 12,000 registros válidos, sin duplicados, casi ordenados por DOI. | El LLM advirtió que muchos artículos no son de ciencia de datos (contienen "data" en el título). Se consultará al docente si el subconjunto es válido para los valores de control. |
| 08/11/2026 | ABB, AVL, montículo, catálogo, mediciones, pruebas, especificación de los TDA y documentación, a nivel principiante. | Todo el código y los documentos. | — *(completar con lo que el equipo cambie al revisar)* |

> El equipo registra aquí cada cambio que haga a lo generado por el LLM.
