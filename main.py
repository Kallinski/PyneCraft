import pygame, sys, random, math, sqlite3, json
from pygame.locals import *
from opensimplex import OpenSimplex

gen = OpenSimplex(seed=random.randint(0, 99999999999))
def noise(nx, ny):
    # Rescale from -1.0:+1.0 to 0.0:1.0
    return gen.noise2d(nx, ny) / 2.0 + 0.5

DEBUG = False

#constants representing colours
BLACK = (0,   0,   0  )
BROWN = (153, 76,  0  )
GREEN = (0,   255, 0  )
BLUE  = (0,   0,   255)
WHITE = (255, 255, 255)

#constants representing the different resources
DIRT   = 0
GRASS  = 1
DGRASS  = 2
WATER  = 3
STONE  = 4
SAND = 5

TREE = 6

WOOD = 0

resourceTextures =  {
                    WOOD: pygame.image.load('wood.png'),
                    }

inventory = {
            WOOD: 0
            }

textures =  {
            DIRT: pygame.image.load('dirt1.png'),
            GRASS: pygame.image.load('grass1.png'),
            DGRASS: pygame.image.load('grass3.png'),
            WATER: pygame.image.load('water1.png'),
            STONE: pygame.image.load('stone1.png'),
            SAND: pygame.image.load('sand1.png'),
            TREE: pygame.image.load('tree2.png'),
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
TPS = 64 #tiles per chunk
MAX_CHUNKS = 4 + int(MAPWIDTH / TPS) * int(MAPHEIGHT / TPS)

FSCREEN = False

resources = [WOOD]
PLAYER_ORIG = pygame.image.load('player.png')
PLAYER = PLAYER_ORIG
SELECTION = pygame.image.load('selection.png')
tilemap = [ [DIRT for w in range(MAPWIDTH)] for h in range(MAPHEIGHT) ]
treemap = [ [None for w in range(MAPWIDTH)] for h in range(MAPHEIGHT) ]

chunksGround = {}
chunksObjects = {}

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

    def selectNearestTile(self, x, y):
        playerX = int(MAPWIDTH / 2) * TILESIZE
        playerY = int(MAPHEIGHT / 2) * TILESIZE

        if  x >= playerX - TILESIZE and x < playerX + 2*TILESIZE and \
            y >= playerY - TILESIZE and y < playerY + 2*TILESIZE:

            nx = int(x / TILESIZE)
            ny = int(y / TILESIZE)

            DISPLAYSURF.blit(SELECTION, (nx * TILESIZE, ny * TILESIZE))

            self.currentSelectionX = nx
            self.currentSelectionY = ny

    def getCurrentSelection(self):
        return (self.currentSelectionX, self.currentSelectionY)

    def update(self):
        DISPLAYSURF.blit(PLAYER, (int(MAPWIDTH / 2) * TILESIZE, int(MAPHEIGHT / 2) * TILESIZE))

class Inventory():
    def update(self):
        # display the inventory, starting 10 pixels in
        placePosition = 10
        for item in resources:
            # add the image
            DISPLAYSURF.blit(resourceTextures[item], (placePosition, MAPHEIGHT * TILESIZE + 20))
            placePosition += 50
            # add the text showing the amount in the inventory
            textObj = INVFONT.render(str(inventory[item]), True, WHITE, BLACK)
            DISPLAYSURF.blit(textObj, (placePosition, MAPHEIGHT * TILESIZE + 20))
            placePosition += 50

class Map():
    def __init__(self):
        global gen, tilemap
        # initial map
        self.update(0, 0)
        startTile = tilemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2)]
        while startTile == WATER:
            gen = OpenSimplex(seed=random.randint(0, 99999999999))
            self.update(0, 0)
            startTile = tilemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2)]

    def worldCoordinatesToChunk(self, x, y):
        xChunk = int(x / TPS)
        yChunk = int(y / TPS)

        if x < 0: xChunk -= 1
        if y < 0: yChunk -= 1
        return xChunk, yChunk

    def generateChunk(self, x, y):
        id = str(x)+","+str(y)
        App.c.execute('''SELECT id FROM map WHERE id=?''', (id,))

        if App.c.fetchone() == None:

            ground = [[DIRT for w in range(TPS)] for h in range(TPS)]
            objects = [ [None for w in range(TPS)] for h in range(TPS) ]
            for row in range(0,TPS):
                for column in range(0,TPS):

                    kx = (x*TPS + column) / MAPWIDTH# - 0.5
                    ky = (y*TPS + row) / MAPHEIGHT# - 0.5

                    e, v = self.noiseParameter(kx, ky)

                    tile = self.biome(e, v)

                    ground[row][column] = tile

                    plants = 0.25 * noise(4 * kx, 2 * ky)
                    if plants > 0.1 and plants < 0.11 and tile != WATER and tile != STONE:
                        objects[row][column] = TREE
                    else:
                        objects[row][column] = None
            App.c.execute('''INSERT INTO map(id, x, y, ground, objects) VALUES(?,?,?,?,?)''', (str(x)+","+str(y), x, y, json.dumps(ground), json.dumps(objects)))
            App.conn.commit()

            return ground, objects

    def loadChunk(self, x, y):
        id = str(x) + "," + str(y)
        App.c.execute('''SELECT id FROM map WHERE id=?''', (id,))
        res = App.c.fetchone()

        if res != None:

            App.c.execute('''SELECT ground FROM map WHERE id=?''', (id,))
            ground = json.loads(App.c.fetchone()[0])

            App.c.execute('''SELECT objects FROM map WHERE id=?''', (id,))
            objects = json.loads(App.c.fetchone()[0])

        else:

            ground, objects = self.generateChunk(x, y)

        chunksGround.update({str(x)+","+str(y): ground})
        chunksObjects.update({str(x)+","+str(y): objects})


        return ground, objects

    def unloadChunk(self, x, y):
        chunksGround.pop(str(x)+","+str(y), None)
        chunksObjects.pop(str(x)+","+str(y), None)

    def update(self, xPos, yPos):

        neededChunks = []

        for row in range(MAPHEIGHT):
            for column in range(MAPWIDTH):
                cx, cy = self.worldCoordinatesToChunk(xPos + column, yPos + row)
                neededChunks.append(str(cx)+","+str(cy))
                if chunksGround.get(str(cx)+","+str(cy)) != None and chunksObjects.get(str(cx)+","+str(cy)) != None:
                    ground = chunksGround.get(str(cx)+","+str(cy))
                    objects = chunksObjects.get(str(cx)+","+str(cy))
                else:
                    ground, objects = self.loadChunk(cx, cy)

                chunkX = (xPos+column) % TPS
                chunkY = (yPos+row) % TPS

                tile = ground[chunkY][chunkX]
                object = objects[chunkY][chunkX]

                tilemap[row][column] = tile
                treemap[row][column] = object

                DISPLAYSURF.blit(textures[tile], (column * TILESIZE, row * TILESIZE))
                if object != None:
                    DISPLAYSURF.blit(textures[object], (column * TILESIZE, row * TILESIZE))

                if DEBUG == True:
                    textObj = INVFONT.render(str(xPos+column)+","+str(yPos+row), True, WHITE, BLACK)
                    DISPLAYSURF.blit(textObj, (column * TILESIZE, row * TILESIZE))

                    textObj = INVFONT.render(str(chunkX) + "," + str(chunkY), True, BLACK, WHITE)
                    DISPLAYSURF.blit(textObj, (column * TILESIZE, row * TILESIZE+10))

                    textObj = INVFONT.render(str(cx) + "," + str(cy), True, BLACK, GREEN)
                    DISPLAYSURF.blit(textObj, (column * TILESIZE, row * TILESIZE + 20))



    def biome(self, e, v):
        if e < 0.4: return WATER
        if e < 0.45: return SAND

        if e < 0.6:
            if v < 0.5: return DGRASS
            return GRASS
        if e < 0.7:
            if v < 0.2: return SAND
            return DGRASS
        if e < 0.8:
            if v < 0.8: return DIRT
            return STONE
        return STONE

    def noiseParameter(self, kx, ky):
        # elevation
        e = 0.5 * noise(0.5 * kx, 0.5 * ky) \
            + 0.4 * noise(2 * kx, 2 * ky) \
            + 0.1 * noise(2 * kx, 2 * ky)

        v = 0.6 * noise(0.5 * kx, 0.5 * ky) \
            + 0.3 * noise(2 * kx, 2 * ky) \
            + 0.2 * noise(2 * kx, 2 * ky)

        return e,v

