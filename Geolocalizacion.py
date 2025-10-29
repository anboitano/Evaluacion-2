import requests
import urllib.parse

url_ruta = "https://graphhopper.com/api/1/route?"
clave_api = "a03fbd85-937d-4ebd-91fc-2948e71b4eda"

def geocodificacion(ubicacion, clave_api):
    while ubicacion == "":
        ubicacion = input("Por favor, ingresa la ubicación nuevamente: ")
        if ubicacion.lower() in ["s", "salir"]:
            return None, None, None, None
    url_geocodificacion = "https://graphhopper.com/api/1/geocode?"
    parametros_geocodificacion = {"q": ubicacion, "limit": "1", "key": clave_api, "locale": "es"}
    url = url_geocodificacion + urllib.parse.urlencode(parametros_geocodificacion)

    respuesta = requests.get(url)
    datos = respuesta.json()
    estado = respuesta.status_code

    if estado == 200 and len(datos["hits"]) != 0:
        latitud = datos["hits"][0]["point"]["lat"]
        longitud = datos["hits"][0]["point"]["lng"]
        nombre = datos["hits"][0]["name"]
        tipo_ubicacion = datos["hits"][0]["osm_value"]

        pais = datos["hits"][0].get("country", "")
        estado_ubicacion = datos["hits"][0].get("state", "")

        if estado_ubicacion and pais:
            ubicacion_completa = nombre + ", " + estado_ubicacion + ", " + pais
        elif pais:
            ubicacion_completa = nombre + ", " + pais
        else:
            ubicacion_completa = nombre

        print("URL de la API de geocodificación para " + ubicacion_completa + " (Tipo de ubicación: " + tipo_ubicacion + ")\n" + url)
    else:
        latitud = "null"
        longitud = "null"
        ubicacion_completa = ubicacion
        if estado != 200:
            print("Estado de la API de geocodificación: " + str(estado) + "\nMensaje de error: " + datos.get("message", "Desconocido"))
    return estado, latitud, longitud, ubicacion_completa

while True:
    print("\n+++++++++++++++++++++++++++++++++++++++++++++")
    print("Perfiles de vehículos disponibles en Graphhopper:")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    print("auto, bicicleta, pie")
    print("+++++++++++++++++++++++++++++++++++++++++++++")
    perfiles = ["car", "bike", "foot"]
    perfiles_es = {"auto": "car", "bicicleta": "bike", "pie": "foot"}
    perfil = input("Ingresa un perfil de vehículo de la lista anterior: ").lower()
    if perfil in ["s", "salir"]:
        print("¡Gracias por usar el programa! Hasta pronto.")
        break
    if perfil in perfiles_es:
        perfil_vehiculo = perfiles_es[perfil]
    elif perfil in perfiles:
        perfil_vehiculo = perfil
    else:
        perfil_vehiculo = "car"
        print("No ingresaste un perfil de vehículo válido. Se usará el perfil 'auto'.")

    ubicacion_inicio = input("Ubicación de inicio: ")
    if ubicacion_inicio.lower() in ["s", "salir"]:
        print("¡Gracias por usar el programa! Hasta pronto.")
        break
    origen = geocodificacion(ubicacion_inicio, clave_api)
    if origen[0] is None:
        print("¡Gracias por usar el programa! Hasta pronto.")
        break

    print(origen)
    ubicacion_destino = input("Destino: ")
    if ubicacion_destino.lower() in ["s", "salir"]:
        print("¡Gracias por usar el programa! Hasta pronto.")
        break
    destino = geocodificacion(ubicacion_destino, clave_api)
    if destino[0] is None:
        print("¡Gracias por usar el programa! Hasta pronto.")
        break

    print("=================================================")
    if origen[0] == 200 and destino[0] == 200:
        punto_origen = "&point=" + str(origen[1]) + "%2C" + str(origen[2])
        punto_destino = "&point=" + str(destino[1]) + "%2C" + str(destino[2])
        parametros_ruta = {
            "key": clave_api,
            "vehicle": perfil_vehiculo,
            "locale": "es"
        }
        url_camino = (
            url_ruta +
            urllib.parse.urlencode(parametros_ruta) +
            punto_origen +
            punto_destino
        )
        respuesta_camino = requests.get(url_camino)
        estado_camino = respuesta_camino.status_code
        datos_camino = respuesta_camino.json()

        print("Estado de la API de rutas: " + str(estado_camino) + "\nURL de la API de rutas:\n" + url_camino)
        print("=================================================")
        print("Direcciones desde " + origen[3] + " hasta " + destino[3] + " en " + perfil)
        print("=================================================")
        if estado_camino == 200:
            kilometros = datos_camino["paths"][0]["distance"] / 1000
            millas = kilometros / 1.61
            segundos = int(datos_camino["paths"][0]["time"] / 1000 % 60)
            minutos = int(datos_camino["paths"][0]["time"] / 1000 / 60 % 60)
            horas = int(datos_camino["paths"][0]["time"] / 1000 / 60 / 60)
            print("Distancia recorrida: {0:.2f} millas / {1:.2f} km".format(millas, kilometros))
            print("Duración del viaje: {0:02d}:{1:02d}:{2:02d} (horas:minutos:segundos)".format(horas, minutos, segundos))
            print("=================================================")
            print("Narrativa del viaje:")
            for instruccion in datos_camino["paths"][0]["instructions"]:
                texto_instruccion = instruccion["text"]
                distancia_instruccion = instruccion["distance"]
                km_instruccion = distancia_instruccion / 1000
                mi_instruccion = km_instruccion / 1.61
                print("{0} ( {1:.2f} km / {2:.2f} millas )".format(texto_instruccion, km_instruccion, mi_instruccion))
            print("=============================================")
        else:
            print("Mensaje de error: " + datos_camino.get("message", "Desconocido"))
            print("*************************************************")
    else:
        print("No se pudo obtener la ruta para las ubicaciones proporcionadas.")