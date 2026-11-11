"""
abb.py
Miniproyecto 2 - Catálogo consultable de producción científica
Equipo: Diaz Bello Israel Jaziz, Flores Canaán Raúl Hased, Miranda Chávez Gabriela

Árbol Binario de Búsqueda (ABB), implementado a mano.
Lo usan avl_monticulo.py (el AVL hereda del ABB) y catalogo.py.

Política de claves duplicadas: se rechazan.
"""

import sys


# Con inserción ordenada el ABB se degenera y su altura puede llegar a miles
# de nodos. Como los recorridos son recursivos, se amplía el límite de
# recursión de Python para evitar errores con árboles muy altos.
sys.setrecursionlimit(50000)


# Cada nodo guarda su clave (lo que se compara), su valor (el artículo)
# y apuntadores al hijo izquierdo, al hijo derecho y al padre.
class Nodo:
    def __init__(self, clave, valor):
        self.clave = clave
        self.valor = valor
        self.izq = None
        self.der = None
        self.padre = None


class ABB:
    def __init__(self):
        self.raiz = None
        self.tamanio = 0

    # ------------------------------------------------------------
    # BÚSQUEDA   O(h)
    # Se baja por la izquierda si la clave es menor y por la derecha
    # si es mayor, hasta encontrarla o llegar a None.
    # ------------------------------------------------------------
    def buscar_nodo(self, clave):
        x = self.raiz
        while x is not None and clave != x.clave:
            if clave < x.clave:
                x = x.izq
            else:
                x = x.der
        return x

    def buscar(self, clave):
        nodo = self.buscar_nodo(clave)
        if nodo is None:
            return None
        return nodo.valor

    # ------------------------------------------------------------
    # INSERCIÓN   O(h)
    # Se desciende hasta una posición vacía; "y" conserva el último
    # nodo visitado, que será el padre del nuevo nodo.
    # Si la clave ya existe, se rechaza y regresa False.
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

        z = Nodo(clave, valor)
        z.padre = y
        if y is None:
            self.raiz = z
        elif clave < y.clave:
            y.izq = z
        else:
            y.der = z
        self.tamanio += 1
        return True

    # ------------------------------------------------------------
    # MÍNIMO, MÁXIMO Y SUCESOR   O(h)
    # El mínimo es el nodo más a la izquierda y el máximo el más a la
    # derecha. Sucesor:
    #   caso 1: si x tiene hijo derecho, es el mínimo de ese subárbol;
    #   caso 2: si no, es el primer ancestro alcanzado desde un hijo izquierdo.
    # ------------------------------------------------------------
    def minimo_nodo(self, x):
        while x.izq is not None:
            x = x.izq
        return x

    def maximo_nodo(self, x):
        while x.der is not None:
            x = x.der
        return x

    def minimo(self):
        if self.raiz is None:
            return None
        return self.minimo_nodo(self.raiz)

    def maximo(self):
        if self.raiz is None:
            return None
        return self.maximo_nodo(self.raiz)

    def sucesor_nodo(self, x):
        if x.der is not None:
            return self.minimo_nodo(x.der)
        y = x.padre
        while y is not None and x == y.der:
            x = y
            y = y.padre
        return y

    def sucesor(self, clave):
        x = self.buscar_nodo(clave)
        if x is None:
            return None
        return self.sucesor_nodo(x)

    # ------------------------------------------------------------
    # ELIMINACIÓN   O(h)
    # TRANSPLANT pone el subárbol v en el lugar que ocupaba u.
    # Casos de eliminación:
    #   caso 1: z no tiene hijos      -> se quita;
    #   caso 2: z tiene un solo hijo  -> el hijo sube a su lugar;
    #   caso 3: z tiene dos hijos     -> se sustituye por su sucesor
    #           (el mínimo del subárbol derecho). Si el sucesor no es
    #           hijo directo de z, primero se saca de su posición.
    # ------------------------------------------------------------
    def transplant(self, u, v):
        if u.padre is None:
            self.raiz = v
        elif u == u.padre.izq:
            u.padre.izq = v
        else:
            u.padre.der = v
        if v is not None:
            v.padre = u.padre

    def eliminar(self, clave):
        z = self.buscar_nodo(clave)
        if z is None:
            return False

        if z.izq is None:
            self.transplant(z, z.der)
        elif z.der is None:
            self.transplant(z, z.izq)
        else:
            y = self.minimo_nodo(z.der)
            if y.padre != z:
                self.transplant(y, y.der)
                y.der = z.der
                y.der.padre = y
            self.transplant(z, y)
            y.izq = z.izq
            y.izq.padre = y

        self.tamanio -= 1
        return True

    # ------------------------------------------------------------
    # RECORRIDOS   O(n)
    #   inorden   (izq - raíz - der): valores ordenados por clave; se usa
    #             para el listado cronológico (problema 1).
    #   preorden  (raíz - izq - der): reconstruye un árbol con la misma forma.
    #   postorden (izq - der - raíz): visita a los hijos antes que al padre;
    #             es el orden que sigue el cálculo de la altura.
    # ------------------------------------------------------------
    def inorden(self):
        resultado = []
        self._inorden(self.raiz, resultado)
        return resultado

    def _inorden(self, x, resultado):
        if x is not None:
            self._inorden(x.izq, resultado)
            resultado.append(x.valor)
            self._inorden(x.der, resultado)

    def preorden(self):
        resultado = []
        self._preorden(self.raiz, resultado)
        return resultado

    def _preorden(self, x, resultado):
        if x is not None:
            resultado.append(x.clave)
            self._preorden(x.izq, resultado)
            self._preorden(x.der, resultado)

    def postorden(self):
        resultado = []
        self._postorden(self.raiz, resultado)
        return resultado

    def _postorden(self, x, resultado):
        if x is not None:
            self._postorden(x.izq, resultado)
            self._postorden(x.der, resultado)
            resultado.append(x.clave)

    # ------------------------------------------------------------
    # ALTURA   O(n)
    # Número de aristas del camino más largo raíz-hoja (vacío = -1).
    # ------------------------------------------------------------
    def altura(self):
        return self._altura(self.raiz)

    def _altura(self, x):
        if x is None:
            return -1
        alt_izq = self._altura(x.izq)
        alt_der = self._altura(x.der)
        return 1 + max(alt_izq, alt_der)

    # ------------------------------------------------------------
    # VERIFICADOR DEL INVARIANTE   O(n)
    # Revisa que lo de la izquierda sea menor y lo de la derecha mayor,
    # que cada hijo apunte a su padre y que el tamaño coincida.
    # Si algo falla, lanza AssertionError indicando el nodo.
    # ------------------------------------------------------------
    def verificar(self):
        if self.raiz is not None:
            assert self.raiz.padre is None, "La raíz no debe tener padre"
        contados = self._verificar(self.raiz, None, None)
        assert contados == self.tamanio, (
            f"El tamaño guardado ({self.tamanio}) no coincide con los nodos ({contados})"
        )
        return True

    def _verificar(self, x, minimo, maximo):
        if x is None:
            return 0
        if minimo is not None:
            assert x.clave > minimo, f"Orden roto en el nodo {x.clave}"
        if maximo is not None:
            assert x.clave < maximo, f"Orden roto en el nodo {x.clave}"
        if x.izq is not None:
            assert x.izq.padre == x, f"Padre mal asignado en {x.izq.clave}"
        if x.der is not None:
            assert x.der.padre == x, f"Padre mal asignado en {x.der.clave}"
        return (1
                + self._verificar(x.izq, minimo, x.clave)
                + self._verificar(x.der, x.clave, maximo))