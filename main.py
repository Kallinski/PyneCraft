import pygame, sys, random, _thread
from pygame.locals import *
from opensimplex import OpenSimplex

gen = OpenSimplex(seed=random.randint(0, 99999999999))
def noise(nx, ny):
    # Rescale from -1.0:+1.0 to 0.0:1.0
    return gen.noise2d(nx, ny) / 2.0 + 0.5

#constants representing colours
BLACK = (0,   0,   0  )
BROWN = (153, 76,  0  )
GREEN = (0,   255, 0  )
BLUE  = (0,   0,   255)
WHITE = (255, 255, 255)

#constants representing the different resources
DIRT  = 0
GRASS = 1
WATER = 2
COAL  = 3
DK_GRASS = 4
SAND = 6
TREE = 7

#a dictionary linking resources to textures
textures =   {
                DIRT   : pygame.image.load('dirt.png'),
                GRASS  : pygame.image.load('grass.png'),
                DK_GRASS  : pygame.image.load('dark_grass.png'),
                WATER  : pygame.image.load('water.png'),
                COAL   : pygame.image.load('coal.png'),
                SAND   : pygame.image.load('sand.png'),
                TREE   : pygame.image.load('bausch.png'),
            }

inventory =   {
                DIRT   : 0,
                GRASS  : 0,
                DK_GRASS: 0,
                WATER  : 0,
                COAL   : 0,
                SAND: 0
            }

#useful game dimensions
TILESIZE  = 40
SCREENWIDTH = 1920
SCREENHEIGHT = 1080 - TILESIZE*2
MAPWIDTH  = int(SCREENWIDTH / TILESIZE)
MAPHEIGHT = int(SCREENHEIGHT / TILESIZE)
HEIGHT_OFF = 2*TILESIZE
DISPLAYSURF = None
INVFONT = None
CLOCK = None

resources = [DIRT,GRASS,WATER,COAL, SAND, DK_GRASS]
PLAYER = pygame.image.load('player.png')
tilemap = [ [DIRT for w in range(MAPWIDTH)] for h in range(MAPHEIGHT) ]
treemap = [ [None for w in range(MAPWIDTH)] for h in range(MAPHEIGHT) ]

class Player():
    def __init__(self):
        self.xPos = 0
        self.yPos = 0

    def move(self, x, y):
        self.xPos += x
        self.yPos += y

    def update(self):
        DISPLAYSURF.blit(PLAYER, (int(MAPWIDTH / 2) * TILESIZE, int(MAPHEIGHT / 2) * TILESIZE))

class Inventory():
    def update(self):
        # display the inventory, starting 10 pixels in
        placePosition = 10
        for item in resources:
            # add the image
            DISPLAYSURF.blit(textures[item], (placePosition, MAPHEIGHT * TILESIZE + 20))
            placePosition += 30
            # add the text showing the amount in the inventory
            textObj = INVFONT.render(str(inventory[item]), True, WHITE, BLACK)
            DISPLAYSURF.blit(textObj, (placePosition, MAPHEIGHT * TILESIZE + 20))
            placePosition += 50

