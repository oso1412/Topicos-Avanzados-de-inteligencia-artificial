import pandas as pd
import random


# 1. CONFIGURACIÓN DEL PROBLEMA

archivo_distancias = "metodo_tabu/matriz_distancias.xlsx"
archivo_combustible = "metodo_tabu/matriz_costos_combustible.xlsx"

# Centros de distribución: nodos 1 al 10
centros = list(range(1, 11))

# Tiendas: nodos 11 al 100
tiendas = list(range(11, 101))

# Parámetros de búsqueda tabú
ITERACIONES = 500
TAMAÑO = 20
SEMILLA = 42


# 2. CARGAR MATRICES


df_distancias = pd.read_excel(archivo_distancias)
df_combustible = pd.read_excel(archivo_combustible)

print("=== INFORMACIÓN MATRIZ DISTANCIAS ===")
print(df_distancias.info())

print("\n=== PRIMERAS FILAS MATRIZ DISTANCIAS ===")
print(df_distancias.head())

print("\n=== DIMENSIONES MATRIZ DISTANCIAS ===")
print(df_distancias.shape)

print("\n=== INFORMACIÓN MATRIZ COMBUSTIBLE ===")
print(df_combustible.info())

print("\n=== PRIMERAS FILAS MATRIZ COMBUSTIBLE ===")
print(df_combustible.head())

print("\n=== DIMENSIONES MATRIZ COMBUSTIBLE ===")
print(df_combustible.shape)

matriz_distancias = df_distancias.to_numpy()
matriz_combustible = df_combustible.to_numpy()

filas_d, columnas_d = matriz_distancias.shape
filas_c, columnas_c = matriz_combustible.shape

if filas_d != columnas_d:
    raise ValueError("La matriz de distancias debe ser cuadrada.")

if filas_c != columnas_c:
    raise ValueError("La matriz de combustible debe ser cuadrada.")

if matriz_distancias.shape != matriz_combustible.shape:
    raise ValueError("La matriz de distancias y la matriz de combustible deben tener el mismo tamaño.")


# 3. FUNCIONES AUXILIARES


def distancia(nodo_a, nodo_b):
    """
    Devuelve la distancia entre nodo_a y nodo_b.
    Nodo_1 está en índice 0, por eso usamos nodo-1.
    """
    return matriz_distancias[nodo_a - 1][nodo_b - 1]


def costo_combustible_tramo(nodo_a, nodo_b):
    """
    Devuelve el costo de combustible entre nodo_a y nodo_b.
    """
    return matriz_combustible[nodo_a - 1][nodo_b - 1]


def distancia_total_ruta(ruta):
    """
    Calcula la distancia total de una ruta cerrada.
    Ejemplo:
    [3, 15, 22, 40]
    significa:
    3 -> 15 -> 22 -> 40 -> 3
    """
    if len(ruta) <= 1:
        return 0

    total = 0
    for i in range(len(ruta) - 1):
        total += distancia(ruta[i], ruta[i + 1])

    total += distancia(ruta[-1], ruta[0])
    return total


def costo_total_combustible_ruta(ruta):
    """
    Calcula el costo total de combustible de una ruta cerrada.
    """
    if len(ruta) <= 1:
        return 0

    total = 0
    for i in range(len(ruta) - 1):
        total += costo_combustible_tramo(ruta[i], ruta[i + 1])

    total += costo_combustible_tramo(ruta[-1], ruta[0])
    return total


def generar_ruta_inicial(deposito, tiendas_asignadas):
    """
    Genera una ruta inicial aleatoria:
    [deposito, tiendas mezcladas]
    """
    ruta_tiendas = tiendas_asignadas[:]
    random.shuffle(ruta_tiendas)
    return [deposito] + ruta_tiendas


def generar_vecinos_intercambio(ruta):
    """
    Genera vecinos intercambiando dos tiendas.
    La posición 0 no se mueve porque es el centro.
    """
    vecinos = []

    if len(ruta) <= 2:
        return vecinos

    for i in range(1, len(ruta)):
        for j in range(i + 1, len(ruta)):
            nueva_ruta = ruta[:]
            nueva_ruta[i], nueva_ruta[j] = nueva_ruta[j], nueva_ruta[i]

            movimiento = tuple(sorted((ruta[i], ruta[j])))
            vecinos.append((nueva_ruta, movimiento))

    return vecinos


def imprimir_ruta(ruta):
    """
    Devuelve la ruta cerrada como texto.
    """
    if len(ruta) == 1:
        return f"Nodo_{ruta[0]} -> Nodo_{ruta[0]}"

    ruta_cerrada = ruta + [ruta[0]]
    return " -> ".join(f"Nodo_{n}" for n in ruta_cerrada)


# 4. ASIGNACIÓN DE TIENDAS AL MEJOR CENTRO

def asignar_tiendas_a_centros(centros, tiendas):
    """
    Asigna cada tienda al centro con menor distancia directa.
    Además guarda el costo de combustible de ese tramo.
    """
    asignacion = {centro: [] for centro in centros}
    detalle = []

    for tienda in tiendas:
        mejor_centro = None
        mejor_distancia = float("inf")

        for centro in centros:
            d = distancia(centro, tienda)

            if d < mejor_distancia:
                mejor_distancia = d
                mejor_centro = centro

        asignacion[mejor_centro].append(tienda)

        detalle.append({
            "Tienda": tienda,
            "Centro_Asignado": mejor_centro,
            "Distancia_Centro_Tienda": mejor_distancia,
            "Costo_Combustible_Centro_Tienda": costo_combustible_tramo(mejor_centro, tienda)
        })

    return asignacion, pd.DataFrame(detalle)


