import math
import data.src.globals as glob
import pygame
from data.src.Inventory import Inventory

class Player(pygame.sprite.Sprite):
    def __init__(self, surface, id=-1, x=0, y=0, inventory=None):
        pygame.sprite.Sprite.__init__(self)
        self.surface = surface
        self.xPos = x
        self.yPos = y
        self.currentSelectionX = 0
        self.currentSelectionY = 0
        if inventory == None: self.inventory = Inventory()
        else: self.inventory = Inventory(inventory)

    def move(self, x, y):
        self.xPos += x
        self.yPos += y

    def rotateTo(self, x, y):
        glob.PLAYER = glob.PLAYER_ORIG
        xOff, yOff = glob.PLAYER.get_rect().center

        myradians = math.atan2(int(glob.MAPWIDTH / 2) * glob.TILESIZE + xOff - x, int(glob.MAPHEIGHT / 2) * glob.TILESIZE + yOff - y)
        angle = math.degrees(myradians)

        orig_rect = glob.PLAYER.get_rect()
        rot_image = pygame.transform.rotozoom(glob.PLAYER, angle, 1)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        glob.PLAYER = rot_image
        self.angle = angle

        return angle

    def selectNearestTile(self, x, y):
        playerX = int(glob.MAPWIDTH / 2) * glob.TILESIZE
        playerY = int(glob.MAPHEIGHT / 2) * glob.TILESIZE

        if  x >= playerX - glob.TILESIZE and x < playerX + 2*glob.TILESIZE and \
            y >= playerY - glob.TILESIZE and y < playerY + 2*glob.TILESIZE and not \
            (y >= playerY and y < playerY + glob.TILESIZE and x >= playerX and x < playerX + glob.TILESIZE):

            nx = int(x / glob.TILESIZE)
            ny = int(y / glob.TILESIZE)

            glob.DISPLAYSURF.blit(glob.SELECTION, (nx * glob.TILESIZE, ny * glob.TILESIZE))

            self.currentSelectionX = nx
            self.currentSelectionY = ny

    def getCurrentSelection(self):
        return (self.currentSelectionX, self.currentSelectionY)

    def update(self):
        glob.DISPLAYSURF.blit(glob.PLAYER, (int(glob.MAPWIDTH / 2) * glob.TILESIZE, int(glob.MAPHEIGHT / 2) * glob.TILESIZE))