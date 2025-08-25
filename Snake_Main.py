import pygame
import sys
import random
import time
import json
import os

# Inicializar Pygame
pygame.init()

# Configuración del juego usando tuplas para dimensiones
DIMENSIONES = (800, 600)
TAMANO_CELDA = 30
FILAS, COLUMNAS = DIMENSIONES[1] // TAMANO_CELDA, DIMENSIONES[0] // TAMANO_CELDA
FPS = 10

# Colores usando diccionario para mejor organización
COLORES = {
    "NEGRO": (0, 0, 0),
    "BLANCO": (255, 255, 255),
    "VERDE": (0, 255, 0),
    "ROJO": (255, 0, 0),
    "AZUL": (0, 0, 255),
    "GRIS": (40, 40, 40),
    "AMARILLO": (255, 255, 0),
    "TRANSPARENTE": (0, 0, 0, 128),
    "NARANJA": (255, 165, 0),
    "PURPURA": (128, 0, 128)
}

# Direcciones usando diccionario para mapeo
DIRECCIONES = {
    "ARRIBA": (0, -1),
    "ABAJO": (0, 1),
    "IZQUIERDA": (-1, 0),
    "DERECHA": (1, 0)
}

# Direcciones opuestas para validación
DIRECCIONES_OPUESTAS = {
    "ARRIBA": "ABAJO",
    "ABAJO": "ARRIBA",
    "IZQUIERDA": "DERECHA",
    "DERECHA": "IZQUIERDA"
}

# Archivo para guardar las puntuaciones altas
ARCHIVO_PUNTUACIONES = "puntuaciones_altas.json"

# Crear ventana
ventana = pygame.display.set_mode(DIMENSIONES)
pygame.display.set_caption("Juego de la Serpiente")
reloj = pygame.time.Clock()

# Estructuras lógicas para manejar el estado del juego
ESTADOS_JUEGO = {
    "JUGANDO": 0,
    "PAUSA": 1,
    "GAME_OVER": 2,
    "PUNTUACIONES_ALTAS": 3
}

def cargar_puntuaciones():
    """Carga las puntuaciones altas desde el archivo JSON"""
    if os.path.exists(ARCHIVO_PUNTUACIONES):
        try:
            with open(ARCHIVO_PUNTUACIONES, 'r') as archivo:
                return json.load(archivo)
        except:
            return []
    return []

def guardar_puntuaciones(puntuaciones):
    """Guarda las puntuaciones altas en el archivo JSON"""
    with open(ARCHIVO_PUNTUACIONES, 'w') as archivo:
        json.dump(puntuaciones, archivo)

def actualizar_puntuaciones_altas(puntuacion, puntuaciones_altas):
    """Actualiza la lista de puntuaciones altas si corresponde"""
    # Añadir la nueva puntuación
    puntuaciones_altas.append(puntuacion)
    
    # Ordenar de mayor a menor
    puntuaciones_altas.sort(reverse=True)
    
    # Mantener solo las 5 mejores
    return puntuaciones_altas[:5]

