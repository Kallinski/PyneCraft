import pygame, sys, random, math, sqlite3, json, os
from pygame.locals import *
from opensimplex import OpenSimplex

RANDSEED = random.randint(0, 99999999999)
SEED = 0

gen = OpenSimplex(seed=SEED)
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
DIRT1   = 101
DIRT2 = 102

GRASS1  = 201
GRASS2  = 202
GRASS3  = 203
GRASS_B = 205
GRASS_BL = 206
GRASS_BR = 207
GRASS_L = 208
GRASS_R = 209
GRASS_T = 210
GRASS_TL = 211
GRASS_TR = 212
GRASS_TRB = 213
GRASS_TLB = 214
GRASS_BRB = 215
GRASS_BLB = 216

DGRASS1  = 301
DGRASS2  = 302
DGRASS3  = 303

WATER1  = 401
WATER2  = 402
WATER3  = 403
WATER4 = 404
WATER_B = 405
WATER_BL = 406
WATER_BR = 407
WATER_L = 408
WATER_R = 409
WATER_T = 410
WATER_TL = 411
WATER_TR = 412
WATER_TRB = 413
WATER_TLB = 414
WATER_BRB = 415
WATER_BLB = 416

STONE1  = 501
STONE2  = 502

SAND1 = 601
SAND2 = 602
SAND3 = 603
SAND4 = 604

TREE1 = 1001
TREE2 = 1002

WOOD = 2001

if not os.path.isdir("data/savegames/"): os.makedirs("data/savegames/")
if not os.path.isdir("data/textures/"): os.makedirs("data/textures/")

resourceTextures =  {
                    WOOD: pygame.image.load("data/textures/wood.png"),
                    }

textures =  {
            DIRT1: pygame.image.load('data/textures/dirt1.png'),
            DIRT2: pygame.image.load('data/textures/dirt2.png'),

            GRASS1: pygame.image.load('data/textures/grass1.png'),
            GRASS2: pygame.image.load('data/textures/grass2.png'),
            GRASS3: pygame.image.load('data/textures/grass3.png'),
            GRASS_B: pygame.image.load('data/textures/grass_b.png'),
            GRASS_BL: pygame.image.load('data/textures/grass_bl.png'),
            GRASS_BR: pygame.image.load('data/textures/grass_br.png'),
            GRASS_L: pygame.image.load('data/textures/grass_l.png'),
            GRASS_R: pygame.image.load('data/textures/grass_r.png'),
            GRASS_T: pygame.image.load('data/textures/grass_t.png'),
            GRASS_TL: pygame.image.load('data/textures/grass_tl.png'),
            GRASS_TR: pygame.image.load('data/textures/grass_tr.png'),
            GRASS_TRB: pygame.image.load('data/textures/grass_trb.png'),
            GRASS_TLB: pygame.image.load('data/textures/grass_tlb.png'),
            GRASS_BRB: pygame.image.load('data/textures/grass_brb.png'),
            GRASS_BLB: pygame.image.load('data/textures/grass_blb.png'),

            DGRASS1: pygame.image.load('data/textures/dgrass1.png'),
            DGRASS2: pygame.image.load('data/textures/dgrass2.png'),
            DGRASS3: pygame.image.load('data/textures/dgrass3.png'),

            WATER1: pygame.image.load('data/textures/water1.png'),
            WATER2: pygame.image.load('data/textures/water2.png'),
            WATER3: pygame.image.load('data/textures/water3.png'),
            WATER4: pygame.image.load('data/textures/water4.png'),
            WATER_B: pygame.image.load('data/textures/water_b.png'),
            WATER_BL: pygame.image.load('data/textures/water_bl.png'),
            WATER_BR: pygame.image.load('data/textures/water_br.png'),
            WATER_L: pygame.image.load('data/textures/water_l.png'),
            WATER_R: pygame.image.load('data/textures/water_r.png'),
            WATER_T: pygame.image.load('data/textures/water_t.png'),
            WATER_TL: pygame.image.load('data/textures/water_tl.png'),
            WATER_TR: pygame.image.load('data/textures/water_tr.png'),
            WATER_TRB: pygame.image.load('data/textures/water_trb.png'),
            WATER_TLB: pygame.image.load('data/textures/water_tlb.png'),
            WATER_BRB: pygame.image.load('data/textures/water_brb.png'),
            WATER_BLB: pygame.image.load('data/textures/water_blb.png'),

            STONE1: pygame.image.load('data/textures/stone1.png'),
            STONE2: pygame.image.load('data/textures/stone2.png'),

            SAND1: pygame.image.load('data/textures/sand1.png'),
            SAND2: pygame.image.load('data/textures/sand2.png'),
            SAND3: pygame.image.load('data/textures/sand3.png'),
            SAND4: pygame.image.load('data/textures/sand4.png'),

            TREE1: pygame.image.load('data/textures/tree1.png'),
            TREE2: pygame.image.load('data/textures/tree2.png'),
            }

