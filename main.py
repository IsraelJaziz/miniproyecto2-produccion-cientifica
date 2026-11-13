"""
main.py
Miniproyecto 2 - Catálogo consultable de producción científica
Equipo: Diaz Bello Israel Jaziz, Flores Canaán Raúl Hased, Miranda Chávez Gabriela

Programa principal: mediciones (evidencia experimental), batería de
pruebas y menú.

Se ejecuta con articulos.csv y los demás .py en la misma carpeta:
    python main.py
y elegir una opción del menú.
"""

import heapq
import math
import os
import random
import statistics
import time

from abb import ABB
from avl_monticulo import AVL, NodoAVL, MinHeap, ColaRevision, top_k
from catalogo import Catalogo, cargar_articulos, mostrar_resultados


# ======================================================================
# MEDICIONES - evidencia experimental
# Claves = DOI reales; tiempos en ns con time.perf_counter_ns();
# 30 repeticiones y se reporta la MEDIANA; semilla 2026.
# Tamaños 1000, 2000 y 4000: con inserción ordenada el ABB cuesta O(n^2)
# al construirse. En cada repetición se buscan 100 claves.
# ======================================================================

REPETICIONES = 30
TAMANIOS = [1000, 2000, 4000]
BUSQUEDAS = 100
SEMILLA = 2026


# Ejecuta la función REPETICIONES veces y regresa la mediana en ns.
def mediana_ns(funcion):
    tiempos = []
    for _ in range(REPETICIONES):
        inicio = time.perf_counter_ns()
        funcion()
        tiempos.append(time.perf_counter_ns() - inicio)
    return statistics.median(tiempos)


def construir(clase, claves):
    arbol = clase()
    for c in claves:
        arbol.insertar(c, c)
    return arbol


def buscar_todas(arbol, claves):
    for c in claves:
        arbol.buscar(c)


# Experimento 1: altura y búsqueda del ABB frente al AVL, con DOI en orden
# y en orden aleatorio, contrastadas con las cotas teóricas.
def experimento_alturas(dois):
    print("=== 1) ABB frente a AVL: altura y búsqueda ===")
    print("Cotas teóricas: altura mínima posible = piso(log2 n);")
    print("                AVL <= 1.44 * log2(n + 2);  ABB en orden = n - 1")
    print()
    print(f"{'n':>6} {'orden':>10} {'alt ABB':>8} {'alt AVL':>8} "
          f"{'log2 n':>7} {'1.44log2':>9} {'busq ABB ns':>12} {'busq AVL ns':>12}")

    azar = random.Random(SEMILLA)
    for n in TAMANIOS:
        muestra = azar.sample(dois, n)
        ordenadas = sorted(muestra)
        aleatorias = muestra[:]
        azar.shuffle(aleatorias)
        a_buscar = azar.sample(muestra, BUSQUEDAS)

        for nombre, claves in (("ordenado", ordenadas), ("aleatorio", aleatorias)):
            abb = construir(ABB, claves)
            avl = construir(AVL, claves)
            avl.verificar()
            t_abb = mediana_ns(lambda: buscar_todas(abb, a_buscar)) / BUSQUEDAS
            t_avl = mediana_ns(lambda: buscar_todas(avl, a_buscar)) / BUSQUEDAS
            print(f"{n:>6} {nombre:>10} {abb.altura():>8} {avl.altura():>8} "
                  f"{math.floor(math.log2(n)):>7} {1.44 * math.log2(n + 2):>9.1f} "
                  f"{t_abb:>12.0f} {t_avl:>12.0f}")
    print()


