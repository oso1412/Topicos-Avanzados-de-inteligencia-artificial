import folium

class MarcadorTienda:
    def __init__(self, nombre, latitud, longitud):
        self.nombre = nombre
        self.latitud = latitud
        self.longitud = longitud

    def agregar_a_mapa(self, mapa):
        folium.Marker(
            location=[self.latitud, self.longitud],
            popup=self.nombre,
            tooltip=self.nombre,
            icon=folium.Icon(color="blue", icon="truck", prefix="fa")
        ).add_to(mapa)


class MarcadorTienda2:
    def __init__(self, nombre, latitud, longitud):
        self.nombre = nombre
        self.latitud = latitud
        self.longitud = longitud

    def agregar_a_mapa(self, mapa):
        folium.Marker(
            location=[self.latitud, self.longitud],
            popup=self.nombre,
            tooltip=self.nombre,
            icon=folium.Icon(color="red", icon="store", prefix="fa")
        ).add_to(mapa)