def inicializar_serpiente():
    """Inicializa la serpiente en posición central con 3 segmentos"""
    cabeza = (COLUMNAS // 2, FILAS // 2)
    # Usar comprensión de listas para crear el cuerpo
    return [cabeza, 
            (cabeza[0] - 1, cabeza[1]), 
            (cabeza[0] - 2, cabeza[1])]

def generar_comida(serpiente):
    """Genera comida en posición aleatoria no ocupada por la serpiente"""
    # Convertir la serpiente a un conjunto para búsquedas más eficientes
    posiciones_serpiente = set(serpiente)
    
    # Generar todas las posiciones posibles
    todas_posiciones = [(x, y) for x in range(COLUMNAS) for y in range(FILAS)]
    
    # Filtrar posiciones ocupadas
    posiciones_libres = [pos for pos in todas_posiciones if pos not in posiciones_serpiente]
    
    # Elegir una posición aleatoria si hay posiciones libres
    if posiciones_libres:
        return random.choice(posiciones_libres)
    return None  # En caso de que no haya posiciones libres (juego completo)

def dibujar_cuadricula():
    """Dibuja la cuadrícula del juego"""
    for x in range(0, DIMENSIONES[0], TAMANO_CELDA):
        pygame.draw.line(ventana, COLORES["GRIS"], (x, 0), (x, DIMENSIONES[1]))
    for y in range(0, DIMENSIONES[1], TAMANO_CELDA):
        pygame.draw.line(ventana, COLORES["GRIS"], (0, y), (DIMENSIONES[0], y))

def dibujar_serpiente(serpiente):
    """Dibuja la serpiente en la ventana"""
    for i, segmento in enumerate(serpiente):
        color = COLORES["VERDE"] if i == 0 else COLORES["AZUL"]  # Cabeza verde, cuerpo azul
        pygame.draw.rect(
            ventana, 
            color, 
            pygame.Rect(
                segmento[0] * TAMANO_CELDA,
                segmento[1] * TAMANO_CELDA,
                TAMANO_CELDA,
                TAMANO_CELDA
            )
        )

def dibujar_comida(comida):
    """Dibuja la comida en la ventana"""
    pygame.draw.rect(
        ventana, 
        COLORES["ROJO"], 
        pygame.Rect(
            comida[0] * TAMANO_CELDA,
            comida[1] * TAMANO_CELDA,
            TAMANO_CELDA,
            TAMANO_CELDA
        )
    )

def mostrar_puntuacion(puntuacion):
    """Muestra la puntuación actual"""
    fuente = pygame.font.SysFont(None, 36)
    texto = fuente.render(f"Puntuación: {puntuacion}", True, COLORES["BLANCO"])
    ventana.blit(texto, (10, 10))

def mostrar_pausa():
    """Muestra el mensaje de pausa"""
    # Crear una superficie semitransparente
    overlay = pygame.Surface(DIMENSIONES, pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Negro semitransparente
    ventana.blit(overlay, (0, 0))
    
    fuente_titulo = pygame.font.SysFont(None, 72)
    fuente_texto = pygame.font.SysFont(None, 36)
    
    titulo = fuente_titulo.render("PAUSA", True, COLORES["AMARILLO"])
    texto_continuar = fuente_texto.render("Presiona P para continuar", True, COLORES["BLANCO"])
    
    ventana.blit(titulo, (DIMENSIONES[0] // 2 - titulo.get_width() // 2, DIMENSIONES[1] // 3))
    ventana.blit(texto_continuar, (DIMENSIONES[0] // 2 - texto_continuar.get_width() // 2, DIMENSIONES[1] // 2))

def dibujar_elementos(serpiente, comida, puntuacion, pausa=False):
    """Dibuja todos los elementos del juego"""
    ventana.fill(COLORES["NEGRO"])
    
    # Dibujar cuadrícula
    dibujar_cuadricula()
    
    # Dibujar serpiente
    dibujar_serpiente(serpiente)
    
    # Dibujar comida
    dibujar_comida(comida)
    
    # Mostrar puntuación
    mostrar_puntuacion(puntuacion)
    
    # Si está en pausa, mostrar mensaje
    if pausa:
        mostrar_pausa()

def mostrar_puntuaciones_altas(puntuaciones_altas):
    """Muestra la pantalla de puntuaciones altas"""
    ventana.fill(COLORES["NEGRO"])
    fuente_titulo = pygame.font.SysFont(None, 72)
    fuente_texto = pygame.font.SysFont(None, 36)
    fuente_puntuaciones = pygame.font.SysFont(None, 48)
    
    titulo = fuente_titulo.render("MEJORES PUNTUACIONES", True, COLORES["NARANJA"])
    ventana.blit(titulo, (DIMENSIONES[0] // 2 - titulo.get_width() // 2, 50))
    
    # Mostrar las 5 mejores puntuaciones
    for i, puntuacion in enumerate(puntuaciones_altas):
        texto_puntuacion = fuente_puntuaciones.render(f"{i+1}. {puntuacion}", True, COLORES["AMARILLO"])
        ventana.blit(texto_puntuacion, (DIMENSIONES[0] // 2 - texto_puntuacion.get_width() // 2, 150 + i * 60))
    
    texto_volver = fuente_texto.render("Presiona ESPACIO para volver al menú", True, COLORES["BLANCO"])
    ventana.blit(texto_volver, (DIMENSIONES[0] // 2 - texto_volver.get_width() // 2, DIMENSIONES[1] - 100))
    
    pygame.display.update()

def mostrar_game_over(puntuacion, puntuaciones_altas):
    """Muestra mensaje de Game Over y opciones"""
    ventana.fill(COLORES["NEGRO"])
    fuente_titulo = pygame.font.SysFont(None, 72)
    fuente_texto = pygame.font.SysFont(None, 36)
    
    titulo = fuente_titulo.render("GAME OVER", True, COLORES["ROJO"])
    texto_puntos = fuente_texto.render(f"Puntuación final: {puntuacion}", True, COLORES["BLANCO"])
    texto_reinicio = fuente_texto.render("Presiona R para reiniciar", True, COLORES["VERDE"])
    texto_salir = fuente_texto.render("Presiona ESC para salir", True, COLORES["BLANCO"])
    texto_puntuaciones = fuente_texto.render("Presiona M para ver mejores puntuaciones", True, COLORES["AMARILLO"])
    
    ventana.blit(titulo, (DIMENSIONES[0] // 2 - titulo.get_width() // 2, DIMENSIONES[1] // 4))
    ventana.blit(texto_puntos, (DIMENSIONES[0] // 2 - texto_puntos.get_width() // 2, DIMENSIONES[1] // 2 - 50))
    ventana.blit(texto_reinicio, (DIMENSIONES[0] // 2 - texto_reinicio.get_width() // 2, DIMENSIONES[1] // 2))
    ventana.blit(texto_salir, (DIMENSIONES[0] // 2 - texto_salir.get_width() // 2, DIMENSIONES[1] // 2 + 50))
    ventana.blit(texto_puntuaciones, (DIMENSIONES[0] // 2 - texto_puntuaciones.get_width() // 2, DIMENSIONES[1] // 2 + 100))
    
    pygame.display.update()

def verificar_colision(serpiente, direccion):
    """Verifica si la serpiente colisiona con los bordes o consigo misma"""
    cabeza = serpiente[0]
    nueva_cabeza = (cabeza[0] + DIRECCIONES[direccion][0], cabeza[1] + DIRECCIONES[direccion][1])
    
    # Verificar colisión con bordes
    if (nueva_cabeza[0] < 0 or nueva_cabeza[0] >= COLUMNAS or 
        nueva_cabeza[1] < 0 or nueva_cabeza[1] >= FILAS):
        return True
    
    # Verificar colisión con el cuerpo (excepto la cola que se moverá)
    # Usamos slicing para omitir el último segmento que se moverá
    return nueva_cabeza in serpiente[:-1]

def mover_serpiente(serpiente, direccion, comida):
    """Mueve la serpiente y verifica si come"""
    cabeza = serpiente[0]
    nueva_cabeza = (cabeza[0] + DIRECCIONES[direccion][0], cabeza[1] + DIRECCIONES[direccion][1])
    
    # Insertar nueva cabeza
    serpiente.insert(0, nueva_cabeza)
    
    # Verificar si comió
    if nueva_cabeza == comida:
        comida = generar_comida(serpiente)
        return serpiente, comida, True
    
    # Si no comió, eliminar la cola
    serpiente.pop()
    return serpiente, comida, False

def manejar_eventos(direccion_actual, estado_juego):
    """Maneja los eventos del juego y devuelve la nueva dirección y estado"""
    nueva_direccion = direccion_actual
    nuevo_estado = estado_juego
    
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_p and estado_juego == ESTADOS_JUEGO["JUGANDO"]:  # Tecla P para pausar
                nuevo_estado = ESTADOS_JUEGO["PAUSA"]
            elif evento.key == pygame.K_p and estado_juego == ESTADOS_JUEGO["PAUSA"]:  # Tecla P para reanudar
                nuevo_estado = ESTADOS_JUEGO["JUGANDO"]
            elif estado_juego == ESTADOS_JUEGO["JUGANDO"]:
                # Cambiar dirección si no es opuesta a la actual
                if (evento.key == pygame.K_UP and 
                    direccion_actual != DIRECCIONES_OPUESTAS["ARRIBA"]):
                    nueva_direccion = "ARRIBA"
                elif (evento.key == pygame.K_DOWN and 
                      direccion_actual != DIRECCIONES_OPUESTAS["ABAJO"]):
                    nueva_direccion = "ABAJO"
                elif (evento.key == pygame.K_LEFT and 
                      direccion_actual != DIRECCIONES_OPUESTAS["IZQUIERDA"]):
                    nueva_direccion = "IZQUIERDA"
                elif (evento.key == pygame.K_RIGHT and 
                      direccion_actual != DIRECCIONES_OPUESTAS["DERECHA"]):
                    nueva_direccion = "DERECHA"
            elif estado_juego == ESTADOS_JUEGO["GAME_OVER"]:
                # Manejar reinicio, salida y ver puntuaciones
                if evento.key == pygame.K_r:  # Reiniciar
                    return "DERECHA", ESTADOS_JUEGO["JUGANDO"], True
                elif evento.key == pygame.K_ESCAPE:  # Salir
                    pygame.quit()
                    sys.exit()
                elif evento.key == pygame.K_m:  # Ver mejores puntuaciones
                    nuevo_estado = ESTADOS_JUEGO["PUNTUACIONES_ALTAS"]
            elif estado_juego == ESTADOS_JUEGO["PUNTUACIONES_ALTAS"]:
                if evento.key == pygame.K_SPACE:  # Volver al menú
                    nuevo_estado = ESTADOS_JUEGO["GAME_OVER"]
    
    return nueva_direccion, nuevo_estado, False

def main():
    """Función principal del juego"""
    # Cargar puntuaciones altas
    puntuaciones_altas = cargar_puntuaciones()
    
    # Inicializar estado del juego
    serpiente = inicializar_serpiente()
    direccion = "DERECHA"
    comida = generar_comida(serpiente)
    puntuacion = 0
    estado_juego = ESTADOS_JUEGO["JUGANDO"]
    reiniciar = False
    
    # Bucle principal del juego
    while True:
        # Manejar eventos
        direccion, estado_juego, reiniciar = manejar_eventos(direccion, estado_juego)
        
        if reiniciar:
            return main()
        
        if estado_juego == ESTADOS_JUEGO["JUGANDO"]:
            # Verificar colisiones
            if verificar_colision(serpiente, direccion):
                estado_juego = ESTADOS_JUEGO["GAME_OVER"]
                # Actualizar puntuaciones altas
                puntuaciones_altas = actualizar_puntuaciones_altas(puntuacion, puntuaciones_altas)
                guardar_puntuaciones(puntuaciones_altas)
            else:
                # Mover serpiente
                serpiente, comida, comio = mover_serpiente(serpiente, direccion, comida)
                if comio:
                    puntuacion += 1
        
        # Dibujar elementos según el estado del juego
        if estado_juego == ESTADOS_JUEGO["GAME_OVER"]:
            mostrar_game_over(puntuacion, puntuaciones_altas)
        elif estado_juego == ESTADOS_JUEGO["PUNTUACIONES_ALTAS"]:
            mostrar_puntuaciones_altas(puntuaciones_altas)
        else:
            dibujar_elementos(serpiente, comida, puntuacion, estado_juego == ESTADOS_JUEGO["PAUSA"])
        
        pygame.display.update()
        reloj.tick(FPS)

if __name__ == "__main__":
    main()