import pygame, sys, random, _thread, math
import numpy as np
from pygame.locals import *
from opensimplex import OpenSimplex

gen = OpenSimplex(seed=random.randint(0, 99999999999))
def noise(nx, ny):
    # Rescale from -1.0:+1.0 to 0.0:1.0
    return gen.noise2d(nx, ny) / 2.0 + 0.5

def angle_between(p1, p2):
    ang1 = np.arctan2(*p1[::-1])
    ang2 = np.arctan2(*p2[::-1])
    return np.rad2deg((ang1 - ang2) % (2 * np.pi))

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

FSCREEN = False

resources = [DIRT,GRASS,WATER,COAL, SAND, DK_GRASS]
PLAYER_ORIG = pygame.image.load('player.png')
PLAYER = PLAYER_ORIG
SELECTION = pygame.image.load('selection.png')
tilemap = [ [DIRT for w in range(MAPWIDTH)] for h in range(MAPHEIGHT) ]
treemap = [ [None for w in range(MAPWIDTH)] for h in range(MAPHEIGHT) ]

class Player():
    def __init__(self):
        self.xPos = 0
        self.yPos = 0
        self.angle = 0

    def move(self, x, y):
        self.xPos += x
        self.yPos += y

    def rotateTo(self, x, y):
        global PLAYER
        PLAYER = PLAYER_ORIG
        xOff, yOff = PLAYER.get_rect().center

        #math.atan2(playerX - mouseX, playerY - mouseY)
        myradians = math.atan2(int(MAPWIDTH / 2) * TILESIZE + xOff - x, int(MAPHEIGHT / 2) * TILESIZE + yOff - y)
        angle = math.degrees(myradians)

        orig_rect = PLAYER.get_rect()
        rot_image = pygame.transform.rotozoom(PLAYER, angle, 1)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        PLAYER = rot_image
        self.angle = angle

        return angle

    def selectNearestTile(self, angle):
        x = int(MAPWIDTH / 2) * TILESIZE
        y = int(MAPHEIGHT / 2) * TILESIZE
        print(angle)
        if abs(angle) >= 135:
            y += TILESIZE
        elif angle < 135 and angle >= 55:
            x -= TILESIZE
        elif angle > -135 and angle <= -55:
            x += TILESIZE
        elif abs(angle) < 55:
            y -= TILESIZE

        DISPLAYSURF.blit(SELECTION, (x, y))

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

                plants = 0.25 * noise(4 * kx, 2 * ky)
                if plants > 0.1 and plants < 0.11 and tile != WATER and tile != COAL:
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
            return DK_GRASS
        if e < 0.8:
            if v < 0.8: return DIRT
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
        global DISPLAYSURF
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
        elif key == K_F11:
            global FSCREEN
            if FSCREEN:
                DISPLAYSURF = pygame.display.set_mode((MAPWIDTH * TILESIZE, MAPHEIGHT * TILESIZE + HEIGHT_OFF), FULLSCREEN)
            else:
                DISPLAYSURF = pygame.display.set_mode((MAPWIDTH * TILESIZE, MAPHEIGHT * TILESIZE + HEIGHT_OFF))
            FSCREEN = not FSCREEN

    def OnMouseMovement(self, x, y):
        angle = self.player.rotateTo(x, y)
        self.player.selectNearestTile(angle)

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

            x, y = pygame.mouse.get_pos()
            self.OnMouseMovement(x, y)

            # update the display
            pygame.display.update()

            CLOCK.tick(60)

if __name__ == '__main__':
    app = App()
