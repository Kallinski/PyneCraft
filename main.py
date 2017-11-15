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

#a dictionary linking resources to textures
textures =   {
                DIRT   : pygame.image.load('dirt.png'),
                GRASS  : pygame.image.load('grass.png'),
                WATER  : pygame.image.load('water.png'),
                COAL   : pygame.image.load('coal.png'),
            }

textures1 = {
                DIRT   : BROWN,
                GRASS  : GREEN,
                WATER  : BLUE,
                COAL   : BLACK,
            }

inventory =   {
                DIRT   : 0,
                GRASS  : 0,
                WATER  : 0,
                COAL   : 0
            }

#useful game dimensions
TILESIZE  = 40
SCREENWIDTH = 1920
SCREENHEIGHT = 1080 - TILESIZE*2
MAPWIDTH  = int(SCREENWIDTH / TILESIZE)
MAPHEIGHT = int(SCREENHEIGHT / TILESIZE)
HEIGHT_OFF = 2*TILESIZE

#the player image
PLAYER = pygame.image.load('player.png')
#the position of the player [x,y]
playerPos = [0,0]

#a list of resources
resources = [DIRT,GRASS,WATER,COAL]
#use list comprehension to create our tilemap
tilemap = [ [DIRT for w in range(MAPWIDTH)] for h in range(MAPHEIGHT) ]

#set up the display
pygame.init()
modes = pygame.display.list_modes(16)
DISPLAYSURF = pygame.display.set_mode((MAPWIDTH*TILESIZE, MAPHEIGHT*TILESIZE + HEIGHT_OFF), FULLSCREEN)


#add a font for our inventory
INVFONT = pygame.font.Font('Font.ttf', 18)

mapClock = pygame.time.Clock()
displayClock = pygame.time.Clock()

def updateMap(xPos, yPos):
    # loop through each row
    for row in range(MAPHEIGHT):
        # loop through each column in the row
        for column in range(MAPWIDTH):
            kx = (xPos + column) / MAPWIDTH - 0.5
            ky = (yPos + row) / MAPHEIGHT - 0.5
            value = 0.9 * noise(0.5 * kx, 0.5 * ky) \
                    + 0.4 * noise(2 * kx, 2 * ky) \
                    + 0.15 * noise(2 * kx, 2 * ky)

            if value > 0.65 and value <= 0.7:
                tile = DIRT
            elif value > 0.7 and value <= 0.9:
                tile = GRASS
            elif value > 0.9:
                tile = COAL
            else:
                tile = WATER

            tilemap[row][column] = tile

            DISPLAYSURF.blit(textures[tilemap[row][column]], (column * TILESIZE, row * TILESIZE))

#loop through each row
for rw in range(MAPHEIGHT):
    #loop through each column in that row
    for cl in range(MAPWIDTH):
        kx = (cl) / MAPWIDTH - 0.5
        ky = (rw) / MAPHEIGHT - 0.5
        value = 0.75 * noise(0.5 * kx, 0.5 * ky) \
                + 0.5 * noise(2 * kx, 2 * ky) \
                + 0.25 * noise(3 * kx, 3 * ky)

        if value > 0.65 and value <= 0.7:
            tile = DIRT
        elif value > 0.7 and value <= 0.9:
            tile = GRASS
        elif value > 0.9:
            tile = COAL
        else:
            tile = WATER
        #set the position in the tilemap to the randomly chosen tile
    tilemap[rw][cl] = tile


while True:

    #get all the user events
    for event in pygame.event.get():
        #if the user wants to quit
        if event.type == QUIT:
            #and the game and close the window
            pygame.quit()
            sys.exit()
        #if a key is pressed
        elif event.type == KEYDOWN:
            #placing dirt
            if (event.key == K_1):
                #get the tile to swap with the dirt
                currentTile = tilemap[playerPos[1]][playerPos[0]]
                #if we have dirt in our inventory
                if inventory[DIRT] > 0:
                    #remove one dirt and place it
                    inventory[DIRT] -= 1
                    tilemap[playerPos[1]][playerPos[0]] = DIRT
                    #swap the item that was there before
                    inventory[currentTile] += 1
            elif event.key == K_SPACE:
                # what resource is the player standing on?
                currentTile = tilemap[playerPos[1]][playerPos[0]]
                # player now has 1 more of this resource
                inventory[currentTile] += 1
                # the player is now standing on dirt
                tilemap[playerPos[1]][playerPos[0]] = DIRT


    keys = pygame.key.get_pressed()
    # if the right arrow is pressed
    if (keys[K_RIGHT] or keys[K_d]):
        # change the player's x position
        playerPos[0] += 1
    if (keys[K_LEFT] or keys[K_a]):
        # change the player's x position
        playerPos[0] -= 1
    if (keys[K_UP] or keys[K_w]):
        # change the player's x position
        playerPos[1] -= 1
    if (keys[K_DOWN] or keys[K_s]):
        # change the player's x position
        playerPos[1] += 1

    #display the inventory, starting 10 pixels in
    placePosition = 10
    for item in resources:
        #add the image
        DISPLAYSURF.blit(textures[item],(placePosition,MAPHEIGHT*TILESIZE+20))
        placePosition += 30
        #add the text showing the amount in the inventory
        textObj = INVFONT.render(str(inventory[item]), True, WHITE, BLACK)
        DISPLAYSURF.blit(textObj,(placePosition,MAPHEIGHT*TILESIZE+20))
        placePosition += 50

    updateMap(playerPos[0], playerPos[1])
    DISPLAYSURF.blit(PLAYER, (int(MAPWIDTH / 2)*TILESIZE, int(MAPHEIGHT / 2)*TILESIZE))

    # update the display
    pygame.display.update()

    mapClock.tick(60)