class App():
    def __init__(self):
        global DISPLAYSURF, INVFONT, CLOCK
        # set up the display
        pygame.init()
        modes = pygame.display.list_modes(16)
        DISPLAYSURF = pygame.display.set_mode((MAPWIDTH * TILESIZE, MAPHEIGHT * TILESIZE + HEIGHT_OFF))
        # add a font for our inventory
        INVFONT = pygame.font.Font('Font.ttf', 8)
        CLOCK = pygame.time.Clock()

        App.conn = sqlite3.connect('map.db')
        App.c = self.conn.cursor()
        App.c.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='map';''')
        res = App.c.fetchall()
        if ('map',) in res:
            App.c.execute('''DROP TABLE map''')
        App.c.execute('''CREATE TABLE map (id string, x int, y int, ground blob, objects blob, PRIMARY KEY (id))''')

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

        # diagonal
        if (keys[K_w] and keys[K_d]) \
             and tilemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2) + 1] != WATER \
             and treemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2) + 1] != TREE:
            self.player.move(+1, -1)

        elif (keys[K_w] and keys[K_a]) \
             and tilemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2) - 1] != WATER \
             and treemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2) - 1] != TREE:
            self.player.move(-1, -1)

        elif (keys[K_s] and keys[K_d]) \
             and tilemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2) + 1] != WATER \
             and treemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2) + 1] != TREE:
            self.player.move(+1, +1)
        elif (keys[K_s] and keys[K_a]) \
             and tilemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2) - 1] != WATER \
             and treemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2) - 1] != TREE:
            self.player.move(-1, +1)

        elif (keys[K_d]) \
                and tilemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) + 1] != WATER \
                and treemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) + 1] != TREE:
            self.player.move(+1, 0)
        elif (keys[K_a]) \
                and tilemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) - 1] != WATER \
                and treemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) - 1] != TREE:
            self.player.move(-1, 0)
        elif (keys[K_w]) \
                and tilemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2)] != WATER \
                and treemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2)] != TREE:
            self.player.move(0, -1)
        elif (keys[K_s]) \
                and tilemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2)] != WATER \
                and treemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2)] != TREE:
            self.player.move(0, +1)



    def OnKeydownEvent(self, key):
        global DISPLAYSURF
        if key == K_e:
            x, y = self.player.getCurrentSelection()
            currentRes = treemap[y][x]
            if currentRes == TREE:
                # player now has 1 more of this resource
                inventory[WOOD] += 1

        elif key == K_ESCAPE:
            pygame.quit()
            sys.exit()
        elif key == K_F11:
            global FSCREEN
            FSCREEN = not FSCREEN
            if FSCREEN:
                DISPLAYSURF = pygame.display.set_mode((MAPWIDTH * TILESIZE, MAPHEIGHT * TILESIZE + HEIGHT_OFF), FULLSCREEN)
            else:
                DISPLAYSURF = pygame.display.set_mode((MAPWIDTH * TILESIZE, MAPHEIGHT * TILESIZE + HEIGHT_OFF))

        elif key == K_F12:
            global DEBUG
            DEBUG = not DEBUG

    def OnMouseMovement(self, x, y):
        angle = self.player.rotateTo(x, y)
        self.player.selectNearestTile(x, y)

    def loop(self):

        self.map.generateChunk(0, 0)
        self.map.loadChunk(0, 0)

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
