class Hero(pygame.sprite.Sprite):
    """ Hero class above.
    """

class QuestGame(object):
    """ This class is a basic game.

    This class will load data, create a pyscroll group, a hero object.
    It also reads input and moves the Hero around the map.
    Finally, it uses a pyscroll group to render the map and Hero.
    """
    def __init__(self):
        # true while running
        self.running = False

        # load data from pytmx
        tmx_data = pytmx.load_pygame(self.filename)

        # create new data source for pyscroll
        map_data = pyscroll.data.TiledMapData(tmx_data)

        w, h = screen.get_size()

        # create new renderer (camera)
        # clamp_camera is used to prevent the map from scrolling past the edge
        self.map_layer = pyscroll.BufferedRenderer(map_data,
                                                   (w / 2, h / 2),
                                                   clamp_camera=True)

        self.group = pyscroll.PyscrollGroup(map_layer=self.map_layer) 
# I use "from pyscroll.group import PyscrollGroup", if you do this don't use the pyscroll bit above.
        self.hero = Hero()

        # put the hero in the center of the map
        self.hero.position = self.map_layer.rect.center

        # add our hero to the group
        self.group.add(self.hero)

    def draw(self, surface):
        """ Drawing code goes here
        """
        # center the map/screen on our Hero
        self.group.center(self.hero.rect.center)

        # draw the map and all sprites
        self.group.draw(surface)

    def handle_input(self):
        """ Handle pygame input events
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
                break

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                    pygame.exit()
                    break

#        """ You might want to add in debug keys here, like print(self.hero.position), etc.
 #           A list of all PyGame keybindings can be found at http://www.pygame.org/docs/ref/key.html 
  #      """

            # this will be handled if the window is resized
            elif event.type == VIDEORESIZE:
                init_screen(event.w, event.h)
                self.map_layer.set_size((event.w / 2, event.h / 2))

        # using get_pressed is slightly less accurate than testing for events,
        # but is much easier to use.
        pressed = pygame.key.get_pressed()
        if pressed[K_UP]:
            self.hero.velocity[1] = -HERO_MOVE_SPEED
        elif pressed[K_DOWN]:
            self.hero.velocity[1] = HERO_MOVE_SPEED

        if pressed[K_LEFT]:
            self.hero.velocity[0] = -HERO_MOVE_SPEED
        elif pressed[K_RIGHT]:
            self.hero.velocity[0] = HERO_MOVE_SPEED

    def run(self):
        """ Run the game loop
        """
        clock = pygame.time.Clock()
        fps = 60
        scale = pygame.transform.scale
        self.running = True

        try:
            while self.running:
                dt = clock.tick(fps) / 1000.
                self.handle_input()
                self.update(dt)
                self.draw(temp_surface)
                scale(temp_surface, screen.get_size(), screen)
                pygame.display.flip()

        except KeyboardInterrupt:
            self.running = False
            pygame.exit()