# Experimento 2: estructuras propias frente a dict, sorted y heapq,
# con el subconjunto completo en el orden del cursor.
def experimento_nativas(articulos):
    print("=== 2) Estructuras propias frente a las nativas de Python ===")
    print(f"Subconjunto completo, n = {len(articulos)}, en el orden del cursor")
    print()
    dois = [a["doi"] for a in articulos]
    a_buscar = random.Random(SEMILLA).sample(dois, BUSQUEDAS)

    abb = construir(ABB, dois)
    avl = construir(AVL, dois)
    diccionario = {d: d for d in dois}

    def buscar_dict():
        for c in a_buscar:
            diccionario.get(c)

    print("Búsqueda por DOI (ns por búsqueda):")
    print(f"  ABB  {mediana_ns(lambda: buscar_todas(abb, a_buscar)) / BUSQUEDAS:>10.0f}")
    print(f"  AVL  {mediana_ns(lambda: buscar_todas(avl, a_buscar)) / BUSQUEDAS:>10.0f}")
    print(f"  dict {mediana_ns(buscar_dict) / BUSQUEDAS:>10.0f}")
    print()

    print("Listado ordenado por DOI (ns por listado completo):")
    print(f"  inorden ABB {mediana_ns(abb.inorden):>14.0f}")
    print(f"  inorden AVL {mediana_ns(avl.inorden):>14.0f}")
    print(f"  sorted      {mediana_ns(lambda: sorted(dois)):>14.0f}")
    print()

    claves_cola = [((-a["citas"], a["doi"]), a) for a in articulos]

    def cola_propia():
        cola = ColaRevision()
        for a in articulos:
            cola.agregar(a)
        while cola.atender() is not None:
            pass

    def cola_heapq():
        h = []
        for par in claves_cola:
            heapq.heappush(h, par)
        while h:
            heapq.heappop(h)

    print("Cola de revisión: insertar todos y atenderlos todos (ns):")
    print(f"  montículo propio {mediana_ns(cola_propia):>14.0f}")
    print(f"  heapq            {mediana_ns(cola_heapq):>14.0f}")
    print()

    k = 10
    propio = [a["doi"] for a in top_k(articulos, k)]
    nativo = [c[1] for c in heapq.nsmallest(k, (par[0] for par in claves_cola))]
    print(f"Top-{k} más citados (ns):")
    print(f"  top_k propio     {mediana_ns(lambda: top_k(articulos, k)):>14.0f}")
    print(f"  heapq.nsmallest  "
          f"{mediana_ns(lambda: heapq.nsmallest(k, (p[0] for p in claves_cola))):>14.0f}")
    print(f"  ¿Mismo resultado que heapq? {propio == nativo}")


def correr_mediciones():
    articulos = cargar_articulos()
    dois = [a["doi"] for a in articulos]
    experimento_alturas(dois)
    experimento_nativas(articulos)

# ======================================================================
# PRUEBAS
# Cubre las cuatro rotaciones (aisladas), los tres casos de eliminación,
# las operaciones del montículo y los cinco problemas del catálogo.
# ======================================================================

def arbol_de(clase, claves):
    arbol = clase()
    for c in claves:
        arbol.insertar(c, c)
    return arbol


# ================================================================
# ABB
# ================================================================
def prueba_abb_basico():
    t = arbol_de(ABB, [50, 30, 70, 20, 40, 60, 80])
    t.verificar()
    assert t.buscar(40) == 40
    assert t.buscar(45) is None
    assert t.minimo().clave == 20
    assert t.maximo().clave == 80
    assert t.sucesor(40).clave == 50
    assert t.sucesor(50).clave == 60
    assert t.sucesor(80) is None
    assert t.tamanio == 7


def prueba_abb_recorridos():
    t = arbol_de(ABB, [50, 30, 70, 20, 40, 60, 80])
    assert t.inorden() == [20, 30, 40, 50, 60, 70, 80]
    assert t.preorden() == [50, 30, 20, 40, 70, 60, 80]
    assert t.postorden() == [20, 40, 30, 60, 80, 70, 50]
    copia = arbol_de(ABB, t.preorden())
    assert copia.preorden() == t.preorden()
    assert t.altura() == 2


def prueba_abb_duplicados():
    t = arbol_de(ABB, [5, 3, 8])
    assert t.insertar(3, "otro") is False
    assert t.tamanio == 3
    assert t.buscar(3) == 3


def prueba_abb_eliminar_hoja():
    t = arbol_de(ABB, [50, 30, 70, 20, 40])
    assert t.eliminar(20)
    t.verificar()
    assert t.inorden() == [30, 40, 50, 70]


def prueba_abb_eliminar_un_hijo():
    t = arbol_de(ABB, [50, 30, 70, 20])
    assert t.eliminar(30)
    t.verificar()
    assert t.raiz.izq.clave == 20
    t = arbol_de(ABB, [50, 30, 70, 80])
    assert t.eliminar(70)
    t.verificar()
    assert t.raiz.der.clave == 80


def prueba_abb_eliminar_dos_hijos():
    t = arbol_de(ABB, [50, 30, 70, 20, 40])
    assert t.eliminar(30)
    t.verificar()
    assert t.raiz.izq.clave == 40
    t = arbol_de(ABB, [50, 30, 70, 60, 80, 65])
    assert t.eliminar(50)
    t.verificar()
    assert t.raiz.clave == 60
    assert t.raiz.der.izq.clave == 65
    assert t.inorden() == [30, 60, 65, 70, 80]
    assert t.eliminar(99) is False


def prueba_abb_aleatoria():
    for semilla in range(50):
        azar = random.Random(semilla)
        claves = azar.sample(range(300), 80)
        t = arbol_de(ABB, claves)
        vivos = set(claves)
        for c in azar.sample(claves, 50):
            t.eliminar(c)
            vivos.remove(c)
            t.verificar()
        assert t.inorden() == sorted(vivos)


