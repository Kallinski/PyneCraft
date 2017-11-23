import math
from data.src.globals import *
from data.src.Inventory import Inventory

class Player(pygame.sprite.Sprite):
    def __init__(self, surface, id=-1, x=0, y=0):
        pygame.sprite.Sprite.__init__(self)
        self.surface = surface
        self.xPos = x
        self.yPos = y
        self.currentSelectionX = 0
        self.currentSelectionY = 0
        self.inventory = Inventory()

    def move(self, x, y):
        self.xPos += x
        self.yPos += y

    def rotateTo(self, x, y):
        global PLAYER, PLAYER_ORIG
        PLAYER = PLAYER_ORIG
        xOff, yOff = globals.PLAYER.get_rect().center

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

    def selectNearestTile(self, x, y):
        global DISPLAYSURF
        playerX = int(MAPWIDTH / 2) * TILESIZE
        playerY = int(MAPHEIGHT / 2) * TILESIZE

        if  x >= playerX - TILESIZE and x < playerX + 2*TILESIZE and \
            y >= playerY - TILESIZE and y < playerY + 2*TILESIZE and not \
            (y >= playerY and y < playerY + TILESIZE and x >= playerX and x < playerX + TILESIZE):

            nx = int(x / TILESIZE)
            ny = int(y / TILESIZE)

            DISPLAYSURF.blit(SELECTION, (nx * TILESIZE, ny * TILESIZE))

            self.currentSelectionX = nx
            self.currentSelectionY = ny

    def getCurrentSelection(self):
        return (self.currentSelectionX, self.currentSelectionY)

    def update(self):
        global DISPLAYSURF
        DISPLAYSURF.blit(self.surface, (int(MAPWIDTH / 2) * TILESIZE, int(MAPHEIGHT / 2) * TILESIZE))