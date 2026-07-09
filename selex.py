#!/usr/bin/env python3

import pygame, os, sys, random
from pathlib import Path
from platformdirs import user_config_dir
import tkinter as tk
from tkinter import filedialog

SIZE = 125

def get_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def clean_newline(s):
    return "".join([char for char in s if char not in "\n"])

class App:
    def __init__(self, config_dir, last_path):
        pygame.init()
        pygame.font.init()

        self.horizontal_mode = (SIZE * 5, SIZE)
        self.vertical_mode = (SIZE, SIZE * 5)
        
        self.es_horizontal = True
        self.display = pygame.display.set_mode(self.horizontal_mode)
        pygame.display.set_caption("Selex")
        
        try:
            icon = pygame.image.load(get_path("data/images/icon.png")).convert_alpha()
            pygame.display.set_icon(icon)
        except:
            pass

        self.config_dir = config_dir
        self.save_path = config_dir / "save.txt"
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 24, bold=True)

        self.dir_selected = None
        self.selection = []
        self.selection_amount = 0
        self.abriendo_dialogo = False 

        if last_path and os.path.exists(last_path):    
            self.cargar_directorio(last_path)
            self.show_menu = False
            self.show_selection = True
        else:
            self.show_menu = True
            self.show_selection = False

        self.running = True

    def cambiar_a_horizontal(self):
        if self.es_horizontal:
            return
        self.es_horizontal = True
        self.display = pygame.display.set_mode(self.horizontal_mode)

    def cambiar_a_vertical(self):
        if not self.es_horizontal:
            return
        self.es_horizontal = False
        self.display = pygame.display.set_mode(self.vertical_mode)

    def select_dir(self):
        if self.abriendo_dialogo:
            return
            
        self.abriendo_dialogo = True
        
        modo_actual = self.horizontal_mode if self.es_horizontal else self.vertical_mode
        
        pygame.display.set_mode(modo_actual, pygame.HIDDEN)
        
        root = tk.Tk()
        root.withdraw()
        root.update()
        root.focus_force()
        
        dir_path = filedialog.askdirectory(title="Selecciona una carpeta con imágenes", initialdir=Path.home())
        root.destroy()

        self.display = pygame.display.set_mode(modo_actual, pygame.SHOWN)
        pygame.event.clear() 
        self.abriendo_dialogo = False

        if dir_path:
            self.cargar_directorio(dir_path)
            with open(self.save_path, "w") as f:
                f.write(dir_path)
        else:
            if not self.dir_selected:
                self.show_menu = True
                self.show_selection = False

    def cargar_directorio(self, path):
        self.dir_selected = Dir(path)
        if self.dir_selected.pool:
            self.select_random(min(5, len(self.dir_selected.pool)))
            self.show_menu = False
            self.show_selection = True
            with open(self.save_path, "w") as f:
                f.write(path)
        else:
            self.dir_selected = None
            self.show_menu = True
            self.show_selection = False

    def run(self):
        while self.running:
            mx, my = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: 
                        self.clic(mx, my)    

                if event.type == pygame.KEYDOWN:

                    if event.key in [pygame.K_ESCAPE, pygame.K_BACKSPACE]:
                        self.dir_selected = None
                        self.show_selection = False
                        self.show_menu = True
                        pygame.event.clear() 

                    if event.key == pygame.K_h:
                        self.cambiar_a_horizontal()
                    if event.key == pygame.K_v:
                        self.cambiar_a_vertical()
                        
                    if self.show_selection and self.dir_selected:
                        teclas = {
                            pygame.K_1: 1, pygame.K_KP1: 1,
                            pygame.K_2: 2, pygame.K_KP2: 2,
                            pygame.K_3: 3, pygame.K_KP3: 3,
                            pygame.K_4: 4, pygame.K_KP4: 4,
                            pygame.K_5: 5, pygame.K_KP5: 5
                        }
                        if event.key in teclas:
                            cant = min(teclas[event.key], len(self.dir_selected.pool))
                            if cant > 0:
                                self.select_random(cant)

            self.update()
            self.render()

    def clic(self, mx, my):
        if self.show_menu:
            self.select_dir()

        elif self.show_selection:
            max_w = self.horizontal_mode[0] if self.es_horizontal else self.vertical_mode[0]
            max_h = self.horizontal_mode[1] if self.es_horizontal else self.vertical_mode[1]

            if self.es_horizontal:
                offset_x = (max_w - (self.selection_amount * SIZE)) // 2
                mx_ajustado = mx - offset_x
                ancho_total = self.selection_amount * SIZE
                
                if 0 <= mx_ajustado < ancho_total:
                    idx = mx_ajustado // SIZE
                    if idx < self.selection_amount:
                        self.change_one(idx)
            else:
                offset_y = (max_h - (self.selection_amount * SIZE)) // 2
                my_ajustado = my - offset_y
                alto_total = self.selection_amount * SIZE
                
                if 0 <= my_ajustado < alto_total:
                    idx = my_ajustado // SIZE
                    if idx < self.selection_amount:
                        self.change_one(idx)

    def change_one(self, idx):
        if not self.dir_selected or len(self.dir_selected.pool) <= len(self.selection):
            return 

        pool = self.dir_selected.pool.copy()
        for icon in self.selection:            
            if icon in pool:
                pool.remove(icon)

        self.selection[idx] = random.choice(pool)

    def select_random(self, n):
        if not self.dir_selected or not self.dir_selected.pool:
            return
            
        self.selection_amount = n
        pool = self.dir_selected.pool.copy()

        self.selection = []
        for _ in range(n):
            pool_choice = random.choice(pool)
            self.selection.append(pool_choice)
            pool.remove(pool_choice)

    def update(self):
        pygame.display.update()
        self.clock.tick(30)

    def render(self):
        self.display.fill((40, 44, 52)) 

        max_w = self.horizontal_mode[0] if self.es_horizontal else self.vertical_mode[0]
        max_h = self.horizontal_mode[1] if self.es_horizontal else self.vertical_mode[1]

        if self.show_menu:
            texto = self.font.render("Clic here to open folder", True, (255, 255, 255))
            texto_rect = texto.get_rect(center=(max_w // 2, max_h // 2))
            self.display.blit(texto, texto_rect)

        if self.show_selection:
            if self.es_horizontal:
                offset_x = (max_w - (self.selection_amount * SIZE)) // 2
                for idx in range(self.selection_amount):
                    icon: Icon = self.selection[idx]
                    icon.render(self.display, (offset_x + (SIZE * idx), 0))
            else:
                offset_y = (max_h - (self.selection_amount * SIZE)) // 2
                for idx in range(self.selection_amount):
                    icon: Icon = self.selection[idx]
                    icon.render(self.display, (0, offset_y + (SIZE * idx)))


class Dir:
    def __init__(self, path):
        self.path = path
        self.pool = []
        valid_extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.gif')
        
        try:
            for file in os.listdir(path):
                if file.lower().endswith(valid_extensions):
                    full_file_path = os.path.join(path, file)
                    self.pool.append(Icon(full_file_path))
            # print(f"Cargadas {len(self.pool)} imagenes desde: {path}")
        except Exception as e:
            pass
            # print(f"Error al leer la carpeta: {e}")

class Icon:
    def __init__(self, path):
        self.w = SIZE
        self.h = SIZE
        self.path = path
        
        img = pygame.image.load(path).convert_alpha()
        self.img = pygame.transform.scale(img, (self.w, self.h))

    def render(self, surf, pos):
        surf.blit(self.img, pos)


if __name__ == "__main__":
    config_dir = Path(user_config_dir("selex", roaming=True))
    config_dir.mkdir(parents=True, exist_ok=True)

    save_path = config_dir / "save.txt"
    last_path = ""

    if save_path.exists():
        with open(save_path, "r") as f:
            last_path = clean_newline(f.readline())

    App(config_dir, last_path).run()