import asyncio
import pygame
import random
import math

# Configuración para PyGBag
import sys
import platform

# Inicializar Pygame
pygame.init()

# Constantes
ANCHO = 800
ALTO = 600
FPS = 60

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
AZUL = (0, 100, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AMARILLO = (255, 255, 0)
GRIS = (128, 128, 128)
MARRON = (139, 69, 19)
DORADO = (255, 215, 0)
NARANJA = (255, 165, 0)
MORADO = (128, 0, 128)

class Bala:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidad = 10
        self.ancho = 3
        self.alto = 8
        
    def mover(self):
        self.y -= self.velocidad
        
    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, AMARILLO, (self.x, self.y, self.ancho, self.alto))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)

class Asteroide:
    def __init__(self, tipo="gris"):
        self.tipo = tipo
        self.x = random.randint(0, ANCHO - 40)
        self.y = -40
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        
        if tipo == "gris":
            self.vida = 1
            self.puntos = 10
            self.color = GRIS
            self.tamaño = 30
            self.velocidad = random.uniform(2, 4)
        elif tipo == "marron":
            self.vida = 2
            self.vida_max = 2
            self.puntos = 25
            self.color = MARRON
            self.tamaño = 35
            self.velocidad = random.uniform(1, 2.5)
        elif tipo == "rojo":
            self.vida = 1
            self.puntos = 50
            self.color = ROJO
            self.tamaño = 25
            self.velocidad = random.uniform(4, 6)
        elif tipo == "dorado":
            self.vida = 1
            self.puntos = 100
            self.color = DORADO
            self.tamaño = 32
            self.velocidad = random.uniform(1.5, 3)
            
    def mover(self):
        self.y += self.velocidad
        self.rotation += self.rotation_speed
        
    def dibujar(self, pantalla):
        # Efecto de brillo para asteroides dorados
        if self.tipo == "dorado":
            for i in range(3):
                color_brillo = (min(255, self.color[0] + i*20), 
                              min(255, self.color[1] + i*20), 
                              self.color[2])
                pygame.draw.circle(pantalla, color_brillo, 
                                 (int(self.x + self.tamaño//2), int(self.y + self.tamaño//2)), 
                                 self.tamaño//2 + i)
        
        # Color diferente para asteroides dañados
        color_actual = self.color
        if self.tipo == "marron" and hasattr(self, 'vida_max') and self.vida < self.vida_max:
            color_actual = (self.color[0]//2, self.color[1]//2, self.color[2]//2)
            
        pygame.draw.circle(pantalla, color_actual, 
                         (int(self.x + self.tamaño//2), int(self.y + self.tamaño//2)), 
                         self.tamaño//2)
        
        # Borde más oscuro
        pygame.draw.circle(pantalla, NEGRO, 
                         (int(self.x + self.tamaño//2), int(self.y + self.tamaño//2)), 
                         self.tamaño//2, 2)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.tamaño, self.tamaño)

class PowerUp:
    def __init__(self, x, y, tipo):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.velocidad = 2
        self.tamaño = 20
        self.tiempo_vida = 300  # 5 segundos a 60 FPS
        
        colores = {
            "doble": AZUL,
            "escudo": VERDE,
            "lento": MORADO,
            "laser": NARANJA
        }
        self.color = colores.get(tipo, BLANCO)
        
    def mover(self):
        self.y += self.velocidad
        self.tiempo_vida -= 1
        
    def dibujar(self, pantalla):
        # Efecto de parpadeo cuando está por expirar
        if self.tiempo_vida < 60 and self.tiempo_vida % 10 < 5:
            return
            
        pygame.draw.rect(pantalla, self.color, 
                        (self.x - self.tamaño//2, self.y - self.tamaño//2, 
                         self.tamaño, self.tamaño))
        pygame.draw.rect(pantalla, BLANCO, 
                        (self.x - self.tamaño//2, self.y - self.tamaño//2, 
                         self.tamaño, self.tamaño), 2)
        
        # Icono según el tipo
        font = pygame.font.Font(None, 16)
        iconos = {"doble": "2x", "escudo": "S", "lento": "T", "laser": "L"}
        texto = font.render(iconos.get(self.tipo, "?"), True, BLANCO)
        texto_rect = texto.get_rect(center=(self.x, self.y))
        pantalla.blit(texto, texto_rect)
        
    def get_rect(self):
        return pygame.Rect(self.x - self.tamaño//2, self.y - self.tamaño//2, 
                          self.tamaño, self.tamaño)

class Nave:
    def __init__(self):
        self.x = ANCHO // 2
        self.y = ALTO - 80
        self.ancho = 40
        self.alto = 30
        self.velocidad = 6
        self.vidas = 3
        self.escudo = False
        self.doble_disparo = False
        self.tiempo_escudo = 0
        self.tiempo_doble = 0
        
    def mover(self, teclas):
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            self.x = max(0, self.x - self.velocidad)
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            self.x = min(ANCHO - self.ancho, self.x + self.velocidad)
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            self.y = max(ALTO//2, self.y - self.velocidad)
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            self.y = min(ALTO - self.alto, self.y + self.velocidad)
            
    def actualizar_powerups(self):
        if self.tiempo_escudo > 0:
            self.tiempo_escudo -= 1
            if self.tiempo_escudo == 0:
                self.escudo = False
                
        if self.tiempo_doble > 0:
            self.tiempo_doble -= 1
            if self.tiempo_doble == 0:
                self.doble_disparo = False
        
    def dibujar(self, pantalla):
        # Dibujar escudo si está activo
        if self.escudo:
            pygame.draw.circle(pantalla, VERDE, 
                             (self.x + self.ancho//2, self.y + self.alto//2), 
                             self.ancho//2 + 10, 3)
        
        # Dibujar nave
        puntos = [
            (self.x + self.ancho//2, self.y),
            (self.x, self.y + self.alto),
            (self.x + self.ancho//4, self.y + self.alto - 5),
            (self.x + 3*self.ancho//4, self.y + self.alto - 5),
            (self.x + self.ancho, self.y + self.alto)
        ]
        pygame.draw.polygon(pantalla, AZUL, puntos)
        pygame.draw.polygon(pantalla, BLANCO, puntos, 2)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.ancho, self.alto)
        
    def recibir_daño(self):
        if self.escudo:
            self.escudo = False
            self.tiempo_escudo = 0
            return False
        else:
            self.vidas -= 1
            return True

class Juego:
    def __init__(self):
        self.pantalla = pygame.display.set_mode((ANCHO, ALTO))
        pygame.display.set_caption("🚀 Asteroid Defender")
        self.reloj = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.font_grande = pygame.font.Font(None, 72)
        self.font_pequeño = pygame.font.Font(None, 24)
        
        # Estado del juego
        self.estado = "menu"  # "menu", "jugando", "game_over", "puntuaciones", "tutorial"
        
        self.reset_juego()
        # PyGBag compatible - puntuaciones en memoria
        self.puntuaciones = []
        
    def reset_juego(self):
        self.nave = Nave()
        self.balas = []
        self.asteroides = []
        self.powerups = []
        self.fragmentos = []
        self.puntos = 0
        self.combo = 0
        self.tiempo_sin_golpe = 0
        self.oleada = 1
        self.tiempo_spawn = 0
        self.tiempo_oleada = 0
        self.tiempo_lento = 0
        self.ultimo_disparo = 0
        
    def agregar_puntuacion(self, puntos):
        self.puntuaciones.append(puntos)
        self.puntuaciones.sort(reverse=True)
        self.puntuaciones = self.puntuaciones[:5]  # Solo top 5
        
    def crear_asteroide(self):
        # Probabilidades según la oleada
        prob_dorado = min(5 + self.oleada, 15)
        prob_rojo = min(10 + self.oleada * 2, 30)
        prob_marron = min(15 + self.oleada * 2, 35)
        
        rand = random.randint(1, 100)
        
        if rand <= prob_dorado:
            return Asteroide("dorado")
        elif rand <= prob_dorado + prob_rojo:
            return Asteroide("rojo")
        elif rand <= prob_dorado + prob_rojo + prob_marron:
            return Asteroide("marron")
        else:
            return Asteroide("gris")
    
    def crear_fragmentos(self, asteroide):
        """Crear fragmentos cuando explota un asteroide rojo"""
        fragmentos = []
        for _ in range(3):
            frag = Asteroide("gris")
            frag.x = asteroide.x + random.randint(-10, 10)
            frag.y = asteroide.y + random.randint(-10, 10)
            frag.tamaño = 15
            frag.puntos = 5
            frag.velocidad = random.uniform(2, 5)
            fragmentos.append(frag)
        return fragmentos
        
    def crear_powerup(self, x, y):
        tipos = ["doble", "escudo", "lento", "laser"]
        tipo = random.choice(tipos)
        return PowerUp(x, y, tipo)
        
    def aplicar_powerup(self, powerup):
        if powerup.tipo == "doble":
            self.nave.doble_disparo = True
            self.nave.tiempo_doble = 600  # 10 segundos
        elif powerup.tipo == "escudo":
            self.nave.escudo = True
            self.nave.tiempo_escudo = 300  # 5 segundos
        elif powerup.tipo == "lento":
            self.tiempo_lento = 600  # 10 segundos
        elif powerup.tipo == "laser":
            # Mega láser que destruye todo en pantalla
            self.puntos += len(self.asteroides) * 20
            self.combo += len(self.asteroides)
            self.asteroides.clear()
            
    def disparar(self):
        if self.nave.doble_disparo:
            self.balas.append(Bala(self.nave.x + 10, self.nave.y))
            self.balas.append(Bala(self.nave.x + 30, self.nave.y))
        else:
            self.balas.append(Bala(self.nave.x + self.nave.ancho//2, self.nave.y))
            
    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            elif evento.type == pygame.KEYDOWN:
                if self.estado == "menu":
                    if evento.key == pygame.K_1:
                        self.estado = "jugando"
                    elif evento.key == pygame.K_2:
                        self.estado = "puntuaciones"
                    elif evento.key == pygame.K_3:
                        self.estado = "tutorial"
                    elif evento.key == pygame.K_4:
                        return False
                        
                elif self.estado == "jugando":
                    if evento.key == pygame.K_SPACE:
                        tiempo_actual = pygame.time.get_ticks()
                        if tiempo_actual - self.ultimo_disparo > 200:
                            self.disparar()
                            self.ultimo_disparo = tiempo_actual
                    elif evento.key == pygame.K_ESCAPE:
                        self.estado = "menu"
                        
                elif self.estado == "game_over":
                    if evento.key == pygame.K_r:
                        self.reset_juego()
                        self.estado = "jugando"
                    elif evento.key == pygame.K_m:
                        self.estado = "menu"
                        
                else:  # puntuaciones o tutorial
                    self.estado = "menu"
                    
        return True
            
    def actualizar_juego(self):
        if self.estado != "jugando":
            return
            
        # Actualizar nave
        self.nave.actualizar_powerups()
        
        # Mover balas
        for bala in self.balas[:]:
            bala.mover()
            if bala.y < 0:
                self.balas.remove(bala)
                
        # Mover asteroides (con efecto de tiempo lento)
        velocidad_multiplicador = 0.3 if self.tiempo_lento > 0 else 1.0
        if self.tiempo_lento > 0:
            self.tiempo_lento -= 1
            
        for asteroide in self.asteroides[:]:
            asteroide.velocidad_original = getattr(asteroide, 'velocidad_original', asteroide.velocidad)
            asteroide.velocidad = asteroide.velocidad_original * velocidad_multiplicador
            asteroide.mover()
            if asteroide.y > ALTO:
                self.asteroides.remove(asteroide)
                
        # Mover power-ups
        for powerup in self.powerups[:]:
            powerup.mover()
            if powerup.y > ALTO or powerup.tiempo_vida <= 0:
                self.powerups.remove(powerup)
                
        # Spawn de asteroides
        self.tiempo_spawn += 1
        spawn_rate = max(30 - self.oleada * 2, 10)  # Más rápido cada oleada
        
        if self.tiempo_spawn >= spawn_rate:
            self.tiempo_spawn = 0
            self.asteroides.append(self.crear_asteroide())
            
        # Control de oleadas
        self.tiempo_oleada += 1
        if self.tiempo_oleada >= 1800:  # 30 segundos por oleada
            self.oleada += 1
            self.tiempo_oleada = 0
            self.puntos += 200  # Bonus por sobrevivir oleada
            
        # Colisiones bala-asteroide
        for bala in self.balas[:]:
            for asteroide in self.asteroides[:]:
                if bala.get_rect().colliderect(asteroide.get_rect()):
                    self.balas.remove(bala)
                    asteroide.vida -= 1
                    
                    if asteroide.vida <= 0:
                        self.puntos += asteroide.puntos + (self.combo * 5)
                        self.combo += 1
                        self.tiempo_sin_golpe = 0
                        
                        # Crear fragmentos si es asteroide rojo
                        if asteroide.tipo == "rojo":
                            self.asteroides.extend(self.crear_fragmentos(asteroide))
                            
                        # Crear power-up si es asteroide dorado
                        if asteroide.tipo == "dorado":
                            self.powerups.append(self.crear_powerup(
                                asteroide.x + asteroide.tamaño//2,
                                asteroide.y + asteroide.tamaño//2
                            ))
                            
                        self.asteroides.remove(asteroide)
                    break
                    
        # Colisiones nave-asteroide
        for asteroide in self.asteroides[:]:
            if self.nave.get_rect().colliderect(asteroide.get_rect()):
                if self.nave.recibir_daño():
                    self.combo = 0  # Reset combo al recibir daño
                self.asteroides.remove(asteroide)
                
        # Colisiones nave-powerup
        for powerup in self.powerups[:]:
            if self.nave.get_rect().colliderect(powerup.get_rect()):
                self.aplicar_powerup(powerup)
                self.powerups.remove(powerup)
                
        # Sistema de combos
        self.tiempo_sin_golpe += 1
        if self.tiempo_sin_golpe > 180:  # 3 segundos sin golpear
            self.combo = 0
            
        # Control de movimiento de nave
        teclas = pygame.key.get_pressed()
        self.nave.mover(teclas)
        
        # Verificar game over
        if self.nave.vidas <= 0:
            self.agregar_puntuacion(self.puntos)
            self.estado = "game_over"
            
    def dibujar_fondo(self):
        self.pantalla.fill(NEGRO)
        
        # Dibujar estrellas de fondo
        for i in range(50):
            x = (i * 137) % ANCHO  # Patrón pseudo-aleatorio
            y = (i * 197 + pygame.time.get_ticks()//10) % ALTO
            pygame.draw.circle(self.pantalla, BLANCO, (x, y), 1)
    
    def dibujar_hud(self):
        # Puntos
        texto_puntos = self.font.render(f"Puntos: {self.puntos}", True, BLANCO)
        self.pantalla.blit(texto_puntos, (10, 10))
        
        # Vidas
        texto_vidas = self.font.render(f"Vidas: {self.nave.vidas}", True, BLANCO)
        self.pantalla.blit(texto_vidas, (10, 50))
        
        # Oleada
        texto_oleada = self.font.render(f"Oleada: {self.oleada}", True, BLANCO)
        self.pantalla.blit(texto_oleada, (10, 90))
        
        # Combo
        if self.combo > 0:
            texto_combo = self.font.render(f"Combo x{self.combo}!", True, AMARILLO)
            self.pantalla.blit(texto_combo, (ANCHO - 200, 10))
            
        # Power-ups activos
        y_offset = 130
        if self.nave.escudo:
            texto_escudo = self.font_pequeño.render("ESCUDO ACTIVO", True, VERDE)
            self.pantalla.blit(texto_escudo, (10, y_offset))
            y_offset += 25
            
        if self.nave.doble_disparo:
            texto_doble = self.font_pequeño.render("DISPARO DOBLE", True, AZUL)
            self.pantalla.blit(texto_doble, (10, y_offset))
            y_offset += 25
            
        if self.tiempo_lento > 0:
            texto_lento = self.font_pequeño.render("TIEMPO LENTO", True, MORADO)
            self.pantalla.blit(texto_lento, (10, y_offset))
            
    def dibujar_menu(self):
        self.dibujar_fondo()
        
        # Título
        titulo = self.font_grande.render("ASTEROID DEFENDER", True, AMARILLO)
        titulo_rect = titulo.get_rect(center=(ANCHO//2, 100))
        self.pantalla.blit(titulo, titulo_rect)
        
        # Menú
        opciones = [
            "1 - Iniciar Misión",
            "2 - Hall de la Fama", 
            "3 - Tutorial",
            "4 - Salir"
        ]
        
        for i, opcion in enumerate(opciones):
            texto = self.font.render(opcion, True, BLANCO)
            texto_rect = texto.get_rect(center=(ANCHO//2, 250 + i * 50))
            self.pantalla.blit(texto, texto_rect)
            
        # Instrucciones
        instruccion = self.font_pequeño.render("Usa las teclas numéricas para navegar", True, GRIS)
        instruccion_rect = instruccion.get_rect(center=(ANCHO//2, 500))
        self.pantalla.blit(instruccion, instruccion_rect)
        
    def dibujar_puntuaciones(self):
        self.dibujar_fondo()
        
        titulo = self.font_grande.render("HALL DE LA FAMA", True, DORADO)
        titulo_rect = titulo.get_rect(center=(ANCHO//2, 100))
        self.pantalla.blit(titulo, titulo_rect)
        
        for i, puntos in enumerate(self.puntuaciones):
            texto = self.font.render(f"{i+1}. {puntos} puntos", True, BLANCO)
            texto_rect = texto.get_rect(center=(ANCHO//2, 200 + i * 40))
            self.pantalla.blit(texto, texto_rect)
            
        if not self.puntuaciones:
            texto = self.font.render("¡Aún no hay puntuaciones!", True, GRIS)
            texto_rect = texto.get_rect(center=(ANCHO//2, 300))
            self.pantalla.blit(texto, texto_rect)
            
        volver = self.font_pequeño.render("Presiona cualquier tecla para volver", True, GRIS)
        volver_rect = volver.get_rect(center=(ANCHO//2, 500))
        self.pantalla.blit(volver, volver_rect)
        
    def dibujar_tutorial(self):
        self.dibujar_fondo()
        
        titulo = self.font_grande.render("TUTORIAL", True, VERDE)
        titulo_rect = titulo.get_rect(center=(ANCHO//2, 50))
        self.pantalla.blit(titulo, titulo_rect)
        
        instrucciones = [
            "CONTROLES:",
            "WASD o Flechas - Mover nave",
            "ESPACIO - Disparar",
            "",
            "ASTEROIDES:",
            "Gris (10pts) - 1 disparo",
            "Marrón (25pts) - 2 disparos", 
            "Rojo (50pts) - Rápido, explota en fragmentos",
            "Dorado (100pts) - Suelta power-ups",
            "",
            "POWER-UPS:",
            "Azul (2x) - Disparo doble",
            "Verde (S) - Escudo protector",
            "Morado (T) - Tiempo lento",
            "Naranja (L) - Mega láser"
        ]
        
        for i, linea in enumerate(instrucciones):
            if linea == "":
                continue
            color = AMARILLO if linea.endswith(":") else BLANCO
            texto = self.font_pequeño.render(linea, True, color)
            self.pantalla.blit(texto, (50, 120 + i * 25))
            
        volver = self.font_pequeño.render("Presiona cualquier tecla para volver", True, GRIS)
        volver_rect = volver.get_rect(center=(ANCHO//2, 550))
        self.pantalla.blit(volver, volver_rect)
        
    def dibujar_game_over(self):
        self.dibujar_fondo()
        
        titulo = self.font_grande.render("GAME OVER", True, ROJO)
        titulo_rect = titulo.get_rect(center=(ANCHO//2, 200))
        self.pantalla.blit(titulo, titulo_rect)
        
        puntos_texto = self.font.render(f"Puntuación Final: {self.puntos}", True, BLANCO)
        puntos_rect = puntos_texto.get_rect(center=(ANCHO//2, 280))
        self.pantalla.blit(puntos_texto, puntos_rect)
        
        oleada_texto = self.font.render(f"Oleadas Completadas: {self.oleada}", True, BLANCO)
        oleada_rect = oleada_texto.get_rect(center=(ANCHO//2, 320))
        self.pantalla.blit(oleada_texto, oleada_rect)
        
        opciones = self.font.render("R - Reintentar    M - Menú Principal", True, AMARILLO)
        opciones_rect = opciones.get_rect(center=(ANCHO//2, 400))
        self.pantalla.blit(opciones, opciones_rect)
        
    def dibujar_juego(self):
        self.dibujar_fondo()
        
        # Dibujar objetos del juego
        for bala in self.balas:
            bala.dibujar(self.pantalla)
            
        for asteroide in self.asteroides:
            asteroide.dibujar(self.pantalla)
            
        for powerup in self.powerups:
            powerup.dibujar(self.pantalla)
            
        self.nave.dibujar(self.pantalla)
        self.dibujar_hud()
        
    def dibujar(self):
        if self.estado == "menu":
            self.dibujar_menu()
        elif self.estado == "jugando":
            self.dibujar_juego()
        elif self.estado == "game_over":
            self.dibujar_game_over()
        elif self.estado == "puntuaciones":
            self.dibujar_puntuaciones()
        elif self.estado == "tutorial":
            self.dibujar_tutorial()
            
        pygame.display.flip()

# Función principal para PyGBag
async def main():
    juego = Juego()
    ejecutando = True
    
    while ejecutando:
        ejecutando = juego.manejar_eventos()
        juego.actualizar_juego()
        juego.dibujar()
        juego.reloj.tick(FPS)
        
        # Yield control para PyGBag
        await asyncio.sleep(0)
        
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())