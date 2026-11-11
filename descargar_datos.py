"""
descargar_datos.py
Miniproyecto 2 - Catálogo consultable de producción científica
Equipo: Diaz Bello Israel Jaziz, Flores Canaán Raúl Hased, Miranda Chávez Gabriela

Descarga de la Crossref REST API el subconjunto asignado:
    Área temática: ciencia de datos
    Tamaño: 12,000 registros (artículos de revista)
y se guarda en el archivo articulos.csv.

Cómo se arma el subconjunto:
  1. Se buscan artículos de revista con cada término del área, en este
     orden: "data science", "big data", "data mining". Los resultados se
     piden ordenados por relevancia (los que más se parecen salen primero).
  2. Crossref busca las palabras sueltas, así que el script se queda SOLO
     con los artículos que tienen el término completo en el título.
  3. Se descartan los que no tienen DOI, título o fecha, y los DOI repetidos.
  4. Cuando un término ya no da más artículos, se pasa al siguiente.
     Se detiene al juntar 12,000.

¿Por qué tres términos? Con "data science" solo, Crossref entrega unos
5,000 artículos que lo tengan en el título; los términos "big data" y
"data mining" son parte del área de ciencia de datos y completan los 12,000.

Solo se ejecuta UNA vez. Después, catalogo.py lee articulos.csv.

Se necesita internet para ejecutarlo y tarda varios minutos):
    python descargar_datos.py
"""

import csv
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

# ---------------------------------------------------------------
# Configuración del subconjunto
# ---------------------------------------------------------------
URL_BASE = "https://api.crossref.org/works"
# Términos del área en el orden en que se buscan
TERMINOS = ["data science", "big data", "data mining"]
FILTRO = "type:journal-article"    # solo artículos de revista
TOTAL_DESEADO = 12000              # registros asignados
POR_PAGINA = 1000                  # máximo que permite Crossref por página
MAX_PAGINAS = 300                  # límite de seguridad por término
PAGINAS_SIN_NADA = 10              # si 10 páginas seguidas no traen nada útil, se para
ARCHIVO_SALIDA = "articulos.csv"

# Crossref recomienda poner un correo de contacto (parámetro mailto)
# para entrar al conjunto de acceso preferente, que es más rápido.
CORREO = ""

# Campos que pedimos a la API (así cada respuesta pesa menos)
CAMPOS = "DOI,title,issued,author,container-title,is-referenced-by-count"


