import random
import time

N = 5


def generar_estado_inicial(n=5):
 
    return [random.randint(0, n - 1) for _ in range(n)]


def contar_conflictos(estado):

    conflictos = 0
    n = len(estado)

    for i in range(n):
        for j in range(i + 1, n):
            # Misma fila
            if estado[i] == estado[j]:
                conflictos += 1

            # Misma diagonal
            elif abs(estado[i] - estado[j]) == abs(i - j):
                conflictos += 1

    return conflictos


def generar_vecinos(estado):

    vecinos = []
    n = len(estado)

    for col in range(n):
        fila_actual = estado[col]

        for nueva_fila in range(n):
            if nueva_fila != fila_actual:
                vecino = estado[:]
                vecino[col] = nueva_fila
                movimiento = (col, fila_actual, nueva_fila)
                vecinos.append((vecino, movimiento))

    return vecinos


def imprimir_tablero(estado):
    
    n = len(estado)
    for fila in range(n):
        linea = []
        for col in range(n):
            if estado[col] == fila:
                linea.append("Q")
            else:
                linea.append(".")
        print(" ".join(linea))


def busqueda_tabu(n=8, max_iter=1000, tabu_tam=15):

    inicio = time.perf_counter()

    # Estado inicial aleatorio
    estado_actual = generar_estado_inicial(n)
    costo_actual = contar_conflictos(estado_actual)

    mejor_estado = estado_actual[:]
    mejor_costo = costo_actual

    lista_tabu = []
    movimientos = 0

    for iteracion in range(max_iter):
        # Si ya no hay conflictos, terminamos
        if costo_actual == 0:
            break

        vecinos = generar_vecinos(estado_actual)

        mejor_vecino = None
        mejor_movimiento = None
        mejor_costo_vecino = float("inf")

        for vecino, movimiento in vecinos:
            costo_vecino = contar_conflictos(vecino)

            # Regla de aspiración:
            # aunque el movimiento sea tabú, se permite si mejora
            # la mejor solución global encontrada.
            es_tabu = movimiento in lista_tabu

            if es_tabu and costo_vecino >= mejor_costo:
                continue

            if costo_vecino < mejor_costo_vecino:
                mejor_vecino = vecino
                mejor_movimiento = movimiento
                mejor_costo_vecino = costo_vecino

        # Si no se encontró vecino válido, terminamos
        if mejor_vecino is None:
            break

        # Actualizar estado actual
        estado_actual = mejor_vecino
        costo_actual = mejor_costo_vecino
        movimientos += 1

        # Agregar movimiento a lista tabú
        lista_tabu.append(mejor_movimiento)
        if len(lista_tabu) > tabu_tam:
            lista_tabu.pop(0)

        # Actualizar mejor solución global
        if costo_actual < mejor_costo:
            mejor_estado = estado_actual[:]
            mejor_costo = costo_actual

    fin = time.perf_counter()
    tiempo_total = fin - inicio

    return {
        "mejor_estado": mejor_estado,
        "conflictos": mejor_costo,
        "movimientos": movimientos,
        "tiempo": tiempo_total
    }


# EJECUCIÓN PRINCIPAL

resultado = busqueda_tabu(n=5, max_iter=2000, tabu_tam=20)

print("Mejor estado encontrado:", resultado["mejor_estado"])
print("Cantidad de conflictos:", resultado["conflictos"])
print("Cantidad de movimientos:", resultado["movimientos"])
print("Tiempo de ejecución: {:.6f} segundos".format(resultado["tiempo"]))
print("\nTablero final:")
imprimir_tablero(resultado["mejor_estado"])