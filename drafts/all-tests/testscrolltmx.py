from pytmx.util_pygame import load_pygame
import pygame
import pyscroll


class Sprite(pygame.sprite.Sprite):
    """
    Simple Sprite class for on-screen things
    
    """
    def __init__(self, surface) -> None:
        self.image = surface
        self.rect = surface.get_rect()


# Load TMX data
tmx_data = load_pygame("carte_prof.tmx")

# Make the scrolling layer
map_layer = pyscroll.BufferedRenderer(
    data=pyscroll.TiledMapData(tmx_data),
    size=(400,400),
)

# make the pygame SpriteGroup with a scrolling map
group = pyscroll.PyscrollGroup(map_layer=map_layer)

# Add sprite(s) to the group
surface = pygame.image.load("carte.png").convert_alpha()
sprite = Sprite(surface)
group.add(sprite)

# Center the camera on the sprite
group.center(sprite.rect.center)

# Draw map and sprites using the group
# Notice I did not `screen.fill` here!  Clearing the screen is not
# needed since the map will clear it when drawn
group.draw(screen)
