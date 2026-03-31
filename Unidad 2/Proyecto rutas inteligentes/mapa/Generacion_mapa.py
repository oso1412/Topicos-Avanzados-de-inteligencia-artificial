import folium

class MapaCuliacan:
    def __init__(self, lat_centro=24.8091, lon_centro=-107.3940, zoom=12):
        self.mapa = folium.Map(location=[lat_centro, lon_centro], zoom_start=zoom)

    def agregar_marcador(self, marcador):
        marcador.agregar_a_mapa(self.mapa)

    def guardar(self, nombre_archivo="mapa_culiacan.html"):
        self.mapa.save(nombre_archivo)