class Map():
    def update(self, xPos, yPos):
        global gen
        gen = OpenSimplex(seed=random.randint(0, 99999999999))
        # loop through each row
        for row in range(MAPHEIGHT):
            # loop through each column in the row
            for column in range(MAPWIDTH):

                kx = (xPos + column) / MAPWIDTH - 0.5
                ky = (yPos + row) / MAPHEIGHT - 0.5

                #elevation
                e = 0.5 * noise(0.5 * kx, 0.5 * ky) \
                    + 0.4 * noise(2 * kx, 2 * ky) \
                    + 0.1 * noise(2 * kx, 2 * ky)

                v = 0.6 * noise(0.5 * kx, 0.5 * ky) \
                    + 0.3 * noise(2 * kx, 2 * ky) \
                    + 0.2 * noise(2 * kx, 2 * ky)

                tile = self.biome(e, v)

                tilemap[row][column] = tile

                DISPLAYSURF.blit(textures[tile], (column * TILESIZE, row * TILESIZE))

                plants = 1 * noise(4 * kx, 2 * ky)
                if plants > 0.7 and plants < 0.8 and tile != WATER and tile != COAL and random.randint(0,9) <= 5:
                    DISPLAYSURF.blit(textures[TREE], (column * TILESIZE, row * TILESIZE))
                    treemap[row][column] = TREE
                else:
                    treemap[row][column] = None

    def biome(self, e, v):
        if e < 0.4: return WATER
        if e < 0.45: return SAND

        if e < 0.6:
            if v < 0.5: return DK_GRASS
            return GRASS
        if e < 0.7:
            if v < 0.2: return SAND
            return DIRT
        if e < 0.8:
            if v < 0.8: return DK_GRASS
            return COAL
        return COAL

class App():
    def __init__(self):
        global DISPLAYSURF, INVFONT, CLOCK
        # set up the display
        pygame.init()
        modes = pygame.display.list_modes(16)
        DISPLAYSURF = pygame.display.set_mode((MAPWIDTH * TILESIZE, MAPHEIGHT * TILESIZE + HEIGHT_OFF))
        # add a font for our inventory
        INVFONT = pygame.font.Font('Font.ttf', 18)
        CLOCK = pygame.time.Clock()
        self.map = Map()
        self.inventory = Inventory()
        self.player = Player()
        self.loop()

    def OnEvent(self, event):
            # if the user wants to quit
            if event.type == QUIT:
                # and the game and close the window
                pygame.quit()
                sys.exit()
            # if a key is pressed
            elif event.type == KEYDOWN:
                self.OnKeydownEvent(event.key)

    def OnKeysPressed(self, keys):
        # if the right arrow is pressed
        if (keys[K_RIGHT] or keys[K_d]) \
                and tilemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) + 1] != WATER \
                and treemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) + 1] != TREE:
            # change the player's x position
            self.player.move(+1, 0)
        if (keys[K_LEFT] or keys[K_a]) \
                and tilemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) - 1] != WATER \
                and treemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) - 1] != TREE:
            # change the player's x position
            self.player.move(-1, 0)
        if (keys[K_UP] or keys[K_w]) \
                and tilemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2)] != WATER \
                and treemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2)] != TREE:
            # change the player's x position
            self.player.move(0, -1)
        if (keys[K_DOWN] or keys[K_s]) \
                and tilemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2)] != WATER \
                and treemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2)] != TREE:
            # change the player's x position
            self.player.move(0, +1)

    def OnKeydownEvent(self, key):
        # placing dirt
        if (key == K_1):
            # get the tile to swap with the dirt
            currentTile = tilemap[(int(MAPHEIGHT / 2))][(int(MAPWIDTH / 2))]
            # if we have dirt in our inventory
            if inventory[DIRT] > 0:
                # remove one dirt and place it
                inventory[DIRT] -= 1
                # swap the item that was there before
                inventory[currentTile] += 1
        elif key == K_SPACE:
            # what resource is the player standing on?
            currentTile = tilemap[(int(MAPHEIGHT / 2))][(int(MAPWIDTH / 2))]
            # player now has 1 more of this resource
            inventory[currentTile] += 1
            # the player is now standing on dirt
            tilemap[(int(MAPHEIGHT / 2))][(int(MAPWIDTH / 2))] = DIRT
        elif key == K_ESCAPE:
            pygame.quit()
            sys.exit()

    def loop(self):

        #initial map
        self.map.update(0, 0)

        while True:
            for event in pygame.event.get():
                self.OnEvent(event)

            self.OnKeysPressed(pygame.key.get_pressed())

            self.inventory.update()
            self.map.update(self.player.xPos, self.player.yPos)
            self.player.update()

            # update the display
            pygame.display.update()

            CLOCK.tick(60)

if __name__ == '__main__':
    app = App()
