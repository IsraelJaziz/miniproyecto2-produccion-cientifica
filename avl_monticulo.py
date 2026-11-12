"""
avl_monticulo.py
Miniproyecto 2 - Catálogo consultable de producción científica
Equipo: Diaz Bello Israel Jaziz, Flores Canaán Raúl Hased, Miranda Chávez Gabriela

Árbol AVL (con las cuatro rotaciones) y montículo binario mínimo
(min-heap) sobre arreglo, con la cola de revisión y top-k.
Los usa catalogo.py.

Política de claves duplicadas: se RECHAZAN.
"""

from abb import ABB


# ======================================================================
# AVL - ABB que se mantiene balanceado
# Cada nodo guarda además su altura. El factor de balance de cada nodo
# queda en -1, 0 o 1, así la altura es O(log n) aunque los datos
# lleguen ordenados. Hereda del ABB lo que no cambia.
# ======================================================================

class NodoAVL:
    def __init__(self, clave, valor):
        self.clave = clave
        self.valor = valor
        self.izq = None
        self.der = None
        self.padre = None
        self.altura = 0


# Altura de un nodo; un subárbol vacío (None) tiene altura -1.
def alt(nodo):
    if nodo is None:
        return -1
    return nodo.altura


class AVL(ABB):

    # ------------------------------------------------------------
    # ALTURA Y FACTOR DE BALANCE   O(1)
    # altura = 1 + la mayor altura de los hijos
    # FB     = altura(izquierdo) - altura(derecho)
    # ------------------------------------------------------------
    def actualizar_altura(self, nodo):
        nodo.altura = 1 + max(alt(nodo.izq), alt(nodo.der))

    def factor_balance(self, nodo):
        return alt(nodo.izq) - alt(nodo.der)

    def altura(self):
        return alt(self.raiz)

    # ------------------------------------------------------------
    # ROTACIONES SIMPLES   O(1)
    # Izquierda: el hijo derecho (y) sube y x baja a su izquierda;
    #            el hijo izquierdo de y pasa a ser hijo derecho de x.
    # Derecha:   el caso espejo.
    # Se actualiza primero la altura del nodo que bajó.
    # ------------------------------------------------------------
    def rotar_izquierda(self, x):
        y = x.der
        x.der = y.izq
        if y.izq is not None:
            y.izq.padre = x
        y.padre = x.padre
        if x.padre is None:
            self.raiz = y
        elif x == x.padre.izq:
            x.padre.izq = y
        else:
            x.padre.der = y
        y.izq = x
        x.padre = y
        self.actualizar_altura(x)
        self.actualizar_altura(y)
        return y

    def rotar_derecha(self, y):
        x = y.izq
        y.izq = x.der
        if x.der is not None:
            x.der.padre = y
        x.padre = y.padre
        if y.padre is None:
            self.raiz = x
        elif y == y.padre.izq:
            y.padre.izq = x
        else:
            y.padre.der = x
        x.der = y
        y.padre = x
        self.actualizar_altura(y)
        self.actualizar_altura(x)
        return x

    # ------------------------------------------------------------
    # LOS CUATRO CASOS   O(1)
    #   LL: FB(z) = +2 y FB(hijo izq) >= 0  -> rotar a la derecha z
    #   LR: FB(z) = +2 y FB(hijo izq) = -1  -> izquierda al hijo, derecha a z
    #   RR: FB(z) = -2 y FB(hijo der) <= 0  -> rotar a la izquierda z
    #   RL: FB(z) = -2 y FB(hijo der) = +1  -> derecha al hijo, izquierda a z
    # El rebalanceo sube en cascada desde el nodo dado hasta la raíz.
    # ------------------------------------------------------------
    def rotacion_LL(self, z):
        return self.rotar_derecha(z)

    def rotacion_RR(self, z):
        return self.rotar_izquierda(z)

    def rotacion_LR(self, z):
        self.rotar_izquierda(z.izq)
        return self.rotar_derecha(z)

    def rotacion_RL(self, z):
        self.rotar_derecha(z.der)
        return self.rotar_izquierda(z)

    def balancear(self, z):
        fb = self.factor_balance(z)
        if fb > 1:
            if self.factor_balance(z.izq) >= 0:
                return self.rotacion_LL(z)
            else:
                return self.rotacion_LR(z)
        if fb < -1:
            if self.factor_balance(z.der) <= 0:
                return self.rotacion_RR(z)
            else:
                return self.rotacion_RL(z)
        return z

    def rebalancear_hacia_arriba(self, nodo):
        while nodo is not None:
            self.actualizar_altura(nodo)
            nodo = self.balancear(nodo)
            nodo = nodo.padre

    # ------------------------------------------------------------
    # INSERCIÓN   O(log n)
    # Igual que en el ABB (se rechazan duplicados) y después se
    # rebalancea desde el padre del nuevo nodo hasta la raíz.
    # ------------------------------------------------------------
    def insertar(self, clave, valor):
        y = None
        x = self.raiz
        while x is not None:
            y = x
            if clave == x.clave:
                return False
            elif clave < x.clave:
                x = x.izq
            else:
                x = x.der

        z = NodoAVL(clave, valor)
        z.padre = y
        if y is None:
            self.raiz = z
        elif clave < y.clave:
            y.izq = z
        else:
            y.der = z
        self.tamanio += 1

        self.rebalancear_hacia_arriba(y)
        return True

    # ------------------------------------------------------------
    # ELIMINACIÓN   O(log n)
    # Igual que en el ABB (tres casos, TRANSPLANT y sucesor). "inicio"
    # guarda el nodo más profundo cuya altura pudo cambiar; desde ahí se
    # rebalancea en cascada. Puede requerir varias rotaciones.
    # ------------------------------------------------------------
    def eliminar(self, clave):
        z = self.buscar_nodo(clave)
        if z is None:
            return False

        if z.izq is None:
            inicio = z.padre
            self.transplant(z, z.der)
        elif z.der is None:
            inicio = z.padre
            self.transplant(z, z.izq)
        else:
            y = self.minimo_nodo(z.der)
            if y.padre != z:
                inicio = y.padre
                self.transplant(y, y.der)
                y.der = z.der
                y.der.padre = y
            else:
                inicio = y
            self.transplant(z, y)
            y.izq = z.izq
            y.izq.padre = y

        self.tamanio -= 1

        self.rebalancear_hacia_arriba(inicio)
        return True

    # ------------------------------------------------------------
    # CONSULTA POR RANGO   O(log n + m)
    # Inorden que solo entra a las ramas que pueden tener claves
    # entre bajo y alto.
    # ------------------------------------------------------------
    def rango(self, bajo, alto):
        resultado = []
        self._rango(self.raiz, bajo, alto, resultado)
        return resultado

    def _rango(self, x, bajo, alto, resultado):
        if x is None:
            return
        if bajo < x.clave:
            self._rango(x.izq, bajo, alto, resultado)
        if bajo <= x.clave <= alto:
            resultado.append(x.valor)
        if x.clave < alto:
            self._rango(x.der, bajo, alto, resultado)

    # ------------------------------------------------------------
    # VERIFICADOR DEL INVARIANTE AVL   O(n)
    # Revisa el orden, los padres, que la altura guardada sea la real
    # y que el FB esté entre -1 y 1. Si algo falla, lanza AssertionError.
    # ------------------------------------------------------------
    def verificar(self):
        if self.raiz is not None:
            assert self.raiz.padre is None, "La raíz no debe tener padre"
        contados = self._verificar_avl(self.raiz, None, None)[1]
        assert contados == self.tamanio, (
            f"El tamaño guardado ({self.tamanio}) no coincide con los nodos ({contados})"
        )
        return True

    def _verificar_avl(self, x, minimo, maximo):
        if x is None:
            return -1, 0
        if minimo is not None:
            assert x.clave > minimo, f"Orden roto en el nodo {x.clave}"
        if maximo is not None:
            assert x.clave < maximo, f"Orden roto en el nodo {x.clave}"
        if x.izq is not None:
            assert x.izq.padre == x, f"Padre mal asignado en {x.izq.clave}"
        if x.der is not None:
            assert x.der.padre == x, f"Padre mal asignado en {x.der.clave}"

        alt_izq, n_izq = self._verificar_avl(x.izq, minimo, x.clave)
        alt_der, n_der = self._verificar_avl(x.der, x.clave, maximo)
        altura_real = 1 + max(alt_izq, alt_der)
        assert x.altura == altura_real, f"Altura mal guardada en {x.clave}"
        assert abs(alt_izq - alt_der) <= 1, f"Nodo {x.clave} desbalanceado"
        return altura_real, 1 + n_izq + n_der