G_WATER = [WATER1,WATER2,WATER3,WATER4]
G_WATER_ALL = [WATER1,WATER2,WATER3,WATER4,WATER_B,WATER_BL,WATER_BR,WATER_T,WATER_TL,WATER_TR,WATER_R,WATER_L,
               WATER_TRB,WATER_BRB,WATER_TLB,WATER_BLB]
G_SAND = [SAND1,SAND2,SAND3,SAND4]
G_GRASS = [GRASS1,GRASS2,GRASS3]
G_DGRASS = [DGRASS1,DGRASS2,DGRASS3]

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
PLAYER_ORIG = pygame.image.load('data/textures/player.png')
PLAYER = PLAYER_ORIG
SELECTION = pygame.image.load('data/textures/selection.png')
BOTTOM_BAR = pygame.image.load('data/textures/bottom_bar.png')
tilemap = [ [DIRT1 for w in range(MAPWIDTH)] for h in range(MAPHEIGHT) ]
treemap = [ [None for w in range(MAPWIDTH)] for h in range(MAPHEIGHT) ]

chunksGround = {}
chunksObjects = {}

class Player():
    def __init__(self, id=-1, x=0, y=0, inventory={str(WOOD): 0}):
        self.xPos = x
        self.yPos = y
        self.inventory = Inventory(inventory)

        if id == -1:
            App.c.execute('''INSERT INTO player(id, lastX, lastY, inventory) VALUES(?,?,?,?)''', (0, 0, 0, json.dumps(self.inventory.items)))
            App.conn.commit()

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
        DISPLAYSURF.blit(PLAYER, (int(MAPWIDTH / 2) * TILESIZE, int(MAPHEIGHT / 2) * TILESIZE))

class Inventory():

    def __init__(self, inventory={str(WOOD): 0}):
        self.items = inventory

    def add(self, item, amount):
        self.items.update({str(item): self.items.get(str(item))+amount})

    def get(self, item):
        return self.items.get(str(item))

    def update(self):
        # display the inventory, starting 10 pixels in
        placePosition = 10
        for item in resources:
            # add the image
            DISPLAYSURF.blit(resourceTextures[item], (placePosition, MAPHEIGHT * TILESIZE + 25))
            placePosition += 40
            # add the text showing the amount in the inventory
            textObj = INVFONT.render(str(self.items.get(str(item))), True, BLACK, None)
            DISPLAYSURF.blit(textObj, (placePosition, MAPHEIGHT * TILESIZE + 20))
            placePosition += 50