# 5. BÚSQUEDA TABÚ USANDO COSTO DE COMBUSTIBLE

def busqueda_tabu_combustible(deposito, tiendas_asignadas, iteraciones=500, tamaño=20, mostrar_progreso=False):
    """
    Optimiza la ruta minimizando costo de combustible.
    Devuelve:
    - mejor ruta
    - distancia total de esa ruta
    - costo total de combustible de esa ruta
    """
    if len(tiendas_asignadas) == 0:
        return [deposito], 0, 0

    if len(tiendas_asignadas) == 1:
        ruta = [deposito] + tiendas_asignadas
        return ruta, distancia_total_ruta(ruta), costo_total_combustible_ruta(ruta)

    solucion_actual = generar_ruta_inicial(deposito, tiendas_asignadas)
    costo_actual = costo_total_combustible_ruta(solucion_actual)

    mejor_solucion = solucion_actual[:]
    mejor_costo_combustible = costo_actual

    lista_tabu = []

    if mostrar_progreso:
        print(f"\n=== CENTRO {deposito} | RUTA INICIAL ===")
        print(imprimir_ruta(solucion_actual))
        print(f"Distancia inicial: {distancia_total_ruta(solucion_actual):.4f}")
        print(f"Costo combustible inicial: {costo_actual:.4f}\n")

    for it in range(iteraciones):
        vecinos = generar_vecinos_intercambio(solucion_actual)

        mejor_vecino = None
        mejor_movimiento = None
        mejor_costo_vecino = float("inf")

        for vecino, movimiento in vecinos:
            costo_vecino = costo_total_combustible_ruta(vecino)

            es_tabu = movimiento in lista_tabu
            mejora_global = costo_vecino < mejor_costo_combustible

            if (not es_tabu) or mejora_global:
                if costo_vecino < mejor_costo_vecino:
                    mejor_vecino = vecino
                    mejor_movimiento = movimiento
                    mejor_costo_vecino = costo_vecino

        if mejor_vecino is None:
            continue

        solucion_actual = mejor_vecino[:]
        costo_actual = mejor_costo_vecino

        lista_tabu.append(mejor_movimiento)
        if len(lista_tabu) > tamaño:
            lista_tabu.pop(0)

        if costo_actual < mejor_costo_combustible:
            mejor_solucion = solucion_actual[:]
            mejor_costo_combustible = costo_actual

        if mostrar_progreso:
            print(
                f"Centro {deposito} | Iteración {it+1:03d} | "
                f"Costo combustible actual: {costo_actual:.4f} | "
                f"Mejor costo combustible: {mejor_costo_combustible:.4f}"
            )

    return (
        mejor_solucion,
        distancia_total_ruta(mejor_solucion),
        costo_total_combustible_ruta(mejor_solucion)
    )


# 6. ASIGNAR TIENDAS

random.seed(SEMILLA)

asignacion_centros, df_asignacion = asignar_tiendas_a_centros(centros, tiendas)

print("\n" + "=" * 60)
print("ASIGNACIÓN DE TIENDAS A CENTROS")
print("=" * 60)
print(df_asignacion)

print("\n=== CANTIDAD DE TIENDAS POR CENTRO ===")
for centro in centros:
    print(f"Centro {centro}: {len(asignacion_centros[centro])} tiendas")


# 7. OPTIMIZAR RUTAS POR CADA CENTRO

resumen_rutas = []
detalle_rutas = []

print("\n" + "=" * 60)
print("OPTIMIZACIÓN DE RUTAS POR CENTRO")
print("=" * 60)

for centro in centros:
    tiendas_centro = asignacion_centros[centro]

    print(f"\n--- Centro {centro} ---")
    print(f"Tiendas asignadas: {tiendas_centro}")

    mejor_ruta, mejor_distancia, mejor_costo_comb = busqueda_tabu_combustible(
        deposito=centro,
        tiendas_asignadas=tiendas_centro,
        iteraciones=ITERACIONES,
        tamaño=TAMAÑO,
        mostrar_progreso=False
    )

    print("Mejor ruta encontrada:")
    print(imprimir_ruta(mejor_ruta))
    print(f"Distancia total: {mejor_distancia:.4f}")
    print(f"Costo total combustible: {mejor_costo_comb:.4f}")

    resumen_rutas.append({
        "Centro": centro,
        "Numero_Tiendas": len(tiendas_centro),
        "Distancia_Ruta": mejor_distancia,
        "Costo_Combustible_Ruta": mejor_costo_comb,
        "Ruta": imprimir_ruta(mejor_ruta)
    })

    ruta_cerrada = mejor_ruta + [centro]

    for paso, nodo in enumerate(ruta_cerrada, start=1):
        detalle_rutas.append({
            "Centro": centro,
            "Paso": paso,
            "Nodo": nodo
        })


# 8. RESULTADOS FINALES

df_resumen_rutas = pd.DataFrame(resumen_rutas)
df_detalle_rutas = pd.DataFrame(detalle_rutas)

distancia_total_sistema = df_resumen_rutas["Distancia_Ruta"].sum()
costo_total_combustible_sistema = df_resumen_rutas["Costo_Combustible_Ruta"].sum()

print("\n" + "=" * 60)
print("RESUMEN FINAL")
print("=" * 60)
print(df_resumen_rutas)

print(f"\nDistancia total del sistema: {distancia_total_sistema:.4f}")
print(f"Costo total de combustible del sistema: {costo_total_combustible_sistema:.4f}")