def pedir_pagina(termino, cursor):
    """Pide una página de resultados a Crossref y regresa el JSON."""
    parametros = {
        "query.bibliographic": termino,
        "filter": FILTRO,
        "sort": "relevance",       # primero los que más se parecen
        "order": "desc",
        "rows": POR_PAGINA,
        "cursor": cursor,
        "select": CAMPOS,
    }
    if CORREO:
        parametros["mailto"] = CORREO

    url = URL_BASE + "?" + urllib.parse.urlencode(parametros)
    peticion = urllib.request.Request(url, headers={"User-Agent": "miniproyecto2-itorizaba"})

    # Si la API falla, se reintenta hasta 3 veces
    for intento in range(3):
        try:
            with urllib.request.urlopen(peticion, timeout=60) as respuesta:
                return json.loads(respuesta.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            if error.code == 400:
                # Petición mal formada: reintentar no sirve
                print("Crossref rechazó la petición:", error.read().decode("utf-8")[:300])
                raise
            print(f"  Error ({error}), reintento {intento + 1} de 3...")
            time.sleep(5)
        except Exception as error:
            print(f"  Error ({error}), reintento {intento + 1} de 3...")
            time.sleep(5)
    raise RuntimeError("No se pudo descargar la página después de 3 intentos")


def convertir_registro(item):
    """
    Convierte un registro de Crossref en un diccionario sencillo.
    Regresa None si al registro le falta DOI, título o fecha.
    """
    doi = item.get("DOI", "").strip().lower()
    partes_fecha = item.get("issued", {}).get("date-parts", [[None]])[0]
    titulos = item.get("title", [])
    if not doi or not titulos or not partes_fecha or partes_fecha[0] is None:
        return None

    anio = partes_fecha[0]
    mes = partes_fecha[1] if len(partes_fecha) > 1 else 1
    dia = partes_fecha[2] if len(partes_fecha) > 2 else 1

    revistas = item.get("container-title", [])
    revista = revistas[0] if revistas else "(sin revista)"

    autores = []
    for autor in item.get("author", []):
        nombre = (autor.get("given", "") + " " + autor.get("family", "")).strip()
        if nombre:
            autores.append(nombre)

    return {
        "doi": doi,
        # quita etiquetas HTML como <i>...</i> y espacios o saltos de línea extra
        "titulo": " ".join(re.sub(r"<[^>]+>", "", titulos[0]).split()),
        "fecha": f"{anio:04d}-{mes:02d}-{dia:02d}",
        "anio": anio,
        "autores": "; ".join(autores),
        "revista": revista,
        "citas": item.get("is-referenced-by-count", 0),
    }


def tiene_termino(registro, termino):
    """True si el título contiene el término (sin importar mayúsculas ni guiones)."""
    titulo = registro["titulo"].lower().replace("-", " ")
    return termino in titulo


def main():
    registros = []
    dois_vistos = set()
    revisados = 0
    sin_datos = 0
    sin_termino = 0
    duplicados = 0
    por_termino = {}

    for termino in TERMINOS:
        if len(registros) == TOTAL_DESEADO:
            break
        print(f"Buscando artículos con '{termino}' en el título...")
        antes = len(registros)
        paginas = 0
        paginas_sin_nada = 0
        cursor = "*"   # "*" indica a Crossref que es la primera página

        while len(registros) < TOTAL_DESEADO and paginas < MAX_PAGINAS:
            datos = pedir_pagina(termino, cursor)
            items = datos["message"]["items"]
            if not items:
                print("  La API ya no tiene más resultados.")
                break
            paginas += 1

            nuevos_en_pagina = 0
            for item in items:
                revisados += 1
                registro = convertir_registro(item)
                if registro is None:
                    sin_datos += 1
                elif not tiene_termino(registro, termino):
                    sin_termino += 1
                elif registro["doi"] in dois_vistos:
                    duplicados += 1
                else:
                    dois_vistos.add(registro["doi"])
                    registros.append(registro)
                    nuevos_en_pagina += 1
                if len(registros) == TOTAL_DESEADO:
                    break

            # Si ya casi no salen artículos con el término, se pasa al siguiente
            if nuevos_en_pagina == 0:
                paginas_sin_nada += 1
                if paginas_sin_nada == PAGINAS_SIN_NADA:
                    print(f"  {PAGINAS_SIN_NADA} páginas seguidas sin artículos nuevos; "
                          "se pasa al siguiente término.")
                    break
            else:
                paginas_sin_nada = 0

            cursor = datos["message"]["next-cursor"]
            print(f"  Página {paginas}: llevamos {len(registros)} artículos")
            time.sleep(1)   # pausa para no saturar la API

        por_termino[termino] = len(registros) - antes

    # Se guarda en el mismo orden en que llegó del cursor (No se ordena)
    columnas = ["doi", "titulo", "fecha", "anio", "autores", "revista", "citas"]
    with open(ARCHIVO_SALIDA, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(registros)

    print()
    print(f"Listo: {len(registros)} artículos guardados en {ARCHIVO_SALIDA}")
    for termino, cuantos in por_termino.items():
        print(f"  con '{termino}': {cuantos}")
    print(f"Resultados revisados: {revisados}")
    print(f"Descartados sin DOI, título o fecha: {sin_datos}")
    print(f"Descartados sin el término en el título: {sin_termino}")
    print(f"Descartados por DOI repetido: {duplicados}")
    print(f"Fecha de descarga: {time.strftime('%Y-%m-%d')}")
    if len(registros) < TOTAL_DESEADO:
        print(f"OJO: solo se juntaron {len(registros)} de {TOTAL_DESEADO}.")


if __name__ == "__main__":
    main()