class Map():
    def __init__(self, x=0, y=0):
        global gen, tilemap
        # initial map
        self.update(x, y)

    def worldCoordinatesToChunk(self, x, y):
        if x < 0:
            xChunk = int((x-TPS+1) / TPS)
        else:
            xChunk = int(x / TPS)

        if y < 0:
            yChunk = int((y-TPS+1) / TPS)
        else:
            yChunk = int(y / TPS)

        return xChunk, yChunk

    def generateChunk(self, x, y):
        id = str(x)+","+str(y)
        App.c.execute('''SELECT id FROM map WHERE id=?''', (id,))

        if App.c.fetchone() == None:

            ground = [[DIRT1 for w in range(TPS)] for h in range(TPS)]
            objects = [ [None for w in range(TPS)] for h in range(TPS) ]
            for row in range(0,TPS):
                for column in range(0,TPS):

                    kx = (x*(TPS) + column) / MAPWIDTH# - 0.5
                    ky = (y*(TPS) + row) / MAPHEIGHT# - 0.5

                    e = self.noiseParameter(kx, ky)

                    tile = self.biome(e)

                    ground[row][column] = tile

                    if  tile not in G_WATER_ALL and \
                        tile not in [STONE1,STONE2] and \
                        tile not in G_SAND:
                            if tile in G_GRASS and random.randint(0,60) == 0:
                                objects[row][column] = TREE1+random.randint(0,1)
                            elif tile in G_DGRASS and random.randint(0,1) == 0:
                                objects[row][column] = TREE1+random.randint(0, 1)
                    else:
                        objects[row][column] = None

                    tr = self.biome(self.noiseParameter((x * (TPS) + column + 1) / MAPWIDTH, (y * (TPS) + row - 1) / MAPHEIGHT))
                    r = self.biome(self.noiseParameter((x * (TPS) + column + 1) / MAPWIDTH, (y * (TPS) + row) / MAPHEIGHT))
                    br = self.biome(self.noiseParameter((x * (TPS) + column + 1) / MAPWIDTH, (y * (TPS) + row + 1) / MAPHEIGHT))
                    tl = self.biome(self.noiseParameter((x * (TPS) + column - 1) / MAPWIDTH, (y * (TPS) + row - 1) / MAPHEIGHT))
                    l = self.biome(self.noiseParameter((x * (TPS) + column - 1) / MAPWIDTH, (y * (TPS) + row) / MAPHEIGHT))
                    bl = self.biome(self.noiseParameter((x * (TPS) + column - 1) / MAPWIDTH, (y * (TPS) + row + 1) / MAPHEIGHT))
                    t = self.biome(self.noiseParameter((x * (TPS) + column) / MAPWIDTH, (y * (TPS) + row - 1) / MAPHEIGHT))
                    b = self.biome(self.noiseParameter((x * (TPS) + column) / MAPWIDTH, (y * (TPS) + row + 1) / MAPHEIGHT))

                    if tile in G_WATER:
                        if      r in G_SAND and tl in G_WATER and l in G_WATER and \
                                bl in G_WATER and t in G_WATER and b in G_WATER:
                                    ground[row][column] = WATER_R
                        elif    tr in G_SAND and r in G_WATER and br in G_WATER and tl in G_WATER and \
                                l in G_WATER and bl in G_WATER and t in G_WATER and b in G_WATER:
                                    ground[row][column] = WATER_TR
                        elif    tr in G_SAND and r in G_SAND and l in G_WATER and \
                                bl in G_WATER and t in G_SAND and b in G_WATER:
                                    ground[row][column] = WATER_TRB
                        elif    r in G_SAND and br in G_SAND and tl in G_WATER and \
                                l in G_WATER and t in G_WATER and  b in G_SAND:
                                    ground[row][column] = WATER_BRB
                        elif    tr in G_WATER and r in G_WATER and br in G_WATER and \
                                l in G_SAND and t in G_WATER and b in G_WATER:
                                    ground[row][column] = WATER_L
                        elif    tr in G_WATER and r in G_WATER and br in G_WATER and tl in G_WATER and \
                                l in G_WATER and bl in G_SAND and t in G_WATER and b in G_WATER:
                                    ground[row][column] = WATER_BL
                        elif    tr in G_WATER and r in G_WATER and br in G_WATER and tl in G_SAND and \
                                l in G_WATER and bl in G_WATER and t in G_WATER and b in G_WATER:
                                    ground[row][column] = WATER_TL
                        elif    r in G_WATER and br in G_WATER and tl in G_SAND and \
                                l in G_SAND and t in G_SAND and b in G_WATER:
                                    ground[row][column] = WATER_TLB
                        elif    tr in G_WATER and r in G_WATER and l in G_SAND and \
                                bl in G_SAND and t in G_WATER and b in G_SAND:
                                    ground[row][column] = WATER_BLB
                        elif    tr in G_WATER and r in G_WATER and tl in G_WATER and \
                                l in G_WATER and t in G_WATER and b in G_SAND:
                                    ground[row][column] = WATER_B
                        elif    r in G_WATER and br in G_WATER and l in G_WATER and \
                                bl in G_WATER and t in G_SAND and b in G_WATER:
                                    ground[row][column] = WATER_T
                        elif    tr in G_WATER and br in G_SAND and tl in G_WATER and \
                                l in G_WATER and bl in G_WATER and t in G_WATER:
                                    ground[row][column] = WATER_BR
                    elif tile in G_SAND:
                        if      r in G_GRASS and tl in G_SAND and l in G_SAND and \
                                bl in G_SAND and t in G_SAND and b in G_SAND:
                                    ground[row][column] = GRASS_R
                        elif    tr in G_GRASS and r in G_SAND and br in G_SAND and tl in G_SAND and \
                                l in G_SAND and bl in G_SAND and t in G_SAND and b in G_SAND:
                                    ground[row][column] = GRASS_TR
                        elif    tr in G_GRASS and r in G_GRASS and l in G_SAND and \
                                bl in G_SAND and t in G_GRASS and b in G_SAND:
                                    ground[row][column] = GRASS_TRB
                        elif    r in G_GRASS and br in G_GRASS and tl in G_SAND and \
                                l in G_SAND and t in G_SAND and  b in G_GRASS:
                                    ground[row][column] = GRASS_BRB
                        elif    tr in G_SAND and r in G_SAND and br in G_SAND and \
                                l in G_GRASS and t in G_SAND and b in G_SAND:
                                    ground[row][column] = GRASS_L
                        elif    tr in G_SAND and r in G_SAND and br in G_SAND and tl in G_SAND and \
                                l in G_SAND and bl in G_GRASS and t in G_SAND and b in G_SAND:
                                    ground[row][column] = GRASS_BL
                        elif    tr in G_SAND and r in G_SAND and br in G_SAND and tl in G_GRASS and \
                                l in G_SAND and bl in G_SAND and t in G_SAND and b in G_SAND:
                                    ground[row][column] = GRASS_TL
                        elif    r in G_SAND and br in G_SAND and tl in G_GRASS and \
                                l in G_GRASS and t in G_GRASS and b in G_SAND:
                                    ground[row][column] = GRASS_TLB
                        elif    tr in G_SAND and r in G_SAND and l in G_GRASS and \
                                bl in G_GRASS and t in G_SAND and b in G_GRASS:
                                    ground[row][column] = GRASS_BLB
                        elif    tr in G_SAND and r in G_SAND and tl in G_SAND and \
                                l in G_SAND and t in G_SAND and b in G_GRASS:
                                    ground[row][column] = GRASS_B
                        elif    r in G_SAND and br in G_SAND and l in G_SAND and \
                                bl in G_SAND and t in G_GRASS and b in G_SAND:
                                    ground[row][column] = GRASS_T
                        elif    tr in G_SAND and br in G_GRASS and tl in G_SAND and \
                                l in G_SAND and bl in G_SAND and t in G_SAND:
                                    ground[row][column] = GRASS_BR


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

        xPos -= int(MAPWIDTH / 2)
        yPos -= int(MAPHEIGHT / 2)

        if DEBUG == True:
            INVFONT = pygame.font.Font('data/Font.ttf', 8)

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



    def biome(self, e):
        if e < 0.5: return WATER1+random.randint(0,3)
        if e < 0.58: return SAND1+random.randint(0,3)
        if e < 0.7: return GRASS1+random.randint(0,2)
        return DGRASS1+random.randint(0,2)

    def noiseParameter(self, kx, ky):
        # elevation
        e = 0.8 * noise(0.5 * kx, 0.5 * ky) \
            + 0.2 * noise(2 * kx, 2 * ky) #\
            #+ 0.1 * noise(2 * kx, 2 * ky)

        return e