# ================================================================
# AVL: rotaciones aisladas sobre árboles armados a mano
# nodo() arma un nodo conectando padres y calculando su altura.
# Las cuatro rotaciones básicas deben dejar 20 con hijos 10 y 30.
# ================================================================
def nodo(clave, izq=None, der=None):
    n = NodoAVL(clave, clave)
    n.izq = izq
    n.der = der
    if izq is not None:
        izq.padre = n
    if der is not None:
        der.padre = n
    alt_izq = izq.altura if izq else -1
    alt_der = der.altura if der else -1
    n.altura = 1 + max(alt_izq, alt_der)
    return n


def arbol_a_mano(raiz, tamanio):
    t = AVL()
    t.raiz = raiz
    t.tamanio = tamanio
    return t


def prueba_rotacion_LL():
    t = arbol_a_mano(nodo(30, izq=nodo(20, izq=nodo(10))), 3)
    assert t.factor_balance(t.raiz) == 2
    t.rotacion_LL(t.raiz)
    t.verificar()
    assert t.preorden() == [20, 10, 30]


def prueba_rotacion_RR():
    t = arbol_a_mano(nodo(10, der=nodo(20, der=nodo(30))), 3)
    assert t.factor_balance(t.raiz) == -2
    t.rotacion_RR(t.raiz)
    t.verificar()
    assert t.preorden() == [20, 10, 30]


def prueba_rotacion_LR():
    t = arbol_a_mano(nodo(30, izq=nodo(10, der=nodo(20))), 3)
    assert t.factor_balance(t.raiz.izq) == -1
    t.rotacion_LR(t.raiz)
    t.verificar()
    assert t.preorden() == [20, 10, 30]


def prueba_rotacion_RL():
    t = arbol_a_mano(nodo(10, der=nodo(30, izq=nodo(20))), 3)
    assert t.factor_balance(t.raiz.der) == 1
    t.rotacion_RL(t.raiz)
    t.verificar()
    assert t.preorden() == [20, 10, 30]


def prueba_rotacion_con_subarboles():
    t = arbol_a_mano(
        nodo(40, izq=nodo(30, izq=nodo(20, izq=nodo(10)), der=nodo(35)),
             der=nodo(50)), 6)
    t.rotacion_LL(t.raiz)
    t.verificar()
    assert t.preorden() == [30, 20, 10, 40, 35, 50]
    assert t.raiz.der.izq.clave == 35
    assert t.raiz.der.izq.padre.clave == 40


# ================================================================
# AVL: inserción y eliminación con rebalanceo
# Incluye una eliminación que requiere rotaciones en cascada
# (al borrar 80, la raíz final es 20).
# ================================================================
def prueba_avl_insercion_cuatro_casos():
    assert arbol_de(AVL, [30, 20, 10]).preorden() == [20, 10, 30]
    assert arbol_de(AVL, [10, 20, 30]).preorden() == [20, 10, 30]
    assert arbol_de(AVL, [30, 10, 20]).preorden() == [20, 10, 30]
    assert arbol_de(AVL, [10, 30, 20]).preorden() == [20, 10, 30]


def prueba_avl_insercion_ordenada():
    t = AVL()
    for i in range(1, 1024):
        t.insertar(i, i)
    t.verificar()
    assert t.altura() == 9


def prueba_avl_eliminacion_tres_casos():
    t = arbol_de(AVL, [50, 30, 70, 20, 40, 60, 80, 10])
    assert t.eliminar(10)
    t.verificar()
    assert t.eliminar(20) and t.eliminar(30)
    t.verificar()
    assert t.eliminar(50)
    t.verificar()
    assert t.inorden() == [40, 60, 70, 80]


def prueba_avl_eliminacion_en_cascada():
    t = arbol_de(AVL, [50, 20, 70, 10, 30, 60, 80, 5, 15, 25, 40, 65, 3])
    t.verificar()
    assert t.eliminar(80)
    t.verificar()
    assert t.raiz.clave == 20


def prueba_avl_aleatoria():
    for semilla in range(50):
        azar = random.Random(semilla)
        claves = azar.sample(range(500), 150)
        t = AVL()
        for c in claves:
            t.insertar(c, c)
            t.verificar()
        vivos = set(claves)
        for c in azar.sample(claves, 100):
            t.eliminar(c)
            vivos.remove(c)
            t.verificar()
        assert t.inorden() == sorted(vivos)
        assert t.rango(100, 300) == [x for x in sorted(vivos) if 100 <= x <= 300]


# ================================================================
# MONTÍCULO
# ================================================================
def prueba_heap_insertar_extraer():
    h = MinHeap()
    for x in [7, 3, 9, 1, 5, 8, 2]:
        h.insertar(x, f"v{x}")
        h.verificar()
    assert h.ver_minimo() == (1, "v1")
    salida = []
    while not h.esta_vacio():
        salida.append(h.extraer_minimo()[0])
        h.verificar()
    assert salida == [1, 2, 3, 5, 7, 8, 9]
    assert h.extraer_minimo() is None


