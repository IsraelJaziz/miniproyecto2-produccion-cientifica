"""
catalogo.py
Miniproyecto 2 - Catálogo consultable de producción científica
Equipo: Diaz Bello Israel Jaziz, Flores Canaán Raúl Hased, Miranda Chávez Gabriela

Carga del subconjunto (articulos.csv) y solución de los cinco
problemas del enunciado con las tres estructuras:
    Problemas 1 y 2 -> ABB (abb.py)
    Problemas 3 y 4 -> AVL (avl_monticulo.py)
    Problema 5      -> montículo (avl_monticulo.py)
"""

import csv

from abb import ABB
from avl_monticulo import AVL, ColaRevision, top_k


# ======================================================================
# CATÁLOGO
# Claves: DOI (localizar), (fecha, DOI) (orden cronológico),
#         (-citas, DOI) (cola de revisión)
# ======================================================================

ARCHIVO = "articulos.csv"


# Lee el CSV en el orden del archivo (orden del cursor de Crossref).
# El módulo csv solo se usa aquí, en la carga inicial.
def cargar_articulos(ruta=ARCHIVO):
    articulos = []
    with open(ruta, encoding="utf-8") as archivo:
        for fila in csv.DictReader(archivo):
            fila["anio"] = int(fila["anio"])
            fila["citas"] = int(fila["citas"])
            articulos.append(fila)
    return articulos


class Catalogo:

    # ------------------------------------------------------------
    # Construcción del catálogo
    # Cada artículo se inserta en dos árboles por DOI, dos por fecha y
    # en la cola. El AVL por DOI se consulta primero: si el DOI ya
    # existe, el artículo se rechaza y no entra a ninguna estructura.
    # ------------------------------------------------------------
    def __init__(self, articulos):
        self.abb_doi = ABB()
        self.abb_fecha = ABB()
        self.avl_doi = AVL()
        self.avl_fecha = AVL()
        self.cola = ColaRevision()
        self.rechazados = 0
        for art in articulos:
            self.alta(art)

    def alta(self, art):
        if not self.avl_doi.insertar(art["doi"], art):
            self.rechazados += 1
            return False
        self.avl_fecha.insertar((art["fecha"], art["doi"]), art)
        self.abb_doi.insertar(art["doi"], art)
        self.abb_fecha.insertar((art["fecha"], art["doi"]), art)
        self.cola.agregar(art)
        return True

    def verificar(self):
        self.abb_doi.verificar()
        self.abb_fecha.verificar()
        self.avl_doi.verificar()
        self.avl_fecha.verificar()
        self.cola.heap.verificar()
        return True

    # ------------------------------------------------------------
    # Problema 1 (ABB): localizar por DOI, O(h), y listar en orden
    # cronológico con el inorden del árbol por fecha, O(n).
    # ------------------------------------------------------------
    def localizar(self, doi):
        return self.abb_doi.buscar(doi.strip().lower())

    def listar_cronologico(self):
        return self.abb_fecha.inorden()

    # ------------------------------------------------------------
    # Problema 2 (ABB): dar de baja un artículo de todas las
    # estructuras, para que el resto siga ordenado y consultable.
    # ------------------------------------------------------------
    def dar_de_baja(self, doi):
        doi = doi.strip().lower()
        art = self.abb_doi.buscar(doi)
        if art is None:
            return False
        clave_fecha = (art["fecha"], doi)
        self.abb_doi.eliminar(doi)
        self.abb_fecha.eliminar(clave_fecha)
        self.avl_doi.eliminar(doi)
        self.avl_fecha.eliminar(clave_fecha)
        self.cola.retirar(doi)
        return True

    # ------------------------------------------------------------
    # Problema 3 (AVL): búsqueda por DOI en O(log n) garantizado,
    # aunque los datos lleguen ordenados.
    # ------------------------------------------------------------
    def localizar_avl(self, doi):
        return self.avl_doi.buscar(doi.strip().lower())

    # ------------------------------------------------------------
    # Problema 4 (AVL): rango de años, más antiguo, más reciente y
    # siguiente. En el rango, los límites son ('AAAA-01-01', '') y
    # ('AAAA-12-31', 'zzzz'): todo DOI empieza con '10.', que queda
    # entre '' y 'zzzz'.
    # ------------------------------------------------------------
    def entre_anios(self, anio_inicio, anio_fin):
        bajo = (f"{anio_inicio:04d}-01-01", "")
        alto = (f"{anio_fin:04d}-12-31", "zzzz")
        return self.avl_fecha.rango(bajo, alto)

    def mas_antiguo(self):
        nodo = self.avl_fecha.minimo()
        return None if nodo is None else nodo.valor

    def mas_reciente(self):
        nodo = self.avl_fecha.maximo()
        return None if nodo is None else nodo.valor

    def siguiente(self, doi):
        art = self.avl_doi.buscar(doi.strip().lower())
        if art is None:
            return None
        nodo = self.avl_fecha.sucesor((art["fecha"], art["doi"]))
        return None if nodo is None else nodo.valor

    # ------------------------------------------------------------
    # Problema 5 (montículo): cola de revisión (primero el más citado)
    # y los k más citados sin ordenar toda la colección.
    # ------------------------------------------------------------
    def siguiente_a_revisar(self):
        return self.cola.siguiente()

    def atender_revision(self):
        return self.cola.atender()

    def mas_citados(self, k):
        return top_k(self.avl_doi.inorden(), k)