class App():
    def __init__(self):
        global DISPLAYSURF, INVFONT, CLOCK
        # set up the display
        pygame.init()
        modes = pygame.display.list_modes(16)
        DISPLAYSURF = pygame.display.set_mode((MAPWIDTH * TILESIZE, MAPHEIGHT * TILESIZE + HEIGHT_OFF))
        # add a font for our inventory
        INVFONT = pygame.font.Font('data/Font.ttf', 13)
        CLOCK = pygame.time.Clock()

        if not os.path.isfile("data/savegames/"+str(SEED)+'.db'):
            if not os.path.isdir("data/savegames/"): os.makedirs("/savegames/")
            App.conn = sqlite3.connect("data/savegames/"+str(SEED)+'.db')
            App.c = self.conn.cursor()
            App.c.execute('''CREATE TABLE map (id string, x int, y int, ground blob, objects blob, PRIMARY KEY (id))''')
            App.c.execute('''CREATE TABLE player (id int, lastX int, lastY int, inventory blob, PRIMARY KEY (id))''')

            self.map = Map()
            self.player = Player()

        else:
            App.conn  = sqlite3.connect("data/savegames/"+str(SEED)+'.db')
            App.c = self.conn.cursor()
            App.c.execute('''SELECT lastX, lastY, inventory FROM player WHERE id=0''')
            res = App.c.fetchall()
            x = res[0][0]
            y = res[0][1]
            inventory = json.loads(res[0][2])

            self.map = Map(x, y)
            self.player = Player(0, x, y, inventory)

        self.loop()

    def save(self):
        for key in chunksGround:
            ground = chunksGround.get(key)
            objects = chunksObjects.get(key)
            App.c.execute('''UPDATE map SET ground=?, objects=? WHERE id=?''',(json.dumps(ground), json.dumps(objects), key))
            App.c.execute('''UPDATE player SET lastX=?, lastY=?, inventory=? WHERE id=0''', (self.player.xPos, self.player.yPos, json.dumps(self.player.inventory.items)))
            App.conn.commit()

    def OnEvent(self, event):
            # if the user wants to quit
            if event.type == QUIT:
                # and the game and close the window
                self.save()
                pygame.quit()
                sys.exit()
            # if a key is pressed
            elif event.type == KEYDOWN:
                self.OnKeydownEvent(event.key)

    def OnKeysPressed(self, keys):

        # diagonal
        if (keys[K_w] and keys[K_d]) \
             and tilemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2) + 1] not in G_WATER_ALL \
             and treemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2) + 1] not in [TREE1, TREE2]:
            self.player.move(+1, -1)

        elif (keys[K_w] and keys[K_a]) \
             and tilemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2) - 1] not in G_WATER_ALL \
             and treemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2) - 1] not in [TREE1, TREE2]:
            self.player.move(-1, -1)

        elif (keys[K_s] and keys[K_d]) \
             and tilemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2) + 1] not in G_WATER_ALL \
             and treemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2) + 1] not in [TREE1, TREE2]:
            self.player.move(+1, +1)
        elif (keys[K_s] and keys[K_a]) \
             and tilemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2) - 1] not in G_WATER_ALL \
             and treemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2) - 1] not in [TREE1, TREE2]:
            self.player.move(-1, +1)

        elif (keys[K_d]) \
                and tilemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) + 1] not in G_WATER_ALL \
                and treemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) + 1] not in [TREE1, TREE2]:
            self.player.move(+1, 0)
        elif (keys[K_a]) \
                and tilemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) - 1] not in G_WATER_ALL \
                and treemap[int(MAPHEIGHT / 2)][int(MAPWIDTH / 2) - 1] not in [TREE1, TREE2]:
            self.player.move(-1, 0)
        elif (keys[K_w]) \
                and tilemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2)] not in G_WATER_ALL \
                and treemap[int(MAPHEIGHT / 2) - 1][int(MAPWIDTH / 2)] not in [TREE1, TREE2]:
            self.player.move(0, -1)
        elif (keys[K_s]) \
                and tilemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2)] not in G_WATER_ALL \
                and treemap[int(MAPHEIGHT / 2) + 1][int(MAPWIDTH / 2)] not in [TREE1, TREE2]:
            self.player.move(0, +1)



    def OnKeydownEvent(self, key):
        global DISPLAYSURF
        if key == K_e:
            x, y = self.player.getCurrentSelection()
            playerX = int(MAPWIDTH / 2)
            playerY = int(MAPHEIGHT / 2)
            offX = x - playerX
            offY = y - playerY
            currentRes = treemap[y][x]
            cX, cY = self.map.worldCoordinatesToChunk(self.player.xPos + offX, self.player.yPos + offY)
            relX = (self.player.xPos+offX) % TPS
            relY = (self.player.yPos+offY) % TPS
            if currentRes in [TREE1, TREE2]:
                # player now has 1 more of this resource
                self.player.inventory.add(WOOD, 1)
                objects = chunksObjects.get(str(cX)+","+str(cY))
                objects[relY][relX] = None
                chunksObjects.update({str(cX)+","+str(cY): objects})

        elif key == K_f:
            x, y = self.player.getCurrentSelection()
            playerX = int(MAPWIDTH / 2)
            playerY = int(MAPHEIGHT / 2)
            offX = x - playerX
            offY = y - playerY
            cT = tilemap[y][x]
            currentObj = treemap[y][x]
            cX, cY = self.map.worldCoordinatesToChunk(self.player.xPos + offX, self.player.yPos + offY)
            relX = (self.player.xPos + offX) % TPS
            relY = (self.player.yPos + offY) % TPS
            if currentObj not in [TREE1, TREE2] and \
                cT not in [WATER1,WATER2,WATER3] and \
                cT not in [STONE1,STONE2] and \
                self.player.inventory.get(WOOD) > 0:
                    # player now has 1 more of this resource
                    self.player.inventory.add(WOOD, -1)
                    objects = chunksObjects.get(str(cX) + "," + str(cY))
                    objects[relY][relX] = TREE1+random.randint(0,1)
                    chunksObjects.update({str(cX) + "," + str(cY): objects})

        elif key == K_ESCAPE:
            self.save()
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

    def update_bottomBar(self):
        for i in range(MAPWIDTH):
            DISPLAYSURF.blit(BOTTOM_BAR, (i*TILESIZE, MAPHEIGHT*TILESIZE))

    def loop(self):
        chunkX, chunkY = self.map.worldCoordinatesToChunk(self.player.xPos, self.player.yPos)
        self.map.loadChunk(chunkX, chunkY)

        while True:
            DISPLAYSURF.fill(BLACK)
            for event in pygame.event.get():
                self.OnEvent(event)

            self.OnKeysPressed(pygame.key.get_pressed())

            self.update_bottomBar()
            self.map.update(self.player.xPos, self.player.yPos)
            self.player.update()
            self.player.inventory.update()

            x, y = pygame.mouse.get_pos()
            self.OnMouseMovement(x, y)

            # update the display
            pygame.display.update()
            CLOCK.tick(60)

if __name__ == '__main__':
    app = App()