def prueba_heap_decrementar():
    h = MinHeap()
    for x in [10, 20, 30, 40, 50]:
        h.insertar(x, x)
    i = h.datos.index((50, 50))
    h.decrementar_clave(i, 5)
    h.verificar()
    assert h.ver_minimo() == (5, 50)
    try:
        h.decrementar_clave(0, 100)
        assert False, "Debió lanzar ValueError"
    except ValueError:
        pass


def prueba_heap_construir():
    azar = random.Random(7)
    valores = [azar.randint(0, 1000) for _ in range(300)]
    h = MinHeap()
    h.construir([(v, v) for v in valores])
    h.verificar()
    assert [h.extraer_minimo()[0] for _ in range(300)] == sorted(valores)


def prueba_cola_revision():
    arts = [{"doi": "a", "citas": 5}, {"doi": "b", "citas": 50},
            {"doi": "c", "citas": 20}, {"doi": "d", "citas": 20}]
    cola = ColaRevision()
    for a in arts:
        cola.agregar(a)
    assert cola.siguiente()["doi"] == "b"
    assert cola.actualizar_citas("a", 100)
    cola.heap.verificar()
    assert cola.atender()["doi"] == "a"
    assert cola.retirar("b")
    cola.heap.verificar()
    assert cola.atender()["doi"] == "c"
    assert cola.atender()["doi"] == "d"
    assert cola.atender() is None


def prueba_top_k_contra_heapq():
    azar = random.Random(3)
    arts = [{"doi": f"10.{i}", "citas": azar.randint(0, 50)} for i in range(1000)]
    propio = [a["doi"] for a in top_k(arts, 15)]
    nativo = [a["doi"] for a in
              heapq.nsmallest(15, arts, key=lambda a: (-a["citas"], a["doi"]))]
    assert propio == nativo


# ================================================================
# CATÁLOGO con el subconjunto real
# Compara los cinco problemas contra resultados calculados con
# sorted y heapq. Se omite si no está articulos.csv.
# ================================================================
def prueba_catalogo():
    if not os.path.exists("articulos.csv"):
        print("  (se omite: no está articulos.csv)")
        return
    arts = cargar_articulos()
    cat = Catalogo(arts)
    cat.verificar()
    assert cat.avl_doi.tamanio == len(arts)

    for a in arts[:50]:
        assert cat.localizar(a["doi"]) is a
    fechas = [(a["fecha"], a["doi"]) for a in cat.listar_cronologico()]
    assert fechas == sorted(fechas)

    assert cat.avl_doi.altura() <= 1.44 * math.log2(len(arts) + 2)

    esperado = sorted((a for a in arts if 2018 <= a["anio"] <= 2020),
                      key=lambda a: (a["fecha"], a["doi"]))
    assert cat.entre_anios(2018, 2020) == esperado
    ordenados = sorted(arts, key=lambda a: (a["fecha"], a["doi"]))
    assert cat.mas_antiguo() is ordenados[0]
    assert cat.mas_reciente() is ordenados[-1]
    assert cat.siguiente(ordenados[10]["doi"]) is ordenados[11]

    nativo = heapq.nsmallest(10, arts, key=lambda a: (-a["citas"], a["doi"]))
    assert cat.mas_citados(10) == nativo
    assert cat.siguiente_a_revisar() is nativo[0]

    doi = arts[0]["doi"]
    assert cat.dar_de_baja(doi)
    cat.verificar()
    assert cat.localizar(doi) is None and cat.localizar_avl(doi) is None
    assert cat.cola.posicion_de(doi) == -1
    assert cat.dar_de_baja(doi) is False
    assert cat.alta(arts[1]) is False


# Ejecuta todas las funciones cuyo nombre empieza con prueba_.
def correr_pruebas():
    pruebas = [nombre for nombre in globals() if nombre.startswith("prueba_")]
    for nombre in pruebas:
        globals()[nombre]()
        print(f"OK  {nombre}")
    print(f"\nTodas las pruebas pasaron ({len(pruebas)}).")

# ======================================================================
# MENÚ
# ======================================================================

def main():
    print("Catálogo de producción científica")
    print("  1. Ver resultados del subconjunto (problemas 1 a 5)")
    print("  2. Correr las pruebas")
    print("  3. Correr las mediciones")
    opcion = input("Elige una opción (1, 2 o 3): ").strip()
    print()
    if opcion == "1":
        mostrar_resultados()
    elif opcion == "2":
        correr_pruebas()
    elif opcion == "3":
        correr_mediciones()
    else:
        print("Opción no válida")


if __name__ == "__main__":
    main()