# ======================================================================
# MONTÍCULO - min-heap sobre arreglo
# padre(i) = (i-1)//2, izquierdo(i) = 2i+1, derecho(i) = 2i+2.
# Cada elemento es una pareja (clave, valor); la raíz es el mínimo.
# ======================================================================

class MinHeap:
    def __init__(self):
        self.datos = []

    def tamanio(self):
        return len(self.datos)

    def esta_vacio(self):
        return len(self.datos) == 0

    def padre(self, i):
        return (i - 1) // 2

    def izquierdo(self, i):
        return 2 * i + 1

    def derecho(self, i):
        return 2 * i + 2

    def intercambiar(self, i, j):
        self.datos[i], self.datos[j] = self.datos[j], self.datos[i]

    def menor(self, i, j):
        return self.datos[i][0] < self.datos[j][0]

    # ------------------------------------------------------------
    # FLOTAR Y HUNDIR   O(log n)
    # Flotar: sube el elemento mientras sea menor que su padre.
    # Hundir: lo cambia por su hijo menor mientras alguno sea menor.
    # ------------------------------------------------------------
    def flotar(self, i):
        while i > 0 and self.menor(i, self.padre(i)):
            self.intercambiar(i, self.padre(i))
            i = self.padre(i)

    def hundir(self, i):
        n = len(self.datos)
        while True:
            izq = self.izquierdo(i)
            der = self.derecho(i)
            menor = i
            if izq < n and self.menor(izq, menor):
                menor = izq
            if der < n and self.menor(der, menor):
                menor = der
            if menor == i:
                break
            self.intercambiar(i, menor)
            i = menor

    # ------------------------------------------------------------
    # OPERACIONES
    #   insertar:          al final y se hace flotar        O(log n)
    #   ver_minimo:        la raíz                          O(1)
    #   extraer_minimo:    el último pasa a la raíz y se hunde   O(log n)
    #   decrementar_clave: se baja la clave y se hace flotar O(log n)
    #   construir:         se hunden los nodos internos, de n//2 - 1
    #                      hasta 0                           O(n)
    # ------------------------------------------------------------
    def insertar(self, clave, valor):
        self.datos.append((clave, valor))
        self.flotar(len(self.datos) - 1)

    def ver_minimo(self):
        if self.esta_vacio():
            return None
        return self.datos[0]

    def extraer_minimo(self):
        if self.esta_vacio():
            return None
        minimo = self.datos[0]
        ultimo = self.datos.pop()
        if not self.esta_vacio():
            self.datos[0] = ultimo
            self.hundir(0)
        return minimo

    def decrementar_clave(self, i, nueva_clave):
        if nueva_clave > self.datos[i][0]:
            raise ValueError("La nueva clave es mayor que la actual")
        self.datos[i] = (nueva_clave, self.datos[i][1])
        self.flotar(i)

    def construir(self, parejas):
        self.datos = list(parejas)
        for i in range(len(self.datos) // 2 - 1, -1, -1):
            self.hundir(i)

    # ------------------------------------------------------------
    # VERIFICADOR DE LA PROPIEDAD DE MIN-HEAP   O(n)
    # Revisa que ningún hijo tenga una clave menor que su padre.
    # ------------------------------------------------------------
    def verificar(self):
        for i in range(1, len(self.datos)):
            assert not self.menor(i, self.padre(i)), (
                f"Propiedad de min-heap rota en la posición {i}"
            )
        return True


# ================================================================
# COLA DE REVISIÓN BIBLIOGRÁFICA (problema 5)
# Atiende primero al artículo con más citas. La clave es (-citas, DOI):
# al negar las citas, el más citado queda con la clave menor, y el DOI
# desempata. Un cambio de citas se hace con decrementar clave; buscar la
# posición de un DOI cuesta O(n) porque el arreglo no está ordenado por DOI.
# ================================================================
class ColaRevision:

    def __init__(self):
        self.heap = MinHeap()

    def clave_de(self, articulo):
        return (-articulo["citas"], articulo["doi"])

    def agregar(self, articulo):
        self.heap.insertar(self.clave_de(articulo), articulo)

    def construir(self, articulos):
        parejas = [(self.clave_de(a), a) for a in articulos]
        self.heap.construir(parejas)

    def siguiente(self):
        par = self.heap.ver_minimo()
        if par is None:
            return None
        return par[1]

    def atender(self):
        par = self.heap.extraer_minimo()
        if par is None:
            return None
        return par[1]

    def posicion_de(self, doi):
        for i in range(self.heap.tamanio()):
            if self.heap.datos[i][1]["doi"] == doi:
                return i
        return -1

    def actualizar_citas(self, doi, nuevas_citas):
        i = self.posicion_de(doi)
        if i == -1:
            return False
        articulo = self.heap.datos[i][1]
        if nuevas_citas < articulo["citas"]:
            raise ValueError("Las citas de un artículo no disminuyen")
        articulo["citas"] = nuevas_citas
        self.heap.decrementar_clave(i, self.clave_de(articulo))
        return True

    # Baja de un artículo: su clave se decrementa a -infinito para que
    # suba a la raíz y después se extrae.
    def retirar(self, doi):
        i = self.posicion_de(doi)
        if i == -1:
            return False
        self.heap.decrementar_clave(i, (float("-inf"), ""))
        self.heap.extraer_minimo()
        return True


# Los k artículos más citados sin ordenar toda la colección:
# construir el montículo O(n) y extraer k veces O(k log n).
def top_k(articulos, k):
    cola = ColaRevision()
    cola.construir(articulos)
    mejores = []
    for _ in range(min(k, len(articulos))):
        mejores.append(cola.atender())
    return mejores