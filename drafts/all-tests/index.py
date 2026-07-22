import pygame
import pytmx
from pytmx.util_pygame import load_pygame

# Initialisation de Pygame
pygame.init()

# Configuration de la fenêtre
screen_width = 1408  # 88 tuiles * 16 pixels
screen_height = 320  # 20 tuiles * 16 pixels
screen = pygame.display.set_mode((screen_width, screen_height))

pygame.display.set_caption("pyri")

# Chargement de la carte TMX

tmx_data = load_pygame("carte.tmx", pixelalpha=True)

####Fonction pour dessiner la carte
##def draw_map(surface, tmx_data):
##    for layer in tmx_data.visible_layers:
##        if isinstance(layer, pytmx.TiledTileLayer):
##            for x, y, gid in layer:
##                if gid > 0:  # Ignore les tuiles vides
##                    real_gid = gid - tmx_data.get_tileset_from_gid(gid).firstgid + 1
##                    tile = tmx_data.get_tile_image_by_gid(gid)
##
##                    # Affiche les infos des tuiles
##                   
##                    if tile:
##                        surface.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))
##                               ##  pygame.draw.rect(surface, (255, 0, 0), (x * 16, y * 16, 16, 16), 1)  # Grille rouge
####            for x, y, gid in layer:
####                if gid == 0:
####                    print(f"Aucune tuile à ({x}, {y})")
####                elif gid > len(tmx_data.tilesets) * 256:
####                    print(f"GID trop élevé ({gid}) à ({x}, {y}) ! Vérifie le tileset.")
##
def draw_map(surface, tmx_data):
    layer_name = "Calque de Tuiles 5"  # Change le nom selon ton test
    layer = tmx_data.get_layer_by_name(layer_name)
    if isinstance(layer, pytmx.TiledTileLayer):
        for x, y, gid in layer:
            tile = tmx_data.get_tile_image_by_gid(gid)
            if tile:
                surface.blit(tile, (x * tmx_data.tilewidth, y * tmx_data.tileheight))

# Boucle principale
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Effacer l'écran
    screen.fill((0, 0, 0))

    # Dessiner la carte
    draw_map(screen, tmx_data)

    # Mettre à jour l'affichage
    pygame.display.flip()

# Quitter Pygame
pygame.quit()