# Imprime los resultados del subconjunto (opción 1 del menú).
def mostrar_resultados():
    articulos = cargar_articulos()
    cat = Catalogo(articulos)
    cat.verificar()

    print("=== Resultados del subconjunto asignado ===")
    print(f"Artículos cargados: {len(articulos)}")
    print(f"DOI duplicados rechazados: {cat.rechazados}")
    print(f"Altura ABB por DOI:   {cat.abb_doi.altura()}")
    print(f"Altura AVL por DOI:   {cat.avl_doi.altura()}")
    print(f"Altura ABB por fecha: {cat.abb_fecha.altura()}")
    print(f"Altura AVL por fecha: {cat.avl_fecha.altura()}")
    print()

    doi = articulos[0]["doi"]
    print("Problema 1 - Localizar por DOI:", doi)
    art = cat.localizar(doi)
    print(f"  {art['titulo'][:70]} ({art['anio']})")
    print("Problema 1 - Primeros 3 en orden cronológico:")
    for a in cat.listar_cronologico()[:3]:
        print(f"  {a['fecha']}  {a['doi']}")
    print()

    print("Problema 4 - Consultas por fecha (AVL):")
    viejo = cat.mas_antiguo()
    nuevo = cat.mas_reciente()
    sig = cat.siguiente(viejo["doi"])
    print(f"  Más antiguo:  {viejo['fecha']}  {viejo['doi']}")
    print(f"  Más reciente: {nuevo['fecha']}  {nuevo['doi']}")
    print(f"  Siguiente al más antiguo: {sig['fecha']}  {sig['doi']}")
    print(f"  Artículos entre 2018 y 2020: {len(cat.entre_anios(2018, 2020))}")
    print()

    print("Problema 5 - Los 5 artículos más citados:")
    for a in cat.mas_citados(5):
        print(f"  {a['citas']:>5} citas  {a['doi']}")
    primero = cat.siguiente_a_revisar()
    print(f"  Primero en la cola de revisión: {primero['doi']}")
    print()

    print("Problema 2 - Dar de baja:", doi)
    cat.dar_de_baja(doi)
    cat.verificar()
    print(f"  ¿Sigue en el catálogo? {cat.localizar(doi) is not None}")
    print(f"  Artículos restantes: {cat.abb_doi.tamanio} (ABB), "
          f"{cat.avl_doi.tamanio} (AVL), {cat.cola.heap.tamanio()} (cola)")