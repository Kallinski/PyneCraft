import math
import data.src.globals as glob
import pygame
from data.src.Inventory import Inventory

walkingAnimations = {"up": 8, "left": 9, "down": 10, "right": 11}
attackingAnimations = {"up": 12, "left": 13, "down": 14, "right": 15}

class Player(pygame.sprite.Sprite):
    def __init__(self, surface, id=-1, x=0, y=0, inventory=None):
        pygame.sprite.Sprite.__init__(self)
        self.surface = surface
        self.xPos = x
        self.yPos = y
        self.currentSelectionX = 0
        self.currentSelectionY = 0
        self.status = "standing"
        self.walkingDir = "forwards"
        self.current_animation = 0
        self.last_animation = pygame.time.get_ticks()
        self.max_animation = 6
        self.animation_cooldown = 30
        self.direction = "down"
        if inventory == None: self.inventory = Inventory()
        else: self.inventory = Inventory(inventory)

    def move(self, x, y):
        '''
        if x == 0 and y < 0:
            #if self.direction == ""
            self.status = "walking up"
        elif x == 0 and y > 0:
            self.status = "walking down"
        elif x < 0:
            self.status = "walking left"
        elif x > 0:
            self.status = "walking right"'''

        self.status = "walking"

        self.xPos += x
        self.yPos += y

    def rotateTo(self, x, y):
        xOff, yOff = glob.PLAYER.get_rect().center

        myradians = math.atan2(int(glob.MAPWIDTH / 2) * glob.TILESIZE + xOff - x, int(glob.MAPHEIGHT / 2) * glob.TILESIZE + yOff - y)
        angle = math.degrees(myradians)

        if abs(angle) <= 60:
            self.direction = "up"
        elif angle < -45 and angle >= -165:
            self.direction = "right"
        elif angle > 45 and angle <= 165:
            self.direction = "left"
        else:
            self.direction = "down"

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

    def stopAnimation(self):
        self.current_animation = 0

    def attack(self):
        self.status = "attacking"

    def update(self):
        glob.DISPLAYSURF.blit(glob.shadow, (int(glob.MAPWIDTH / 2) * glob.TILESIZE, int(glob.MAPHEIGHT / 2) * glob.TILESIZE),)
        if self.status == "standing":
            glob.DISPLAYSURF.blit(glob.character, (int(glob.MAPWIDTH / 2) * glob.TILESIZE - 32/ 2, int(glob.MAPHEIGHT / 2) * glob.TILESIZE - glob.TILESIZE) ,(self.current_animation * 64, walkingAnimations[self.direction] * 64, 64, 64 ))
            return

        if self.status == "walking":
            animation = walkingAnimations
            self.max_animation = 8
            self.animation_cooldown = 30
        elif self.status == "attacking":
            self.max_animation = 5
            self.animation_cooldown = 60
            animation = attackingAnimations

        time_now = pygame.time.get_ticks()
        if time_now - self.last_animation >= self.animation_cooldown:
            self.last_animation = pygame.time.get_ticks()
            if self.current_animation == self.max_animation:
                self.current_animation = 0
                self.status = "standing"
            else:
                self.current_animation += 1

        glob.DISPLAYSURF.blit(glob.character, (int(glob.MAPWIDTH / 2) * glob.TILESIZE - (64 - 32) / 2,int(glob.MAPHEIGHT / 2) * glob.TILESIZE - glob.TILESIZE),(self.current_animation * 64, animation[self.direction] * 64, 64, 64))
