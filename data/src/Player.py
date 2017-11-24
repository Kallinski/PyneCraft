import math
import data.src.globals as glob
import pygame
from data.src.Inventory import Inventory

sheet = pygame.image.load("data/textures/character.png")

class Player(pygame.sprite.Sprite):
    def __init__(self, surface, id=-1, x=0, y=0, inventory=None):
        pygame.sprite.Sprite.__init__(self)
        self.surface = surface
        self.xPos = x
        self.yPos = y
        self.currentSelectionX = 0
        self.currentSelectionY = 0
        self.status = "standing"
        self.current_animation = 0
        self.last_animation = pygame.time.get_ticks()
        self.animation_cooldown = 30
        self.max_animation = 6
        if inventory == None: self.inventory = Inventory()
        else: self.inventory = Inventory(inventory)

    def move(self, x, y):
        if x == 0 and y < 0:
            self.status = "walking up"
        elif x == 0 and y > 0:
            self.status = "walking down"
        elif x < 0:
            self.status = "walking left"
        elif x > 0:
            self.status = "walking right"

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
        RANGE = 3
        playerX = int(glob.MAPWIDTH / 2) * glob.TILESIZE
        playerY = int(glob.MAPHEIGHT / 2) * glob.TILESIZE

        if  x >= playerX - RANGE*glob.TILESIZE and x < playerX + (RANGE+1)*glob.TILESIZE and \
            y >= playerY - RANGE*glob.TILESIZE and y < playerY + (RANGE+1)*glob.TILESIZE and not \
            (y >= playerY and y < playerY + glob.TILESIZE and x >= playerX and x < playerX + glob.TILESIZE):

            nx = int(x / glob.TILESIZE)
            ny = int(y / glob.TILESIZE)

            glob.DISPLAYSURF.blit(glob.SELECTION, (nx * glob.TILESIZE, ny * glob.TILESIZE))

            self.currentSelectionX = nx
            self.currentSelectionY = ny

    def getCurrentSelection(self):
        return (self.currentSelectionX, self.currentSelectionY)

    def update(self):
        if self.status == "walking up":
            time_now = pygame.time.get_ticks()
            if time_now - self.last_animation >= self.animation_cooldown:
                self.last_animation = pygame.time.get_ticks()
                if self.current_animation == self.max_animation:
                    self.current_animation = 0
                    self.status = "standing"
                else:
                    self.current_animation += 1
            glob.DISPLAYSURF.blit(sheet, (int(glob.MAPWIDTH / 2) * glob.TILESIZE - (64 - 40) / 2,int(glob.MAPHEIGHT / 2) * glob.TILESIZE - 24),(self.current_animation * 64, 8 * 64, 64, 64))
        elif self.status == "walking down":
            time_now = pygame.time.get_ticks()
            if time_now - self.last_animation >= self.animation_cooldown:
                self.last_animation = pygame.time.get_ticks()
                if self.current_animation == self.max_animation:
                    self.current_animation = 0
                    self.status = "standing"
                else:
                    self.current_animation += 1
            glob.DISPLAYSURF.blit(sheet, (
            int(glob.MAPWIDTH / 2) * glob.TILESIZE - (64 - 40) / 2, int(glob.MAPHEIGHT / 2) * glob.TILESIZE - 24),
                                  (self.current_animation * 64, 10 * 64, 64, 64))
        elif self.status == "walking left":
            time_now = pygame.time.get_ticks()
            if time_now - self.last_animation >= self.animation_cooldown:
                self.last_animation = pygame.time.get_ticks()
                if self.current_animation == self.max_animation:
                    self.current_animation = 0
                    self.status = "standing"
                else:
                    self.current_animation += 1
            glob.DISPLAYSURF.blit(sheet, (
            int(glob.MAPWIDTH / 2) * glob.TILESIZE - (64 - 40) / 2, int(glob.MAPHEIGHT / 2) * glob.TILESIZE - 24),
                                  (self.current_animation * 64, 9 * 64, 64, 64))
        elif self.status == "walking right":
            time_now = pygame.time.get_ticks()
            if time_now - self.last_animation >= self.animation_cooldown:
                self.last_animation = pygame.time.get_ticks()
                if self.current_animation == self.max_animation:
                    self.current_animation = 0
                    self.status = "standing"
                else:
                    self.current_animation += 1
            glob.DISPLAYSURF.blit(sheet, (
            int(glob.MAPWIDTH / 2) * glob.TILESIZE - (64 - 40) / 2, int(glob.MAPHEIGHT / 2) * glob.TILESIZE - 24),
                                  (self.current_animation * 64, 11 * 64, 64, 64))

        else:
            glob.DISPLAYSURF.blit(sheet, (int(glob.MAPWIDTH / 2) * glob.TILESIZE - 24/ 2, int(glob.MAPHEIGHT / 2) * glob.TILESIZE - 24) ,(self.current_animation * 64, 2 * 64, 64, 64 ))
